---
layout: post
title: "LLM 推理服务上线清单：从单机验证到多节点运维"
display_title: "LLM 推理服务上线清单：从单机验证到多节点运维"
summary: "整合 vLLM、Ray、Docker、模型网关和离线部署笔记，给出模型服务从容量估算到灰度、监控与回滚的生产检查表。"
lang: zh-CN
date: 2026-09-24 09:50:00
categories:
  - AI & LLM
tags:
  - LLM
  - vLLM
  - Ray
  - Docker
  - GPU
  - Deployment
curated: true
content_origin: curated
curation_level: synthesis
version: curated-v1
source_posts:
  - "_posts/2026-06-12-Multi-Node-LLM-Serving-Architecture,-Frameworks-and-Best-Practices-(LLM-Generated).md"
  - "_posts/2026-06-12-Multi-Node-LLM-Serving-vLLM+Ray(Docker).md"
  - "_posts/2026-09-05-vllm-cluster-docker-deploy.md"
  - "_posts/2026-06-12-Python-Ray-Offline-Installation-Guide.md"
  - "_posts/2026-09-05-New-API-Multi-Process-Docker.md"
  - "_posts/2026-09-05-DeepSeek-V4-Flash-0731-4090D-Docker.md"
  - "_posts/2026-06-10-Model-MiniCPM5-1B.md"
  - "_posts/2026-06-10-Model-MiniCPM5-1B-Deploy-Ollama(Docker).md"
  - "_posts/2026-06-10-Model-MiniCPM5-1B-Deploy-llama.cpp(Docker).md"
---

推理服务的难点不只是把模型启动起来，而是让它在目标硬件、上下文长度、并发和网络条件下稳定运行。生产上线应把“架构选择”“资源估算”“部署验证”“流量治理”和“故障回滚”分开验收。

> 本文是对多篇部署记录的安全化重组。历史文章中的具体 GPU、CUDA、驱动、端口和模型版本都可能过时；不要直接照抄命令，先在隔离环境验证。

<!--more-->

## 先选并行策略

| 目标 | 优先考虑 | 主要代价 |
| --- | --- | --- |
| 单模型、低延迟 | 节点内张量并行 | 节点内通信和显存压力 |
| 模型装不下 | 张量并行 + 流水线并行 | 跨节点通信、流水线气泡 |
| 多用户吞吐 | 多个数据并行副本 | 内存、调度和请求路由 |
| MoE 模型 | 专家并行，必要时结合张量并行 | All-to-All 通信复杂 |

节点内优先利用高速互联，跨节点优先考虑通信量和可观测性。不要只按 GPU 数量决定并行度，先确认显存容量、模型精度、KV Cache 预算和上下文上限。架构背景可回看 [多节点 LLM Serving 架构](#source-posts-title)。

## 容量估算记录表

```text
模型与精度：
权重占用估算：
最大上下文：
预留 KV Cache：
单卡/单节点显存：
GPU 数量与拓扑：
并行方式：
目标 QPS / tokens per second：
TTFT / TPOT 目标：
可接受的尾延迟：
```

公式只能做早期估算，不能替代实测。尤其是 KV Cache、运行时工作区和框架版本都会改变显存边界。MiniCPM 的单机 Ollama/llama.cpp 记录可以作为轻量路径参考，但不应直接外推到 70B 或多节点服务：[MiniCPM5-1B 概览](#source-posts-title)、[Ollama 部署](#source-posts-title)、[llama.cpp 部署](#source-posts-title)。

## 部署前的分层检查

### 基础设施

- GPU 驱动、运行时和容器工具版本已记录；
- GPU 拓扑、NUMA、网卡和存储路径已验证；
- 节点间时间同步、权限和网络策略已确认；
- 模型文件有校验值，所有节点能以一致路径读取。

### 分布式组件

Ray、NCCL、共享存储和服务进程要分开验证。Ray 集群“节点在线”不代表 NCCL 通信正常；模型能加载也不代表长上下文和并发请求稳定。离线环境应使用 [Ray 离线安装记录](#source-posts-title) 中的清单思路，并为每个依赖保留校验信息。

### 服务层

至少验证：健康检查、模型列表、普通请求、流式请求、超时、取消、错误响应和网关转发。多进程方案可参考 [New-API 双进程部署](#source-posts-title)，但要确认健康检查、负载均衡和会话状态是否真的由该架构承担。

## 灰度与流量治理

1. 先用固定数据集做离线回归；
2. 再用小流量真实请求测 TTFT、TPOT、吞吐和错误率；
3. 逐步增加并发，观察显存、GPU 利用率和尾延迟；
4. 任何资源接近阈值时，自动降级或拒绝，而不是继续堆积请求；
5. 保留一个可回退的单机或旧版本路径。

多节点部署的具体操作可结合 [vLLM + Ray Docker](#source-posts-title) 与 [vLLM 集群实战](#source-posts-title)，但要删掉未经评估的“关闭防火墙”“关闭交换分区”等通用化步骤，改成组织自己的安全基线。

## 必看指标

- 请求成功率、排队时间和取消率；
- TTFT、TPOT、端到端延迟及 P95/P99；
- 输入/输出 token 吞吐；
- GPU 显存、GPU 利用率、功耗和温度；
- NCCL/Ray/容器重启次数；
- 网卡带宽、共享存储延迟和模型加载时间；
- 每次发布对应的模型、镜像、配置和提示词版本。

## 故障回滚清单

发生 OOM、NCCL 超时、模型加载失败或尾延迟飙升时：

1. 停止继续放大流量；
2. 保存日志、指标和最小请求；
3. 判断是单节点、单请求模式、模型版本还是基础设施问题；
4. 切换到已知可用的模型/实例；
5. 恢复后再做根因分析，不要通过盲目增大并发“验证”。

模型服务的可靠性来自可重复的实验和清晰的回滚路径，而不是某一条看起来很完整的启动命令。
