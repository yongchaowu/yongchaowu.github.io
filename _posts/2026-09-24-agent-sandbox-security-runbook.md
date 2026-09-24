---
layout: post
title: "Agent 沙箱与工具权限：从 Docker 到可审计执行边界"
display_title: "Agent 沙箱与工具权限：从 Docker 到可审计执行边界"
summary: "以威胁模型为中心整理 DeepAgents、OpenCode、Agent Swarm 和文件服务实践中的最小权限、网络、密钥、审批、预算与审计设计。"
lang: zh-CN
date: 2026-09-24 11:30:00
categories:
  - AI & LLM
tags:
  - AI Agent
  - Security
  - Sandbox
  - Least Privilege
  - Observability
  - OpenCode
curated: true
content_origin: curated
curation_level: synthesis
version: curated-v1
source_posts:
  - "_posts/2026-05-19-基于DeepAgents的可私有化部署的沙箱方案.md"
  - "_posts/2026-05-22-DeepAgents接入DeepSeek-配置指南.md"
  - "_posts/2026-09-05-OpenSource-Agent-Swarm.md"
  - "_posts/2026-06-02-AI-coding-agent-OpenCode.md"
  - "_posts/2026-09-05-opencode-cli-guide.md"
  - "_posts/2026-06-02-Tool-CC-Switch.md"
  - "_posts/2026-09-18-LAN-File-Share-Single-File-Python.md"
---

把 Agent 放进 Docker 或 Kubernetes 只能提供一个执行边界，不能自动解决提示注入、恶意工具参数、密钥泄露、越权文件访问或失控循环。真正的沙箱设计需要从“允许什么、拒绝什么、谁来批准、如何发现和如何清理”开始。

> 本文只讨论防御性架构和授权测试。示例环境应使用合成数据、测试凭据和隔离网络，不要把模型输出直接当作可信代码或高权限命令。

<!--more-->

## 1. 先写威胁模型

至少列出以下主体和资产：

```text
模型 / Provider：可能返回不可信文本
用户：可信程度和授权范围可能不同
工具：可能读写文件、访问网络或调用外部服务
沙箱：可能配置错误、被逃逸或被滥用
日志：可能包含密钥、个人信息和内部路径
```

对每一种资产定义机密性、完整性和可用性要求，再决定控制措施。不要先问“要不要 Docker”，而要先问：

- Agent 能否读取工作区之外的文件？
- 能否访问内网、云 metadata 或任意公网地址？
- 能否执行 shell、编译、安装依赖或启动长期进程？
- 工具参数由谁生成、谁验证、谁批准？
- 任务失败时能否停止、回滚和清理？

## 2. 最小权限的工具清单

把工具分成只读、可写和高风险三档：

| 等级 | 示例 | 默认策略 |
| --- | --- | --- |
| 只读 | 读取指定文档、查询测试 API | 允许，但限制路径和返回大小 |
| 可写 | 生成补丁、写入临时目录、提交草稿 | 需要任务身份和可回滚目录 |
| 高风险 | 删除、发布、发信、付款、改权限 | 默认拒绝，必须人工审批 |

不要用“工具名称”判断权限；权限应绑定到参数、资源范围和任务状态。模型返回的 URL、路径和 shell 片段都属于不可信输入，必须经过 allowlist、规范化、编码和权限检查。

## 3. 网络和文件隔离

建议把执行环境拆成明确的层次：

```text
Agent runtime
  ├── 只读知识目录
  ├── 每任务临时工作目录
  ├── 受限工具代理
  └── 出站网络代理 / allowlist
```

- 不把宿主机 Docker socket、SSH agent、云凭据目录挂进沙箱；
- 禁止默认访问内网、管理端口和云 metadata；
- 出站请求使用域名/端口 allowlist，并记录请求目的；
- 临时目录按任务隔离，完成后清理；
- 写操作输出 diff、校验值和回滚信息；
- 对上传/下载设置大小、类型、超时和配额限制。

[DeepAgents 沙箱方案](#source-posts-title) 和 [Agent Swarm 部署记录](#source-posts-title) 适合研究容器化与任务编排，但“能启动容器”不能写成“绝对安全”。还应考虑内核漏洞、挂载权限、凭证转发和供应链镜像。

## 4. 密钥和隐私处理

密钥不应放进 prompt、任务描述或普通日志。运行时通过短期凭据或受控代理提供，按任务和工具最小授权，并设置过期时间。日志至少做以下处理：

```text
API Key / token：脱敏或完全排除
用户文件：只记录路径摘要和大小
命令：记录规范化命令，不记录任意秘密参数
模型输入输出：按保留策略和访问控制存储
```

[DeepSeek 配置记录](#source-posts-title) 和 [CC Switch](#source-posts-title) 可以帮助理解 Provider 切换，但远程 Provider 依赖意味着“离线部署”必须逐项验证；只要仍访问远程 API，就不能称为 air-gapped。

## 5. 审批、预算和停止

每个任务都应有可观察的状态机：

```text
received → planning → running tool → awaiting approval → completed
                                      ↘ failed / cancelled / rolled back
```

限制最大步数、最大 token、最大运行时间、最大并发和单任务成本。工具执行前显示目标、参数摘要和影响范围；高风险动作使用审批令牌和幂等键。取消信号必须能到达队列、工作进程和外部请求，而不只是让 UI 停止显示。

## 6. 审计与事件响应

每次工具调用记录：任务 ID、Agent/模型版本、工具、参数摘要、权限决策、开始/结束时间、结果状态、产物位置和清理结果。对以下事件建立告警：

- 访问未授权路径或域名；
- 短时间大量网络请求；
- 反复重试或预算耗尽；
- 试图读取密钥、挂载点或宿主机信息；
- 工具参数与审批内容不一致。

[OpenCode 使用记录](#source-posts-title) 和 [CLI 深入解析](#source-posts-title) 适合研究 Agent 运行时，但日志格式、权限检查和 hook 行为应按当前版本重新确认。

## 上线前检查

- [ ] 工具是否有明确的能力、资源和副作用声明？
- [ ] 是否默认只读，写操作是否需要审批？
- [ ] 文件、进程和网络是否有 allowlist 与配额？
- [ ] 密钥是否不进入 prompt、源码和普通日志？
- [ ] 任务是否可取消、可重试、可回滚和可清理？
- [ ] 是否记录了完整的工具审计轨迹？
- [ ] 是否在无凭据、无宿主机挂载的隔离环境做过演练？

安全的 Agent 不是“更会写代码的容器”，而是把模型的不确定性限制在可观察、可撤销的权限边界内。
