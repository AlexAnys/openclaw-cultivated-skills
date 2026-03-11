#!/usr/bin/env python3
"""
Batch trigger accuracy evaluation for skills.

For each skill, auto-generates eval queries using Claude, then tests trigger
accuracy by running queries against `claude -p` and checking whether the
Skill tool is invoked.

Usage:
    python -m pipeline.batch_trigger_eval --skills-dir <dir> --output report.json --workers 4
"""

import argparse
import json
import os
import re
import select
import subprocess
import sys
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# SKILL.md parsing (self-contained)
# ---------------------------------------------------------------------------

def _parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter (no opening ---)")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing frontmatter (no closing ---)")

    name = ""
    description = ""
    frontmatter_lines = lines[1:end_idx]
    i = 0
    while i < len(frontmatter_lines):
        line = frontmatter_lines[i]
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip("\"'")
        elif line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value in (">", "|", ">-", "|-"):
                continuation: list[str] = []
                i += 1
                while i < len(frontmatter_lines) and (
                    frontmatter_lines[i].startswith("  ") or frontmatter_lines[i].startswith("\t")
                ):
                    continuation.append(frontmatter_lines[i].strip())
                    i += 1
                description = " ".join(continuation)
                continue
            else:
                description = value.strip("\"'")
        i += 1

    return name, description, content


# ---------------------------------------------------------------------------
# Eval query generation via claude -p
# ---------------------------------------------------------------------------

QUERY_GENERATION_PROMPT = """\
You are generating evaluation queries for a Claude Code skill trigger test.

Skill name: {name}
Skill description: {description}

Generate exactly 20 JSON objects in a JSON array. Each object has:
- "query": a realistic user query (concrete, specific, with file paths, personal context, realistic details)
- "should_trigger": boolean

Requirements:
- 10 queries where should_trigger=true (the skill SHOULD be triggered)
- 10 queries where should_trigger=false (the skill should NOT be triggered)
- should_trigger=true queries must clearly relate to the skill's purpose
- should_trigger=false queries must be plausible user queries that are adjacent but outside the skill's scope
- Include edge cases: ambiguous queries, queries with unusual phrasing, queries that mention related but different topics
- Make queries concrete and realistic (include file paths like ./src/app.tsx, personal context like "my React project", specific technical details)
- Vary query length and style (short imperative, longer explanatory, question format)

Output ONLY the JSON array, no other text.
"""


def generate_eval_queries(
    skill_name: str,
    skill_description: str,
    model: str | None = None,
) -> list[dict[str, Any]] | None:
    """Generate eval queries for a skill using claude -p.

    Returns a list of query dicts or None on failure.
    """
    prompt = QUERY_GENERATION_PROMPT.format(name=skill_name, description=skill_description)

    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if model:
        cmd.extend(["--model", model])

    # Remove CLAUDECODE to allow nesting
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Warning: Failed to generate queries: {e}", file=sys.stderr)
        return None

    if result.returncode != 0:
        print(f"Warning: claude -p exited with code {result.returncode}", file=sys.stderr)
        return None

    # Parse the response - try to extract JSON array from the output
    output = result.stdout.strip()

    # The output may be wrapped in a JSON response object
    try:
        response = json.loads(output)
        # If claude --output-format json wraps in {"result": "..."}, extract
        if isinstance(response, dict) and "result" in response:
            output = response["result"]
        elif isinstance(response, list):
            return response
    except json.JSONDecodeError:
        pass

    # Try to find a JSON array in the text
    array_match = re.search(r"\[[\s\S]*\]", output)
    if array_match:
        try:
            queries = json.loads(array_match.group())
            if isinstance(queries, list) and len(queries) > 0:
                return queries
        except json.JSONDecodeError:
            pass

    print(f"Warning: Could not parse eval queries from Claude output", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# Project root discovery (same pattern as run_eval.py)
# ---------------------------------------------------------------------------

def _find_project_root() -> Path:
    """Find the project root by walking up from cwd looking for .claude/."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


# ---------------------------------------------------------------------------
# Single query evaluation (mirrors run_eval.py logic)
# ---------------------------------------------------------------------------

def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
) -> bool:
    """Run a single query and return whether the skill was triggered.

    Creates a temporary command file in .claude/commands/ and runs `claude -p`
    with stream-json output to detect Skill tool invocation.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    project_commands_dir = Path(project_root) / ".claude" / "commands"
    command_file = project_commands_dir / f"{clean_name}.md"

    try:
        project_commands_dir.mkdir(parents=True, exist_ok=True)
        # Use YAML block scalar to avoid breaking on quotes in description
        indented_desc = "\n  ".join(skill_description.split("\n"))
        command_content = (
            f"---\n"
            f"description: |\n"
            f"  {indented_desc}\n"
            f"---\n\n"
            f"# {skill_name}\n\n"
            f"This skill handles: {skill_description}\n"
        )
        command_file.write_text(command_content)

        cmd = [
            "claude",
            "-p", query,
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
        ]
        if model:
            cmd.extend(["--model", model])

        # Remove CLAUDECODE env var to allow nesting
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=project_root,
            env=env,
        )

        triggered = False
        start_time = time.time()
        buffer = ""
        pending_tool_name = None
        accumulated_json = ""

        try:
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    remaining = process.stdout.read()
                    if remaining:
                        buffer += remaining.decode("utf-8", errors="replace")
                    break

                ready, _, _ = select.select([process.stdout], [], [], 1.0)
                if not ready:
                    continue

                chunk = os.read(process.stdout.fileno(), 8192)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8", errors="replace")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Early detection via stream events
                    if event.get("type") == "stream_event":
                        se = event.get("event", {})
                        se_type = se.get("type", "")

                        if se_type == "content_block_start":
                            cb = se.get("content_block", {})
                            if cb.get("type") == "tool_use":
                                tool_name = cb.get("name", "")
                                if tool_name in ("Skill", "Read"):
                                    pending_tool_name = tool_name
                                    accumulated_json = ""
                                else:
                                    return False

                        elif se_type == "content_block_delta" and pending_tool_name:
                            delta = se.get("delta", {})
                            if delta.get("type") == "input_json_delta":
                                accumulated_json += delta.get("partial_json", "")
                                if clean_name in accumulated_json:
                                    return True

                        elif se_type in ("content_block_stop", "message_stop"):
                            if pending_tool_name:
                                return clean_name in accumulated_json
                            if se_type == "message_stop":
                                return False

                    # Fallback: full assistant message
                    elif event.get("type") == "assistant":
                        message = event.get("message", {})
                        for content_item in message.get("content", []):
                            if content_item.get("type") != "tool_use":
                                continue
                            tool_name = content_item.get("name", "")
                            tool_input = content_item.get("input", {})
                            if tool_name == "Skill" and clean_name in tool_input.get("skill", ""):
                                triggered = True
                            elif tool_name == "Read" and clean_name in tool_input.get("file_path", ""):
                                triggered = True
                            return triggered

                    elif event.get("type") == "result":
                        return triggered
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()

        return triggered
    finally:
        if command_file.exists():
            command_file.unlink()


