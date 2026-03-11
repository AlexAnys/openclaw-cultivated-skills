# Contributing

[中文版](./CONTRIBUTING_zh.md)

Thank you for your interest in contributing to openclaw-cultivated-skills! This guide explains how to submit a skill for evaluation, how to self-check before submitting, and what our quality standards are.

All evaluation currently runs on Claude Opus 4.6 via Claude Code CLI.

---

## How to Submit a Skill

1. **Prepare your skill repository.** Your skill must live in its own public Git repository and follow the [Claude Code skill specification](https://github.com/anthropics/skill-creator). At minimum, it must contain a valid `SKILL.md` with proper YAML frontmatter.

2. **Self-evaluate first.** Before submitting, run `quick_validate.py` from [skill-creator](https://github.com/anthropics/skill-creator) against your skill to catch structural issues early (see the self-evaluation section below).

3. **Open an issue.** Go to the [openclaw-cultivated-skills issue tracker](https://github.com/AlexAnys/openclaw-cultivated-skills/issues) and create a new issue with:
   - **Title:** `[Skill Submission] your-skill-name`
   - **Body:** Include the URL of your skill repository, a brief description of what it does, and the category it belongs to (e.g., `developer-tools`, `writing-and-documents`, `ai-and-models`, etc.)

4. **Wait for evaluation.** A maintainer will pick up your submission and run it through our [4-layer evaluation pipeline](./METHODOLOGY.md). You will receive feedback on the issue:
   - **Approved** -- your skill will be added to the curated collection with a Quality Passport
   - **Request Changes** -- specific improvements are needed; address them and comment on the issue
   - **Rejected** -- the skill does not meet our standards; reasons will be provided

---

## Self-Evaluation Before Submitting

Running the structural validator locally saves time for everyone. Here is how:

```bash
# Clone skill-creator if you haven't already
git clone https://github.com/anthropics/skill-creator.git

# Run quick_validate against your skill directory
python skill-creator/src/quick_validate.py /path/to/your-skill/

# Check the output -- fix any errors before submitting
```

**What `quick_validate.py` checks:**

- `SKILL.md` exists in the skill root
- YAML frontmatter is valid and parseable
- Required fields (`name`, `description`) are present
- Skill name is kebab-case and at most 64 characters
- Description is under 1024 characters
- No unexpected properties in frontmatter

If your skill passes `quick_validate.py` with no errors, it is ready for submission.

---

## Quality Standards

We evaluate every submitted skill across four dimensions. See [METHODOLOGY.md](./METHODOLOGY.md) for the full technical details.

**What we look for:**

- **Correct structure** -- valid `SKILL.md`, proper frontmatter, sensible naming
- **Trigger discipline** -- the skill activates when it should and stays quiet when it should not (>80% accuracy required)
- **Functional value** -- the skill provides measurable improvement as assessed during human review
- **Safety and security** -- no dangerous code patterns, no malicious behavior, no privacy violations
- **Usefulness** -- the skill addresses a real need and provides genuine value to users

**Tier system:**

All approved skills receive a tier rating in their Quality Passport:

| Tier | Trigger Accuracy | Security | Human Review |
|---|---|---|---|
| Gold | >90% | Clean | No reservations |
| Silver | >80% | Clean | Minor notes |
| Bronze | >70% | Warnings OK | Caveats noted |

---

## What Gets Auto-Rejected

The following will cause immediate rejection without full evaluation:

- **No `SKILL.md`** -- the submission does not contain a `SKILL.md` file, or the file is missing required YAML frontmatter. This is the most basic requirement.

- **Spam or low-effort submissions** -- skills that are clearly auto-generated filler, duplicates of existing skills with no meaningful changes, or submissions that do not represent a genuine attempt at a useful skill.

- **Crypto, gambling, or financially exploitative content** -- skills designed to promote cryptocurrency schemes, gambling platforms, or other financially predatory services.

- **Malicious code** -- any skill containing code that attempts to:
  - Execute shell commands with `shell=True` in an unsafe manner
  - Make network requests to unknown or suspicious hosts
  - Traverse the filesystem outside the workspace directory
  - Exfiltrate data, install backdoors, or compromise system security
  - Obfuscate its true behavior

If your submission is auto-rejected, you will receive a brief explanation on your issue. You are welcome to fix the problems and resubmit.

---

## Questions?

Open an issue with the `[Question]` tag or start a discussion in the repository. We are happy to help!
