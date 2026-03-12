# Evaluation Methodology

This document describes the evaluation pipeline used by **openclaw-cultivated-skills** to vet, score, and certify community-contributed Claude Code skills. Every skill that enters the curated collection passes through a 4-layer funnel before it earns a Quality Passport and is published to the `skills/` directory.

---

## Evaluation Pipeline

The pipeline is designed as a progressive funnel: each layer is cheaper and faster than the next, so obviously broken skills are rejected early, and expensive human time is reserved for skills that have already proven themselves mechanically.

```
  Submitted Skill
        |
        v
 +--------------------------+
 | Layer 1: Structural      |   fast, deterministic
 |          Validation      |
 +--------------------------+
        |  pass
        v
 +--------------------------+
 | Layer 2: Trigger         |   automated, stochastic
 |          Accuracy        |
 +--------------------------+
        |  pass
        v
 +--------------------------+
 | Layer 3: Functional      |   automated, deeper
 |          Testing         |
 +--------------------------+
        |  pass
        v
 +--------------------------+
 | Layer 4: Human Review    |   manual, final gate
 +--------------------------+
        |  approved
        v
   Quality Passport
   issued & published
```

---

### Layer 1: Structural Validation

**Purpose:** Confirm the skill conforms to the Claude Code skill specification and contains no obvious hazards.

**Primary tool:** `quick_validate.py` from Anthropic's [skill-creator](https://github.com/anthropics/skill-creator) repository.

#### Standard checks (via `quick_validate.py`)

| Check | Requirement |
|---|---|
| `SKILL.md` exists | The skill root must contain a `SKILL.md` file |
| Valid YAML frontmatter | The frontmatter block must parse without errors |
| Required fields | `name` and `description` must be present in frontmatter |
| Naming conventions | Skill name must be kebab-case, maximum 64 characters |
| Description length | `description` must be fewer than 1024 characters |
| No unexpected properties | Frontmatter must not contain properties outside the recognized set |

#### Extended checks (added by this project)

We supplement `quick_validate.py` with additional checks:

1. **Security scan of `scripts/` directory**
   - No use of `subprocess.call` (or related) with `shell=True`
   - No network requests to unknown or non-allowlisted hosts
   - No filesystem traversal outside the workspace (e.g., `../../`, absolute paths to system directories)

2. **License compatibility**
   - If the skill repository includes a LICENSE file, it must be compatible with redistribution (MIT, Apache-2.0, BSD, ISC, or similarly permissive)
   - Skills with no license are flagged for contributor follow-up

3. **Total skill size**
   - The entire skill directory (including all assets) must be under **1 MB**
   - Skills exceeding this limit are rejected; contributors are asked to trim or externalize large assets

**Outcome:** Pass or Fail. Failures include a list of specific violations so the contributor can fix and resubmit.

---

### Layer 2: Trigger Accuracy

**Purpose:** Verify that the skill activates when it should, and does not activate when it should not.

**Primary tool:** `run_eval.py` from Anthropic's skill-creator infrastructure.

#### Procedure

1. **Generate eval queries.** For each skill, create **20 evaluation queries**:
   - **10 should-trigger queries** -- prompts that clearly fall within the skill's domain and should cause it to activate
   - **10 should-not-trigger queries** -- prompts that are superficially related or entirely unrelated and should *not* cause activation

2. **Run each query 3 times.** Each query is executed via `claude -p` three separate times to account for stochastic variation in trigger behavior. A query is considered "triggered" if the skill activates in at least 2 of 3 runs.

3. **Compute precision and recall.**
   - **Precision** = (true negatives among should-not-trigger queries) / (total should-not-trigger queries). Measures: "Does the skill stay quiet when it should?"
   - **Recall** = (true positives among should-trigger queries) / (total should-trigger queries). Measures: "Does the skill activate when it should?"
   - **Overall trigger accuracy** = harmonic mean of precision and recall

4. **Threshold:** The skill must achieve **>80% overall trigger accuracy** to advance to Layer 3.

**Outcome:** Pass (with precision/recall/overall scores recorded) or Fail.

