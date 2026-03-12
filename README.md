<p align="center">
  <!-- TODO: Replace with actual logo -->
  <img src="https://via.placeholder.com/200x200?text=Cultivated+Skills" alt="openclaw-cultivated-skills" width="200"/>
</p>

<h1 align="center">openclaw-cultivated-skills</h1>

<p align="center">
  <strong>从 5,000+ 社区 Skills 中精选验证的高质量技能集</strong><br/>
  <em>Quality-verified skills curated from 5,000+ community submissions</em>
</p>

<p align="center">
  <a href="https://github.com/AlexAnys/openclaw-cultivated-skills/stargazers"><img src="https://img.shields.io/github/stars/AlexAnys/openclaw-cultivated-skills?style=flat-square" alt="Stars"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/AlexAnys/openclaw-cultivated-skills?style=flat-square" alt="License"/></a>
  <img src="https://img.shields.io/badge/skills-evaluating-blue?style=flat-square" alt="Skill Count"/>
  <img src="https://img.shields.io/badge/compatible_agents-30%2B-green?style=flat-square" alt="30+ Compatible Agents"/>
  <img src="https://img.shields.io/badge/format-SKILL.md-purple?style=flat-square" alt="SKILL.md Format"/>
</p>

<p align="center">
  <a href="#why-this-exists--为什么做这个项目">为什么</a> ·
  <a href="#quality-standard--质量标准">质量标准</a> ·
  <a href="#skill-catalog--技能目录">技能目录</a> ·
  <a href="#how-to-install--安装方式">安装</a> ·
  <a href="#quality-passport--质量护照">质量护照</a> ·
  <a href="#contributing--参与贡献">贡献</a>
</p>

---

## Why This Exists / 为什么做这个项目

**问题 / The Problem**

Agent Skills 生态正在爆发式增长。仅 [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) 一个仓库就收录了 13,729 个 Skills，筛选后仍有 5,494 个。[awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) 又新增了 549+ 个官方团队贡献的技能。

数量多并不等于质量高。社区提交的 Skills 存在以下常见问题：

- 触发词设计不当，导致误触发或无法触发
- 功能描述含糊，Agent 无法正确理解意图
- 缺乏安全边界，可能执行危险操作
- 未经真实环境验证，实际使用时出错

**解决方案 / The Solution**

本项目对每一个收录的 Skill 执行标准化的四层评估流程（自动化测试 + 人工审核），只有通过全部验证的 Skill 才能获得 **Quality Passport（质量护照）** 并进入本仓库。

> The Agent Skills ecosystem is growing fast — over 5,000 skills exist across community repositories. But quantity does not equal quality. This project applies a rigorous 4-layer evaluation pipeline (automated testing + human review) to every skill. Only those that pass receive a **Quality Passport** and are included here.

---

## Quality Standard / 质量标准

每个 Skill 必须通过以下四层评估漏斗，才能被收录：

Every skill must pass through this 4-layer evaluation funnel before inclusion:

```
  13,729 community skills (raw)
         |
    Layer 1: Structural Validation ──── batch_validate.py + security_scan.py
         |   格式校验、必填字段检查、安全扫描
         |
    Layer 2: Trigger Accuracy ───────── batch_trigger_eval.py
         |   触发词精准度测试（正向触发 + 反向不触发）
         |
    Layer 3: Functional & Security ──── batch_functional_eval.py + grader agent
         |   功能正确性验证（with-skill vs without-skill 对比 + 断言评分）
         |
    Layer 4: Human Review ───────────── eval-viewer (interactive review UI)
         |   人工深度审核 + 真实场景测试 + 兼容性验证
         ▼
    ✓ Quality Passport issued ── issue_passport.py → 收录至本仓库
```

| 层级 / Layer | 名称 / Name | 说明 / Description |
|:---:|:---|:---|
| L1 | **结构校验** / Structural Validation | 验证 SKILL.md 格式规范、必填字段完整性、元数据有效性。对应工具：`quick_validate` |
| L2 | **触发精准度** / Trigger Accuracy | 使用正向和反向测试用例验证触发词是否能精准匹配目标场景且不误触发。对应工具：`run_eval` |
| L3 | **功能与安全** / Functional & Security | 在沙箱环境中执行功能测试，同时扫描潜在安全风险（如未授权的文件系统操作、网络请求、敏感数据泄露） |
| L4 | **人工审核** / Human Review | 由维护者在真实项目中测试，评估输出质量、边界情况处理、多 Agent 兼容性 |