# ---------------------------------------------------------------------------
# Full eval for a single skill
# ---------------------------------------------------------------------------

def evaluate_skill(
    skill_path: Path,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 3,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    regen_queries: bool = False,
) -> dict[str, Any]:
    """Run trigger evaluation for a single skill.

    Generates eval queries if needed, runs them, computes accuracy metrics.
    """
    name, description, _ = _parse_skill_md(skill_path)
    print(f"  Evaluating skill: {name}", file=sys.stderr)

    # Load or generate eval queries
    eval_file = skill_path / "trigger-eval.json"
    eval_set: list[dict[str, Any]] | None = None

    if eval_file.exists() and not regen_queries:
        try:
            eval_set = json.loads(eval_file.read_text())
            print(f"  Loaded {len(eval_set)} existing queries from trigger-eval.json", file=sys.stderr)
        except (json.JSONDecodeError, OSError):
            eval_set = None

    if eval_set is None:
        print(f"  Generating eval queries via claude -p ...", file=sys.stderr)
        eval_set = generate_eval_queries(name, description, model)
        if eval_set is None:
            return {
                "skill_name": name,
                "skill_path": str(skill_path),
                "status": "error",
                "error": "Failed to generate eval queries",
                "results": [],
                "metrics": {},
            }
        # Save for reproducibility
        try:
            eval_file.write_text(json.dumps(eval_set, indent=2))
            print(f"  Saved {len(eval_set)} queries to {eval_file}", file=sys.stderr)
        except OSError as e:
            print(f"  Warning: Could not save eval queries: {e}", file=sys.stderr)

    # Run evaluation
    results: list[dict[str, Any]] = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info: dict[Any, tuple[dict, int]] = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    name,
                    description,
                    timeout,
                    str(project_root),
                    model,
                )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        completed = 0
        total_runs = len(future_to_info)

        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_triggers:
                query_triggers[query] = []
            try:
                query_triggers[query].append(future.result())
            except Exception as e:
                print(f"  Warning: query failed: {e}", file=sys.stderr)
                query_triggers[query].append(False)

            completed += 1
            if completed % 10 == 0 or completed == total_runs:
                print(f"  Progress: {completed}/{total_runs} runs completed", file=sys.stderr)

    # Compute per-query results
    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers) if triggers else 0.0
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold

        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    # Compute aggregate metrics
    true_positives = sum(
        1 for r in results if r["should_trigger"] and r["trigger_rate"] >= trigger_threshold
    )
    false_negatives = sum(
        1 for r in results if r["should_trigger"] and r["trigger_rate"] < trigger_threshold
    )
    true_negatives = sum(
        1 for r in results if not r["should_trigger"] and r["trigger_rate"] < trigger_threshold
    )
    false_positives = sum(
        1 for r in results if not r["should_trigger"] and r["trigger_rate"] >= trigger_threshold
    )

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
    total_queries = len(results)
    correct = true_positives + true_negatives
    accuracy = correct / total_queries if total_queries > 0 else 0.0

    metrics = {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "accuracy": round(accuracy, 4),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "true_negatives": true_negatives,
        "false_negatives": false_negatives,
        "total_queries": total_queries,
        "passed": correct,
        "failed": total_queries - correct,
    }

    return {
        "skill_name": name,
        "skill_path": str(skill_path),
        "description": description,
        "status": "complete",
        "results": results,
        "metrics": metrics,
    }


