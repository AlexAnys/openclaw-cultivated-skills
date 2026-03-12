#!/usr/bin/env python3
"""
Batch functional evaluation for skills (Layer 3).

For each skill, runs with-skill vs without-skill comparisons using realistic
task prompts, grades outputs against assertions, and aggregates results.

This implements Layer 3 of the openclaw-cultivated-skills evaluation pipeline.

Usage:
    python -m pipeline.batch_functional_eval --skills-dir <dir> --output report.json
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _parse_skill_md(skill_path: Path) -> tuple[str, str, str]:
    """Parse a SKILL.md file, returning (name, description, full_content)."""
    content = (skill_path / "SKILL.md").read_text()
    lines = content.split("\n")

    if lines[0].strip() != "---":
        raise ValueError("SKILL.md missing frontmatter")

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        raise ValueError("SKILL.md missing closing ---")

    name = ""
    description = ""
    for line in lines[1:end_idx]:
        if line.startswith("name:"):
            name = line[len("name:"):].strip().strip("\"'")
        elif line.startswith("description:"):
            description = line[len("description:"):].strip().strip("\"'")

    return name, description, content


def _find_project_root() -> Path:
    """Find project root by walking up from cwd looking for .claude/."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def generate_task_prompts(
    skill_name: str,
    skill_description: str,
    skill_content: str,
    model: str | None = None,
) -> list[dict[str, Any]] | None:
    """Generate realistic task prompts for functional testing via claude -p."""
    prompt = f"""You are generating functional test cases for an Agent Skill called "{skill_name}".

Skill description: {skill_description}

Generate exactly 3 test cases as a JSON array. Each object has:
- "id": integer (1, 2, 3)
- "prompt": a realistic, detailed user task prompt that this skill should help with
- "expected_output": description of what a good output looks like
- "expectations": array of 3-5 concrete, verifiable assertions about the output

Requirements:
- Prompts should be realistic tasks a user would actually ask
- Include specific details (file paths, project context, technical specifics)
- Expectations should be objectively verifiable (not subjective quality judgments)
- Cover different aspects of the skill's functionality
- Each expectation should be a statement that can be checked as true/false

Output ONLY the JSON array, no other text."""

    cmd = ["claude", "-p", prompt, "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, env=env,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"  Warning: Failed to generate task prompts: {e}", file=sys.stderr)
        return None

    if result.returncode != 0:
        return None

    import re
    output = result.stdout.strip()
    array_match = re.search(r"\[[\s\S]*\]", output)
    if array_match:
        try:
            prompts = json.loads(array_match.group())
            if isinstance(prompts, list):
                return prompts
        except json.JSONDecodeError:
            pass

    return None


def run_with_skill(
    prompt: str,
    skill_path: Path,
    output_dir: Path,
    model: str | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    """Run a task prompt with the skill available."""
    output_dir.mkdir(parents=True, exist_ok=True)

    task_prompt = f"""Execute this task using the skill at {skill_path}:

First, read the skill at {skill_path}/SKILL.md and follow its instructions.

Task: {prompt}

Save all output files to: {output_dir}/
When done, write a brief summary of what you did to {output_dir}/summary.txt
"""
    cmd = ["claude", "-p", task_prompt, "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    start = time.time()

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, env=env,
        )
        duration = time.time() - start
        return {
            "status": "complete",
            "duration_seconds": round(duration, 1),
            "output": result.stdout[:5000],
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "duration_seconds": timeout}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def run_without_skill(
    prompt: str,
    output_dir: Path,
    model: str | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    """Run the same task without the skill (baseline)."""
    output_dir.mkdir(parents=True, exist_ok=True)

    task_prompt = f"""Execute this task:

Task: {prompt}

Save all output files to: {output_dir}/
When done, write a brief summary of what you did to {output_dir}/summary.txt
"""
    cmd = ["claude", "-p", task_prompt, "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    start = time.time()

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, env=env,
        )
        duration = time.time() - start
        return {
            "status": "complete",
            "duration_seconds": round(duration, 1),
            "output": result.stdout[:5000],
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "duration_seconds": timeout}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def grade_outputs(
    prompt: str,
    expectations: list[str],
    with_skill_output: str,
    without_skill_output: str,
    model: str | None = None,
) -> dict[str, Any]:
    """Grade both outputs against expectations using Claude."""
    grading_prompt = f"""You are grading two outputs for the same task. Grade each expectation as PASS or FAIL with evidence.

Task: {prompt}

Expectations to check:
{json.dumps(expectations, indent=2)}

--- WITH SKILL OUTPUT ---
{with_skill_output[:3000]}

--- WITHOUT SKILL (BASELINE) OUTPUT ---
{without_skill_output[:3000]}

Respond with a JSON object:
{{
  "with_skill": {{
    "expectations": [
      {{"text": "expectation text", "passed": true/false, "evidence": "why"}}
    ],
    "pass_rate": 0.0-1.0
  }},
  "without_skill": {{
    "expectations": [
      {{"text": "expectation text", "passed": true/false, "evidence": "why"}}
    ],
    "pass_rate": 0.0-1.0
  }},
  "improvement": true/false
}}

Output ONLY the JSON, no other text."""

    cmd = ["claude", "-p", grading_prompt, "--output-format", "text"]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, env=env,
        )
    except Exception as e:
        return {"error": str(e)}

    import re
    output = result.stdout.strip()
    obj_match = re.search(r"\{[\s\S]*\}", output)
    if obj_match:
        try:
            return json.loads(obj_match.group())
        except json.JSONDecodeError:
            pass

    return {"error": "Could not parse grading output"}


def evaluate_skill(
    skill_path: Path,
    workspace: Path,
    model: str | None = None,
    timeout: int = 120,
) -> dict[str, Any]:
    """Run full functional evaluation for a single skill."""
    name, description, content = _parse_skill_md(skill_path)
    print(f"  Functional eval: {name}", file=sys.stderr)

    # Check for existing evals
    evals_file = skill_path / "evals" / "evals.json"
    task_prompts = None

    if evals_file.exists():
        try:
            data = json.loads(evals_file.read_text())
            task_prompts = data.get("evals", [])
            print(f"  Loaded {len(task_prompts)} existing evals", file=sys.stderr)
        except (json.JSONDecodeError, OSError):
            pass

    if not task_prompts:
        print(f"  Generating task prompts...", file=sys.stderr)
        task_prompts = generate_task_prompts(name, description, content, model)
        if not task_prompts:
            return {
                "skill_name": name,
                "skill_path": str(skill_path),
                "status": "error",
                "error": "Failed to generate task prompts",
            }

    # Run evaluations
    eval_results = []
    skill_workspace = workspace / name

    for eval_item in task_prompts:
        eval_id = eval_item.get("id", len(eval_results) + 1)
        prompt = eval_item.get("prompt", "")
        expectations = eval_item.get("expectations", [])
        eval_dir = skill_workspace / f"eval-{eval_id}"

        print(f"  Running eval {eval_id}...", file=sys.stderr)

        # Run with and without skill
        with_result = run_with_skill(
            prompt, skill_path, eval_dir / "with_skill" / "outputs", model, timeout,
        )
        without_result = run_without_skill(
            prompt, eval_dir / "without_skill" / "outputs", model, timeout,
        )

        # Grade
        grading = grade_outputs(
            prompt, expectations,
            with_result.get("output", ""),
            without_result.get("output", ""),
            model,
        )

        eval_results.append({
            "eval_id": eval_id,
            "prompt": prompt[:200],
            "with_skill": with_result,
            "without_skill": without_result,
            "grading": grading,
        })

    # Compute aggregate metrics
    total_assertions = 0
    passed_assertions = 0
    improvements = 0

    for er in eval_results:
        g = er.get("grading", {})
        ws = g.get("with_skill", {})
        for exp in ws.get("expectations", []):
            total_assertions += 1
            if exp.get("passed"):
                passed_assertions += 1
        if g.get("improvement"):
            improvements += 1

    pass_rate = passed_assertions / total_assertions if total_assertions > 0 else 0.0
    improvement_rate = improvements / len(eval_results) if eval_results else 0.0

    return {
        "skill_name": name,
        "skill_path": str(skill_path),
        "status": "complete",
        "eval_results": eval_results,
        "metrics": {
            "pass_rate": round(pass_rate, 4),
            "improvement_rate": round(improvement_rate, 4),
            "total_assertions": total_assertions,
            "passed_assertions": passed_assertions,
            "evals_run": len(eval_results),
            "evals_with_improvement": improvements,
        },
    }


def _find_skills_in_directory(directory: Path) -> list[Path]:
    """Find all skill directories containing SKILL.md."""
    return sorted(p.parent for p in directory.rglob("SKILL.md"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch functional evaluation for skills (Layer 3)",
    )
    parser.add_argument(
        "--skills-dir", required=True, type=Path,
        help="Directory containing skill subdirectories",
    )
    parser.add_argument(
        "--workspace", type=Path, default=None,
        help="Workspace directory for eval results (default: <skills-dir>/../eval-workspace)",
    )
    parser.add_argument("--output", default=None, help="Output JSON report path")
    parser.add_argument("--model", default=None, help="Model for claude -p")
    parser.add_argument("--timeout", type=int, default=120, help="Timeout per run")
    args = parser.parse_args()

    skills = _find_skills_in_directory(args.skills_dir)
    if not skills:
        print(f"No skills found under {args.skills_dir}", file=sys.stderr)
        sys.exit(1)

    workspace = args.workspace or (args.skills_dir.parent / "eval-workspace")
    workspace.mkdir(parents=True, exist_ok=True)

    print(f"Found {len(skills)} skills to evaluate", file=sys.stderr)
    results = []

    for i, skill in enumerate(skills, 1):
        print(f"\n[{i}/{len(skills)}] {skill.name}", file=sys.stderr)
        result = evaluate_skill(skill, workspace, args.model, args.timeout)
        results.append(result)

        if result["status"] == "complete":
            m = result["metrics"]
            print(
                f"  => pass_rate={m['pass_rate']:.0%} improvement={m['improvement_rate']:.0%}",
                file=sys.stderr,
            )

    # Build report
    completed = [r for r in results if r["status"] == "complete"]
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_skills": len(results),
            "completed": len(completed),
            "avg_pass_rate": round(
                sum(r["metrics"]["pass_rate"] for r in completed) / len(completed), 4
            ) if completed else 0.0,
            "avg_improvement_rate": round(
                sum(r["metrics"]["improvement_rate"] for r in completed) / len(completed), 4
            ) if completed else 0.0,
        },
        "results": results,
    }

    output_json = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(output_json)
        print(f"\nReport written to {args.output}", file=sys.stderr)
    else:
        print(output_json)


if __name__ == "__main__":
    main()