---

## Skill Catalog / 技能目录

Skills 按领域分类组织，目录结构如下：

```
skills/
├── document-processing/    # 文档处理
├── development-workflow/   # 开发工作流
├── frontend/               # 前端开发
├── infrastructure/         # 基础设施与 DevOps
├── security/               # 安全
├── productivity/           # 效率工具
├── ml-ai/                  # 机器学习与 AI
├── research/               # 研究与分析
├── china-ecosystem/        # 中国生态（飞书、钉钉、企微、小红书等）
└── creative-media/         # 创意与媒体
```

| 分类 / Category | 数量 / Count | 亮点 / Highlights | 状态 / Status |
|:---|:---:|:---|:---:|
| **Document Processing** / 文档处理 | — | PDF 解析、Markdown 转换、文档生成、合同审查 | 🔄 Evaluating |
| **Development Workflow** / 开发工作流 | — | Git 工作流、Code Review、CI/CD、重构辅助 | 🔄 Evaluating |
| **Frontend** / 前端开发 | — | React/Vue 组件生成、CSS 优化、响应式设计 | 🔄 Evaluating |
| **Infrastructure** / 基础设施 | — | Docker、Kubernetes、Terraform、云部署 | 🔄 Evaluating |
| **Security** / 安全 | — | 漏洞扫描、依赖审计、安全加固、合规检查 | 🔄 Evaluating |
| **Productivity** / 效率工具 | — | 任务管理、邮件起草、会议纪要、数据整理 | 🔄 Evaluating |
| **ML/AI** / 机器学习 | — | 模型训练辅助、数据预处理、Prompt 工程 | 🔄 Evaluating |
| **Research** / 研究分析 | — | 论文检索、数据可视化、竞品分析、市场调研 | 🔄 Evaluating |
| **China Ecosystem** / 中国生态 | — | 飞书/钉钉/企微集成、小红书自动化、中文写作优化 | 🔄 Evaluating |
| **Creative & Media** / 创意媒体 | — | 图像处理、视频脚本、文案创作、设计稿解析 | 🔄 Evaluating |

> 各分类的具体 Skill 数量将在首批评估完成后更新。
> Skill counts will be updated after the first evaluation batch completes.

---

## How to Install / 安装方式

### OpenClaw

```bash
# 安装单个 Skill
clawhub install AlexAnys/openclaw-cultivated-skills/skills/development-workflow/<skill-name>

# 安装整个分类
clawhub install AlexAnys/openclaw-cultivated-skills/skills/development-workflow
```

### Claude Code

```bash
# 将 SKILL.md 复制到 Claude Code 的 skills 目录
cp skills/development-workflow/<skill-name>/SKILL.md ~/.claude/skills/<skill-name>.md

# 或创建符号链接以保持同步
ln -s $(pwd)/skills/development-workflow/<skill-name>/SKILL.md ~/.claude/skills/<skill-name>.md
```

### Generic Agent Skills Path

大多数支持 Agent Skills 标准的工具都会从项目根目录或用户配置目录中读取 `SKILL.md` 文件。通用安装方式：

Most agents that support the Agent Skills standard read `SKILL.md` files from the project root or user config directory. General installation:

```bash
# 方式一：复制到项目根目录
cp skills/<category>/<skill-name>/SKILL.md /your/project/.skills/<skill-name>.md

# 方式二：复制到用户级配置目录（具体路径因 Agent 而异）
cp skills/<category>/<skill-name>/SKILL.md ~/.config/<agent>/skills/<skill-name>.md
```

**兼容 Agent 列表 / Compatible Agents** (30+):
Claude Code, Cursor, Codex, Gemini CLI, OpenCode, Kiro, Windsurf, Cline, Aider, Continue, Zed AI, Amp, Roo Code, Trae, PearAI, Melty, Void, Plandex, Goose, Aide, Refact, Sourcegraph Cody, Tabnine Chat, Mentat, avante.nvim, Supermaven, Blackbox AI, Amazon Q CLI 等。

---

## Quality Passport / 质量护照

每个通过评估的 Skill 都会获得一份 Quality Passport，存放在 `passports/` 目录下。护照包含以下信息：

