# RedNote Skill

小红书（RedNote / Xiaohongshu）数据采集、运营分析、舆情监控 Skill — 作为 Claude Code Agent 的工具集运行。

> **状态**：设计方案阶段 → 即将进入 v1 实现  
> **v1 重点**：数据采集（搜索、笔记详情、用户主页、评论）

---

## 项目概述

本项目创建一个 Claude Code Skill，通过 CLI 封装小红书 API 的逆向工程、请求签名、数据采集和报告生成，让 Agent 能够：

- **运营分析** — 采集自己/竞品账号数据，自动生成 HTML 分析报告
- **舆情监控** — 监控关键词/话题，异常内容通过 Webhook 推送告警
- **按需采集** — 手动触发搜索、查看账号、获取评论互动等

## 使用模式

| 模式 | 说明 | 频率 |
|------|------|------|
| 日常按需采集 | 手动触发，搜索关键词、查看账号 | 偶尔，几十次请求 |
| 周期性批量采集 | 定时扫描关键词/账号，生成分析报告 | 每天/每周，几百到几千条 |
| 近实时监控 | 持续轮询关键话题，分钟级发现异常 | 高频，特定主题 |

## 架构一览

```
用户 ←→ Agent (SKILL.md 引导)
              │
              ▼
         rednote CLI
   (scrape / monitor / report
    crypto / config)
              │
              ▼
        rednote_core
(crypto / client / apis
 report / alert)
              │
              ▼
        小红书 API
              │
              ▼
     data/reports/*.html
```

**核心思路**：SKILL.md 是 Agent 的操作手册，所有复杂逻辑封装在 CLI 和内核中，Agent 只负责匹配用户意图 → 执行命令 → 展示结果。

## 目录结构

```
rednote-skill/
├── SKILL.md                     # Skill 本体（核心交付物）
├── pyproject.toml               # 项目配置 + CLI 入口点
├── rednote/                     # CLI 命令包
│   └── commands/                #   scrape, monitor, report, crypto, config
├── rednote_core/                # 内核库
│   ├── crypto/                  #   加密参数生成与刷新
│   ├── client/                  #   HTTP 请求、签名注入、重试
│   ├── apis/                    #   小红书 API 接口封装
│   ├── report/                  #   报告模板 + HTML 渲染
│   └── alert/                   #   告警规则 + Webhook 推送
├── workflows/                   # 编排工作流
├── data/reports/                # HTML 报告产出
├── config/                      # 配置文件
├── docs/                        # 设计文档
└── tests/
```

## v1 接口覆盖

| 接口 | 命令 |
|------|------|
| 搜索笔记 | `rednote scrape search` |
| 笔记详情 | `rednote scrape note` |
| 用户主页 | `rednote scrape user` |
| 评论 | `rednote scrape comments` |
| 点赞 | `rednote scrape likes` |
| 关注/粉丝 | `rednote scrape follows` |

## 后续路线

| 阶段 | 能力 |
|------|------|
| v1 | 数据采集 |
| v2 | 内容创作 + 图文生成 |
| v3 | 发布运营（定时发布、多账号） |
| v4 | 互动评论管理 |
| v5 | 深度分析复盘 |

## 技术栈

- **语言**：Python
- **加密**：基于 PyCryptodome 的纯 Python 逆向
- **CLI 框架**：Click / Typer
- **报告**：自包含 HTML（内嵌 CSS + 图表）
- **参考项目**：GitHub 上 `xiaohongshutools`

## 文档

- [完整设计方案](rednote-skill-design.md)
- [设计方案 spec 备份](docs/superpowers/specs/2026-07-09-rednote-skill-design.md)

## 许可

Private — 仅供个人使用
