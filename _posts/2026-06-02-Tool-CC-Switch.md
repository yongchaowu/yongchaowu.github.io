---
layout: post
title: CC Switch
summary: >
  CC Switch unifies management of AI coding assistants — routing, usage tracking,
  session handling, and skill configuration across seven supported apps.
lang: zh-CN
date: 2026-06-02 07:16:00
categories:
- Developer Tools
tags:
- Tool
- CCSwitch
---

一个应用管理供应商、路由、用量、会话和技能

<!--more-->
- [CC Switch](https://ccswitch.io/zh/)
- [CC Switch Releases](https://github.com/farion1231/cc-switch/releases)

---

1. 统一管理七大应用

一个界面管理 Claude Code、Claude Desktop、Codex、Gemini CLI、OpenCode、OpenClaw 和 Hermes Agent 的供应商配置。

2. 自动故障转移

本地路由内置熔断器、健康监控和故障转移队列，主 Provider 异常时自动切换到备用 Provider。

3. 用量与额度可见

实时追踪请求、Token、缓存命中、成本和订阅额度，支持日期范围筛选与自定义模型价格。

4. 安全本地存储

所有配置和 API Key 安全存储在本地 SQLite 数据库，支持完整的 Schema 迁移。

5. MCP / Skills / 会话

统一管理 MCP、Skills、Prompts、Hermes Memory 和跨应用会话恢复，无需手动编辑配置文件。

6. 开源免费

基于 MIT 协议开源，完全免费使用。社区驱动开发，欢迎贡献代码和反馈。

---

零配置，开箱即用

无需修改代码，开启本地路由即可获得格式转换、热切换、故障转移、请求日志和用量统计。


- SQLite 数据持久化

所有配置存储在本地 SQLite 数据库，安全可靠，支持完整的 Schema 迁移。

 - Rust 后端 + React 前端

基于 Tauri 2.x 构建，结合 Rust 的性能和 React 的灵活性。

- 智能用量追踪

实时监控 Token、缓存、订阅额度和费用，按应用与 Provider 分类统计分析。