---

### Layer 3: Functional Testing

**Purpose:** Confirm that the skill actually improves Claude Code's output quality on tasks within its domain.

#### Procedure

1. **Create task prompts.** For each skill, write **3-5 realistic task prompts** that represent the kind of work a user would invoke the skill for.

2. **Run with-skill vs. without-skill.** Each task prompt is executed twice via subagents:
   - **With-skill:** Claude Code runs with the skill installed
   - **Without-skill (baseline):** Claude Code runs without the skill

3. **Grade outputs.** Each output pair is graded using a `grader.md` rubric that defines specific **assertions** -- concrete, verifiable statements about what the output should contain or how it should behave. Examples of assertions:
   - "Output contains a valid SQL query"
   - "Generated code compiles without errors"
   - "Response addresses all 3 sub-questions in the prompt"

4. **Aggregate results.** Use `aggregate_benchmark.py` to compute:
   - **Assertion pass rate** across all tasks and assertions
   - **Improvement over baseline** -- the delta between with-skill and without-skill pass rates

5. **Thresholds:** The skill must achieve:
   - **>70% assertion pass rate** AND
   - **Measurable improvement over baseline** (the with-skill pass rate must be strictly higher than without-skill)

**Outcome:** Pass (with pass rate, improvement delta, and assertion count recorded) or Fail.

---

### Layer 4: Human Review

**Purpose:** Final qualitative gate. A human reviewer examines the skill's outputs, edge-case behavior, safety profile, and overall usefulness.

**Primary tool:** `generate_review.py` from the pipeline, which produces an eval viewer -- an HTML report consolidating all automated results plus sample outputs for human inspection.

#### Review criteria

| Criterion | What the reviewer checks |
|---|---|
| **Output quality** | Are the skill-assisted outputs well-written, correct, and complete? |
| **Edge cases** | Does the skill degrade gracefully on unusual inputs? |
| **Safety** | Could the skill produce harmful, misleading, or privacy-violating outputs? |
| **Usefulness** | Does the skill provide genuine value that justifies its inclusion? |

#### Decisions

- **Approve** -- Skill passes all criteria. Issued a Quality Passport.
- **Reject** -- Skill has fundamental issues (safety, quality, or relevance). Contributor is informed with specific reasons.
- **Request Changes** -- Skill is promising but needs specific improvements. Contributor receives actionable feedback.

All approved skills receive a **Quality Passport** (see below) and are published to the curated collection.

---

## Quality Passport Schema

Every approved skill receives a Quality Passport -- a structured JSON document stored in the `passports/` directory. The passport is both a certificate of evaluation and a machine-readable metadata record.

```json
{
  "skill_name": "string",
  "version": "string",
  "source_repo": "string",
  "publisher": "string",
  "evaluated_date": "ISO 8601",
  "evaluator": "string",
  "structural_validation": {
    "passed": true,
    "details": "string"
  },
  "trigger_accuracy": {
    "precision": 0.95,
    "recall": 0.90,
    "overall": 0.92
  },
  "functional_score": {
    "pass_rate": 0.85,
    "improvement_over_baseline": 0.30,
    "assertions_tested": 15
  },
  "security_scan": {
    "passed": true,
    "warnings": []
  },
  "human_review": {
    "approved": true,
    "reviewer": "string",
    "notes": "string"
  },
  "compatible_agents_tested": ["Claude Code", "OpenClaw"],
  "recommended_use_cases": ["string"],
  "known_limitations": ["string"],
  "overall_tier": "gold | silver | bronze"
}
```

### Tier Definitions

| Tier | Trigger Accuracy | Functional Score | Security | Human Review |
|---|---|---|---|---|
| **Gold** | >90% overall | >85% pass rate | Clean (no warnings) | Approved with no reservations |
| **Silver** | >80% overall | >70% pass rate | Clean (no warnings) | Approved with minor notes |
| **Bronze** | >70% overall | >60% pass rate | Clean (warnings acceptable) | Approved with caveats |

