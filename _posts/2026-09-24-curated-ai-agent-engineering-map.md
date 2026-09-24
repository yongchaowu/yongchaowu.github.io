---
layout: post
title: "AI Agent 工程化学习地图：从模型调用到可控协作"
display_title: "AI Agent 工程化学习地图：从模型调用到可控协作"
summary: "把 RAG、LangChain、LangGraph、DeepAgents、OpenCode 和模型网关等历史文章整理成一条从 API 调用到可观测 Agent 系统的学习路线。"
lang: zh-CN
date: 2026-09-24 09:40:00
categories:
  - AI & LLM
tags:
  - LLM
  - AI Agent
  - RAG
  - LangChain
  - LangGraph
  - DeepAgents
  - OpenCode
curated: true
content_origin: curated
curation_level: roadmap
version: curated-v1
source_posts:
  - "_posts/2026-09-05-LangChain-RAG-LangGraph-Learning-Roadmap.md"
  - "_posts/2026-05-19-基于DeepAgents的可私有化部署的沙箱方案.md"
  - "_posts/2026-05-22-DeepAgents接入DeepSeek-配置指南.md"
  - "_posts/2026-09-05-OpenSource-Agent-Swarm.md"
  - "_posts/2026-06-02-AI-coding-agent-OpenCode.md"
  - "_posts/2026-09-05-opencode-cli-guide.md"
  - "_posts/2026-06-02-Tool-CC-Switch.md"
  - "_posts/2026-06-01-AI-model-hub-New-API.md"
  - "_posts/2026-06-01-Model-Sentence-Transformers-models-Sentence-BERT-模型.md"
  - "_posts/2026-06-03-Yuxi-Know.md"
---

搭建 Agent 的第一步不是选择最多的框架，而是明确系统边界：模型负责生成和决策，检索负责提供可追溯知识，编排层负责状态与流程，工具执行环境负责限制真实副作用。把这些职责混在一个提示词里，Demo 可能很快，但很难测试、回滚和审计。

> 本文是站内 AI 文章的重组阅读地图。模型、SDK、Provider 和安全策略变化很快，示例配置必须以当前官方文档和你有权使用的服务为准。

<!--more-->

## 一张架构图

```text
用户 / IDE / API
        │
        ▼
  Agent Runtime  ── 状态、记忆、审批、重试
        │
        ├── Model Gateway ── 模型路由、限流、成本
        ├── Retrieval ───── 文档、向量库、引用
        ├── Tools ───────── 受限 API、文件、数据库
        ├── Sandbox ────── 网络/文件系统/进程隔离
        └── Observability  日志、轨迹、指标、评测
```

[从零到一的 LLM 应用路线](#source-note-1) 适合补齐 RAG、LangChain 和 LangGraph 的概念关系；本文进一步强调工程边界和上线顺序。

## 推荐学习顺序

### 1. 先会调用模型

先掌握 OpenAI 兼容接口、流式输出、上下文管理、超时和错误处理。不要一开始就引入多 Agent；先能可靠地完成一个单请求任务。模型网关和 Provider 切换可参考 [New API](#source-note-8) 与 [CC Switch](#source-note-7)。

### 2. 再做可评估的 RAG

RAG 的最小闭环是：文档如何进入系统、如何切分、如何检索、如何引用、答案如何被评估。没有评测集时，增加向量库和 Agent 只会让错误更难定位。Sentence-BERT 的模型说明见 [Sentence Transformers / Sentence-BERT](#source-note-9)。

### 3. 再学习状态图和人工介入

当流程出现循环、分支、暂停、恢复或人工审批时，再引入 LangGraph 一类状态编排工具。状态应显式定义，节点应有幂等策略，失败应可重试或转人工，而不是把所有判断塞进一个超长 prompt。

### 4. 最后引入长任务和多 Agent

[Agent Swarm](#source-note-4) 和 [DeepAgents 沙箱](#source-note-2) 适合研究容器化/本地编排、任务队列和多角色协作；这不等于模型 Provider 或模型文件已经离线。前提是单 Agent 流程已经可观测、可停止、可恢复，并且每个工具的权限边界已经明确。

## 一个可上线的最小契约

每次工具调用至少记录：

```text
任务 ID：
Agent / 模型版本：
输入摘要（脱敏）：
工具名称与参数：
权限决策：
开始 / 结束时间：
结果状态与错误：
人工审批：
产物位置与清理策略：
```

不要把 API Key、完整用户隐私或未经脱敏的文件内容直接写入日志。对外返回的答案应区分“模型生成”“检索证据”和“工具执行结果”，这样用户和审计人员才能知道结论来自哪里。

## Agent 的安全边界

- 工具默认只读，写入、删除、付款、发信和发布必须显式授权。
- 沙箱不是“装进 Docker 就安全”，仍需限制网络、挂载目录、权限和资源。
- 远程模型输出属于不可信输入，不能直接拼接成 shell、SQL 或高权限 URL 请求。
- 对循环、重试和子 Agent 设置预算、时间上限和最大步数。
- 重要动作提供预览、审批、幂等键和回滚路径。
- 所谓“离线/内网”部署要逐项核对：模型文件、Provider、SDK、容器镜像、遥测和更新服务是否仍会访问外部网络。

## 从历史文章中继续阅读

- [OpenCode 使用与配置](#source-note-5)：从 coding agent 的工作区与工具权限开始。
- [OpenCode CLI 深入解析](#source-note-6)：理解 Agent 运行时、配置和扩展点。
- [DeepAgents 接入 DeepSeek](#source-note-3)：理解模型兼容配置。
- [Yuxi Know](#source-note-10)：补充知识检索和工具组合的实践视角。

最终的判断标准不是 Agent “能完成多少任务”，而是每一步是否可解释、可停止、可恢复，并且不会超出授权范围。
