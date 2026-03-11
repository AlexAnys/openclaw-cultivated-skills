# 贡献指南

[English](./CONTRIBUTING.md)

感谢你对 openclaw-cultivated-skills 的关注！本指南介绍如何提交技能、提交前如何自检，以及我们的质量标准。

目前所有评估均在 Claude Code CLI 上使用 Claude Opus 4.6 进行。

---

## 如何提交技能

1. **准备好你的技能仓库。** 技能必须放在独立的公开 Git 仓库中，并遵循 [Claude Code 技能规范](https://github.com/anthropics/skill-creator)。最基本的要求是包含一份格式正确的 `SKILL.md`，带有 YAML 前置元数据。

2. **先做自检。** 提交之前，用 [skill-creator](https://github.com/anthropics/skill-creator) 里的 `quick_validate.py` 跑一遍你的技能目录，尽早发现结构问题（具体见下方自检说明）。

3. **提交 Issue。** 前往 [openclaw-cultivated-skills Issue 页面](https://github.com/AlexAnys/openclaw-cultivated-skills/issues)，新建 Issue，包含以下信息：
   - **标题：** `[Skill Submission] your-skill-name`
   - **内容：** 技能仓库地址、简要功能说明、所属分类（如 `developer-tools`、`writing-and-documents`、`ai-and-models` 等）

4. **等待评估。** 维护者会接手你的提交，通过 [四层评估流程](./METHODOLOGY.md) 进行审核，并在 Issue 中反馈结果：
   - **通过** -- 技能会被收录到精选集合中，并颁发质量护照（Quality Passport）
   - **需要修改** -- 指出具体改进方向，修改后回复 Issue 即可
   - **未通过** -- 不符合收录标准，会说明原因

---

## 提交前自检

在本地跑一遍结构验证，能帮大家节省不少时间：

```bash
# 克隆 skill-creator（如果还没有的话）
git clone https://github.com/anthropics/skill-creator.git

# 对你的技能目录运行验证
python skill-creator/src/quick_validate.py /path/to/your-skill/

# 查看输出，提交前把所有报错修掉
```

**`quick_validate.py` 会检查以下内容：**

- 技能根目录下存在 `SKILL.md`
- YAML 前置元数据格式正确、可解析
- 包含必填字段（`name`、`description`）
- 技能名称为 kebab-case，不超过 64 个字符
- 描述不超过 1024 个字符
- 前置元数据中没有多余字段

全部通过、没有报错，就可以放心提交了。

---

## 质量标准

我们从四个维度评估每个提交的技能，详细技术说明见 [METHODOLOGY.md](./METHODOLOGY.md)。

**评估要点：**

- **结构规范** -- `SKILL.md` 格式正确、前置元数据完整、命名合理
- **触发精度** -- 该触发时触发、不该触发时安静（准确率要求 >80%）
- **实际效果** -- 经人工评审确认，技能带来了可衡量的改进
- **安全性** -- 不含危险代码、不存在恶意行为、不侵犯隐私
- **实用性** -- 解决真实需求，给用户带来切实价值

**等级体系：**

通过审核的技能会在质量护照中获得对应等级：

| 等级 | 触发准确率 | 安全性 | 人工评审 |
|---|---|---|---|
| 金 | >90% | 无警告 | 无保留意见 |
| 银 | >80% | 无警告 | 有少量备注 |
| 铜 | >70% | 允许警告 | 有附加说明 |

---

## 会被直接拒绝的情况

以下情况不进入完整评估，直接拒绝：

- **缺少 `SKILL.md`** -- 提交中没有 `SKILL.md`，或该文件缺少必要的 YAML 前置元数据。这是最基本的门槛。

- **灌水或敷衍提交** -- 明显是自动生成的占位内容、与现有技能雷同且没有实质改进、或者根本不像是认真做出来的东西。

- **加密货币、赌博或金融诈骗相关** -- 推广加密货币骗局、赌博平台或其他金融掠夺性服务的技能。

- **恶意代码** -- 包含以下行为的代码：
  - 以不安全方式使用 `shell=True` 执行命令
  - 向不明或可疑主机发网络请求
  - 在工作区目录之外遍历文件系统
  - 窃取数据、植入后门或危害系统安全
  - 混淆或隐藏真实行为

被直接拒绝的提交会在 Issue 中收到简要说明。修复问题后欢迎重新提交。

---

## 有问题？

创建带 `[Question]` 标签的 Issue，或在仓库中发起讨论，我们很乐意帮忙！
