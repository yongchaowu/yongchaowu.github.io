---
layout: post
title: "GPU / CUDA / Docker 部署兼容性清单：从镜像到模型服务"
display_title: "GPU / CUDA / Docker 部署兼容性清单：从镜像到模型服务"
summary: "用版本矩阵、镜像 digest、模型校验、GPU 可见性、安全边界和功能验收，把消费级 GPU 部署记录整理成可复用的兼容性案例。"
lang: zh-CN
date: 2026-09-24 18:30:00
categories:
  - AI & LLM
tags:
  - GPU
  - Docker
  - vLLM
  - Model
  - Deployment
  - Testing
curated: true
content_origin: curated
curation_level: deep-dive
version: curated-v1
source_posts:
  - "_posts/2026-09-05-DeepSeek-V4-Flash-0731-4090D-Docker.md"
  - "_posts/2026-09-05-vllm-cluster-docker-deploy.md"
  - "_posts/2026-06-10-OS-Ubuntu-NVIDIA-Driver-Install.md"
---

GPU 部署失败时，最容易把三类问题混在一起：**宿主机驱动不兼容、容器没有看到设备、模型/框架本身不兼容**。这份清单不替代 NVIDIA、CUDA、模型或 vLLM 的兼容性文档，而是提供一个从证据到验收的顺序。

