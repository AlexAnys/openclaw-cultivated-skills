#!/usr/bin/env python3
"""
Issue a Quality Passport for a skill that has passed all evaluation layers.

Aggregates results from structural validation, trigger accuracy, functional
testing, and human review into a standardized Quality Passport JSON document.

Usage:
    python -m pipeline.issue_passport \
        --skill-name <name> \
        --structural-report <path> \
        --trigger-report <path> \
        --functional-report <path> \
        --reviewer <name> \
        --review-notes <notes> \
        --output passports/<name>.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def compute_tier(
    trigger_accuracy: float,
    functional_pass_rate: float,
    security_clean: bool,
) -> str:
    """Determine Quality Passport tier based on scores.

    Tier definitions:
    - Gold:   >90% trigger, >85% functional, clean security
    - Silver: >80% trigger, >70% functional, clean security
    - Bronze: >70% trigger, >60% functional, warnings OK
    """
    if trigger_accuracy > 0.90 and functional_pass_rate > 0.85 and security_clean:
        return "gold"
    elif trigger_accuracy > 0.80 and functional_pass_rate > 0.70 and security_clean:
        return "silver"
    elif trigger_accuracy > 0.70 and functional_pass_rate > 0.60:
        return "bronze"
    else:
        return "rejected"


def load_structural_results(path: Path) -> dict[str, Any]:
    """Load structural validation results."""
    data = json.loads(path.read_text())
    # Handle both single-skill and batch report formats
    if "results" in data:
        # Batch format - find the relevant skill
        results = data["results"]
        if len(results) == 1:
            r = results[0]
            return {
                "passed": r["status"] in ("pass", "warn"),
                "details": "; ".join(f["message"] for f in r.get("findings", [])) or "All checks passed",
            }
    return {
        "passed": data.get("status", "fail") in ("pass", "warn"),
        "details": data.get("details", ""),
    }


def load_trigger_results(path: Path) -> dict[str, Any]:
    """Load trigger accuracy results."""
    data = json.loads(path.read_text())
    # Handle batch format
    if "results" in data and isinstance(data["results"], list):
        for r in data["results"]:
            if "metrics" in r:
                m = r["metrics"]
                return {
                    "precision": m.get("precision", 0.0),
                    "recall": m.get("recall", 0.0),
                    "overall": m.get("accuracy", 0.0),
                }
    # Direct metrics format
    m = data.get("metrics", data)
    return {
        "precision": m.get("precision", 0.0),
        "recall": m.get("recall", 0.0),
        "overall": m.get("accuracy", 0.0),
    }


def load_functional_results(path: Path) -> dict[str, Any]:
    """Load functional testing results."""
    data = json.loads(path.read_text())
    if "results" in data and isinstance(data["results"], list):
        for r in data["results"]:
            if "metrics" in r:
                m = r["metrics"]
                return {
                    "pass_rate": m.get("pass_rate", 0.0),
                    "improvement_over_baseline": m.get("improvement_rate", 0.0),
                    "assertions_tested": m.get("total_assertions", 0),
                }
    m = data.get("metrics", data)
    return {
        "pass_rate": m.get("pass_rate", 0.0),
        "improvement_over_baseline": m.get("improvement_rate", 0.0),
        "assertions_tested": m.get("total_assertions", 0),
    }


def issue_passport(
    skill_name: str,
    version: str,
    source_repo: str,
    publisher: str,
    evaluator: str,
    structural: dict[str, Any],
    trigger: dict[str, Any],
    functional: dict[str, Any],
    security_passed: bool,
    security_warnings: list[str],
    reviewer: str,
    review_notes: str,
    compatible_agents: list[str],
    use_cases: list[str],
    limitations: list[str],
) -> dict[str, Any]:
    """Generate a Quality Passport JSON document."""
    trigger_accuracy = trigger.get("overall", 0.0)
    functional_pass_rate = functional.get("pass_rate", 0.0)

    tier = compute_tier(trigger_accuracy, functional_pass_rate, security_passed)

    return {
        "skill_name": skill_name,
        "version": version,
        "source_repo": source_repo,
        "publisher": publisher,
        "evaluated_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "evaluator": evaluator,
        "structural_validation": structural,
        "trigger_accuracy": trigger,
        "functional_score": functional,
        "security_scan": {
            "passed": security_passed,
            "warnings": security_warnings,
        },
        "human_review": {
            "approved": tier != "rejected",
            "reviewer": reviewer,
            "notes": review_notes,
        },
        "compatible_agents_tested": compatible_agents,
        "recommended_use_cases": use_cases,
        "known_limitations": limitations,
        "overall_tier": tier,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Issue a Quality Passport")
    parser.add_argument("--skill-name", required=True)
    parser.add_argument("--version", default="1.0.0")
    parser.add_argument("--source-repo", default="")
    parser.add_argument("--publisher", default="")
    parser.add_argument("--evaluator", default="openclaw-pipeline")
    parser.add_argument("--structural-report", type=Path, default=None)
    parser.add_argument("--trigger-report", type=Path, default=None)
    parser.add_argument("--functional-report", type=Path, default=None)
    parser.add_argument("--security-clean", action="store_true", default=True)
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--review-notes", default="")
    parser.add_argument("--compatible-agents", nargs="*", default=["Claude Code"])
    parser.add_argument("--use-cases", nargs="*", default=[])
    parser.add_argument("--limitations", nargs="*", default=[])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Load results from reports
    structural = {"passed": True, "details": "All checks passed"}
    if args.structural_report and args.structural_report.exists():
        structural = load_structural_results(args.structural_report)

    trigger = {"precision": 0.0, "recall": 0.0, "overall": 0.0}
    if args.trigger_report and args.trigger_report.exists():
        trigger = load_trigger_results(args.trigger_report)

    functional = {"pass_rate": 0.0, "improvement_over_baseline": 0.0, "assertions_tested": 0}
    if args.functional_report and args.functional_report.exists():
        functional = load_functional_results(args.functional_report)

    passport = issue_passport(
        skill_name=args.skill_name,
        version=args.version,
        source_repo=args.source_repo,
        publisher=args.publisher,
        evaluator=args.evaluator,
        structural=structural,
        trigger=trigger,
        functional=functional,
        security_passed=args.security_clean,
        security_warnings=[],
        reviewer=args.reviewer,
        review_notes=args.review_notes,
        compatible_agents=args.compatible_agents,
        use_cases=args.use_cases,
        limitations=args.limitations,
    )

    # Write passport
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(passport, indent=2) + "\n")

    tier = passport["overall_tier"]
    print(f"Quality Passport issued: {args.skill_name} ({tier.upper()})", file=sys.stderr)
    print(f"  Trigger accuracy: {trigger['overall']:.0%}", file=sys.stderr)
    print(f"  Functional pass rate: {functional['pass_rate']:.0%}", file=sys.stderr)
    print(f"  Written to: {args.output}", file=sys.stderr)

    if tier == "rejected":
        print(f"  WARNING: Skill does not meet minimum Bronze thresholds", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
