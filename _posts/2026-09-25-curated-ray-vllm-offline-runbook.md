---
layout: post
title: "Ray + vLLM 离线多节点部署：从可复现安装到安全运维"
display_title: "Ray + vLLM 离线多节点部署：从可复现安装到安全运维"
summary: "把 Ray wheelhouse、GPU 容器、并行策略、私有网络、认证、健康检查和回滚拆开，避免把一条历史启动命令误当成生产保证。"
lang: zh-CN
date: 2026-09-24 18:20:00
categories:
  - AI & LLM
tags:
  - Ray
  - vLLM
  - Docker
  - GPU
  - Deployment
  - Testing
  - Observability
curated: true
content_origin: curated
curation_level: runbook
version: curated-v1
source_posts:
  - "_posts/2026-06-12-Python-Ray-Offline-Installation-Guide.md"
  - "_posts/2026-06-12-Multi-Node-LLM-Serving-vLLM+Ray(Docker).md"
  - "_posts/2026-06-12-Multi-Node-LLM-Serving-Architecture,-Frameworks-and-Best-Practices-(LLM-Generated).md"
  - "_posts/2026-09-24-curated-llm-serving-production-checklist.md"
---

多节点推理的难点不是把 Ray 和 vLLM 同时启动，而是让**版本、模型、GPU、网络、进程生命周期和回滚路径**形成同一个可验证的交付单元。本文把历史记录整理成一份版本敏感的 runbook；它不是对任何具体硬件或模型性能的保证。

