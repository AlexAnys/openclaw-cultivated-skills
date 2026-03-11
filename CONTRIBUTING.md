# Contributing / 贡献指南

Thank you for your interest in contributing to openclaw-cultivated-skills! This guide explains how to submit a skill for evaluation, how to self-check before submitting, and what our quality standards are.

感谢您对 openclaw-cultivated-skills 的关注！本指南将说明如何提交技能进行评估、如何在提交前自检，以及我们的质量标准。

---

## How to Submit a Skill / 如何提交技能

### English

1. **Prepare your skill repository.** Your skill must live in its own public Git repository and follow the [Claude Code skill specification](https://github.com/anthropics/skill-creator). At minimum, it must contain a valid `SKILL.md` with proper YAML frontmatter.

2. **Self-evaluate first.** Before submitting, run `quick_validate.py` from [skill-creator](https://github.com/anthropics/skill-creator) against your skill to catch structural issues early (see the self-evaluation section below).

3. **Open an issue.** Go to the [openclaw-cultivated-skills issue tracker](https://github.com/AlexAnys/openclaw-cultivated-skills/issues) and create a new issue with:
   - **Title:** `[Skill Submission] your-skill-name`
   - **Body:** Include the URL of your skill repository, a brief description of what it does, and the category it belongs to (e.g., `development-workflow`, `frontend`, `infrastructure`, etc.)

4. **Wait for evaluation.** A maintainer will pick up your submission and run it through our [4-layer evaluation pipeline](./METHODOLOGY.md). You will receive feedback on the issue:
   - **Approved** -- your skill will be added to the curated collection with a Quality Passport
   - **Request Changes** -- specific improvements are needed; address them and comment on the issue
   - **Rejected** -- the skill does not meet our standards; reasons will be provided

### 中文

1. **准备技能仓库。** 您的技能必须存放在独立的公开 Git 仓库中，并遵循 [Claude Code 技能规范](https://github.com/anthropics/skill-creator)。至少需要包含一个有效的 `SKILL.md` 文件，并带有正确的 YAML 前置元数据。

2. **先进行自检。** 在提交之前，使用 [skill-creator](https://github.com/anthropics/skill-creator) 中的 `quick_validate.py` 对您的技能进行验证，以尽早发现结构性问题（请参阅下方的自检部分）。

3. **创建 Issue。** 前往 [openclaw-cultivated-skills Issue 页面](https://github.com/AlexAnys/openclaw-cultivated-skills/issues)，创建一个新 Issue，包含：
   - **标题：** `[Skill Submission] your-skill-name`
   - **内容：** 技能仓库的 URL、功能简述，以及所属分类（如 `development-workflow`、`frontend`、`infrastructure` 等）

4. **等待评估。** 维护者会接手您的提交，并通过我们的 [4 层评估流程](./METHODOLOGY.md) 进行审核。您将在 Issue 中收到反馈：
   - **通过** -- 技能将被添加到精选集合中，并获得质量护照（Quality Passport）
   - **需要修改** -- 需要具体改进；请修改后在 Issue 中回复
   - **拒绝** -- 技能未达到标准；会提供具体原因

---

## Self-Evaluation Before Submitting / 提交前自检

### English

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

### 中文

在本地运行结构验证器可以节省大家的时间。操作方法如下：

```bash
# 如果还没有克隆 skill-creator，请先克隆
git clone https://github.com/anthropics/skill-creator.git

# 对你的技能目录运行 quick_validate
python skill-creator/src/quick_validate.py /path/to/your-skill/

# 检查输出 -- 在提交前修复所有错误
```

**`quick_validate.py` 检查内容：**

- 技能根目录中存在 `SKILL.md`
- YAML 前置元数据有效且可解析
- 包含必填字段（`name`、`description`）
- 技能名称为 kebab-case 格式，且不超过 64 个字符
- 描述不超过 1024 个字符
- 前置元数据中没有意外的属性

如果您的技能通过 `quick_validate.py` 且无错误，即可提交。

---

## Quality Standards / 质量标准

### English

We evaluate every submitted skill across four dimensions. See [METHODOLOGY.md](./METHODOLOGY.md) for the full technical details.

**What we look for:**

- **Correct structure** -- valid `SKILL.md`, proper frontmatter, sensible naming
- **Trigger discipline** -- the skill activates when it should and stays quiet when it should not (>80% accuracy required)
- **Functional value** -- the skill measurably improves Claude Code's output on tasks within its domain (>70% assertion pass rate required)
- **Safety and security** -- no dangerous code patterns, no malicious behavior, no privacy violations
- **Usefulness** -- the skill addresses a real need and provides genuine value to users

**Tier system:**

All approved skills receive a tier rating in their Quality Passport:

| Tier | Trigger Accuracy | Functional Score | Security | Human Review |
|---|---|---|---|---|
| Gold | >90% | >85% | Clean | No reservations |
| Silver | >80% | >70% | Clean | Minor notes |
| Bronze | >70% | >60% | Warnings OK | Caveats noted |

### 中文

我们从四个维度评估每个提交的技能。完整技术细节请参阅 [METHODOLOGY.md](./METHODOLOGY.md)。

**我们关注的方面：**

- **结构正确性** -- 有效的 `SKILL.md`、正确的前置元数据、合理的命名
- **触发准确性** -- 技能在应该激活时激活，不应激活时保持静默（要求 >80% 准确率）
- **功能价值** -- 技能可以可量化地提升 Claude Code 在其领域内任务的输出质量（要求 >70% 断言通过率）
- **安全性** -- 无危险代码模式、无恶意行为、无隐私侵犯
- **实用性** -- 技能解决真实需求，为用户提供切实价值

**等级体系：**

所有通过审核的技能都会在质量护照中获得等级评定：

| 等级 | 触发准确率 | 功能得分 | 安全性 | 人工审核 |
|---|---|---|---|---|
| 金 | >90% | >85% | 无警告 | 无保留意见 |
| 银 | >80% | >70% | 无警告 | 有少量备注 |
| 铜 | >70% | >60% | 允许警告 | 有附加说明 |

---

## What Gets Auto-Rejected / 自动拒绝的情况

### English

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

### 中文

以下情况将被立即拒绝，不进入完整评估流程：

- **没有 `SKILL.md`** -- 提交中不包含 `SKILL.md` 文件，或该文件缺少必要的 YAML 前置元数据。这是最基本的要求。

- **垃圾或低质量提交** -- 明显是自动生成的填充内容、与已有技能重复且无实质改动的技能，或不属于真正有用技能的提交。

- **加密货币、赌博或金融剥削内容** -- 旨在推广加密货币骗局、赌博平台或其他金融掠夺性服务的技能。

- **恶意代码** -- 包含以下行为的代码：
  - 以不安全方式使用 `shell=True` 执行 Shell 命令
  - 向未知或可疑主机发送网络请求
  - 在工作区目录之外进行文件系统遍历
  - 窃取数据、安装后门或危害系统安全
  - 混淆其真实行为

如果您的提交被自动拒绝，您将在 Issue 中收到简要说明。欢迎修复问题后重新提交。

---

## Questions? / 有问题？

Open an issue with the `[Question]` tag or start a discussion in the repository. We are happy to help!

如有疑问，请创建带有 `[Question]` 标签的 Issue，或在仓库中发起讨论。我们很乐意提供帮助！
