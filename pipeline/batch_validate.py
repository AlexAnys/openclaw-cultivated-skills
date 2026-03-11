#!/usr/bin/env python3
"""
Batch structural validation for skills.

Takes a directory of skill directories (or a JSON list of GitHub repo URLs)
and runs structural validation on each, including extended security checks.

Usage:
    python -m pipeline.batch_validate --input <dir-or-json> --output report.json
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# YAML frontmatter parsing (self-contained, mirrors quick_validate logic)
# ---------------------------------------------------------------------------

# Try to use PyYAML if available, fall back to manual parsing
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def _parse_frontmatter(content: str) -> tuple[dict[str, Any] | None, str | None]:
    """Extract and parse YAML frontmatter from SKILL.md content.

    Returns (frontmatter_dict, error_message). On success error_message is None.
    """
    if not content.startswith("---"):
        return None, "No YAML frontmatter found"

    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, "Invalid frontmatter format"

    fm_text = match.group(1)

    if HAS_YAML:
        try:
            fm = yaml.safe_load(fm_text)
            if not isinstance(fm, dict):
                return None, "Frontmatter must be a YAML dictionary"
            return fm, None
        except Exception as e:
            return None, f"Invalid YAML in frontmatter: {e}"
    else:
        # Minimal key: value parser for environments without PyYAML
        fm: dict[str, Any] = {}
        for line in fm_text.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                fm[key.strip()] = value.strip().strip("'\"")
        return fm, None


# ---------------------------------------------------------------------------
# Structural validation (mirrors quick_validate.py with extensions)
# ---------------------------------------------------------------------------

ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}


def _validate_structure(skill_path: Path) -> list[dict[str, str]]:
    """Validate SKILL.md structure. Returns a list of finding dicts."""
    findings: list[dict[str, str]] = []

    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        findings.append({"severity": "CRITICAL", "message": "SKILL.md not found"})
        return findings

    content = skill_md.read_text()
    fm, err = _parse_frontmatter(content)
    if err:
        findings.append({"severity": "CRITICAL", "message": err})
        return findings

    assert fm is not None

    # Unexpected keys
    unexpected = set(fm.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        findings.append({
            "severity": "CRITICAL",
            "message": f"Unexpected frontmatter key(s): {', '.join(sorted(unexpected))}",
        })

    # Required fields
    if "name" not in fm:
        findings.append({"severity": "CRITICAL", "message": "Missing 'name' in frontmatter"})
    else:
        name = str(fm["name"]).strip()
        if not re.match(r"^[a-z0-9-]+$", name):
            findings.append({"severity": "CRITICAL", "message": f"Name '{name}' is not kebab-case"})
        elif name.startswith("-") or name.endswith("-") or "--" in name:
            findings.append({"severity": "CRITICAL", "message": f"Name '{name}' has invalid hyphen placement"})
        if len(name) > 64:
            findings.append({"severity": "CRITICAL", "message": f"Name too long ({len(name)} chars, max 64)"})

    if "description" not in fm:
        findings.append({"severity": "CRITICAL", "message": "Missing 'description' in frontmatter"})
    else:
        desc = str(fm["description"]).strip()
        if "<" in desc or ">" in desc:
            findings.append({"severity": "CRITICAL", "message": "Description contains angle brackets"})
        if len(desc) > 1024:
            findings.append({"severity": "CRITICAL", "message": f"Description too long ({len(desc)} chars, max 1024)"})

    # Compatibility length
    compat = fm.get("compatibility", "")
    if compat and len(str(compat)) > 500:
        findings.append({"severity": "WARNING", "message": f"Compatibility too long ({len(str(compat))} chars, max 500)"})

    return findings


# ---------------------------------------------------------------------------
# Extended security checks
# ---------------------------------------------------------------------------

DANGEROUS_PATTERNS: list[tuple[str, str, str]] = [
    (r"subprocess\.call.*shell\s*=\s*True", "Shell injection via subprocess.call(shell=True)", "CRITICAL"),
    (r"os\.system\(", "Shell injection via os.system()", "CRITICAL"),
    (r"(?<!\w)eval\(", "Code injection via eval()", "CRITICAL"),
    (r"(?<!\w)exec\(", "Code injection via exec()", "CRITICAL"),
    (r"requests\.(get|post|put|delete|patch)\s*\(\s*['\"]https?://", "Hardcoded URL in requests call", "WARNING"),
    (r"open\s*\(\s*['\"]\/etc\/", "Accessing /etc/ filesystem", "CRITICAL"),
    (r"\.\./", "Filesystem traversal pattern (../)", "WARNING"),
]


def _scan_scripts_security(skill_path: Path) -> list[dict[str, str]]:
    """Scan scripts/ directory for dangerous patterns."""
    findings: list[dict[str, str]] = []
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.is_dir():
        return findings

    for script_file in scripts_dir.rglob("*"):
        if not script_file.is_file():
            continue
        try:
            text = script_file.read_text(errors="replace")
        except OSError:
            findings.append({
                "severity": "WARNING",
                "message": f"Could not read {script_file.relative_to(skill_path)}",
            })
            continue

        rel = str(script_file.relative_to(skill_path))
        for pattern, description, severity in DANGEROUS_PATTERNS:
            for m in re.finditer(pattern, text):
                line_num = text[:m.start()].count("\n") + 1
                findings.append({
                    "severity": severity,
                    "message": f"{rel}:{line_num} - {description}",
                })

    return findings


def _check_skill_size(skill_path: Path) -> list[dict[str, str]]:
    """Check total size of a skill directory."""
    findings: list[dict[str, str]] = []
    total = 0
    for f in skill_path.rglob("*"):
        if f.is_file():
            total += f.stat().st_size

    if total > 2 * 1024 * 1024:
        findings.append({
            "severity": "CRITICAL",
            "message": f"Skill size {total / 1024 / 1024:.1f}MB exceeds 2MB limit",
        })
    elif total > 500 * 1024:
        findings.append({
            "severity": "WARNING",
            "message": f"Skill size {total / 1024:.0f}KB exceeds 500KB recommended limit",
        })

    return findings


# ---------------------------------------------------------------------------
# Full single-skill validation
# ---------------------------------------------------------------------------

def validate_skill(skill_path: Path) -> dict[str, Any]:
    """Run full validation on a single skill directory.

    Returns a dict with keys: skill_path, status (pass/fail/warn), findings.
    """
    findings: list[dict[str, str]] = []
    findings.extend(_validate_structure(skill_path))
    findings.extend(_scan_scripts_security(skill_path))
    findings.extend(_check_skill_size(skill_path))

    has_critical = any(f["severity"] == "CRITICAL" for f in findings)
    has_warning = any(f["severity"] == "WARNING" for f in findings)

    if has_critical:
        status = "fail"
    elif has_warning:
        status = "warn"
    else:
        status = "pass"

    return {
        "skill_path": str(skill_path),
        "status": status,
        "findings": findings,
    }


# ---------------------------------------------------------------------------
# Batch processing
# ---------------------------------------------------------------------------

def _find_skills_in_directory(directory: Path) -> list[Path]:
    """Walk a directory tree and return paths containing SKILL.md."""
    skills: list[Path] = []
    for skill_md in sorted(directory.rglob("SKILL.md")):
        skills.append(skill_md.parent)
    return skills


def _clone_and_find_skill(repo_url: str, tmpdir: Path) -> Path | None:
    """Clone a GitHub repo (shallow) and locate the SKILL.md."""
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    dest = tmpdir / repo_name
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(dest)],
            capture_output=True,
            timeout=60,
            check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"Warning: Failed to clone {repo_url}: {e}", file=sys.stderr)
        return None

    found = list(dest.rglob("SKILL.md"))
    if not found:
        print(f"Warning: No SKILL.md found in {repo_url}", file=sys.stderr)
        return None
    return found[0].parent


def batch_validate(input_path: str) -> list[dict[str, Any]]:
    """Validate skills from either a local directory or a JSON list of repo URLs."""
    p = Path(input_path)
    results: list[dict[str, Any]] = []

    if p.is_dir():
        # Local directory mode
        skill_dirs = _find_skills_in_directory(p)
        if not skill_dirs:
            print(f"Warning: No SKILL.md files found under {p}", file=sys.stderr)
        for i, skill_dir in enumerate(skill_dirs, 1):
            print(f"[{i}/{len(skill_dirs)}] Validating {skill_dir.name} ...", file=sys.stderr)
            results.append(validate_skill(skill_dir))

    elif p.is_file() and p.suffix == ".json":
        # JSON list of GitHub URLs
        try:
            urls = json.loads(p.read_text())
        except (json.JSONDecodeError, OSError) as e:
            print(f"Error reading {p}: {e}", file=sys.stderr)
            return results

        if not isinstance(urls, list):
            print(f"Error: JSON file must contain a list of URLs", file=sys.stderr)
            return results

        with tempfile.TemporaryDirectory(prefix="skill_validate_") as tmpdir:
            tmpdir_path = Path(tmpdir)
            for i, url in enumerate(urls, 1):
                print(f"[{i}/{len(urls)}] Cloning and validating {url} ...", file=sys.stderr)
                skill_dir = _clone_and_find_skill(str(url), tmpdir_path)
                if skill_dir is None:
                    results.append({
                        "skill_path": str(url),
                        "status": "fail",
                        "findings": [{"severity": "CRITICAL", "message": "Failed to clone or locate SKILL.md"}],
                    })
                else:
                    result = validate_skill(skill_dir)
                    result["skill_path"] = str(url)
                    results.append(result)
    else:
        print(f"Error: {input_path} must be a directory or a .json file", file=sys.stderr)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch structural validation for skills",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Directory of skill directories, or JSON file with list of GitHub repo URLs",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON report path (default: stdout)",
    )
    args = parser.parse_args()

    results = batch_validate(args.input)

    # Build summary
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "pass")
    warned = sum(1 for r in results if r["status"] == "warn")
    failed = sum(1 for r in results if r["status"] == "fail")

    report = {
        "summary": {
            "total": total,
            "passed": passed,
            "warned": warned,
            "failed": failed,
        },
        "results": results,
    }

    output_json = json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(output_json)

    # Print summary to stderr
    print(f"\nValidation complete: {passed} passed, {warned} warnings, {failed} failed (of {total})", file=sys.stderr)


if __name__ == "__main__":
    main()