> 文中的历史 GPU 型号、CUDA/驱动、wheel、模型和性能数字都必须在目标环境重新确认。`RTX 4090`、`RTX 4090D`、48GB 变体和不同 SM 架构不能只按品牌名称视为同一配置。[DeepSeek source note](#source-note-1) [cluster source note](#source-note-2)

<!--more-->

## 1. 建立兼容性矩阵

至少分别记录宿主机和容器：

| 层 | 需要记录 |
| --- | --- |
| GPU | 型号、显存、计算能力、数量、互联方式 |
| 驱动 | 驱动版本和分支 |
| 容器 | Docker 版本、NVIDIA Container Toolkit 版本 |
| 镜像 | 基础镜像、框架版本、镜像 digest |
| CUDA | 容器内 toolkit/runtime 版本和所需架构 |
| 模型 | 名称、revision、权重大小、量化方式、chat template |
| 框架 | vLLM/FlashInfer/PyTorch 版本和自定义 patch |

不要只记录 `nvidia-smi` 显示的 CUDA 版本。它是驱动可支持的最高 CUDA 版本，不等于容器内 toolkit、PyTorch 或自定义 kernel 的完整组合。

## 2. 构建可复现镜像

镜像应固定 digest：

```bash
docker build --pull \
  --tag <REGISTRY>/<IMAGE>:<VERSION> \
  --file Dockerfile .
docker image inspect <IMAGE> | python3 -m json.tool | grep -A2 RepoDigests
```

如果使用 fork 或预编译 wheel，保存：

- 下载 URL 和 release tag；
- 文件 SHA-256；
- Python ABI 和 CUDA 架构；
- 构建日志；
- 依赖解析结果。

构建机不需要 GPU，但运行机必须有兼容驱动和 NVIDIA Container Toolkit。镜像可以离线传输，模型文件也应单独校验后再挂载。

## 3. 验证宿主机和容器

### 宿主机

```bash
nvidia-smi
nvidia-smi topo -m
```

### Docker GPU 直通

```bash
docker run --rm --gpus all nvidia/cuda:<TAG> nvidia-smi
```

如果这一步失败，先排查驱动、runtime toolkit、Docker daemon 和设备权限，不要先修改 vLLM 参数。`--num-gpus` 或应用层的设备声明不能替代 Docker 的 GPU 注入。

### 容器内检查

至少检查：

```bash
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.device_count())"
nvidia-smi topo -m
```

对于自定义 CUDA 扩展，还要确认实际编译架构与目标 GPU 的 compute capability 一致。

## 4. 模型文件与挂载

模型目录应包含完整的 config、tokenizer、权重和所需的自定义代码，并记录 revision 与校验值。生产挂载建议：

```bash
-v /models/<MODEL>:/model:ro
```

启动前检查：

- 配置文件存在；
- 权重文件没有截断；
- tokenizer 与模型 revision 匹配；
- chat template 或专用编码脚本符合当前模型要求；
- `--trust-remote-code` 确实必要，并且代码已经审查。

模型目录很大时，加载时间、内存映射和共享存储延迟会影响启动与回滚，应单独测量，不要只看 GPU 显存。

## 5. 显存预算不是简单除法

总权重除以 GPU 数只能得到第一轮估算。实际预算还包括：

- pipeline 阶段边界处的复制或未分片层；
- KV cache；
- 激活和临时 workspace；
- CUDA graph 或 JIT 编译峰值；
- 框架运行时和通信 buffer；
- 长上下文和并发带来的动态变化。

启动日志中的实际 KV cache、可用 block、并发估算和最终 `max_model_len` 比手算表更有价值。建议按以下顺序调参：

1. 先使用保守上下文和序列数；
2. 确认模型能完整加载；
3. 逐步增加上下文；
4. 再逐步增加并发；
5. 每次记录 OOM、延迟和输出质量。

`--gpu-memory-utilization` 不是“预留 CUDA 错误”的固定安全余量，不能把 0.95 或 0.90 当成跨环境通用推荐。

## 6. 安全默认值

一个可审计的运行命令应明确：

- 是否需要 GPU、共享内存、InfiniBand 或额外 capability；
- API 绑定哪个地址；
- 谁可以访问端口；
- 是否启用认证；
- 是否允许出站网络；
- 模型是否只读；
- 容器是否自动重启；
- 日志和临时文件如何清理。

不要为了省事默认使用 `--privileged`。如果确实需要特殊能力，单独记录原因、风险和撤销方式。工具调用、远程代码和公网 API 也要视为不可信输入。

## 7. 功能验收优先于性能验收

启动成功后按顺序验证：

1. 模型列表和健康检查；
2. 最小非流式请求；
3. 流式输出；
4. 中英文和特殊字符；
5. 工具调用或结构化输出（如果模型支持）；
6. 取消、超时和服务重启；
7. 长上下文边界；
8. 多用户并发与队列行为。

不要只用一个“Hello”请求和 GPU 利用率截图证明部署成功。工具调用、推理内容、chat template 和模型编码方式可能需要额外验证。

## 8. 性能数据记录模板

```text
GPU / 驱动：
镜像 digest：
模型 revision：
CUDA / PyTorch / vLLM：
并行策略：
上下文与并发：
输入 / 输出 token：
预热方式：
采样参数：
TTFT / TPOT / P95 / P99：
成功请求数与错误：
测试日期与命令：
```

没有这些字段的数字只能作为个人实验记录，不能作为跨机器或跨版本的容量承诺。

## 发布前检查清单

- [ ] GPU 型号、显存和 compute capability 已记录；
- [ ] 宿主机驱动与容器 runtime 已验证；
- [ ] `nvidia-smi` 在容器内可用；
- [ ] 镜像使用不可变 digest；
- [ ] 模型 revision、文件校验值和挂载方式已记录；
- [ ] 远程代码和工具调用边界已审查；
- [ ] API 认证和网络访问策略已配置；
- [ ] 显存预算来自实际启动日志和压力测试；
- [ ] 功能测试覆盖流式、取消、错误和长上下文；
- [ ] 性能数据包含完整实验条件；
- [ ] 有版本回滚和故障恢复步骤。

## 官方入口

- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [vLLM supported models](https://docs.vllm.ai/en/latest/models/supported_models.html)
- [vLLM parallelism and scaling](https://docs.vllm.ai/en/latest/serving/parallelism_scaling/)
- [vLLM online serving](https://docs.vllm.ai/en/latest/serving/online_serving/)