> 原文中的安装包、端口、镜像、参数和性能数字都可能只对当时的版本成立。Ray、vLLM、CUDA、NCCL 和模型文件必须以目标环境的实际版本为准。[Ray source note](#source-note-1) [vLLM + Ray source note](#source-note-2)

<!--more-->

## 先写部署契约

在下载任何包之前，先记录以下内容：

```text
节点数量与角色：
每节点 GPU 数量、型号和互联：
GPU 驱动 / CUDA / NCCL：
Python 版本与实现：
Ray 版本与 extras：
vLLM 版本与镜像 digest：
模型仓库、revision 和文件校验值：
模型存储方式（本地副本或共享文件系统）：
Head / Worker 通信地址：
推理 API 的认证边界：
允许的出站网络：
失败时的回滚实例：
```

没有这张表，就无法判断失败是依赖问题、GPU 可见性问题、网络问题、模型问题还是服务参数问题。

## 1. 选择并行策略

不要只按 GPU 总数决定并行度。先确认模型能否放入单节点，再选择拓扑：

| 场景 | 起点 | 需要验证的代价 |
| --- | --- | --- |
| 模型能放入单节点 | 节点内 TP 或多个副本 | 显存、批处理和尾延迟 |
| 单节点放不下 | 节点内 TP，跨节点 PP | 跨节点通信和流水线气泡 |
| 模型能放入单节点且要吞吐 | 多个独立副本 / DP | 请求路由和负载均衡 |
| MoE 模型 | 根据模型实现评估 EP、TP、PP | All-to-All、专家放置和显存 |

对于 2 个节点、每节点 8 张 GPU 的示例，常见的起点是 `TP=8, PP=2`；也可以根据模型、网络和 vLLM 版本评估总 GPU 数的 TP。并行度不是越大越好，必须用目标请求长度、上下文和并发进行测量。[vLLM parallelism guidance](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/)

## 2. 建立离线交付物

### Ray wheelhouse

在联网机器上准备与目标环境匹配的 wheelhouse：

```bash
mkdir -p ray-wheelhouse
python3 -m pip download \
  --dest ray-wheelhouse \
  --only-binary=:all: \
  'ray[default]==<PINNED_RAY_VERSION>'
```

如果目标环境位于容器内，下载机的 Python 版本、Linux 架构、ABI 和 pip 约束必须与容器一致。交付时同时保存：

- 完整依赖清单；
- 每个文件的 SHA-256；
- Python 与 pip 版本；
- 下载日期和来源索引；
- 安装后的 `pip freeze` 与 `pip check` 输出。

目标机的安装应禁止隐式联网：

```bash
python3 -m pip install \
  --no-index \
  --find-links=./ray-wheelhouse \
  'ray[default]==<PINNED_RAY_VERSION>'
python3 -m pip check
ray --version
```

不要把“下载了 Ray 主包”当成“整个运行环境已经离线可复现”。vLLM、PyTorch、CUDA、tokenizer、NCCL 和模型文件都需要单独确认。

### 镜像与模型

生产交付至少固定：

- 镜像 digest，而不是只使用 `latest`；
- 模型 revision 或 commit；
- 模型文件清单和校验值；
- tokenizer/config 文件；
- 启动参数和配置文件的 hash。

模型目录建议只读挂载。镜像可以提前构建，但“镜像能构建”不代表“模型、运行时和驱动兼容”。

## 3. 先验证 GPU 可见性

Ray 的 `--num-gpus=8` 只是向调度器声明资源，不能替代 Docker 的 GPU 设备注入。每个容器都应先验证：

```bash
docker run --rm --gpus all <IMAGE> nvidia-smi
```

正式容器至少需要：

```bash
docker run --rm --gpus all <IMAGE> sh -lc \
  'nvidia-smi && python -c "import torch; print(torch.cuda.device_count())"'
```

如果使用 NVIDIA Container Toolkit，先按官方文档配置 Docker runtime，并用实际 GPU 型号验证。`--privileged` 不应作为“让 GPU 工作”的默认答案。[NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

## 4. 建立 Ray 集群

Head 和 Worker 必须在相同的 Ray/vLLM/Python 环境中运行。Ray 多节点集群通常由一个 head 和多个 worker 组成：

```bash
# Head
ray start --head --node-ip-address=<HEAD_IP> --port=6379

# Worker
ray start --address=<HEAD_IP>:6379 --node-ip-address=<WORKER_IP>
```

启动后不要只看进程是否存在：

```bash
ray status
ray list nodes
```

应确认：

- 预期数量的节点已加入；
- 每个节点暴露预期的 GPU 数量；
- 节点 IP 是 Ray 和 vLLM 都能访问的地址；
- 版本没有混用；
- Worker 不是只“在线”但无法进行 GPU/NCCL 通信。

Head 的地址、端口和网络策略应通过配置注入，不要把示例 IP 直接复制到生产环境。Ray head 可使用 6379，但完整部署还涉及其他内部通信和安全边界；防火墙规则应按实际版本和网络拓扑建立，而不是简单开放所有端口。

## 5. 安全运行 vLLM

一个更安全的通用拓扑是：

- 容器只使用 `--gpus all`，不默认使用 `--privileged`；
- Ray、vLLM 和管理端口放在受控私网；
- vLLM 绑定合适的 host，外部访问经过认证网关或反向代理；
- 启用 API key、TLS 或等价的服务层认证；
- 模型和配置只读挂载；
- 禁止不必要的出站网络；
- 为容器设置 CPU、内存、GPU 和日志限制。

vLLM 当前文档提供容器化 Ray 集群示例，并提醒集群通信不应暴露给不可信网络。具体参数随版本变化，应以[官方在线服务文档](https://docs.vllm.ai/en/latest/serving/online_serving/)为准。

通用启动模板：

```bash
vllm serve <MODEL_PATH> \
  --served-model-name <MODEL_NAME> \
  --tensor-parallel-size <TP> \
  --pipeline-parallel-size <PP> \
  --distributed-executor-backend ray \
  --host <PRIVATE_BIND_ADDRESS> \
  --port <API_PORT>
```

不要把 `HF_HUB_OFFLINE=1` 当作完整网络隔离证明。模型 revision、远程代码、遥测、包管理和服务更新策略都要单独审查。

## 6. 健康检查和功能验收

“进程启动”不等于“服务可用”。至少验证：

1. Ray 节点和 GPU 资源；
2. 模型加载完成；
3. `/health` 或 `/v1/models`；
4. 普通非流式请求；
5. 流式请求；
6. 取消和超时；
7. 认证失败与认证成功；
8. 长上下文和边界长度；
9. 并发增加时的排队、显存和尾延迟；
10. 单节点故障时的拒绝或回滚行为。

功能测试和性能测试要分开。吞吐数字必须附带硬件、镜像 digest、模型 revision、请求输入/输出长度、并发、采样参数、预热方式和测试日期。

## 7. 监控和回滚

至少记录：

- Ray 节点加入/退出和重启次数；
- GPU 利用率、显存、温度和功耗；
- NCCL 初始化、重试和错误；
- vLLM 队列、TTFT、TPOT、P95/P99；
- API 成功率、取消率和认证失败；
- 模型加载时间与存储延迟；
- 当前镜像、模型、参数和配置版本。

发生 OOM、NCCL 超时或模型加载失败时：

1. 停止继续放大流量；
2. 保存日志、指标和最小请求；
3. 判断问题属于节点、网络、版本、模型还是参数；
4. 切换到已知可用的实例或旧版本；
5. 完成根因分析后再恢复流量。

## 发布前检查清单

- [ ] Ray wheelhouse 有完整依赖和 hash；
- [ ] 容器内实际安装了匹配的 Ray/vLLM；
- [ ] 每个容器都能看到预期 GPU；
- [ ] Ray head/worker 版本和网络地址一致；
- [ ] 模型 revision、文件校验值和存储方式已记录；
- [ ] 镜像使用 digest 而不是浮动 tag；
- [ ] 没有把 `--privileged`、host network 或开放 dashboard 当成默认方案；
- [ ] API 有认证和网络边界；
- [ ] 已测试取消、超时、长上下文和错误响应；
- [ ] 性能数据有可复现实验条件；
- [ ] 有可执行的停止、回滚和恢复步骤。

## 来源与官方入口

- [Ray on-premise cluster setup](https://docs.ray.io/en/latest/cluster/vms/user-guides/launching-clusters/on-premises.html)
- [vLLM parallelism and scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/)
- [vLLM distributed troubleshooting](https://docs.vllm.ai/en/latest/serving/distributed_troubleshooting/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
