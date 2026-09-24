---

layout: post
title: 'New-API 部署同一模型双进程双端口：实现负载均衡与高可用的完整指南'
summary: 'Deploy two New-API processes for the same model on separate ports to achieve load balancing and high availability, with complete Docker Compose configuration and tuning notes.'
lang: zh-CN
date: 2026-09-05 02:26:00
categories:
- AI & LLM
tags:
- NewAPI
- Docker
- Model
- LLM
---
{% raw %}
> 在生产环境中部署大语言模型时，单点故障和性能瓶颈是常见的挑战。本文将详细介绍如何通过 New-API 部署同一模型的两个独立进程，并配置不同端口，实现负载均衡和高可用架构。

---

<!--more-->

## 目录

- [背景与动机](#背景与动机)
- [架构概览](#架构概览)
- [环境准备](#环境准备)
- [方案一：独立 Worker + New-API 网关（推荐）](#方案一独立-worker--new-api-网关推荐)
- [方案二：两个 New-API 实例（内置 Worker 模式）](#方案二两个-new-api-实例内置-worker-模式)
- [Docker Compose 完整部署](#docker-compose-完整部署)
- [验证与测试](#验证与测试)
- [性能调优](#性能调优)
- [常见问题排查](#常见问题排查)
- [安全注意事项](#安全注意事项)
- [总结与建议](#总结与建议)

---

## 背景与动机

### 什么是 New-API？

New-API 是一个开源的 API 网关和管理平台，专门用于统一管理和调度多个大语言模型（LLM）后端。它兼容 OpenAI API 格式，支持 vLLM、llama.cpp、transformers 等多种推理后端，并提供用户管理、计费、限流等企业级功能。

### 为什么需要多进程部署？

在实际生产环境中，我们经常面临以下挑战：

1. **高可用性需求**：单个 Worker 进程崩溃会导致服务完全中断
2. **并发处理能力**：单个进程可能无法处理大量并发请求
3. **滚动更新**：需要在不中断服务的情况下更新模型或配置
4. **负载分担**：将请求分布到多个 Worker 以提高整体吞吐量

通过部署同一模型的两个独立进程，我们可以：

- 实现故障转移：一个 Worker 崩溃时，另一个继续服务
- 自动负载均衡：New-API 自动在两个 Worker 间轮询分配请求
- 无缝维护：可以逐个重启 Worker 而不影响整体服务

### 架构选择：何时使用多进程？

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 高可用要求高 | 多进程部署 | 故障自动转移 |
| 单 GPU 显存充足 | 单 Worker + 张量并行 | 更高效利用显存 |
| 多 GPU 可用 | 多进程或张量并行 | 根据显存和性能需求选择 |
| 开发测试环境 | 单 Worker | 简单快速 |

---

## 架构概览

### 整体架构

```
                    ┌─────────────────────────────────────┐
                    │          New-API Gateway            │
                    │            (port 3000)              │
                    │                                     │
                    │   用户请求 ──► 路由决策              │
                    │                     │               │
                    │              ┌──────┴──────┐       │
                    │              ▼             ▼       │
                    │    Channel 1         Channel 2     │
                    │    (Worker 1)        (Worker 2)    │
                    │      :8000             :8001       │
                    └─────────────┬───────────┬─────────┘
                                  │           │
                                  ▼           ▼
                    ┌─────────────────┐ ┌─────────────────┐
                    │   vLLM Worker 1 │ │   vLLM Worker 2 │
                    │    (port 8000)  │ │    (port 8001)  │
                    │                 │ │                 │
                    │  GPU 0          │ │  GPU 1          │
                    │  模型权重       │ │  模型权重       │
                    │  推理引擎       │ │  推理引擎       │
                    └────────┬────────┘ └────────┬────────┘
                             │                   │
                             ▼                   ▼
                    ┌─────────────────────────────────────┐
                    │       模型存储（宿主机挂载）         │
                    │   -v /data/models:/models           │
                    │   或 NFS/NAS 共享存储               │
                    └─────────────────────────────────────┘
```

### 负载均衡机制

New-API 内置的负载均衡器采用**轮询（Round-Robin）算法**：

1. 收到用户请求后，检查目标模型有哪些可用的 Channel
2. 按顺序依次分配请求到各个 Channel
3. 如果某个 Channel 失败，自动尝试下一个
4. 支持配置重试策略和超时时间

```python
# New-API 内部负载均衡逻辑示意
current_index = 0

def route_request(model_name, channels):
    global current_index
    available = [ch for ch in channels if ch.model == model_name and ch.is_healthy]
    if not available:
        raise NoAvailableChannel()
    
    # 轮询选择
    selected = available[current_index % len(available)]
    current_index += 1
    
    return selected.endpoint
```

---

## 环境准备

### 硬件要求

| 资源 | 最低要求 | 推荐配置 |
|------|----------|----------|
| GPU | 1x 24GB VRAM（如 RTX 4090） | 2x 24GB VRAM（双卡） |
| CPU | 8 核 | 16 核以上 |
| 内存 | 32GB | 64GB 以上 |
| 存储 | 100GB SSD（模型存储） | 500GB NVMe SSD |

### 软件依赖

```bash
# 1. 安装 NVIDIA 驱动（以 Ubuntu 为例）
sudo apt install nvidia-driver-550  # 或更高版本
# 或从 NVIDIA 官网下载 .run 安装包手动安装

# 2. 验证驱动和 CUDA
nvidia-smi
nvcc --version  # 可选，需安装完整 CUDA Toolkit 才有

# 3. 安装 Docker
docker --version  # >= 20.10

# 4. 安装 NVIDIA Container Toolkit
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 5. 验证 GPU 支持
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

### 模型准备

假设我们使用 `Qwen2.5-7B-Instruct` 模型：

```bash
# 创建模型目录
mkdir -p /data/models

# 下载模型（使用 huggingface-cli）
pip install huggingface_hub  # 建议在虚拟环境中安装
huggingface-cli download Qwen/Qwen2.5-7B-Instruct --local-dir /data/models/Qwen2.5-7B-Instruct

# 或者使用已有模型
ls -la /data/models/Qwen2.5-7B-Instruct/
```

---

## 方案一：独立 Worker + New-API 网关（推荐）

这是最灵活、最可控的部署方式，适用于生产环境。

### 步骤 1：启动 Worker 1（端口 8000）

```bash
docker run -d \
  --name vllm-worker-1 \
  --gpus '"device=0"' \
  --shm-size=8g \
  -p 8000:8000 \
  -v /data/models:/models \
  vllm/vllm-openai:latest \
  --model /models/Qwen2.5-7B-Instruct \
  --port 8000 \
  --host 0.0.0.0 \
  --tensor-parallel-size 1 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9 \
  --trust-remote-code \
  --dtype auto
```

**参数说明：**

| 参数 | 说明 | 推荐值 |
|------|------|--------|
| `--gpus` (docker) | 指定使用的 GPU 设备 | `"device=0"` 或 `"device=1"` |
| `--shm-size` (docker) | 共享内存大小 | `8g` 或更大 |
| `--tensor-parallel-size` | 张量并行数 | 单卡设为 `1` |
| `--max-model-len` | 最大上下文长度 | 根据显存调整 |
| `--gpu-memory-utilization` | GPU 显存使用率 | `0.85-0.95` |
| `--trust-remote-code` | 信任远程代码 | 部分模型需要 |
| `--dtype` | 数据类型 | `auto` 或 `half` |

### 步骤 2：启动 Worker 2（端口 8001）

```bash
docker run -d \
  --name vllm-worker-2 \
  --gpus '"device=1"' \
  --shm-size=8g \
  -p 8001:8001 \
  -v /data/models:/models \
  vllm/vllm-openai:latest \
  --model /models/Qwen2.5-7B-Instruct \
  --port 8001 \
  --host 0.0.0.0 \
  --tensor-parallel-size 1 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9 \
  --trust-remote-code \
  --dtype auto
```

**关键点：**

- 使用不同的 GPU 设备（`device=0` 和 `device=1`）
- 使用不同的端口（8000 和 8001）
- 使用不同的容器名称（`vllm-worker-1` 和 `vllm-worker-2`）
- 模型路径保持一致

### 步骤 3：启动 New-API 网关

```bash
docker run -d \
  --name new-api-gateway \
  -p 3000:3000 \
  -e LISTEN=0.0.0.0:3000 \
  -e TZ=Asia/Shanghai \
  newapi/new-api:latest
```

### 步骤 4：配置 New-API Channel

#### 方式一：通过 Web 界面配置

1. 访问 `http://your-server:3000`
2. 使用默认管理员账号登录（首次运行会提示设置密码）
3. 进入 **渠道管理** → **添加渠道**

**Channel 1 配置：**

| 字段 | 值 |
|------|-----|
| 渠道名称 | `Qwen2.5-7B Worker 1` |
| 渠道类型 | `OpenAI-API` |
| 密钥 | `sk-vllm-worker1`（任意值，vLLM 不校验） |
| 地址 | `http://vllm-worker-1:8000/v1` |
| 模型 | `Qwen2.5-7B-Instruct` |

**Channel 2 配置：**

| 字段 | 值 |
|------|-----|
| 渠道名称 | `Qwen2.5-7B Worker 2` |
| 渠道类型 | `OpenAI-API` |
| 密钥 | `sk-vllm-worker2`（任意值，vLLM 不校验） |
| 地址 | `http://vllm-worker-2:8001/v1` |
| 模型 | `Qwen2.5-7B-Instruct` |

#### 方式二：通过 API 配置

> `sk-newapi-admin` 是 New-API 管理员密钥，首次登录管理面板时设置。

```bash
# 创建 Channel 1
curl -X POST http://localhost:3000/api/channel/ \
  -H "Authorization: Bearer sk-newapi-admin" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Qwen2.5-7B Worker 1",
    "type": 1,
    "base_url": "http://vllm-worker-1:8000/v1",
    "key": "sk-vllm-worker1",
    "models": ["Qwen2.5-7B-Instruct"]
  }'

# 创建 Channel 2
curl -X POST http://localhost:3000/api/channel/ \
  -H "Authorization: Bearer sk-newapi-admin" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Qwen2.5-7B Worker 2",
    "type": 1,
    "base_url": "http://vllm-worker-2:8001/v1",
    "key": "sk-vllm-worker2",
    "models": ["Qwen2.5-7B-Instruct"]
  }'
```

#### 方式三：配置文件

创建 `channels.json`：

```json
{
  "channels": [
    {
      "name": "Qwen2.5-7B Worker 1",
      "type": "openai",
      "base_url": "http://vllm-worker-1:8000/v1",
      "api_key": "sk-vllm-worker1",
      "models": ["Qwen2.5-7B-Instruct"]
    },
    {
      "name": "Qwen2.5-7B Worker 2",
      "type": "openai",
      "base_url": "http://vllm-worker-2:8001/v1",
      "api_key": "sk-vllm-worker2",
      "models": ["Qwen2.5-7B-Instruct"]
    }
  ]
}
```

---

## 方案二：两个 New-API 实例（内置 Worker 模式）

如果使用 New-API 内置的 Worker（而非外部 vLLM/llama.cpp），可以启动两个独立的 New-API 实例。

### 实例 1：端口 3000

创建 `.env.1`：

```env
# New-API 实例 1 配置
LISTEN=0.0.0.0:3000
MODEL_PATH=/data/models/Qwen2.5-7B-Instruct
WORKERS=1
WORKERConcurrency=4
MAX_REQUESTS=1000
TZ=Asia/Shanghai

# 数据库配置（可选，用于持久化）
DB_TYPE=sqlite
DB_PATH=/data/new-api-1.db

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

启动命令：

```bash
docker run -d \
  --name new-api-worker-1 \
  --gpus '"device=0"' \
  --env-file .env.1 \
  -p 3000:3000 \
  -v /data/new-api-1:/data \
  newapi/new-api:latest
```

### 实例 2：端口 3001

创建 `.env.2`：

```env
# New-API 实例 2 配置
LISTEN=0.0.0.0:3001
MODEL_PATH=/data/models/Qwen2.5-7B-Instruct
WORKERS=1
WORKERConcurrency=4
MAX_REQUESTS=1000
TZ=Asia/Shanghai

# 数据库配置
DB_TYPE=sqlite
DB_PATH=/data/new-api-2.db

# 管理员配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
```

启动命令：

```bash
docker run -d \
  --name new-api-worker-2 \
  --gpus '"device=1"' \
  --env-file .env.2 \
  -p 3001:3001 \
  -v /data/new-api-2:/data \
  newapi/new-api:latest
```

### 配置网关

启动第三个 New-API 实例作为纯网关（不加载模型）：

```bash
docker run -d \
  --name new-api-gateway \
  -p 8080:3000 \
  -e LISTEN=0.0.0.0:3000 \
  -e WORKERS=0 \
  -e TZ=Asia/Shanghai \
  newapi/new-api:latest
```

然后将两个 Worker 实例注册为 Channel，方式与方案一相同。

---

## Docker Compose 完整部署

### 文件结构

```
new-api-multi-process/
├── docker-compose.yml
└── config/        # New-API 配置文件（首次可为空）
```

### docker-compose.yml

```yaml
services:
  # Worker 1 - 使用 GPU 0
  vllm-worker-1:
    image: vllm/vllm-openai:latest
    container_name: vllm-worker-1
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - /data/models:/models
    command: >
      --model /models/Qwen2.5-7B-Instruct
      --port 8000
      --host 0.0.0.0
      --tensor-parallel-size 1
      --max-model-len 4096
      --gpu-memory-utilization 0.9
      --trust-remote-code
      --dtype auto
      --enforce-eager
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['0']
              capabilities: [gpu]
    shm_size: '8g'
    healthcheck:
      test: ["CMD-SHELL", "python3 -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')\""]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    networks:
      - new-api-network

  # Worker 2 - 使用 GPU 1
  vllm-worker-2:
    image: vllm/vllm-openai:latest
    container_name: vllm-worker-2
    restart: unless-stopped
    ports:
      - "8001:8001"
    volumes:
      - /data/models:/models
    command: >
      --model /models/Qwen2.5-7B-Instruct
      --port 8001
      --host 0.0.0.0
      --tensor-parallel-size 1
      --max-model-len 4096
      --gpu-memory-utilization 0.9
      --trust-remote-code
      --dtype auto
      --enforce-eager
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              device_ids: ['1']
              capabilities: [gpu]
    shm_size: '8g'
    healthcheck:
      test: ["CMD-SHELL", "python3 -c \"import urllib.request; urllib.request.urlopen('http://localhost:8001/health')\""]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 120s
    networks:
      - new-api-network

  # New-API 网关
  new-api:
    image: newapi/new-api:latest
    container_name: new-api-gateway
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - LISTEN=0.0.0.0:3000
      - TZ=Asia/Shanghai
    volumes:
      - ./config:/app/config
    depends_on:
      vllm-worker-1:
        condition: service_healthy
      vllm-worker-2:
        condition: service_healthy
    networks:
      - new-api-network

networks:
  new-api-network:
    driver: bridge
```

### 启动部署

```bash
# 创建必要目录
mkdir -p config

# config 目录用于存放 New-API 配置文件，首次可为空

# 启动所有服务
docker compose up -d

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 停止服务
docker compose down
```

---

## 验证与测试

### 1. 检查服务状态

```bash
# 查看所有容器状态
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 预期输出：
# NAMES                STATUS          PORTS
# vllm-worker-1        Up 2 minutes    0.0.0.0:8000->8000/tcp
# vllm-worker-2        Up 2 minutes    0.0.0.0:8001->8001/tcp
# new-api-gateway      Up 1 minute     0.0.0.0:3000->3000/tcp
```

### 2. 测试 Worker 健康检查

```bash
# 测试 Worker 1
curl http://localhost:8000/health
# 预期输出：{"status":"healthy"}

# 测试 Worker 2
curl http://localhost:8001/health
# 预期输出：{"status":"healthy"}
```

### 3. 测试模型可用性

```bash
# 查询 Worker 1 的模型列表
curl http://localhost:8000/v1/models | jq .
# 预期输出：
# {
#   "data": [
#     {
#       "id": "Qwen2.5-7B-Instruct",
#       "object": "model",
#       ...
#     }
#   ]
# }

# 查询 Worker 2 的模型列表
curl http://localhost:8001/v1/models | jq .
```

### 4. 测试负载均衡

```bash
# 通过 New-API 网关发送多次请求，观察负载均衡效果
for i in {1..10}; do
  echo "=== Request $i ==="
  curl -s http://localhost:3000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer sk-test" \
    -d '{
      "model": "Qwen2.5-7B-Instruct",
      "messages": [{"role": "user", "content": "Hello"}],
      "max_tokens": 10
    }' | jq -r '.choices[0].message.content'
  echo ""
done

# 在另一个终端查看 Worker 日志，可以看到请求被交替分配
# 终端 1：
docker logs --tail 5 -f vllm-worker-1 2>&1 | grep "POST /v1/chat/completions"
# 终端 2：
docker logs --tail 5 -f vllm-worker-2 2>&1 | grep "POST /v1/chat/completions"
```

### 5. Python 测试脚本

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:3000/v1",
    api_key="sk-test"
)

# 发送测试请求
for i in range(5):
    response = client.chat.completions.create(
        model="Qwen2.5-7B-Instruct",
        messages=[
            {"role": "user", "content": f"Hello, this is test request {i+1}"}
        ],
        max_tokens=50
    )
    print(f"Request {i+1}: {response.choices[0].message.content}")
    # 查看 Worker 日志可确认请求被分配到哪个 Worker
```

---

## 性能调优

### 1. GPU 显存优化

```bash
# 根据显存调整 GPU 使用率
--gpu-memory-utilization 0.85  # 留 15% 显存给系统和临时缓冲

# 如果显存不足，可以减小上下文长度
--max-model-len 2048  # 从 4096 降到 2048

# 使用量化模型减少显存占用
--quantization awq  # 或 gptq, squeezellm
```

### 2. 并发处理优化

```bash
# 增加 Worker 并发数
--max-num-seqs 64  # 最大并发序列数
--max-num-batched-tokens 8192  # 最大批处理 token 数
```

### 3. 网络优化

```bash
# docker run 时使用 host 网络模式减少网络延迟
docker run ... --network host vllm/vllm-openai ...

# 或者使用 Docker 内部网络（已在 docker-compose.yml 中配置）
```

### 4. 监控指标

关键监控指标：

| 指标 | 说明 | 正常范围 |
|------|------|----------|
| GPU 利用率 | GPU 计算资源使用 | 70-95% |
| 显存使用 | GPU 显存占用 | < 90% |
| 请求延迟 | 单次请求响应时间 | < 2s（7B 模型） |
| 吞吐量 | 每秒处理的 token 数 | 根据模型大小而定 |
| 队列长度 | 等待处理的请求数 | < 10 |

监控命令：

```bash
# 实时 GPU 监控
watch -n 1 nvidia-smi

# Docker 容器资源使用
docker stats --no-stream
```

---

## 常见问题排查

### 问题 1：Worker 启动失败

**现象：** 容器立即退出或重启

**排查步骤：**

```bash
# 查看容器日志
docker logs vllm-worker-1

# 检查端口占用
lsof -i :8000
netstat -tlnp | grep 8000

# 检查 GPU 是否可用
nvidia-smi

# 检查模型路径
docker exec vllm-worker-1 ls /models/
```

**解决方案：**

```bash
# 如果端口被占用，停止占用进程
sudo lsof -ti :8000 | xargs kill -9

# 如果 GPU 不可用，检查 NVIDIA 驱动
nvidia-smi  # 应该显示 GPU 信息
docker run --rm --gpus all nvidia/cuda:12.4.0-base nvidia-smi
```

### 问题 2：显存不足（OOM）

**现象：** Worker 启动后崩溃，日志显示 `CUDA out of memory`

**解决方案：**

调整 vLLM 启动参数（在 `docker run` 命令末尾或 `docker-compose.yml` 的 `command` 中添加）：

```bash
# 方案 1：减少 GPU 显存使用率
--gpu-memory-utilization 0.7

# 方案 2：减小上下文长度
--max-model-len 2048

# 方案 3：使用更小的模型
# 将 Qwen2.5-7B-Instruct 替换为 Qwen2.5-3B-Instruct

# 方案 4：使用量化版本（需模型支持）
--quantization awq
```

### 问题 3：负载均衡不工作

**现象：** 所有请求都发送到同一个 Worker

**排查步骤：**

```bash
# 检查 Channel 配置
curl http://localhost:3000/api/channel/ \
  -H "Authorization: Bearer sk-newapi-admin" | jq .

# 检查模型名称是否一致
curl http://localhost:8000/v1/models | jq '.data[0].id'
curl http://localhost:8001/v1/models | jq '.data[0].id'
```

**解决方案：**

- 确保两个 Channel 的模型名称完全一致（区分大小写）
- 确认两个 Channel 的状态为"已启用"
- 重启 New-API 网关：`docker restart new-api-gateway`

### 问题 4：连接被拒绝

**现象：** 从 New-API 网关无法访问 Worker

**解决方案：**

```bash
# 查看 Docker 网络
docker network ls | grep new-api

# 查看网络详情（将 <network-name> 替换为实际网络名）
docker network inspect <network-name>

# 确保容器在同一网络（将 <network-name> 替换为实际网络名）
docker network connect <network-name> vllm-worker-1

# 或者使用容器 IP
docker inspect vllm-worker-1 | grep IPAddress

# 测试容器间通信（在宿主机上执行，将 <network-name> 替换为实际网络名）
docker run --rm --network <network-name> curlimages/curl curl -s http://vllm-worker-1:8000/health
```

### 问题 5：请求超时

**现象：** 请求长时间无响应

**排查步骤：**

```bash
# 检查 Worker 资源使用
docker stats --no-stream vllm-worker-1

# 检查网关到 Worker 的网络连通性
docker exec new-api-gateway python3 -c "import urllib.request; print(urllib.request.urlopen('http://vllm-worker-1:8000/health').read().decode())"

# 检查 Worker 日志（最近 50 行）
docker logs --tail 50 vllm-worker-1 2>&1 | grep -i error
```

**解决方案：**

调整 vLLM 启动参数：

```bash
# 增加 Worker 超时时间
--timeout 300

# 减少并发请求数
--max-num-seqs 32
```

---

## 安全注意事项

### 1. 网络安全

不要将 Worker 端口暴露到公网，只暴露 New-API 网关：

```bash
# 正确：只暴露网关端口
docker run ... -p 3000:3000 newapi/new-api:latest

# 错误：暴露 Worker 端口
# docker run ... -p 8000:8000 vllm/vllm-openai ...
# docker run ... -p 8001:8001 vllm/vllm-openai ...
```

### 2. API Key 管理

```bash
# 使用环境变量存储敏感信息
-e API_KEY=your-secure-api-key

# 或者使用 Docker secrets（需要先初始化 swarm）
# docker swarm init
# echo "your-secure-api-key" | docker secret create api_key -
```

### 3. 访问控制

在 New-API 环境变量中配置管理员凭据并禁用公开注册：

```yaml
environment:
  - ADMIN_USERNAME=admin
  - ADMIN_PASSWORD=your-secure-password
  - ENABLE_REGISTRATION=false
```

### 4. 日志安全

```bash
# 不要在日志中打印敏感信息（如密码、密钥等）
# 使用环境变量传递敏感配置，避免写入日志
```

---

## 总结与建议

### 方案选择指南

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 生产环境，需要高可用 | 方案一（独立 Worker） | 更灵活，更可控 |
| 开发测试环境 | 方案二（内置 Worker） | 更简单，资源占用少 |
| 多 GPU 服务器 | 多进程或张量并行 | 根据显存和性能需求选择 |
| 单 GPU 服务器 | 单 Worker 部署 | 避免显存不足 |

### 关键要点

1. **模型名称必须一致**：两个 Worker 和 Channel 的模型名称必须完全匹配
2. **端口不能冲突**：每个进程使用不同的端口
3. **显存要考虑双倍**：两个进程会加载两份模型权重
4. **网络要互通**：所有容器必须在同一个 Docker 网络中
5. **监控很重要**：实时监控 GPU 使用率和请求延迟

### 下一步

- 配置 HTTPS 和 SSL 证书
- 实现自动扩缩容
- 集成 Prometheus + Grafana 监控
- 配置日志收集和分析
- 实现模型版本管理和灰度发布

---

## 参考资料

- [New-API 官方仓库](https://github.com/Calcium-Ion/new-api/blob/main/README_ZH.md)
- [vLLM 官方文档](https://docs.vllm.ai/)
- [llama.cpp 官方仓库](https://github.com/ggerganov/llama.cpp)
- [Docker Compose 文档](https://docs.docker.com/compose/)

---

*最后更新：2026年9月*
{% endraw %}
