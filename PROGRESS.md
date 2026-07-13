# RedNote CLI 开发进度

> 最后更新: 2026-07-13
> 当前阶段: Phase 1 - 加密层

## 总览

| Phase | 内容 | 状态 |
|-------|------|------|
| Phase 1 | 加密层 (crypto/primitives + cookie + header) | ⏳ 进行中 |
| Phase 2 | HTTP 客户端 (client/) | ⬜ 待开始 |
| Phase 3 | API + 认证 (apis/ + auth/) | ⬜ 待开始 |
| Phase 4 | CLI 命令 + pyproject.toml | ⬜ 待开始 |
| Phase 5 | 报告生成 (report/) | ⬜ 待开始 |
| Phase 6 | SKILL.md + 端到端联调 | ⬜ 待开始 |
| Phase 7 | 测试完善 + 文档 | ⬜ 待开始 |

---

## Phase 1: 加密层

### 1.1 项目骨架
- [ ] 创建 pyproject.toml（项目配置）
- [ ] 创建 rednote_core/ 包结构
- [ ] 创建 rednote/ CLI 包结构
- [ ] 创建 config/settings.yaml

### 1.2 底层加密原语 (primitives/)
- [ ] symmetric.py — AES-CBC, AES-ECB
- [ ] asymmetric.py — RSA
- [ ] hash.py — MD5, SHA256, HMAC
- [ ] encoding.py — Base64, hex, 自定义编码

### 1.3 Cookie 生成 (cookie/)
- [ ] a1_webid.py — a1 + webId 生成
- [ ] gid.py — gid 生成
- [ ] websectiga.py — websectiga 生成
- [ ] acw_tc.py — 阿里云 WAF Token 解密

### 1.4 Header 签名 (header/)
- [ ] x_s_common.py — x-s-common 参数
- [ ] x_s.py — x-s + x-t 签名
- [ ] x_b3.py — x-b3-traceid
- [ ] x_xray.py — x-xray-traceid
- [ ] x_rap_param.py — 风控参数（CBC/ECB）

### 1.5 单元测试
- [ ] primitives 测试
- [ ] cookie 测试
- [ ] header 测试

---

## Phase 2: HTTP 客户端

- [ ] exceptions.py — 自定义异常
- [ ] middleware.py — 签名注入 + 重试中间件
- [ ] session.py — Session + Cookie 管理
- [ ] XHSClient 集成测试

---

## Phase 3: API + 认证

### 3.1 API 封装
- [ ] search.py — 搜索笔记
- [ ] note.py — 笔记详情
- [ ] user.py — 用户信息 + 用户笔记
- [ ] comments.py — 评论 + 子评论
- [ ] homefeed.py — 推荐页

### 3.2 认证
- [ ] auth/login.py — 扫码登录流程
- [ ] auth/persistence.py — Cookie 加密存储

---

## Phase 4: CLI 命令

- [ ] pyproject.toml — [project.scripts] 入口点
- [ ] rednote/__main__.py
- [ ] rednote/commands/login_cmd.py
- [ ] rednote/commands/scrape.py
- [ ] rednote/commands/config_cmd.py
- [ ] rednote/commands/report.py

---

## Phase 5: 报告生成

- [ ] report/templates/ — Jinja2 模板
- [ ] report/renderer.py — HTML 渲染
- [ ] report/charts.py — 图表 (matplotlib → base64)

---

## Phase 6: SKILL.md + 联调

- [ ] 编写 SKILL.md
- [ ] 端到端测试：login → search → note → report
- [ ] 各命令 --help 验证

---

## Phase 7: 收尾

- [ ] 补充单元测试
- [ ] README 更新
- [ ] 清理调试代码

---

## 恢复说明

如果会话中断，从这里继续：
1. 读取本文件，找到第一个未完成 Phase 的未勾选条目
2. 读取 `docs/superpowers/specs/2026-07-13-rednote-cli-design.md` 了解设计
3. 读取 `docs/xhs-api-reference.md` 了解 API 细节
4. 从断点继续开发
