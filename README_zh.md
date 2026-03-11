<div align="center">

[English](README.md) | 中文

</div>

<p align="center">
  <!-- TODO: Replace with actual logo -->
  <img src="https://via.placeholder.com/200x200?text=Cultivated+Skills" alt="openclaw-cultivated-skills" width="200"/>
</p>

<h1 align="center">openclaw-cultivated-skills</h1>

<p align="center">
  <strong>从 5,000+ 社区 Skills 中精选验证的高质量技能集</strong>
</p>

<p align="center">
  <a href="https://github.com/AlexAnys/openclaw-cultivated-skills/stargazers"><img src="https://img.shields.io/github/stars/AlexAnys/openclaw-cultivated-skills?style=flat-square" alt="Stars"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/AlexAnys/openclaw-cultivated-skills?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/skills-evaluating-blue?style=flat-square" alt="Skill Count"/>
  <img src="https://img.shields.io/badge/compatible_agents-30%2B-green?style=flat-square" alt="30+ Compatible Agents"/>
  <img src="https://img.shields.io/badge/format-SKILL.md-purple?style=flat-square" alt="SKILL.md Format"/>
</p>

<p align="center">
  <a href="#为什么做这个项目">为什么</a> ·
  <a href="#质量标准">质量标准</a> ·
  <a href="#技能目录">技能目录</a> ·
  <a href="#安装方式">安装</a> ·
  <a href="#质量护照">质量护照</a> ·
  <a href="#参与贡献">贡献</a>
</p>

---

## 为什么做这个项目

**问题**

Agent Skills 生态正在爆发式增长。仅 [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) 一个仓库就收录了 13,729 个 Skills，经过初步筛选后仍有 5,494 个。[awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) 又贡献了 549+ 个由官方团队提供的技能。

数量多不等于好用。社区 Skills 的典型问题：

- 触发词设计粗糙，该触发的时候不触发，不该触发的时候疯狂干扰
- 功能描述含糊其辞，Agent 根本不知道什么时候该调用
- 缺乏安全边界，可能悄无声息地执行危险操作
- 从未在真实项目中验证过，一跑就出错

**解决方案**

本项目对每一个收录的 Skill 执行标准化的四层评估流水线（自动化测试 + 人工审核），只有通过全部验证的 Skill 才能获得 **Quality Passport（质量护照）** 并进入本仓库。

简单来说：我们替你踩过坑，你只需要挑选和使用。

---

## 质量标准

每个 Skill 必须依次通过以下四层漏斗，才能被收录：

```
  13,729 社区 Skills（原始数据）
         |
    第一层：结构校验 ──────────── batch_validate.py
         |   格式校验、必填字段检查、SKILL.md 规范合规性
         |
    第二层：触发精准度 ─────────── batch_trigger_eval.py
         |   基于 claude -p 驱动，由 Claude Opus 4.6 评估
         |   正向触发 + 反向不触发，双向验证
         |
    第三层：安全扫描 ──────────── security_scan.py
         |   危险命令检测、权限边界检查、敏感操作审计
         |
    第四层：人工审核 ──────────── 在 Claude Code / OpenClaw 中实际测试
         |   真实场景测试、输出质量评估、边界情况验证
         ▼
    ✓ 颁发质量护照 ── 收录至本仓库
```

| 层级 | 名称 | 说明 |
|:---:|:---|:---|
| L1 | **结构校验** | 验证 SKILL.md 格式规范、必填字段完整性、元数据有效性。对应工具：`batch_validate.py` |
| L2 | **触发精准度** | 使用正向和反向测试用例验证触发词是否能精准匹配目标场景且不误触发。对应工具：`batch_trigger_eval.py`（基于 `claude -p`，由 Claude Opus 4.6 驱动） |
| L3 | **安全扫描** | 静态分析潜在安全风险——未授权的文件系统操作、可疑网络请求、敏感数据泄露等。对应工具：`security_scan.py` |
| L4 | **人工审核** | 由维护者在真实项目中使用 Claude Code / OpenClaw 实际测试，评估输出质量、边界情况处理、兼容性表现 |

---

## 技能目录

Skills 按用户场景分类组织。以下是当前的分类体系：

| 分类 | 说明 | 状态 |
|:---|:---|:---:|
| **写作与文档** | 创建、编辑、转换各类文档——从合同到演示文稿 | 评估中 |
| **研究与分析** | 信息检索、数据分析、文献综述、决策支持 | 评估中 |
| **沟通与日程** | 邮件、日历、会议管理——覆盖 Google Workspace、飞书、钉钉、企微 | 评估中 |
| **内容与媒体** | 社交媒体运营（小红书、抖音等）、视频制作、播客、营销素材 | 评估中 |
| **效率与管理** | 任务管理、笔记、知识库、个人 CRM、日常工作流 | 评估中 |
| **财务与商务** | 支付集成、财务分析、电商运营、发票管理 | 评估中 |
| **学习与生活** | 教育、个人成长、健康追踪、家庭管理 | 评估中 |
| **数据与自动化** | 系统对接、工作流自动化、数据处理——无需编码 | 评估中 |
| **开发者工具** | 编码、测试、调试、部署、安全扫描、DevOps | 评估中 |
| **AI 与模型** | AI 模型、提示词工程、训练流水线、Agent 协作 | 评估中 |

> 各分类的具体 Skill 数量将在首批评估完成后更新。

---

## 安装方式

Skills 使用 SKILL.md 标准格式，兼容 30+ Agent 工具，但评估结果仅在 Claude Code (Claude Opus 4.6) 上验证。

