#!/usr/bin/env python3
"""
Dedicated security scanner for skill scripts.

Walks a skill directory's scripts/ folder and checks for dangerous patterns
including shell injection, code injection, network access, filesystem abuse,
and credential access.

Usage:
    python -m pipeline.security_scan --skill-path <path> --output findings.json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Pattern definitions
# ---------------------------------------------------------------------------

# Each pattern: (compiled_regex, description, severity)
# Severity: CRITICAL = auto-reject, WARNING = human review needed, INFO = informational

SECURITY_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    # Shell injection
    (
        re.compile(r"subprocess\.call\s*\(.*shell\s*=\s*True", re.DOTALL),
        "Shell injection risk: subprocess.call with shell=True",
        "CRITICAL",
    ),
    (
        re.compile(r"subprocess\.run\s*\(.*shell\s*=\s*True", re.DOTALL),
        "Shell injection risk: subprocess.run with shell=True",
        "CRITICAL",
    ),
    (
        re.compile(r"subprocess\.Popen\s*\(.*shell\s*=\s*True", re.DOTALL),
        "Shell injection risk: subprocess.Popen with shell=True",
        "CRITICAL",
    ),
    (
        re.compile(r"os\.system\s*\("),
        "Shell injection risk: os.system()",
        "CRITICAL",
    ),
    (
        re.compile(r"os\.popen\s*\("),
        "Shell injection risk: os.popen()",
        "CRITICAL",
    ),

    # Code injection
    (
        re.compile(r"(?<!\w)eval\s*\("),
        "Code injection risk: eval()",
        "CRITICAL",
    ),
    (
        re.compile(r"(?<!\w)exec\s*\("),
        "Code injection risk: exec()",
        "CRITICAL",
    ),
    (
        re.compile(r"(?<!\w)compile\s*\("),
        "Code injection risk: compile()",
        "WARNING",
    ),
    (
        re.compile(r"__import__\s*\("),
        "Dynamic import risk: __import__()",
        "WARNING",
    ),

    # Network access
    (
        re.compile(r"requests\.\w+\s*\("),
        "Network access: requests library usage",
        "WARNING",
    ),
    (
        re.compile(r"urllib\.\w+"),
        "Network access: urllib usage",
        "WARNING",
    ),
    (
        re.compile(r"http\.client\."),
        "Network access: http.client usage",
        "WARNING",
    ),
    (
        re.compile(r"(?<!\w)socket\.\w+"),
        "Network access: raw socket usage",
        "CRITICAL",
    ),
    (
        re.compile(r"from\s+aiohttp\s+import|import\s+aiohttp"),
        "Network access: aiohttp usage",
        "WARNING",
    ),
    (
        re.compile(r"from\s+httpx\s+import|import\s+httpx"),
        "Network access: httpx usage",
        "WARNING",
    ),

    # Filesystem abuse
    (
        re.compile(r"\.\./"),
        "Filesystem traversal: ../ path component",
        "WARNING",
    ),
    (
        re.compile(r"open\s*\(\s*['\"]\/etc\/"),
        "Filesystem access: reading from /etc/",
        "CRITICAL",
    ),
    (
        re.compile(r"open\s*\(\s*['\"]\/tmp\/.*['\"].*['\"]w"),
        "Filesystem access: writing to /tmp/",
        "WARNING",
    ),
    (
        re.compile(r"os\.remove\s*\(|os\.unlink\s*\(|shutil\.rmtree\s*\("),
        "Filesystem modification: file/directory deletion",
        "WARNING",
    ),
    (
        re.compile(r"os\.chmod\s*\(|os\.chown\s*\("),
        "Filesystem modification: permission changes",
        "CRITICAL",
    ),

    # Credential access
    (
        re.compile(r"os\.environ\.get\s*\(\s*['\"].*KEY", re.IGNORECASE),
        "Credential access: reading KEY from environment",
        "WARNING",
    ),
    (
        re.compile(r"os\.environ\.get\s*\(\s*['\"].*SECRET", re.IGNORECASE),
        "Credential access: reading SECRET from environment",
        "CRITICAL",
    ),
    (
        re.compile(r"os\.environ\.get\s*\(\s*['\"].*TOKEN", re.IGNORECASE),
        "Credential access: reading TOKEN from environment",
        "WARNING",
    ),
    (
        re.compile(r"os\.environ\s*\[.*(?:KEY|SECRET|TOKEN)", re.IGNORECASE),
        "Credential access: reading credentials from environment via subscript",
        "WARNING",
    ),

    # Miscellaneous
    (
        re.compile(r"pickle\.loads?\s*\("),
        "Deserialization risk: pickle usage",
        "WARNING",
    ),
    (
        re.compile(r"marshal\.loads?\s*\("),
        "Deserialization risk: marshal usage",
        "CRITICAL",
    ),
    (
        re.compile(r"ctypes\.\w+"),
        "Native code access: ctypes usage",
        "WARNING",
    ),
]


# ---------------------------------------------------------------------------
# Scanning logic
# ---------------------------------------------------------------------------

def scan_file(file_path: Path, skill_root: Path) -> list[dict[str, Any]]:
    """Scan a single file for security findings.

    Returns a list of finding dicts with keys:
        file, line, severity, description, matched_text
    """
    findings: list[dict[str, Any]] = []
    rel_path = str(file_path.relative_to(skill_root))

    try:
        text = file_path.read_text(errors="replace")
    except OSError as e:
        findings.append({
            "file": rel_path,
            "line": 0,
            "severity": "WARNING",
            "description": f"Could not read file: {e}",
            "matched_text": "",
        })
        return findings

    lines = text.split("\n")

    for pattern, description, severity in SECURITY_PATTERNS:
        for match in pattern.finditer(text):
            # Calculate line number
            line_num = text[:match.start()].count("\n") + 1
            matched = match.group().strip()
            # Truncate long matches for readability
            if len(matched) > 120:
                matched = matched[:117] + "..."

            findings.append({
                "file": rel_path,
                "line": line_num,
                "severity": severity,
                "description": description,
                "matched_text": matched,
            })

    # Check for absolute paths outside the skill directory
    abs_path_pattern = re.compile(r"""(?:open|Path)\s*\(\s*['"](\/.+?)['"]""")
    for match in abs_path_pattern.finditer(text):
        path_str = match.group(1)
        # Allow common safe paths
        safe_prefixes = ("/dev/null",)
        if not any(path_str.startswith(s) for s in safe_prefixes):
            line_num = text[:match.start()].count("\n") + 1
            findings.append({
                "file": rel_path,
                "line": line_num,
                "severity": "WARNING",
                "description": f"Absolute path reference outside skill directory: {path_str}",
                "matched_text": match.group().strip(),
            })

    return findings


def scan_skill(skill_path: Path) -> dict[str, Any]:
    """Scan a skill's scripts/ directory for security issues.

    Returns a report dict with keys: skill_path, findings, summary.
    """
    skill_path = Path(skill_path).resolve()
    scripts_dir = skill_path / "scripts"

    all_findings: list[dict[str, Any]] = []

    if not scripts_dir.is_dir():
        # Also check for loose script files in the skill root
        for ext in ("*.py", "*.sh", "*.bash", "*.js", "*.ts"):
            for f in skill_path.glob(ext):
                if f.is_file():
                    all_findings.extend(scan_file(f, skill_path))
    else:
        for script_file in sorted(scripts_dir.rglob("*")):
            if not script_file.is_file():
                continue
            # Only scan text-like script files
            suffixes = {".py", ".sh", ".bash", ".js", ".ts", ".rb", ".pl", ".lua", ""}
            if script_file.suffix.lower() in suffixes:
                all_findings.extend(scan_file(script_file, skill_path))

    # Classify overall severity
    critical_count = sum(1 for f in all_findings if f["severity"] == "CRITICAL")
    warning_count = sum(1 for f in all_findings if f["severity"] == "WARNING")
    info_count = sum(1 for f in all_findings if f["severity"] == "INFO")

    if critical_count > 0:
        verdict = "REJECT"
    elif warning_count > 0:
        verdict = "REVIEW"
    else:
        verdict = "CLEAN"

    # Group findings by file
    findings_by_file: dict[str, list[dict[str, Any]]] = {}
    for f in all_findings:
        fname = f["file"]
        if fname not in findings_by_file:
            findings_by_file[fname] = []
        findings_by_file[fname].append(f)

    return {
        "skill_path": str(skill_path),
        "verdict": verdict,
        "summary": {
            "total_findings": len(all_findings),
            "critical": critical_count,
            "warning": warning_count,
            "info": info_count,
            "files_scanned": len(findings_by_file) if all_findings else len(
                list(scripts_dir.rglob("*")) if scripts_dir.is_dir() else []
            ),
        },
        "findings_by_file": findings_by_file,
        "findings": all_findings,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Security scanner for skill scripts",
    )
    parser.add_argument(
        "--skill-path",
        required=True,
        type=Path,
        help="Path to the skill directory to scan",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output JSON findings path (default: stdout)",
    )
    parser.add_argument(
        "--severity",
        choices=["CRITICAL", "WARNING", "INFO", "ALL"],
        default="ALL",
        help="Minimum severity to include in output (default: ALL)",
    )
    args = parser.parse_args()

    skill_path = args.skill_path.resolve()
    if not skill_path.is_dir():
        print(f"Error: {skill_path} is not a directory", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning {skill_path} ...", file=sys.stderr)
    report = scan_skill(skill_path)

    # Filter by severity if requested
    if args.severity != "ALL":
        severity_order = {"INFO": 0, "WARNING": 1, "CRITICAL": 2}
        min_level = severity_order.get(args.severity, 0)
        report["findings"] = [
            f for f in report["findings"]
            if severity_order.get(f["severity"], 0) >= min_level
        ]
        # Rebuild findings_by_file
        findings_by_file: dict[str, list[dict[str, Any]]] = {}
        for f in report["findings"]:
            fname = f["file"]
            if fname not in findings_by_file:
                findings_by_file[fname] = []
            findings_by_file[fname].append(f)
        report["findings_by_file"] = findings_by_file

    output_json = json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(output_json)
        print(f"Findings written to {args.output}", file=sys.stderr)
    else:
        print(output_json)

    # Print summary to stderr
    s = report["summary"]
    print(f"\nScan complete: {report['verdict']}", file=sys.stderr)
    print(f"  {s['total_findings']} finding(s): {s['critical']} critical, {s['warning']} warning, {s['info']} info", file=sys.stderr)

    # Exit with non-zero if critical findings
    if report["verdict"] == "REJECT":
        sys.exit(1)


if __name__ == "__main__":
    main()