Every skill that passes evaluation receives a Quality Passport stored in `passports/`. A passport contains:

| 字段 / Field | 说明 / Description |
|:---|:---|
| **Trigger Accuracy Rate** / 触发精准率 | 正向触发成功率 + 反向不触发率（目标: ≥ 90%） |
| **Functional Score** / 功能得分 | 输出质量、边界处理、错误恢复（0-100 分） |
| **Security Check** / 安全检查 | PASS / WARN / FAIL — 危险操作检测结果 |
| **Human Review Notes** / 人工审核备注 | 审核者的定性评价、使用建议、已知限制 |
| **Compatible Agents Tested** / 已测试兼容 Agent | 实际验证通过的 Agent 列表及版本 |
| **Evaluation Date** / 评估日期 | 最近一次完整评估的时间 |
| **Source** / 来源 | 原始提交来源（社区仓库、官方团队等） |

护照示例 / Example passport:

```yaml
skill: example-skill
version: 1.0.0
evaluation_date: 2026-03-11
source: VoltAgent/awesome-openclaw-skills

trigger_accuracy:
  positive_rate: 95%    # 正向触发成功率
  negative_rate: 100%   # 反向不触发率

functional_score: 87

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

---

## Evaluation Methodology / 评估方法论

本项目的评估流程基于可复现的自动化测试和结构化的人工审核，具体包括：

- **测试用例设计**：每个 Skill 至少包含 5 个正向触发用例和 3 个反向用例
- **沙箱执行**：功能测试在隔离环境中运行，防止副作用
- **安全扫描**：静态分析 + 动态行为监控
- **多 Agent 兼容性**：在至少 3 个不同 Agent 中验证行为一致性
- **持续回归**：已收录的 Skill 定期重新评估，确保持续合规

详细方法论请参阅 [METHODOLOGY.md](METHODOLOGY.md)。

> For the full evaluation methodology, see [METHODOLOGY.md](METHODOLOGY.md).

---

## Automated Evaluation System / 自动化评估系统

本项目集成了 Anthropic 官方 [skill-creator](https://github.com/anthropics/skills) 的完整评估框架，提供从自动化测试到人工审核的端到端 Skill 质量保障。

> This project integrates Anthropic's official [skill-creator](https://github.com/anthropics/skills) evaluation framework, providing end-to-end skill quality assurance from automated testing to human review.

### Pipeline Architecture / 流水线架构

```
pipeline/
├── batch_validate.py            # Layer 1: 批量结构校验
├── batch_trigger_eval.py        # Layer 2: 批量触发精准度测试
├── batch_functional_eval.py     # Layer 3: 批量功能测试（with/without-skill 对比）
├── security_scan.py             # 安全扫描（28+ 危险模式检测）
├── issue_passport.py            # 质量护照自动生成
├── generate_catalog.py          # 目录生成
├── agents/                      # 评估 Agent 定义（from Anthropic skill-creator）
│   ├── grader.md                # 评分 Agent — 验证断言、提取证据、批评评估质量
│   ├── comparator.md            # 盲评 Agent — 无偏见 A/B 对比，自定义评分维度
│   └── analyzer.md              # 分析 Agent — 揭盲分析 + benchmark 模式识别
├── eval-viewer/                 # 人工审核界面
│   ├── viewer.html              # 交互式审查页面（支持键盘导航、评论、评分查看）
│   └── generate_review.py       # HTTP 服务器 / 静态 HTML 生成
├── scripts/                     # Anthropic skill-creator 核心脚本
│   ├── run_eval.py              # 触发率测试引擎
│   ├── aggregate_benchmark.py   # 统计汇总（均值 ± 标准差）
│   ├── run_loop.py              # 迭代优化循环（train/test 分割防过拟合）
│   ├── improve_description.py   # Claude 驱动的描述优化
│   ├── generate_report.py       # 交互式 HTML 优化报告
│   └── package_skill.py         # Skill 打包为 .skill 分发文件
└── references/
    └── schemas.md               # 8 种 JSON Schema 定义
