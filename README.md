<div align="center">

English | [中文](README_zh.md)

</div>

<p align="center">
  <!-- TODO: Replace with actual logo -->
  <img src="https://via.placeholder.com/200x200?text=Cultivated+Skills" alt="openclaw-cultivated-skills" width="200"/>
</p>

<h1 align="center">openclaw-cultivated-skills</h1>

<p align="center">
  <strong>Quality-verified Agent Skills curated from 5,000+ community submissions</strong>
</p>

<p align="center">
  <a href="https://github.com/AlexAnys/openclaw-cultivated-skills/stargazers"><img src="https://img.shields.io/github/stars/AlexAnys/openclaw-cultivated-skills?style=flat-square" alt="Stars"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/AlexAnys/openclaw-cultivated-skills?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/skills-evaluating-blue?style=flat-square" alt="Skill Count"/>
  <img src="https://img.shields.io/badge/format-SKILL.md-purple?style=flat-square" alt="SKILL.md Format"/>
  <img src="https://img.shields.io/badge/tested_on-Claude_Code-orange?style=flat-square" alt="Tested on Claude Code"/>
</p>

<p align="center">
  <a href="#why-this-exists">Why</a> ·
  <a href="#quality-standard">Quality Standard</a> ·
  <a href="#skill-catalog">Catalog</a> ·
  <a href="#how-to-install">Install</a> ·
  <a href="#quality-passport">Passport</a> ·
  <a href="#contributing">Contributing</a>
</p>

---

## Why This Exists

The Agent Skills ecosystem is growing fast. [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) alone cataloged 13,729 raw skills (5,494 after deduplication), and [awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) added another 549+ from official teams. That is a lot of choice -- but quantity does not equal quality.

Common problems with community-submitted skills:

- **Poor trigger design** -- skills fire on the wrong prompts or fail to fire on the right ones.
- **Vague descriptions** -- the agent cannot figure out what the skill is supposed to do.
- **Missing safety boundaries** -- skills may execute destructive operations without guardrails.
- **Never tested in a real agent** -- they look fine on paper but break in practice.

**The solution:** this repository runs every candidate skill through a 4-layer evaluation pipeline -- automated structural checks, trigger-accuracy testing, security scanning, and hands-on human review. Only skills that pass all four layers receive a **Quality Passport** and are included here.

---

## Quality Standard

Every skill must pass through the following 4-layer evaluation funnel before inclusion:

```
  5,000+ community skills
         |
    Layer 1: Structural Validation ──── batch_validate.py
         |   Format compliance, required fields, SKILL.md spec
         |
    Layer 2: Trigger Accuracy ─────────  batch_trigger_eval.py (claude -p, Claude Opus 4.6)
         |   Positive triggers + negative non-triggers
         |
    Layer 3: Security Scan ────────────  security_scan.py
         |   Dangerous-command detection, permission checks
         |
    Layer 4: Human Review ─────────────  Hands-on testing in Claude Code / OpenClaw
         |   Real-world usage, output quality, edge cases
         v
    Quality Passport issued ── included in this repository
```

| Layer | Name | Description |
|:---:|:---|:---|
| L1 | **Structural Validation** | Validates SKILL.md format, required fields, and metadata integrity. Tool: `batch_validate.py` |
| L2 | **Trigger Accuracy** | Tests positive and negative trigger cases to measure precision and recall. Tool: `batch_trigger_eval.py` via `claude -p`, tested on Claude Opus 4.6 |
| L3 | **Security Scan** | Static analysis for risky patterns -- unauthorized filesystem operations, network requests, sensitive data exposure. Tool: `security_scan.py` |
| L4 | **Human Review** | Maintainer tests the skill in real projects using Claude Code and OpenClaw, evaluating output quality and edge-case handling |

---

## Skill Catalog

Skills are organized into user-centric categories:

```
skills/
├── writing-and-documents/
├── research-and-analysis/
├── communication-and-scheduling/
├── content-and-media/
├── productivity-and-organization/
├── finance-and-commerce/
├── learning-and-wellbeing/
├── data-and-automation/
├── developer-tools/
└── ai-and-models/
```

| Category | Description | Status |
|:---|:---|:---:|
| **Writing & Documents** | Create, edit, convert documents -- contracts to slide decks | Evaluating |
| **Research & Analysis** | Find info, analyze data, review literature, generate insights | Evaluating |
| **Communication & Scheduling** | Email, calendars, meetings across Google Workspace, Feishu, DingTalk | Evaluating |
| **Content & Media** | Social media, videos, podcasts, marketing materials | Evaluating |
| **Productivity & Organization** | Tasks, notes, knowledge bases, personal CRM, daily workflows | Evaluating |
| **Finance & Commerce** | Payments, financial analysis, e-commerce, invoicing | Evaluating |
| **Learning & Wellbeing** | Education, personal development, health tracking, household | Evaluating |
| **Data & Automation** | Connect systems, automate workflows, process data without code | Evaluating |
| **Developer Tools** | Coding, testing, debugging, deployment, security scanning, DevOps | Evaluating |
| **AI & Models** | AI models, prompts, training pipelines, agent orchestration | Evaluating |

