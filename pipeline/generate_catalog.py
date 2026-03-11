#!/usr/bin/env python3
"""
Generate catalog.json and README markdown tables from passport data.

Scans the passports/ directory for all *.json passport files and aggregates
them into a catalog with summary statistics.

Usage:
    python -m pipeline.generate_catalog --passports-dir passports/ --output catalog.json
"""

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


def load_passports(passports_dir: Path) -> list[dict[str, Any]]:
    """Load all passport JSON files from a directory."""
    passports: list[dict[str, Any]] = []

    if not passports_dir.is_dir():
        print(f"Warning: Passports directory not found: {passports_dir}", file=sys.stderr)
        return passports

    for passport_file in sorted(passports_dir.glob("*.json")):
        try:
            data = json.loads(passport_file.read_text())
            data["_source_file"] = str(passport_file.name)
            passports.append(data)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load {passport_file}: {e}", file=sys.stderr)

    return passports


def compute_statistics(values: list[float]) -> dict[str, float]:
    """Compute mean, stddev, min, max for a list of numeric values."""
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "min": 0.0, "max": 0.0}

    n = len(values)
    mean = sum(values) / n
    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        stddev = math.sqrt(variance)
    else:
        stddev = 0.0

    return {
        "mean": round(mean, 4),
        "stddev": round(stddev, 4),
        "min": round(min(values), 4),
        "max": round(max(values), 4),
    }


def generate_catalog(passports: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate passport data into a catalog summary."""
    total = len(passports)

    # Category counts
    categories: Counter[str] = Counter()
    for p in passports:
        cat = p.get("category", p.get("metadata", {}).get("category", "uncategorized"))
        categories[cat] += 1

    # Tier distribution
    tiers: Counter[str] = Counter()
    for p in passports:
        tier = p.get("tier", p.get("metadata", {}).get("tier", "unknown"))
        tiers[str(tier)] += 1

    # Collect scores for averaging
    trigger_accuracies: list[float] = []
    overall_scores: list[float] = []
    for p in passports:
        # Try various common passport score locations
        scores = p.get("scores", p.get("evaluation", {}))
        if isinstance(scores, dict):
            ta = scores.get("trigger_accuracy")
            if ta is not None:
                try:
                    trigger_accuracies.append(float(ta))
                except (ValueError, TypeError):
                    pass
            overall = scores.get("overall", scores.get("overall_score"))
            if overall is not None:
                try:
                    overall_scores.append(float(overall))
                except (ValueError, TypeError):
                    pass

    # Build skill entries for the catalog
    skills: list[dict[str, Any]] = []
    for p in passports:
        entry: dict[str, Any] = {
            "name": p.get("name", p.get("skill_name", "unknown")),
            "description": p.get("description", ""),
            "category": p.get("category", p.get("metadata", {}).get("category", "uncategorized")),
            "tier": p.get("tier", p.get("metadata", {}).get("tier", "unknown")),
        }
        # Include scores if available
        scores = p.get("scores", p.get("evaluation", {}))
        if isinstance(scores, dict):
            entry["scores"] = scores
        # Include source info
        if "repo_url" in p:
            entry["repo_url"] = p["repo_url"]
        if "author" in p:
            entry["author"] = p["author"]
        if "_source_file" in p:
            entry["source_file"] = p["_source_file"]
        skills.append(entry)

    catalog: dict[str, Any] = {
        "total_count": total,
        "categories": dict(sorted(categories.items())),
        "tier_distribution": dict(sorted(tiers.items())),
        "average_scores": {},
        "skills": skills,
    }

    if trigger_accuracies:
        catalog["average_scores"]["trigger_accuracy"] = compute_statistics(trigger_accuracies)
    if overall_scores:
        catalog["average_scores"]["overall"] = compute_statistics(overall_scores)

    return catalog


def generate_markdown_table(catalog: dict[str, Any]) -> str:
    """Generate a markdown table suitable for README insertion."""
    lines: list[str] = []

    # Summary section
    lines.append(f"**Total Skills**: {catalog['total_count']}")
    lines.append("")

    # Category breakdown
    if catalog["categories"]:
        lines.append("### By Category")
        lines.append("")
        lines.append("| Category | Count |")
        lines.append("|----------|-------|")
        for cat, count in sorted(catalog["categories"].items()):
            lines.append(f"| {cat} | {count} |")
        lines.append("")

    # Tier breakdown
    if catalog["tier_distribution"]:
        lines.append("### By Tier")
        lines.append("")
        lines.append("| Tier | Count |")
        lines.append("|------|-------|")
        for tier, count in sorted(catalog["tier_distribution"].items()):
            lines.append(f"| {tier} | {count} |")
        lines.append("")

    # Average scores
    avg = catalog.get("average_scores", {})
    if avg:
        lines.append("### Average Scores")
        lines.append("")
        lines.append("| Metric | Mean | Std Dev | Min | Max |")
        lines.append("|--------|------|---------|-----|-----|")
        for metric, stats in sorted(avg.items()):
            if isinstance(stats, dict):
                lines.append(
                    f"| {metric} | {stats['mean']:.4f} | {stats['stddev']:.4f} "
                    f"| {stats['min']:.4f} | {stats['max']:.4f} |"
                )
        lines.append("")

    # Skills table
    skills = catalog.get("skills", [])
    if skills:
        lines.append("### Skills")
        lines.append("")
        lines.append("| Name | Category | Tier | Description |")
        lines.append("|------|----------|------|-------------|")
        for skill in sorted(skills, key=lambda s: s.get("name", "")):
            name = skill.get("name", "unknown")
            cat = skill.get("category", "-")
            tier = skill.get("tier", "-")
            desc = skill.get("description", "")
            # Truncate long descriptions for table readability
            if len(desc) > 80:
                desc = desc[:77] + "..."
            # Escape pipe characters in description
            desc = desc.replace("|", "\\|")
            lines.append(f"| {name} | {cat} | {tier} | {desc} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate catalog.json and README tables from passport data",
    )
    parser.add_argument(
        "--passports-dir",
        required=True,
        type=Path,
        help="Directory containing passport JSON files",
    )
    parser.add_argument(
        "--output",
        default="catalog.json",
        help="Output path for catalog.json (default: catalog.json)",
    )
    parser.add_argument(
        "--markdown-output",
        default=None,
        help="Output path for markdown table (default: <output>.md)",
    )
    args = parser.parse_args()

    passports = load_passports(args.passports_dir)
    print(f"Loaded {len(passports)} passport(s) from {args.passports_dir}", file=sys.stderr)

    if not passports:
        print("Warning: No passports found. Generating empty catalog.", file=sys.stderr)

    catalog = generate_catalog(passports)

    # Write catalog.json
    output_path = Path(args.output)
    output_path.write_text(json.dumps(catalog, indent=2))
    print(f"Generated: {output_path}", file=sys.stderr)

    # Write markdown
    md_path = Path(args.markdown_output) if args.markdown_output else output_path.with_suffix(".md")
    markdown = generate_markdown_table(catalog)
    md_path.write_text(markdown)
    print(f"Generated: {md_path}", file=sys.stderr)

    # Print summary
    print(f"\nCatalog summary:", file=sys.stderr)
    print(f"  Total skills: {catalog['total_count']}", file=sys.stderr)
    print(f"  Categories: {len(catalog['categories'])}", file=sys.stderr)
    print(f"  Tiers: {dict(catalog['tier_distribution'])}", file=sys.stderr)


if __name__ == "__main__":
    main()
