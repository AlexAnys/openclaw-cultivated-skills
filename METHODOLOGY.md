# Evaluation Methodology

<div align="center">

English | [中文](METHODOLOGY_zh.md)

</div>

This document describes the evaluation pipeline used by **openclaw-cultivated-skills** to vet, score, and certify community-contributed Claude Code skills. Every skill that enters the curated collection passes through a 4-layer funnel before it earns a Quality Passport and is published to the `skills/` directory.

> **Runtime environment:** All automated evaluation runs through `claude -p` invoking Claude Opus 4.6. Results in Quality Passports reflect this specific model and runtime.

---

## Evaluation Pipeline

The pipeline is a progressive funnel: each layer is cheaper and faster than the next, so broken skills are rejected early and expensive human time is reserved for skills that have already proven themselves mechanically.

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
 | Layer 3: Security Scan   |   automated, static analysis
 +--------------------------+
        |  pass
        v
 +--------------------------+
 | Layer 4: Human Review    |   manual, final gate
 +--------------------------+
        |  approved
        v
   Quality Passport
   written & published
```

---

### Layer 1: Structural Validation

**Purpose:** Confirm the skill conforms to the Claude Code skill specification and contains no obvious hazards.

**Tool:** `pipeline/batch_validate.py` -- reimplements `quick_validate.py` logic internally (no external dependency on skill-creator).

| Check | Requirement |
|---|---|
| `SKILL.md` exists | The skill root must contain a `SKILL.md` file |
| Valid YAML frontmatter | The frontmatter block must parse without errors |
| Required fields | `name` and `description` must be present in frontmatter |
| Naming conventions | Skill name must be kebab-case |
| Description length | `description` must be fewer than 1024 characters |
| Allowed frontmatter keys | Frontmatter must not contain properties outside the recognized set |

**Extended checks** (also in `batch_validate.py`):

- **Security pattern scan of `scripts/`** -- flags shell injection patterns, suspicious network access, and filesystem traversal outside the workspace.
- **Total skill size** -- warns above 500 KB, rejects above 2 MB.

**Outcome:** Pass or Fail, with a list of specific violations.

---

### Layer 2: Trigger Accuracy

**Purpose:** Verify that the skill activates when it should and stays quiet when it should not.

**Tool:** `pipeline/batch_trigger_eval.py` -- a self-contained reimplementation (does not use skill-creator's `run_eval.py`).

#### Procedure

1. **Auto-generate eval queries.** For each skill, the tool calls `claude -p` to generate **20 evaluation queries**: 10 should-trigger and 10 should-not-trigger. Queries are cached in `trigger-eval.json` for reproducibility.

2. **Run each query 3 times.** Each query is executed via `claude -p` three separate times to account for stochastic variation. A query is considered "triggered" if the skill activates in at least 2 of 3 runs.

3. **Compute standard ML metrics.**
   - **Precision** = TP / (TP + FP)
   - **Recall** = TP / (TP + FN)
   - **Accuracy** = (TP + TN) / total

4. **Threshold:** The skill must achieve **>80% accuracy** to advance to Layer 3.

**Outcome:** Pass (with precision, recall, and accuracy recorded) or Fail.

---

### Layer 3: Security Scan

**Purpose:** Deep static analysis of all scripts bundled with the skill.

**Tool:** `pipeline/security_scan.py`

The scanner checks for the following pattern categories:

| Category | Examples |
|---|---|
| Shell injection | `subprocess` with `shell=True`, `os.system()`, backtick execution |
| Code injection | `eval()`, `exec()`, dynamic imports |
| Network access | `urllib`, `requests`, `socket`, outbound connections |
| Filesystem abuse | Path traversal (`../../`), writes to system directories |
| Credential access | Reading env vars for tokens, keychain access |
| Deserialization | `pickle.loads`, `yaml.unsafe_load` |
| Native code | Compiled binaries, shared libraries, FFI calls |

**Verdict:** CLEAN, REVIEW, or REJECT.

- **CLEAN** -- no patterns detected.
- **REVIEW** -- patterns detected that may be benign but require human judgment.
- **REJECT** -- patterns detected that are unacceptable.

---

### Layer 4: Human Review

**Purpose:** Final qualitative gate. A human reviewer installs the skill and tests it hands-on.

#### Procedure

1. **Install the skill** locally in Claude Code or OpenClaw.
2. **Run it against realistic tasks** in real projects -- not synthetic benchmarks.
3. **Evaluate** output quality, edge-case behavior, safety, and usefulness.

There is no automated HTML report. Review is hands-on.

#### Decisions

- **Approve** -- Skill passes all criteria. A Quality Passport is written manually.
- **Reject** -- Skill has fundamental issues. Contributor is informed with specific reasons.
- **Request Changes** -- Skill is promising but needs improvements. Contributor receives actionable feedback.

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
    "accuracy": 0.92
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
  "tested_with": "Claude Opus 4.6 via Claude Code CLI",
  "recommended_use_cases": ["string"],
  "known_limitations": ["string"],
  "overall_tier": "gold|silver|bronze"
}
```

### Tier Definitions

| Tier | Trigger Accuracy | Security | Human Review |
|---|---|---|---|
| **Gold** | >90% accuracy | Clean (no warnings) | Approved with no reservations |
| **Silver** | >80% accuracy | Clean (no warnings) | Approved with minor notes |
| **Bronze** | >70% accuracy | Clean (warnings acceptable) | Approved with caveats |

Skills that fail to meet Bronze thresholds are not published. Contributors receive detailed feedback and are encouraged to iterate.

---

## Tools & Dependencies

### Pipeline scripts (`pipeline/`)

| Script | Layer | Purpose |
|---|---|---|
| `batch_validate.py` | 1 | Structural validation and security pattern scanning |
| `batch_trigger_eval.py` | 2 | Auto-generates eval queries via `claude -p`, runs trigger accuracy tests |
| `security_scan.py` | 3 | Deep static analysis of bundled scripts |
| `generate_catalog.py` | -- | Generates `catalog.json` from passport data |

### Runtime dependencies

| Dependency | Required | Notes |
|---|---|---|
| Claude Code CLI (`claude -p`) | Yes | Powers trigger evaluation and query generation |
| Python 3.10+ | Yes | All pipeline scripts are Python |
| PyYAML | Optional | Used for YAML parsing if installed |
| jq | Optional | Useful for inspecting passport JSON from the command line |

> **Note:** This pipeline is inspired by Anthropic's [skill-creator](https://github.com/anthropics/skill-creator) but is entirely self-contained. skill-creator does **not** need to be installed.

---

## Planned Enhancements

The following capabilities are not yet implemented but are on the roadmap:

- **Functional comparison testing** -- with-skill vs. without-skill execution via subagents, measuring actual output quality improvement.
- **Integration with skill-creator tools** -- adopting `grader.md`, `aggregate_benchmark.py`, and `generate_review.py` from Anthropic's skill-creator for standardized grading.
- **Description optimization** -- using skill-creator's `run_loop.py` and `improve_description.py` to iteratively refine skill trigger descriptions.
- **GitHub Actions CI** -- automated evaluation on pull request, so contributors get pipeline results before human review.