> Skill counts will be updated after the first evaluation batch completes.

---

## How to Install

Skills use the **SKILL.md** standard format compatible with 30+ agents, but evaluation results are verified on **Claude Code** with **Claude Opus 4.6**.

### OpenClaw

```bash
# Install a single skill
clawhub install AlexAnys/openclaw-cultivated-skills/skills/developer-tools/<skill-name>

# Install an entire category
clawhub install AlexAnys/openclaw-cultivated-skills/skills/developer-tools
```

### Claude Code

```bash
# Copy a skill into Claude Code's skills directory
cp skills/developer-tools/<skill-name>/SKILL.md ~/.claude/skills/<skill-name>.md

# Or symlink to stay in sync with this repo
ln -s $(pwd)/skills/developer-tools/<skill-name>/SKILL.md ~/.claude/skills/<skill-name>.md
```

### Generic Agent

Most agents that support the SKILL.md standard read skill files from the project root or a user config directory:

```bash
# Project-level
cp skills/<category>/<skill-name>/SKILL.md /your/project/.skills/<skill-name>.md

# User-level (path varies by agent)
cp skills/<category>/<skill-name>/SKILL.md ~/.config/<agent>/skills/<skill-name>.md
```

---

## Quality Passport

Every skill that passes the full evaluation pipeline receives a **Quality Passport** stored in the `passports/` directory. A passport records the evidence behind the evaluation decision.

### Passport Fields

| Field | Description |
|:---|:---|
| **Trigger Accuracy** | Precision, recall, and overall accuracy from Layer 2 testing |
| **Security Check** | PASS / WARN / FAIL -- result of the Layer 3 security scan |
| **Human Review Notes** | Reviewer's qualitative assessment, usage advice, known limitations |
| **Tested With** | The model and agent used for evaluation (Claude Opus 4.6 via Claude Code CLI) |
| **Evaluation Date** | Date of the most recent full evaluation |
| **Source** | Where the skill was originally submitted from |

### Example Passport

```yaml
skill: example-skill
version: 1.0.0
evaluation_date: 2026-03-11
source: VoltAgent/awesome-openclaw-skills
tested_with: "Claude Opus 4.6 via Claude Code CLI"

trigger_accuracy:
  precision: 95%
  recall: 92%
  accuracy: 94%

security_check: PASS

human_review:
  reviewer: AlexAnys
  notes: "Stable output format, handles edge cases well. Consider chunking for very large files."
  known_limitations:
    - "Does not support files larger than 10 MB"
```

### Tier System

| Tier | Trigger Accuracy | Security | Human Review |
|:---:|:---:|:---:|:---|
| **Gold** | > 90% | Clean | No reservations |
| **Silver** | > 80% | Clean | Minor notes |
| **Bronze** | > 70% | Warnings OK | Caveats noted |

---

## Sources & Acknowledgments

This project draws skills and inspiration from the following projects:

| Project | Description |
|:---|:---|
| [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | The largest community collection of Agent Skills (13,729 raw / 5,494 filtered) -- primary source |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 549+ skills contributed by official teams |
| [anthropics/skill-creator](https://github.com/anthropics/skill-creator) | Anthropic's official skill creation tool |
| [obra/superpowers](https://github.com/obra/superpowers) | Agent enhancement collection -- excellent skill design patterns |

Thanks to all original skill authors for their work. Every included skill retains its original attribution.

---

## Contributing

We welcome contributions -- whether you want to submit a skill for evaluation, report an issue with an existing one, or improve the evaluation pipeline itself.

See [CONTRIBUTING.md](CONTRIBUTING.md) for full details.

---

## Related Projects

| Project | Description |
|:---|:---|
| [AlexAnys/awesome-openclaw-usecases-zh](https://github.com/AlexAnys/awesome-openclaw-usecases-zh) | Curated Chinese-language OpenClaw use cases |
| [AlexAnys/opencrew](https://github.com/AlexAnys/opencrew) | Multi-Agent OS for Decision Makers |
| [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | The largest community Agent Skills collection |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | Official-team Agent Skills collection |

---

## License

[MIT](LICENSE)

Skills included in this repository retain their original licenses. The evaluation tooling, templates, and documentation in this repository are licensed under MIT.
