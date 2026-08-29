---
layout: post
title: Graphify
summary: >
  Graphify turns code, documentation, and papers into a queryable knowledge
  graph, giving AI coding assistants deeper context across your codebase.
lang: zh-CN
date: 2026-06-03 07:49:00
categories:
- Developer Tools
tags:
- Tool
- Graphify
---

Graphify 是一项开源技能，通过把代码、文档、论文和图示构建为可查询知识图谱，帮助 AI 编码助手理解多模态代码库。

<!--more-->
- `pip install graphifyy`

- [Home](https://graphify.net/zh/#features)

---

Graphify 是为 AI 编码助手（如 Claude Code、OpenAI Codex、OpenCode）打造的多模态知识图谱构建器。它结合 Tree-sitter 静态分析与 LLM 语义抽取，将整个仓库（源代码、文档、研究论文、图示）转换为可交互图谱，同时解释代码“做什么”和“为什么这样设计”。项目由 Safi Shamsi 维护，采用 MIT 许可证，并建立在 NetworkX 与 Tree-sitter 等成熟库之上。

## 核心能力

Graphify 将静态分析、语义抽取和图聚类统一为一个可被 AI 编码助手直接调用的技能。

- 多模态抽取

解析代码（.py、.js、.go、.java 等）、Markdown、PDF 与图片。Tree-sitter 提取 AST、调用图和注释；LLM 从文本抽取概念；视觉模型读取图示。

- 知识图谱构建

将所有节点与边合并到 NetworkX 图中，并使用 Leiden 算法进行语义社区检测，无需向量嵌入。

- 核心节点与异常连接

识别系统中度数最高的“god nodes”，并标记跨文件、跨领域的意外关联，帮助深挖问题。

- 交互式输出

导出交互式 `graph.html`、可查询 `graph.json` 和可读的 `GRAPH_REPORT.md` 审计报告。

- 助手集成

内置 `/graphify`、`/graphify query`、`/graphify path`、`/graphify explain`，可用于 Claude Code、Codex、OpenCode 等。

- 安全默认

严格输入校验：仅允许 http/https，限制体积与超时，路径约束，节点标签 HTML 转义，防 SSRF/注入/XSS。

## 安装与运行

Graphify 已发布到 PyPI。包名是 `graphifyy`，CLI 命令仍为 `graphify`。

```shell
# 需要 Python 3.10+
pip install graphifyy && graphify install

# 为任意项目目录构建知识图谱
/graphify ./raw

# 输出位于 graphify-out/
graphify-out/
├── graph.html        # 交互式可视化
├── GRAPH_REPORT.md   # 核心节点、异常连接、建议提问
├── graph.json        # 可持久化、可查询图谱
└── cache/            # 增量缓存
```

Graphify 不内置大模型。它复用你在 AI 编码助手（Claude、Codex 等）里已配置的模型 API Key，并且只发送语义内容，不发送原始源码。