### OpenClaw

```bash
# 安装单个 Skill
clawhub install AlexAnys/openclaw-cultivated-skills/skills/<category>/<skill-name>

# 安装整个分类
clawhub install AlexAnys/openclaw-cultivated-skills/skills/<category>
```

### Claude Code

```bash
# 将 SKILL.md 复制到 Claude Code 的 skills 目录
cp skills/<category>/<skill-name>/SKILL.md ~/.claude/skills/<skill-name>.md

# 或者创建符号链接，方便后续同步更新
ln -s $(pwd)/skills/<category>/<skill-name>/SKILL.md ~/.claude/skills/<skill-name>.md
```

### 通用安装路径

大多数支持 Agent Skills 标准的工具都会从项目根目录或用户配置目录中读取 `SKILL.md` 文件：

```bash
# 方式一：复制到项目根目录
cp skills/<category>/<skill-name>/SKILL.md /your/project/.skills/<skill-name>.md

# 方式二：复制到用户级配置目录（具体路径因 Agent 而异）
cp skills/<category>/<skill-name>/SKILL.md ~/.config/<agent>/skills/<skill-name>.md
```

**兼容 Agent 列表** (30+):
Claude Code, Cursor, Codex, Gemini CLI, OpenCode, Kiro, Windsurf, Cline, Aider, Continue, Zed AI, Amp, Roo Code, Trae, PearAI, Melty, Void, Plandex, Goose, Aide, Refact, Sourcegraph Cody, Tabnine Chat, Mentat, avante.nvim, Supermaven, Blackbox AI, Amazon Q CLI 等。

---

## 质量护照

每个通过评估的 Skill 都会获得一份 Quality Passport（质量护照），存放在 `passports/` 目录下。

### 护照字段说明

| 字段 | 说明 |
|:---|:---|
| **trigger_accuracy** / 触发精准率 | 正向触发成功率 + 反向不触发率（目标: >= 90%） |
| **security_check** / 安全检查 | PASS / WARN / FAIL — 危险操作检测结果 |
| **human_review** / 人工审核备注 | 审核者的定性评价、使用建议、已知限制 |
| **compatible_agents_tested** / 已测试兼容 Agent | 实际验证通过的 Agent 列表及版本 |
| **evaluation_date** / 评估日期 | 最近一次完整评估的时间 |
| **source** / 来源 | 原始提交来源（社区仓库、官方团队等） |

### 护照示例

```yaml
skill: example-skill
version: 1.0.0
evaluation_date: 2026-03-11
source: VoltAgent/awesome-openclaw-skills
tested_with: "Claude Opus 4.6 via Claude Code CLI"

trigger_accuracy:
  positive_rate: 95%    # 正向触发成功率
  negative_rate: 100%   # 反向不触发率

security_check: PASS

compatible_agents_tested:
  - claude-code@1.x
  - cursor@0.x
  - gemini-cli@1.x

human_review:
  reviewer: AlexAnys
  notes: "输出格式稳定，边界处理良好。建议在大文件场景下增加分块策略。"
  known_limitations:
    - "不支持超过 10MB 的文件"
```

### 等级体系

所有通过审核的 Skill 都会在质量护照中获得等级评定：

| 等级 | 触发准确率 | 安全性 | 人工审核 |
|:---:|:---:|:---:|:---:|
| 金 | >90% | 无警告 | 无保留意见 |
| 银 | >80% | 无警告 | 有少量备注 |
| 铜 | >70% | 允许警告 | 有附加说明 |

---

## 来源与致谢

本项目的 Skill 来源及灵感来自以下优秀项目：

| 项目 | 说明 |
|:---|:---|
| [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | 35K stars — 社区最大的 Skills 集合（13,729 原始 / 5,494 筛选），本项目的主要来源 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 10.7K stars — 549+ 官方团队贡献的高质量 Skills |
| [anthropics/skill-creator](https://github.com/anthropics/skill-creator) | Anthropic 官方 Skill 创建工具 |
| [obra/superpowers](https://github.com/obra/superpowers) | Agent 增强能力集合，提供了优秀的 Skill 设计模式参考 |

感谢所有 Skill 原作者的创作和分享。本项目旨在通过质量验证为社区筛选最优秀的作品，所有 Skill 均保留原始署名。

---

## 参与贡献

欢迎通过以下方式参与本项目：

- **提交 Skill 进行评估**：Fork 本仓库，将你的 `SKILL.md` 放入对应分类目录，提交 Pull Request
- **报告问题**：发现已收录的 Skill 有问题（功能异常、安全隐患、兼容性问题），请提交 Issue
- **改进评估流程**：评估工具和测试用例也欢迎贡献，详见 `pipeline/` 目录

详细的贡献指南请参阅 [CONTRIBUTING_zh.md](CONTRIBUTING_zh.md)。

---

## 相关项目

| 项目 | 说明 |
|:---|:---|
| [AlexAnys/awesome-openclaw-usecases-zh](https://github.com/AlexAnys/awesome-openclaw-usecases-zh) | 1,626 stars — 40 个精选中文 OpenClaw 使用案例 |
| [AlexAnys/opencrew](https://github.com/AlexAnys/opencrew) | Multi-Agent OS for Decision Makers — 多 Agent 协作框架 |
| [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | 社区最大的 Agent Skills 集合 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 官方团队贡献的 Agent Skills 集合 |

---

## 许可证

[MIT](LICENSE)

本仓库中收录的 Skills 遵循各自的原始许可证。仓库本身的评估工具、模板和文档采用 MIT 许可证。