- **Gold** skills are the highest-quality entries in the collection. They demonstrate excellent trigger discipline, strong functional improvements, a spotless security profile, and unqualified human approval.
- **Silver** skills are solid and recommended for general use. Minor imperfections in trigger accuracy or functional coverage are noted but do not diminish their overall value.
- **Bronze** skills are useful but come with known limitations. They pass all minimum thresholds and are safe to use, but users should be aware of the caveats documented in the passport.

Skills that fail to meet Bronze thresholds are not published. Contributors receive detailed feedback and are encouraged to iterate.

---

## Tools & Dependencies

The evaluation pipeline reuses several tools from Anthropic's [skill-creator](https://github.com/anthropics/skill-creator) repository, supplemented by scripts in this project's `pipeline/` directory.

### From Anthropic's skill-creator (bundled in `pipeline/`)

These tools are bundled directly in this repository under `pipeline/` so no external dependency is needed.

| Tool | Path | Purpose |
|---|---|---|
| `grader.md` | `pipeline/agents/grader.md` | Layer 3 grading agent -- evaluates assertions against outputs with 8-step evidence-based process |
| `comparator.md` | `pipeline/agents/comparator.md` | Blind A/B comparison agent -- scores two outputs without knowing which skill produced them |
| `analyzer.md` | `pipeline/agents/analyzer.md` | Post-hoc analysis agent -- identifies why winner won and generates improvement suggestions |
| `run_eval.py` | `pipeline/scripts/run_eval.py` | Trigger evaluation engine -- tests skill descriptions against `claude -p` |
| `aggregate_benchmark.py` | `pipeline/scripts/aggregate_benchmark.py` | Benchmark aggregation -- computes mean ± stddev across multiple runs |
| `run_loop.py` | `pipeline/scripts/run_loop.py` | Description optimization loop -- iterates eval + improve with train/test split |
| `improve_description.py` | `pipeline/scripts/improve_description.py` | Claude-driven description improvement based on eval failures |
| `generate_report.py` | `pipeline/scripts/generate_report.py` | Interactive HTML optimization report with per-iteration results |
| `quick_validate.py` | `pipeline/scripts/quick_validate.py` | Structural validation -- checks SKILL.md, frontmatter, naming |
| `package_skill.py` | `pipeline/scripts/package_skill.py` | Packages skill into distributable .skill file |
| `viewer.html` | `pipeline/eval-viewer/viewer.html` | Interactive review interface for human evaluation |
| `generate_review.py` | `pipeline/eval-viewer/generate_review.py` | Generates and serves the review HTML interface |
| `schemas.md` | `pipeline/references/schemas.md` | JSON schema definitions for evals, grading, benchmark, comparison, analysis |

### From this project (`pipeline/`)

| Tool | Path | Purpose |
|---|---|---|
| `batch_validate.py` | `pipeline/batch_validate.py` | Layer 1 batch orchestrator -- runs structural validation across multiple skills |
| `batch_trigger_eval.py` | `pipeline/batch_trigger_eval.py` | Layer 2 batch orchestrator -- auto-generates eval queries and runs trigger tests |
| `batch_functional_eval.py` | `pipeline/batch_functional_eval.py` | Layer 3 batch orchestrator -- runs with-skill vs without-skill comparisons and grades outputs |
| `security_scan.py` | `pipeline/security_scan.py` | Security scanner -- detects 28+ dangerous patterns across 6 categories |
| `issue_passport.py` | `pipeline/issue_passport.py` | Post-approval -- generates Quality Passport JSON from aggregated evaluation results |
| `generate_catalog.py` | `pipeline/generate_catalog.py` | Catalog generation -- aggregates passports into catalog.json and README tables |

### Runtime dependencies

- **Claude Code CLI** (`claude`) -- used via `claude -p` for trigger evaluation, functional testing, and description optimization
- **Python 3.10+** -- all pipeline scripts are Python
- **PyYAML** (optional) -- used by `quick_validate.py` for YAML parsing; falls back to manual parsing if unavailable
- **jq** (optional) -- useful for inspecting passport JSON files from the command line