# ---------------------------------------------------------------------------
# Batch orchestration
# ---------------------------------------------------------------------------

def _find_skills_in_directory(directory: Path) -> list[Path]:
    """Find all skill directories containing SKILL.md."""
    skills: list[Path] = []
    for skill_md in sorted(directory.rglob("SKILL.md")):
        skills.append(skill_md.parent)
    return skills


def batch_trigger_eval(
    skills_dir: Path,
    num_workers: int = 4,
    timeout: int = 30,
    runs_per_query: int = 3,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    regen_queries: bool = False,
) -> list[dict[str, Any]]:
    """Run trigger evaluation for all skills in a directory."""
    project_root = _find_project_root()
    skill_dirs = _find_skills_in_directory(skills_dir)

    if not skill_dirs:
        print(f"No skills found under {skills_dir}", file=sys.stderr)
        return []

    print(f"Found {len(skill_dirs)} skills to evaluate", file=sys.stderr)
    results: list[dict[str, Any]] = []

    for i, skill_dir in enumerate(skill_dirs, 1):
        print(f"\n[{i}/{len(skill_dirs)}] {skill_dir.name}", file=sys.stderr)
        result = evaluate_skill(
            skill_path=skill_dir,
            num_workers=num_workers,
            timeout=timeout,
            project_root=project_root,
            runs_per_query=runs_per_query,
            trigger_threshold=trigger_threshold,
            model=model,
            regen_queries=regen_queries,
        )
        results.append(result)

        # Print per-skill summary
        if result["status"] == "complete":
            m = result["metrics"]
            print(
                f"  => accuracy={m['accuracy']:.0%} precision={m['precision']:.0%} "
                f"recall={m['recall']:.0%} ({m['passed']}/{m['total_queries']} passed)",
                file=sys.stderr,
            )
        else:
            print(f"  => {result['status']}: {result.get('error', 'unknown')}", file=sys.stderr)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch trigger accuracy evaluation for skills",
    )
    parser.add_argument(
        "--skills-dir",
        required=True,
        type=Path,
        help="Directory containing skill subdirectories with SKILL.md files",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON report path (default: stdout)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers for query execution (default: 4)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Timeout per query in seconds (default: 30)",
    )
    parser.add_argument(
        "--runs-per-query",
        type=int,
        default=3,
        help="Number of runs per query for reliability (default: 3)",
    )
    parser.add_argument(
        "--trigger-threshold",
        type=float,
        default=0.5,
        help="Trigger rate threshold for pass/fail (default: 0.5)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model to use for claude -p (default: user's configured model)",
    )
    parser.add_argument(
        "--regen-queries",
        action="store_true",
        help="Regenerate eval queries even if trigger-eval.json exists",
    )
    args = parser.parse_args()

    results = batch_trigger_eval(
        skills_dir=args.skills_dir,
        num_workers=args.workers,
        timeout=args.timeout,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
        regen_queries=args.regen_queries,
    )

    # Build summary
    completed = [r for r in results if r["status"] == "complete"]
    errored = [r for r in results if r["status"] != "complete"]

    summary = {
        "total_skills": len(results),
        "completed": len(completed),
        "errored": len(errored),
    }
    if completed:
        summary["average_accuracy"] = round(
            sum(r["metrics"]["accuracy"] for r in completed) / len(completed), 4
        )
        summary["average_precision"] = round(
            sum(r["metrics"]["precision"] for r in completed) / len(completed), 4
        )
        summary["average_recall"] = round(
            sum(r["metrics"]["recall"] for r in completed) / len(completed), 4
        )

    report = {
        "summary": summary,
        "results": results,
    }

    output_json = json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"\nReport written to {args.output}", file=sys.stderr)
    else:
        print(output_json)

    # Print final summary
    print(f"\nBatch evaluation complete:", file=sys.stderr)
    print(f"  {summary['completed']}/{summary['total_skills']} skills evaluated", file=sys.stderr)
    if "average_accuracy" in summary:
        print(f"  Average accuracy:  {summary['average_accuracy']:.0%}", file=sys.stderr)
        print(f"  Average precision: {summary['average_precision']:.0%}", file=sys.stderr)
        print(f"  Average recall:    {summary['average_recall']:.0%}", file=sys.stderr)


if __name__ == "__main__":
    main()
