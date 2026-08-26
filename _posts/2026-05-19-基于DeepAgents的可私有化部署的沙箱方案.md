---
layout: post
title: 基于DeepAgents的可私有化部署的沙箱方案
date: 2026-05-19 18:47:00
categories:
- AI & LLM
tags:
- DeepAgents
---

参考[Deep Agents 概述 - LangChain 文档 - LangChain 教程](https://docs.langchain.org.cn/oss/python/deepagents/overview)

<!--more-->
沙箱 (Sandboxes) 是专门的[后端](https://docs.langchain.org.cn/oss/python/deepagents/backends)，它们在隔离的环境中运行智能体代码，具有自己的文件系统和用于 shell 命令的 `execute` 工具。

如果希望 Deep Agent 编写文件、安装依赖项并运行命令而不更改本地机器上的任何内容，使用沙箱后端。

可以通过在创建 Deep Agent 时将沙箱后端传递给 `backend` 来配置沙箱。

`agent = create_deep_agent(model="google_genai:gemini-3.1-pro-preview", backend=sandbox)` 在隔离环境中执行代码。

沙盒提供文件系统工具以及用于运行 Shell 命令的 `execute` 工具。

可选择 Modal、Daytona、Deno 或本地 VFS

* * *

## 沙盒

[沙盒 - LangChain 文档 - LangChain 教程](https://docs.langchain.org.cn/oss/python/deepagents/sandboxes)

* * *

## 沙盒集成

[沙盒集成 - LangChain 文档 - LangChain 教程](https://docs.langchain.org.cn/oss/python/integrations/sandboxes)

沙盒提供隔离的执行环境，用于安全地运行代理生成的代码

* [DaytonaSandbox 集成 - LangChain 文档 - LangChain 教程](https://docs.langchain.org.cn/oss/python/integrations/sandboxes/daytona)
  
* [ModalSandbox 集成 - LangChain 文档 - LangChain 教程](https://docs.langchain.org.cn/oss/python/integrations/sandboxes/modal)
  
* [RunloopSandbox 集成 - LangChain 文档 - LangChain 教程](https://docs.langchain.org.cn/oss/python/integrations/sandboxes/runloop)
  
* [AgentCoreSandbox 集成 - LangChain 文档 - LangChain 教程](https://docs.langchain.org.cn/oss/python/integrations/sandboxes/aws)
  
* [沙盒概述 - LangChain 文档 - LangChain 教程](https://docs.langchain.org.cn/langsmith/sandboxes)
  

* * *

## Github

[GitHub - langchain-ai/deepagents: Python & TypeScript agent harness built with LangChain and LangGraph. Equipped with a planning tool, a filesystem backend, and the ability to spawn subagents - well-equipped to handle complex agentic tasks. · GitHub](https://github.com/langchain-ai/deepagents)

[GitHub - langchain-ai/langchain-sandbox: Safely run untrusted Python code using Pyodide and Deno · GitHub](https://github.com/langchain-ai/langchain-sandbox)

* * *

三大沙箱项目全景扫描

[AI Agent 沙箱三国杀：OpenSandbox vs CubeSandbox vs E2B，从内核隔离到秒级调度的全链路技术拆解-程序员茄子](https://chenxutan.com/d/2122.html)

### 1.1 Agent 代码执行的安全威胁模型

AI Agent 的代码执行场景与传统 CI/CD 有本质区别：

| 威胁维度 | CI/CD 场景 | AI Agent 场景 |
| --- | --- | --- |
| 代码来源 | 人类编写，有审查 | 大模型生成，不可预测 |
| 执行意图 | 明确的构建/部署任务 | 开放式，可能包含「探索」行为 |
| 恶意风险 | 低（内部开发者） | 高（prompt injection、幻觉代码） |
| 隔离要求 | 进程级即可 | 内核级才够 |
| 执行频率 | 每天数次到数十次 | 每天数千到数万次 |
| 生命周期 | 分钟级 | 秒级到分钟级 |

AI Agent 的核心特征是**不可预测性**。即使是最先进的模型，也可能因为 prompt injection 生成恶意代码，或者因为幻觉产生破坏性操作。沙箱不是「锦上添花」，而是 Agent 系统的安全基座。

### 1.2 沙箱的技术定义

在 AI Agent 语境下，沙箱（Sandbox）是一个满足以下条件的隔离执行环境：

1. **隔离性**：沙箱内的进程无法影响宿主机和其他沙箱
2. **可控性**：宿主机可以精确控制沙箱的资源访问权限（网络、文件系统、系统调用）
3. **可观测性**：沙箱内的所有行为可被监控和审计
4. **极速启停**：满足 Agent 高频、短生命周期的执行模式
5. **可编程性**：提供标准 API，让 Agent 可以动态创建、使用和销毁沙箱

### 2.1 项目概况

| 维度  | OpenSandbox | CubeSandbox | E2B |
| --- | --- | --- | --- |
| 开源方 | 阿里巴巴 | 腾讯云 | E2B (美国创业公司) |
| 开源协议 | Apache 2.0 | Apache 2.0 | 闭源 (SDK 开源) |
| GitHub Stars | ~10K | 刚开源 | N/A |
| 隔离技术 | Docker / Kubernetes 容器 | KVM + RustVMM 硬件虚拟化 | Firecracker microVM |
| 启动速度 | 秒级 (Pool 预热) | 亚百毫秒 (<100ms) | ~150ms |
| 单沙箱内存 | 百MB级 | <5MB | ~30MB |
| 多语言 SDK | Python / Java / JS-TS / C# | Python (E2B 兼容) | Python / JS-TS |
| 运行时 | Docker / K8s 可插拔 | 单机 / 集群 | 云托管 |
| E2B 兼容 | 部分  | Drop-in 级别 | 原生  |


## 基于DeepSeek生成的解决方案
[deepagents后端沙盒设计实现](https://chat.deepseek.com/share/jmsc4yn6co2q3bdxew)