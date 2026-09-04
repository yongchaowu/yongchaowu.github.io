---
layout: post
title: MiniCPM5 1B Deploy llama.cpp
display_title: 'Deploying MiniCPM5-1B with llama.cpp'
summary: >
  Offline deployment of MiniCPM5-1B using llama.cpp server in Docker, with
  Open-WebUI frontend and CPU-only inference configuration.
lang: zh-CN
tested:
  Runtime: "llama.cpp + Open-WebUI"
  Inference: "CPU"
  Model: "MiniCPM5-1B"
date: 2026-06-10 07:47:00
categories:
- AI & LLM
tags:
- Model
- OS
- Docker
---

> For model overview, benchmarks, and quantization options, see [MiniCPM5-1B Overview]({% post_url 2026-06-10-Model-MiniCPM5-1B %}).

## Quick Start

> Goal: 在 Docker 中通过 llama.cpp 部署 MiniCPM5-1B 并通过 Open-WebUI 访问。

<!--more-->

### Prerequisites

- Docker 已安装
- 模型文件 `MiniCPM5-1B-Q4_K_M.gguf` 已下载
- 镜像文件：`llama-cpp-server:cpu`、`open-webui_image.tar`

### 1. 准备目录结构

```bash
mkdir -p models open-webui-data
# 将模型文件放入 models/ 目录
cp MiniCPM5-1B-Q4_K_M.gguf models/
```

### 2. 启动 llama-server

```bash
docker compose up -d
```

### 3. 启动 Open-WebUI

```bash
docker run -d -p 3000:8080 \
  -v ./open-webui-data:/app/backend/data \
  -e OPENAI_API_BASE_URL=http://<your-ip>:8080/v1 \
  -e OPENAI_API_KEY=dummy \
  -e HF_HUB_OFFLINE=true \
  -e ENABLE_MODEL_HUB=false \
  --name open-webui-llamacpp \
  --restart always \
  ghcr.io/open-webui/open-webui:main
```

### Verify

访问 `http://<your-ip>:3000`，在聊天界面输入测试消息，应收到模型回复。

> 完整 docker-compose 配置、Docker 镜像构建和 llama.cpp 编译见下方章节。

## 必备文件

- `llama-cpp-server:cpu` 镜像
- `open-webui_image.tar` Open-WebUI 镜像
- 模型文件：
    - `MiniCPM5-1B-F16.gguf`
    - `MiniCPM5-1B-Q8_0.gguf`
    - `MiniCPM5-1B-Q4_K_M.gguf`
- `docker-compose.yml`
- `llama.cpp.zip` 源码包
- [官方文档](https://github.com/OpenBMB/MiniCPM/blob/main/docs/deployment/llama_cpp.md)

## docker-compose.yml

```yaml
services:
  llama-server:
    image: llama-cpp-server:cpu
    container_name: llama-server
    ports:
      - "8080:8080"
    volumes:
      - ./models:/models
    command: >
      ./llama-server
      -m /models/MiniCPM5-1B-Q4_K_M.gguf
      --host 0.0.0.0
      --port 8080
      -ngl 0
      -c 8192
      --jinja
      --alias MiniCPM5-1B-Q4
    restart: unless-stopped
```

## Docker 镜像构建

使用基础镜像 `ubuntu:22.04` + llama.cpp 源码包构建。

### 编译 llama.cpp

```shell
git clone --depth=1 https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
mkdir -p build && cd build

# CPU-only build
cmake .. -DGGML_CUDA=OFF -DLLAMA_CURL=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release -j $(nproc) --target llama-quantize llama-cli llama-server

# CUDA build（如有 GPU）
# cmake .. -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=90 -DCMAKE_BUILD_TYPE=Release
```

### Dockerfile

```shell
FROM ubuntu:22.04

WORKDIR /app

RUN apt update && apt install -y --no-install-recommends \
    build-essential cmake unzip \
    && rm -rf /var/lib/apt/lists/*

COPY llama.cpp.zip /app/

RUN unzip -q llama.cpp.zip \
    && cd llama.cpp \
    && mkdir -p build && cd build \
    && cmake .. -DGGML_CUDA=OFF -DLLAMA_CURL=OFF -DCMAKE_BUILD_TYPE=Release \
    && cmake --build . --config Release -j $(nproc) \
    && cd ../.. \
    && rm -f llama.cpp.zip

WORKDIR /app/llama.cpp/build/bin

EXPOSE 8080

CMD ["./llama-server", "--help"]
```

构建镜像：

```bash
docker build -t llama-cpp-server:cpu .
```

## llama-cli 命令行

```shell
# 下载模型
huggingface-cli download openbmb/MiniCPM5-1B-GGUF MiniCPM5-1B-Q4_K_M.gguf --local-dir ./minicpm5

# 交互式聊天
llama-cli -m ./minicpm5/MiniCPM5-1B-Q4_K_M.gguf -n 2048 --temp 0.7 --top-p 0.95 -ngl 0

# 启动服务
llama-server -m ./minicpm5/MiniCPM5-1B-Q4_K_M.gguf --host 0.0.0.0 --port 8080 -ngl 0 -c 4096 --jinja -t 6 -b 512 --alias MiniCPM5-1B-Q4

# 测试 API
curl http://localhost:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "MiniCPM5-1B-Q4",
        "messages": [{"role": "user", "content": "1+1=?"}],
        "temperature": 0.7, "top_p": 0.95, "max_tokens": 256
    }'
```

## Reference

### 模型格式

| 文件 | 说明 |
|------|------|
| `MiniCPM5-1B-F16.gguf` | 全精度，体积最大 |
| `MiniCPM5-1B-Q8_0.gguf` | 8-bit 量化 |
| `MiniCPM5-1B-Q4_K_M.gguf` | 4-bit 量化（推荐） |

### 端口

| 端口 | 服务 |
|------|------|
| 8080 | llama-server API |
| 3000 | Open-WebUI |

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `-ngl` | 99 | GPU 层数（CPU 模式可设 0） |
| `-c` | 8192 | 上下文长度 |
| `--jinja` | - | 启用 Jinja 模板 |
| `--alias` | MiniCPM5-1B-Q4 | 模型别名 |