```

### Key Capabilities / 核心能力

| 能力 / Capability | 说明 / Description |
|:---|:---|
| **Grader Agent** | 8 步评分流程：审查执行记录、验证断言、提取隐含声明、批评评估本身的质量 |
| **Blind Comparator** | 盲评两个输出，自定义 Content + Structure 评分维度（1-5 分），防止评估偏见 |
| **Post-hoc Analyzer** | 揭盲后分析赢家优势、输家改进方向；Benchmark 模式分析跨运行趋势 |
| **Eval Viewer** | Web 界面支持逐案审查、键盘导航、评论自动保存、前后版本对比 |
| **Description Optimizer** | 自动优化 Skill 描述的触发精准度，train/test 分割防止过拟合 |
| **Benchmark System** | 多次运行的统计分析（mean ± stddev），with-skill vs without-skill 增量对比 |

### Quick Start / 快速开始

```bash
# Layer 1: 批量结构校验
python -m pipeline.batch_validate --input skills/ --output reports/structural.json

# Layer 2: 批量触发精准度测试
python -m pipeline.batch_trigger_eval --skills-dir skills/ --output reports/trigger.json

# Layer 3: 批量功能测试
python -m pipeline.batch_functional_eval --skills-dir skills/ --output reports/functional.json

# Layer 4: 启动人工审核界面
python pipeline/eval-viewer/generate_review.py <workspace-dir> --skill-name <name>

# 生成质量护照
python -m pipeline.issue_passport \
  --skill-name <name> \
  --structural-report reports/structural.json \
  --trigger-report reports/trigger.json \
  --functional-report reports/functional.json \
  --reviewer <your-name> \
  --output passports/<name>.json
```

---

## Sources & Acknowledgments / 来源与致谢

本项目的 Skill 来源及灵感来自以下优秀项目：

| 项目 / Project | 说明 / Description |
|:---|:---|
| [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | 35K stars — 社区最大的 Skills 集合（13,729 原始 / 5,494 筛选），本项目的主要来源 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 10.7K stars — 549+ 官方团队贡献的高质量 Skills |
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic 官方 Skill 创建与评估框架 — 本项目评估系统的核心基础 |
| [obra/superpowers](https://github.com/obra/superpowers) | Agent 增强能力集合，提供了优秀的 Skill 设计模式参考 |
| Agent Skills Standard | 由 Anthropic 发起、30+ Agent 支持的技能格式标准 |

感谢所有 Skill 原作者的创作和分享。本项目旨在通过质量验证为社区筛选最优秀的作品，所有 Skill 均保留原始署名。

> Thanks to all original skill authors. This project aims to surface the best work through quality verification. All skills retain their original attribution.

---

## Contributing / 参与贡献

欢迎通过以下方式参与：

### 提交 Skill 进行评估 / Submit a Skill for Evaluation

1. Fork 本仓库
2. 将你的 `SKILL.md` 放入对应分类目录：`skills/<category>/<skill-name>/SKILL.md`
3. 提交 Pull Request，并在描述中说明：
   - Skill 的用途和目标场景
   - 已测试的 Agent 列表
   - 任何已知限制
4. 维护者将执行完整的四层评估流程
5. 通过评估后，Skill 将获得 Quality Passport 并被正式收录

### 报告问题 / Report Issues

如果你发现已收录的 Skill 存在问题（功能异常、安全隐患、兼容性问题），请提交 Issue 并附上：

- 使用的 Agent 名称和版本
- 问题复现步骤
- 期望行为 vs 实际行为

### 改进评估流程 / Improve the Evaluation Pipeline

评估工具和测试用例也欢迎贡献，详见 `pipeline/` 目录。

---

## Related Projects / 相关项目

| 项目 / Project | 说明 / Description |
|:---|:---|
| [AlexAnys/awesome-openclaw-usecases-zh](https://github.com/AlexAnys/awesome-openclaw-usecases-zh) | 1,626 stars — 40 个精选中文 OpenClaw 使用案例 |
| [AlexAnys/opencrew](https://github.com/AlexAnys/opencrew) | Multi-Agent OS for Decision Makers — 多 Agent 协作框架 |
| [VoltAgent/awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) | 社区最大的 Agent Skills 集合 |
| [VoltAgent/awesome-agent-skills](https://github.com/VoltAgent/awesome-agent-skills) | 官方团队贡献的 Agent Skills 集合 |

---

## License / 许可证

[MIT](LICENSE)

本仓库中收录的 Skills 遵循各自的原始许可证。仓库本身的评估工具、模板和文档采用 MIT 许可证。

> Skills included in this repository retain their original licenses. The evaluation tooling, templates, and documentation in this repository are licensed under MIT.
