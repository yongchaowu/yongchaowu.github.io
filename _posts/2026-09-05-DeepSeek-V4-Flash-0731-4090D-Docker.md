---

layout: post
title: 'Running DeepSeek-V4-Flash-0731 on 8x RTX 4090D with Docker'
summary: 'Step-by-step guide to building a Docker image and serving DeepSeek-V4-Flash-0731 on 8x RTX 4090D consumer GPUs using the vLLM SM89 fork.'
lang: en
date: 2026-09-05 01:30:00
categories:
- AI & LLM
tags:
- Model
- LLM
- Docker
- NVIDIA
---
A step-by-step guide to building a Docker image and serving DeepSeek-V4-Flash-0731 on consumer-grade GPUs using the [vLLM SM89 fork](https://github.com/yhfgyyf/vllm-deepseek-v4-sm89).

使用 [vLLM SM89 fork](https://github.com/yhfgyyf/vllm-deepseek-v4-sm89) 在消费级 GPU 上构建 Docker 镜像并部署 DeepSeek-V4-Flash-0731 的分步指南。

---

<!--more-->

## Why This Matters / 为什么这很重要

DeepSeek-V4-Flash-0731 is a 167GB MoE model with sparse attention (DSA/Lightning Indexer) and FP4 expert weights. Official vLLM only supports it on SM90/SM100/SM120 (H100/B100/GB300). This fork extends support to **SM89 (Ada Lovelace)** — making it possible to run on RTX 4090/4090D, L40, L40S, and RTX 6000 Ada.

DeepSeek-V4-Flash-0731 是一个 167GB 的 MoE 模型，支持稀疏注意力（DSA/Lightning Indexer）和 FP4 专家权重。官方 vLLM 仅支持 SM90/SM100/SM120（H100/B100/GB300）。这个 fork 扩展了对 **SM89（Ada Lovelace）** 的支持 — 使其可以在 RTX 4090/4090D、L40、L40S 和 RTX 6000 Ada 上运行。

---

## Hardware & Prerequisites / 硬件与前置要求

### Required Hardware / 所需硬件

| Component / 组件 | Specification / 规格 |
|-----------|---------------|
| GPUs | 8x RTX 4090D (24GB GDDR6X each / 每卡 24GB) |
| Total VRAM / 总显存 | 192GB |
| Driver / 驱动 | NVIDIA 595.x or later / 或更高版本 |
| CUDA Toolkit | 13.0 (installed on host / 宿主机安装) |

### Build Machine / 构建机器

The Docker image can be built on any Linux x86_64 machine with Docker. **No GPU is required for building.** GPU is only needed at runtime for serving the model.

Docker 镜像可以在任何安装了 Docker 的 Linux x86_64 机器上构建。**构建不需要 GPU。** GPU 仅在运行时需要。

### Required Software / 所需软件

- Docker with [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- [uv](https://github.com/astral-sh/uv) package manager (for fast Python dependency installation / 用于快速安装 Python 依赖)
- Pre-built wheels from the [latest release](https://github.com/yhfgyyf/vllm-deepseek-v4-sm89/releases/latest):
  - `flashinfer_python-0.6.14+sm89.1-py3-none-any.whl` — SHA256: `667e4c1c1a288681493e192a0d02976e791078a8792c47bad4d7f9186109554e`
  - `vllm-0.23.1rc1.dev904+g8e321cc4f.cu130-cp312-cp312-linux_x86_64.whl` — SHA256: `d1a4e4ee3f64882f129a8d12e47bcd70c46992b83a16c2e6c722d85dbe87b41c`

> **Note / 注意:** Verify SHA256 hashes at release time. These values are from the initial release.
> 请在发布时验证 SHA256 哈希值。以上值来自初始版本。

Place both wheels in a `wheels/` directory next to the Dockerfile.

将两个 wheel 文件放入 Dockerfile 同级目录下的 `wheels/` 目录中。

### Prerequisites Check / 前置检查

Run these commands to verify your environment:

运行以下命令验证你的环境：

```bash
# Check NVIDIA driver / 检查 NVIDIA 驱动
nvidia-smi

# Check Docker / 检查 Docker
docker --version

# Verify GPU passthrough works / 验证 GPU 直通
docker run --rm --gpus all nvidia/cuda:13.0.0-base-ubuntu24.04 nvidia-smi
```

Expected output / 预期输出:

```
+-------------------------+
| NVIDIA-SMI 595.xx       |
| Driver Version: 595.xx  |
| CUDA Version: 13.0      |
|                         |
| GPU 0  RTX 4090D  24GB  |
| GPU 1  RTX 4090D  24GB  |
| ...                     |
| GPU 7  RTX 4090D  24GB  |
+-------------------------+
```

---

## Memory Budget / 显存预算

With 167GB of model weights and 192GB total VRAM across 8 GPUs (TP=4, PP=2):

模型权重 167GB，8 张 GPU 总显存 192GB（TP=4, PP=2）：

| Item / 项目 | Value / 值 |
|------|-------|
| Model weights / 模型权重 | 167GB |
| Weights per pipeline stage / 每个流水线阶段权重 | ~83.5GB |
| Weights per GPU (TP=4) / 每张 GPU 权重 | ~20.9GB |
| Remaining per GPU / 每张 GPU 剩余 | ~3.1GB |
| Total KV cache budget / KV 缓存总预算 | ~25GB |

This is tight. The 4x RTX 4090 (48GB) setup in the README supports 256K context. On 8x 4090D (24GB), we recommend **max-model-len=32768 (32K)** for stability, or **65536 (64K)** if you reduce `gpu-memory-utilization` and `max-num-seqs`.

显存很紧张。README 中的 4x RTX 4090（48GB）配置支持 256K 上下文。在 8x 4090D（24GB）上，我们建议使用 **max-model-len=32768（32K）** 以保证稳定性，或者 **65536（64K）** 同时降低 `gpu-memory-utilization` 和 `max-num-seqs`。

---

## Step 1: The Dockerfile / 第一步：Dockerfile

Merge both Dockerfiles (base + fixed) into a single file:

将基础 Dockerfile 和修复后的 Dockerfile 合并为一个文件：

```dockerfile
FROM nvidia/cuda:13.0.0-devel-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV CUDA_HOME=/usr/local/cuda
ENV PATH=${CUDA_HOME}/bin:$PATH
ENV FLASHINFER_DISABLE_VERSION_CHECK=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV LD_LIBRARY_PATH="/opt/venv/lib/python3.12/site-packages/PyNvVideoCodec:/opt/venv/lib:${LD_LIBRARY_PATH}"

# System dependencies / 系统依赖
RUN apt-get update && apt-get install -y \
    python3.12 python3.12-venv \
    curl git wget \
    ffmpeg libavcodec60 libavformat60 libavutil58 \
    libavdevice60 libavfilter9 libswscale7 libswresample4 \
    python3.12-dev ninja-build build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager / 安装 uv 包管理器
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /opt/app

# Copy pre-built wheels / 复制预构建的 wheel 文件
COPY wheels /opt/wheels

# Create virtual environment and install wheels / 创建虚拟环境并安装 wheel 文件
RUN uv venv --python 3.12 --seed /opt/venv

RUN uv pip install \
    --python /opt/venv/bin/python \
    /opt/wheels/flashinfer_python-0.6.14+sm89.1-py3-none-any.whl \
    /opt/wheels/vllm-0.23.1rc1.dev904+g8e321cc4f.cu130-cp312-cp312-linux_x86_64.whl \
    flashinfer-cubin==0.6.13 \
    torchvision \
    --torch-backend=cu130

WORKDIR /workspace
CMD ["bash"]
```

### Key Details / 关键说明

- **`FLASHINFER_DISABLE_VERSION_CHECK=1`** — Required because the SM89 fork wheels don't match official FlashInfer version tags. / 必须设置，因为 SM89 fork 的 wheel 版本与官方 FlashInfer 版本标签不匹配。
- **`--torch-backend=cu130`** — Ensures uv pulls CUDA 13.0 torch wheels, not CPU-only. / 确保 uv 拉取 CUDA 13.0 的 torch wheel，而非 CPU 版本。
- **`flashinfer-cubin==0.6.13`** — SM89 sparse MLA still JIT-compiles from the 0.6.14 fork source at runtime. / SM89 稀疏 MLA 仍需在运行时从 0.6.14 fork 源码 JIT 编译。
- **`COPY wheels /opt/wheels`** — Wheels must be in the build context. Copy them into the same directory as the Dockerfile before building. / wheel 文件必须在构建上下文中。构建前请将其复制到 Dockerfile 同级目录。

---

## Step 2: Build the Image / 第二步：构建镜像

```bash
# Ensure wheels are in the build context / 确保 wheel 文件在构建上下文中
cp /path/to/*.whl ./wheels/

# Build / 构建
docker build -t deepseek-v4-flash-4090d:latest .
```

---

## Step 2b: Export for Offline/Air-Gapped Deployment / 第二步b：导出用于离线部署

If your target server has no internet access (e.g., Kylin Linux in enterprise environments), build the image on an online machine and transfer it.

如果目标服务器无法访问互联网（如企业环境中的银河麒麟 Linux），请在联网机器上构建镜像并传输。

### Save the Image / 保存镜像

```bash
docker save -o deepseek-v4-flash-4090d.tar deepseek-v4-flash-4090d:latest
gzip deepseek-v4-flash-4090d.tar
```

### Transfer to Target Server / 传输到目标服务器

Copy `deepseek-v4-flash-4090d.tar.gz` to the offline server via USB, internal network, or other transfer method.

通过 USB、内网或其他方式将 `deepseek-v4-flash-4090d.tar.gz` 传输到离线服务器。

### Load on Target Server / 在目标服务器加载

```bash
docker load -i deepseek-v4-flash-4090d.tar.gz
docker images  # Verify image is loaded / 验证镜像已加载
```

### Host Requirements (Offline) / 离线环境宿主机要求

The target server needs / 目标服务器需要:

- NVIDIA GPU with driver installed / 已安装驱动的 NVIDIA GPU
- Docker with NVIDIA Container Toolkit / 安装了 NVIDIA Container Toolkit 的 Docker
- CUDA toolkit is **not** required on the host (it's inside the container) / 宿主机**无需**安装 CUDA toolkit（容器内已有）

---

## Step 3: Download the Model / 第三步：下载模型

```bash
# Using uv to install huggingface_hub / 使用 uv 安装 huggingface_hub
uv tool install huggingface_hub

huggingface-cli download \
    deepseek-ai/DeepSeek-V4-Flash-0731 \
    --local-dir /data/DeepSeek-V4-Flash-0731
```

The model is 167GB across 48 safetensor files. Ensure you have sufficient disk space and a stable connection.

模型共 167GB，包含 48 个 safetensor 文件。请确保有足够的磁盘空间和稳定的网络连接。

---

## Step 4: Deploy with vLLM / 第四步：使用 vLLM 部署

```bash
docker run --gpus all --shm-size=16g \
    -v /data/DeepSeek-V4-Flash-0731:/model \
    -p 8000:8000 \
    deepseek-v4-flash-4090d:latest \
    bash -c "export FLASHINFER_DISABLE_VERSION_CHECK=1 && \
    vllm serve /model \
        --served-model-name deepseek-v4-flash \
        --tensor-parallel-size 4 \
        --pipeline-parallel-size 2 \
        --kv-cache-dtype fp8_ds_mla \
        --block-size 256 \
        --max-model-len 32768 \
        --gpu-memory-utilization 0.95 \
        --max-num-seqs 4 \
        --attention-backend FLASHINFER_MLA_SPARSE_DSV4 \
        --reasoning-parser deepseek_v4 \
        --enable-auto-tool-choice --tool-call-parser deepseek_v4 \
        --trust-remote-code --port 8000"
```

> **Note / 注意:** The `bash -c "..."` is required to run the `export` and `vllm serve` commands in a shell. Without it, `export` will not work.
> 需要使用 `bash -c "..."` 来在 shell 中执行 `export` 和 `vllm serve` 命令。否则 `export` 将无法工作。

### What Each Flag Does / 各参数说明

| Flag / 参数 | Purpose / 用途 |
|------|---------|
| `--tensor-parallel-size 4` | Split model across 4 GPUs per pipeline stage / 每个流水线阶段使用 4 张 GPU 并行 |
| `--pipeline-parallel-size 2` | 2 pipeline stages across 8 GPUs / 8 张 GPU 分为 2 个流水线阶段 |
| `--kv-cache-dtype fp8_ds_mla` | FP8 MLA-compressed KV cache (critical for memory) / FP8 MLA 压缩 KV 缓存（节省显存） |
| `--block-size 256` | Required for SM89 sparse MLA decode / SM89 稀疏 MLA 解码必需 |
| `--max-model-len 32768` | Conservative for 24GB GPUs; increase to 65536 if stable / 24GB GPU 保守设置；稳定时可增至 65536 |
| `--gpu-memory-utilization 0.95` | Leave 5% headroom for CUDA overhead / 预留 5% 显存给 CUDA 开销 |
| `--max-num-seqs 4` | Max concurrent sequences / 最大并发序列数 |
| `--attention-backend FLASHINFER_MLA_SPARSE_DSV4` | Use FlashInfer SM89 sparse MLA path / 使用 FlashInfer SM89 稀疏 MLA 路径 |
| `--reasoning-parser deepseek_v4` | Enable reasoning mode / 启用推理模式 |
| `--enable-auto-tool-choice` | Enable function calling / 启用函数调用 |
| `--shm-size=16g` | Shared memory for tensor parallel communication / 张量并行通信的共享内存 |

### Success Indicators / 成功标志

Watch the logs for / 查看日志中的:

```
Application startup complete.
Using 'MARLIN' Mxfp4 MoE backend
Using FP8 indexer cache
```

---

## Step 5: Verify / 第五步：验证

### Smoke Test / 快速测试

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": "用一句话介绍长城。"}],
        "max_tokens": 256
    }'
```

Expected response / 预期响应:

```json
{
    "choices": [{
        "message": {
            "role": "assistant",
            "content": "长城是中国古代修建的军事防御工程，横跨中国北部..."
        }
    }],
    "usage": {
        "prompt_tokens": 15,
        "completion_tokens": 50,
        "total_tokens": 65
    }
}
```

### Operator-Level Self-Check (inside container) / 算子级自检（容器内）

```python
import torch
from vllm.platforms import current_platform
print("cap:", current_platform.get_device_capability())          # (8, 9)

from vllm.utils.flashinfer import has_flashinfer_sparse_mla_sm89
print("flashinfer sparse MLA SM89:", has_flashinfer_sparse_mla_sm89())  # True

from vllm.v1.attention.backends.mla.indexer import _uses_deep_gemm_scheduler_metadata
print("DeepGEMM scheduler metadata:", _uses_deep_gemm_scheduler_metadata())  # False

from vllm.utils.import_utils import has_cutedsl
print("has_cutedsl:", has_cutedsl())                             # False on SM89
```

### Health Check / 健康检查

```bash
# Check if the server is ready / 检查服务器是否就绪
curl -s http://localhost:8000/health

# List available models / 列出可用模型
curl -s http://localhost:8000/v1/models | python3 -m json.tool

# Get model info / 获取模型信息
curl -s http://localhost:8000/v1/models/deepseek-v4-flash | python3 -m json.tool
```

---

## Multi-User Serving / 多用户并发服务

The default `--max-num-seqs=4` is conservative. For serving multiple users, adjust these parameters:

默认的 `--max-num-seqs=4` 比较保守。如需多用户服务，请调整以下参数：

### Configuration for 8-16 Concurrent Users / 8-16 并发用户配置

```bash
docker run --gpus all --shm-size=16g \
    -v /data/DeepSeek-V4-Flash-0731:/model \
    -p 8000:8000 \
    deepseek-v4-flash-4090d:latest \
    bash -c "export FLASHINFER_DISABLE_VERSION_CHECK=1 && \
    vllm serve /model \
        --served-model-name deepseek-v4-flash \
        --tensor-parallel-size 4 \
        --pipeline-parallel-size 2 \
        --kv-cache-dtype fp8_ds_mla \
        --block-size 256 \
        --max-model-len 16384 \
        --gpu-memory-utilization 0.95 \
        --max-num-seqs 8 \
        --max-num-batched-tokens 32768 \
        --attention-backend FLASHINFER_MLA_SPARSE_DSV4 \
        --reasoning-parser deepseek_v4 \
        --enable-auto-tool-choice --tool-call-parser deepseek_v4 \
        --trust-remote-code --port 8000"
```

| Parameter / 参数 | Low User (default) / 低并发 | High User / 高并发 |
|--------|---------|---------|
| `--max-model-len` | 32768 (32K) | 16384 (16K) |
| `--max-num-seqs` | 4 | 8 |
| `--max-num-batched-tokens` | 8192 (default) | 32768 |
| Context per user / 每用户上下文 | 32K | 16K |

> **Trade-off / 权衡:** More concurrent users = shorter context length per user. / 并发用户越多，每用户可用上下文越短。

### Docker Compose / Docker Compose 部署

```yaml
services:
  deepseek-v4:
    image: deepseek-v4-flash-4090d:latest
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - FLASHINFER_DISABLE_VERSION_CHECK=1
    volumes:
      - /data/DeepSeek-V4-Flash-0731:/model
    ports:
      - "8000:8000"
    shm_size: '16g'
    command: >
      bash -c "vllm serve /model
        --served-model-name deepseek-v4-flash
        --tensor-parallel-size 4
        --pipeline-parallel-size 2
        --kv-cache-dtype fp8_ds_mla
        --block-size 256
        --max-model-len 32768
        --gpu-memory-utilization 0.95
        --max-num-seqs 4
        --attention-backend FLASHINFER_MLA_SPARSE_DSV4
        --reasoning-parser deepseek_v4
        --enable-auto-tool-choice --tool-call-parser deepseek_v4
        --trust-remote-code --port 8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 120s
```

```bash
# Start / 启动
docker compose up -d

# View logs / 查看日志
docker compose logs -f

# Stop / 停止
docker compose down
```

---

## API Authentication / API 认证

The vLLM server does not enable authentication by default. For production use, add an API key:

vLLM 服务器默认不启用认证。生产环境请添加 API 密钥：

```bash
# Set API key / 设置 API 密钥
docker run --gpus all --shm-size=16g \
    -v /data/DeepSeek-V4-Flash-0731:/model \
    -p 8000:8000 \
    -e VLLM_API_KEY=your-secret-key-here \
    deepseek-v4-flash-4090d:latest \
    bash -c "export FLASHINFER_DISABLE_VERSION_CHECK=1 && \
    vllm serve /model \
        --served-model-name deepseek-v4-flash \
        --tensor-parallel-size 4 \
        --pipeline-parallel-size 2 \
        --kv-cache-dtype fp8_ds_mla \
        --block-size 256 \
        --max-model-len 32768 \
        --gpu-memory-utilization 0.95 \
        --max-num-seqs 4 \
        --attention-backend FLASHINFER_MLA_SPARSE_DSV4 \
        --reasoning-parser deepseek_v4 \
        --enable-auto-tool-choice --tool-call-parser deepseek_v4 \
        --trust-remote-code --port 8000"
```

```bash
# Request with API key / 使用 API 密钥请求
curl -X POST http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer your-secret-key-here" \
    -d '{
        "model": "deepseek-v4-flash",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 100
    }'
```

---

## Monitoring / 监控

### GPU Usage / GPU 使用情况

```bash
# Real-time GPU monitoring / 实时 GPU 监控
watch -n 1 nvidia-smi

# Inside container / 容器内
docker exec -it <container_id> nvidia-smi
```

### vLLM Metrics / vLLM 指标

vLLM exposes Prometheus metrics at `/metrics`:

vLLM 在 `/metrics` 端点暴露 Prometheus 指标：

```bash
# Get metrics / 获取指标
curl -s http://localhost:8000/metrics | head -50

# Key metrics to watch / 需要关注的关键指标:
# vllm:num_requests_running   - 当前正在处理的请求数
# vllm:num_requests_waiting   - 等待队列中的请求数
# vllm:gpu_cache_usage_perc   - GPU 缓存使用率
# vllm:avg_generation_throughput - 平均生成吞吐量 (tok/s)
```

### Container Logs / 容器日志

```bash
# Follow logs / 实时查看日志
docker logs -f <container_id>

# Since last 10 minutes / 查看最近 10 分钟日志
docker logs --since 10m <container_id>
```

---

## Tuning for 24GB GPUs / 针对 24GB GPU 的调优

If you hit OOM, try these adjustments in order:

如果遇到 OOM，请按顺序尝试以下调整：

| Problem / 问题 | Fix / 解决方案 |
|---------|-----|
| OOM on startup / 启动时 OOM | Reduce `--max-model-len` to 16384 / 减小到 16384 |
| OOM during prefill / 预填充时 OOM | Reduce `--max-num-seqs` to 2 / 减小到 2 |
| OOM during decode / 解码时 OOM | Reduce `--gpu-memory-utilization` to 0.90 / 减小到 0.90 |
| Still OOM / 仍然 OOM | Disable DSpark speculative decoding if enabled / 禁用 DSpark 推测解码 |

### Alternative: Enable DSpark Speculative Decoding / 替代方案：启用 DSpark 推测解码

~4x decode speedup / 解码速度提升约 4 倍

If you have enough memory headroom (e.g., max-model-len=16384):

如果有足够的显存余量（如 max-model-len=16384）：

```bash
--speculative-config '{"method":"dspark","num_speculative_tokens":6,"draft_sample_method":"greedy"}' \
--max-num-batched-tokens 2048 \
--max-num-seqs 2
```

DSpark adds a draft model that speculatively generates tokens, verified by the main model. On 4x RTX 4090 (48GB), this achieved 286-344 tok/s decode throughput. Expect lower on 4090D due to tighter memory.

DSpark 添加一个草稿模型进行推测性 token 生成，由主模型验证。在 4x RTX 4090（48GB）上，解码吞吐量达到 286-344 tok/s。由于显存更紧张，4090D 上性能会略低。

### Performance Expectations / 性能预期

| Configuration / 配置 | Prefill / 预填充 | Decode / 解码 |
|------|---------|---------|
| 8x 4090D, TP=4, PP=2, 32K ctx | ~2000 tok/s | ~50-80 tok/s |
| 8x 4090D, TP=4, PP=2, 16K ctx, 8 users | ~800 tok/s | ~30-50 tok/s |
| 4x 4090, TP=4, PP=1, 32K ctx | ~2500 tok/s | ~80-120 tok/s |

> **Note / 注意:** Actual performance depends on prompt length, batch size, and system load.
> 实际性能取决于提示长度、批处理大小和系统负载。

---

## Troubleshooting / 故障排除

| Error / 错误 | Cause / 原因 | Fix / 解决方案 |
|-------|-------|-----|
| `RuntimeError: FlashInfer version check failed` | Missing `FLASHINFER_DISABLE_VERSION_CHECK=1` | Add `export FLASHINFER_DISABLE_VERSION_CHECK=1` before vllm serve / 在 vllm serve 前添加 export |
| `torch.cuda.OutOfMemoryError` | Insufficient VRAM for context length / 显存不足 | Reduce `--max-model-len` or `--gpu-memory-utilization` / 减小参数 |
| `No such file or directory: /opt/wheels/...` | Wheels not in build context / wheel 文件不在构建上下文中 | Copy `.whl` files into `wheels/` directory before `docker build` / 复制到 wheels 目录 |
| `NCCL error` | Tensor parallel communication failure / 张量并行通信失败 | Ensure `--shm-size=16g` and all 8 GPUs are visible / 确保共享内存和 GPU 可见 |
| `Connection refused` | Server not ready / 服务器未就绪 | Wait for startup or check logs / 等待启动或查看日志 |
| `401 Unauthorized` | API key required / 需要 API 密钥 | Add `Authorization: Bearer <key>` header / 添加认证头 |

### Useful Debug Commands / 调试命令

```bash
# Check container GPU access / 检查容器 GPU 访问
docker exec -it <container_id> nvidia-smi

# Check model files / 检查模型文件
docker exec -it <container_id> ls -la /model/

# Check vLLM logs / 检查 vLLM 日志
docker exec <container_id> cat /workspace/vllm.log

# Enter container for debugging / 进入容器调试
docker exec -it <container_id> bash

# Check port binding / 检查端口绑定
ss -tlnp | grep 8000

# Test API connectivity / 测试 API 连通性
curl -s http://localhost:8000/health
```

---

## References / 参考资料

- [vLLM SM89 Fork](https://github.com/yhfgyyf/vllm-deepseek-v4-sm89) — FlashInfer sparse MLA JIT for Ada / FlashInfer 稀疏 MLA JIT 适配 Ada
- [DeepSeek-V4-Flash-0731](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731) — Model weights (167GB) / 模型权重
- [FlashInfer 0.6.14 SM89 Fork](https://github.com/yhfgyyf/vllm-deepseek-v4-sm89/releases/latest) — Pre-built wheels / 预构建 wheel 文件
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html) — Docker GPU passthrough / Docker GPU 直通
- [uv Package Manager](https://github.com/astral-sh/uv) — Fast Python package installer / 快速 Python 包安装器
- [vLLM Documentation](https://docs.vllm.ai/) — Official vLLM docs / 官方文档
