---
layout: post
title: 'Multi-Node LLM Serving: vLLM + Ray'
summary: >
  End-to-end offline deployment of vLLM with Ray across two nodes in Docker,
  covering worker discovery, tensor-parallel inference, and automated health checks.
lang: zh-CN
tested:
  Deployment: "Docker multi-node"
  Topology: "2 nodes × 8 GPUs"
  Model: "MiniMax-M2.5-AWQ"
date: 2026-06-12 22:04:00
categories:
- AI & LLM
tags:
- Multi
- LLM
- Model
- Agent
- Docker
---

vLLM+Ray(Docker) 双节点离线一键部署完整方案。

<!--more-->

适配：vllm/vllm-openai 镜像、离线禁 HF 联网、双 8 卡 = 16 张量并行、MiniMax-M2.5-AWQ、脚本挂载启动、自动等待 Worker 就绪再拉起 vLLM。

## Quick Start

> Goal: 在两台 GPU 节点上通过 Docker 启动 vLLM + Ray 多节点推理服务。

### Prerequisites

- 两台 GPU 节点，各 8 张 GPU
- Docker 已安装（见 [Ubuntu NVIDIA Driver Install]({% post_url 2026-06-10-OS-Ubuntu-NVIDIA-Driver-Install %})）
- 两台节点间网络互通（Ray 端口 6379、vLLM 端口 8000）
- Ray 已安装（离线环境见 [Python Ray Offline Installation Guide]({% post_url 2026-06-12-Python-Ray-Offline-Installation-Guide %})）
- 模型文件已下载到两台节点的 `/data/models/minimax-m2.5-awq`

### 1. 准备脚本目录

在两台节点上执行：

```bash
mkdir -p /data/vllm_scripts && cd /data/vllm_scripts
```

### 2. 启动 Worker 节点

在 Worker 节点（`192.168.1.11`）执行：

```bash
docker run -d \
  --name vllm-ray-worker \
  --privileged --net=host --shm-size=64g \
  -v /data/models:/data/models \
  -v /data/vllm_scripts:/opt/scripts \
  -v /etc/localtime:/etc/localtime \
  -e HF_HUB_OFFLINE=1 -e VLLM_NO_USAGE_STATS=1 \
  vllm/vllm-openai \
  /opt/scripts/start_ray_worker.sh
```

### 3. 启动 Head 节点

在 Head 节点（`192.168.1.10`）执行：

```bash
docker run -d \
  --name vllm-ray-head \
  --privileged --net=host --shm-size=64g \
  -v /data/models:/data/models \
  -v /data/vllm_scripts:/opt/scripts \
  -v /etc/localtime:/etc/localtime \
  -e HF_HUB_OFFLINE=1 -e VLLM_NO_USAGE_STATS=1 \
  vllm/vllm-openai \
  /opt/scripts/start_ray_head.sh
```

### Verify

```bash
# 检查 Ray 集群状态（应显示 2 个节点、16 GPU）
docker exec vllm-ray-head ray status

# 检查 vLLM 服务
curl http://192.168.1.10:8000/v1/models

# 测试推理
curl http://192.168.1.10:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"minimax-m2.5-awq","messages":[{"role":"user","content":"Hello"}]}'
```

> 完整脚本准备和配置说明见下方完整部署章节。

## 架构

- Head 节点：运行 Ray Head + vLLM 主服务
- Worker 节点：运行 Ray Worker，提供 GPU 资源
- 通信：Ray 内部调度 + NCCL/GLOO 张量并行
- 模型：两台节点均挂载相同路径 `/data/models/minimax-m2.5-awq`

> For a broader comparison of multi-node serving frameworks, see [Multi-Node LLM Serving: Architecture, Frameworks & Best Practices]({% post_url 2026-06-12-Multi-Node-LLM-Serving-Architecture,-Frameworks-and-Best-Practices-(LLM-Generated) %}).

```
┌─────────────────┐     ┌─────────────────┐
│  Head Node       │     │  Worker Node     │
│  192.168.1.10    │◄───►│  192.168.1.11    │
│  Ray Head + vLLM │     │  Ray Worker      │
│  8× GPU          │     │  8× GPU          │
└─────────────────┘     └─────────────────┘
```

## 完整部署

### 脚本准备

1. 创建脚本目录

    `mkdir -p /data/vllm_scripts && cd /data/vllm_scripts`

2. Ray Head 启动脚本 `start_ray_head.sh`

```bash
#!/bin/bash
set -e

export VLLM_HOST_IP=192.168.1.10

echo "=== 启动Ray Head节点 ==="
ray start --head \
  --node-ip-address=192.168.1.10 \
  --port=6379 \
  --dashboard-host=0.0.0.0 \
  --num-gpus=8 \
  --num-cpus=128

# 轮询等待2个Active节点
MAX_WAIT=100
COUNT=0
TARGET_NODE=2
echo "=== 等待Worker节点接入集群 ==="
while [ $COUNT -lt $MAX_WAIT ]; do
  NODE_COUNT=$(ray status 2>/dev/null | grep -A 10 "Active:" | grep "node_" | wc -l)
  if [ "${NODE_COUNT}" -eq "${TARGET_NODE}" ]; then
    echo "✅ Worker已上线，节点总数：${NODE_COUNT}"
    break
  fi
  COUNT=$((COUNT+1))
  echo "⏳ 当前节点数: ${NODE_COUNT}, 等待进度${COUNT}/${MAX_WAIT}"
  sleep 3
done

if [ $COUNT -ge $MAX_WAIT ]; then
  echo "❌ 等待超时，Worker未接入，终止启动"
  exit 1
fi

echo "=== 启动vLLM OpenAI服务 ==="
python -m vllm.entrypoints.openai.api_server \
  --model /data/models/minimax-m2.5-awq \
  --tensor-parallel-size 16 \
  --pipeline-parallel-size 1 \
  --host 0.0.0.0 \
  --port 8000 \
  --gpu-memory-utilization 0.95 \
  --max-model-len 196608 \
  --distributed-executor-backend ray \
  --enforce-eager > /tmp/vllm_run.log 2>&1 &

# 等待vLLM服务就绪
echo "=== 等待vLLM服务启动 ==="
VLLM_WAIT=0
VLLM_MAX_WAIT=60
while [ $VLLM_WAIT -lt $VLLM_MAX_WAIT ]; do
  if curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
    echo "✅ vLLM服务已就绪"
    break
  fi
  VLLM_WAIT=$((VLLM_WAIT+1))
  echo "⏳ vLLM启动中... ${VLLM_WAIT}/${VLLM_MAX_WAIT}"
  sleep 5
done

if [ $VLLM_WAIT -ge $VLLM_MAX_WAIT ]; then
  echo "❌ vLLM服务启动超时，请检查日志: /tmp/vllm_run.log"
  exit 1
fi

echo "=== 所有服务启动完成，容器持续运行 ==="
tail -f /dev/null
```

3. Ray Worker 启动脚本 `start_ray_worker.sh`

```bash
#!/bin/bash
set -e

export VLLM_HOST_IP=192.168.1.11

echo "=== 等待Head节点Ray服务 ==="
HEAD_WAIT=0
HEAD_MAX_WAIT=30
while [ $HEAD_WAIT -lt $HEAD_MAX_WAIT ]; do
  if ray status --address=192.168.1.10:6379 > /dev/null 2>&1; then
    echo "✅ Head节点Ray服务已就绪"
    break
  fi
  HEAD_WAIT=$((HEAD_WAIT+1))
  echo "⏳ 等待Head节点... ${HEAD_WAIT}/${HEAD_MAX_WAIT}"
  sleep 3
done

if [ $HEAD_WAIT -ge $HEAD_MAX_WAIT ]; then
  echo "❌ Head节点Ray服务未就绪，终止启动"
  exit 1
fi

echo "=== Worker节点连接Ray集群 ==="
ray start --address=192.168.1.10:6379 \
  --node-ip-address=192.168.1.11 \
  --num-gpus=8 \
  --num-cpus=128

echo "=== 验证Worker节点状态 ==="
ray status

echo "=== Ray Worker就绪，进入常驻状态 ==="
tail -f /dev/null
```

4. 赋予脚本执行权限

    `chmod +x /data/vllm_scripts/*.sh`

### 节点容器启动命令

1. Ray Worker 节点（必须优先启动）

```bash
docker run -d \
  --name vllm-ray-worker \
  --privileged --net=host --shm-size=64g \
  -v /data/models:/data/models \
  -v /data/vllm_scripts:/opt/scripts \
  -v /etc/localtime:/etc/localtime \
  -e HF_DATASETS_OFFLINE=1 \
  -e TRANSFORMERS_OFFLINE=1 \
  -e HF_HUB_OFFLINE=1 \
  -e HF_HUB_DISABLE_TELEMETRY=1 \
  -e HF_HUB_LOCAL_FILES_ONLY=1 \
  -e VLLM_NO_USAGE_STATS=1 \
  -e VLLM_DISABLE_UPDATES=1 \
  vllm/vllm-openai \
  /opt/scripts/start_ray_worker.sh
```

2. Ray Head 节点（自动等待 Worker 再启 vLLM）

```bash
docker run -d \
  --name vllm-ray-head \
  --privileged --net=host --shm-size=64g \
  -v /data/models:/data/models \
  -v /data/vllm_scripts:/opt/scripts \
  -v /etc/localtime:/etc/localtime \
  -e HF_DATASETS_OFFLINE=1 \
  -e TRANSFORMERS_OFFLINE=1 \
  -e HF_HUB_OFFLINE=1 \
  -e HF_HUB_DISABLE_TELEMETRY=1 \
  -e HF_HUB_LOCAL_FILES_ONLY=1 \
  -e VLLM_NO_USAGE_STATS=1 \
  -e VLLM_DISABLE_UPDATES=1 \
  vllm/vllm-openai \
  /opt/scripts/start_ray_head.sh
```

## 配置详解

### 显存与 Token 最大化

`--gpu-memory-utilization 0.95` 极限榨取显存，搭配 `196608` 模型原生最大上下文；若出现 OOM，下调至 0.90 稳定生产。

### 离线保障

容器环境变量（`HF_HUB_OFFLINE=1` 等）多重锁死，完全不会访问 huggingface 外网。

### 常驻原理

Worker 用 `tail -f /dev/null` 保活 Ray 进程；Head 同方式保活，vLLM 后台异步运行不阻塞常驻 PID1。

### 通信兼容

NCCL/GLOO 双通信网卡绑定，解决跨节点多卡张量并行通信超时问题。

### Ray 适配修复

脚本改用统计 node_ 行数判断节点数，兼容无 Total Nodes 输出的 Ray 新版本。

## 运维

### 查看集群状态

```bash
docker exec vllm-ray-head ray status
```

Active 列表出现 2 个 node_id、资源总量 16GPU 即集群正常。

### 查看日志

```bash
# Head 完整启动日志
docker logs -f vllm-ray-head
# Worker Ray 日志
docker logs -f vllm-ray-worker
# vLLM 推理实时日志
docker exec -it vllm-ray-head tail -f /tmp/vllm_run.log
```

### 启停命令

```bash
# 停止容器服务
docker stop vllm-ray-head vllm-ray-worker
# 彻底删除容器重建
docker rm -f vllm-ray-head vllm-ray-worker
```

### 手动调试

```bash
docker exec -it vllm-ray-head bash
docker exec -it vllm-ray-worker bash
```

## Reference

### 端口

| 端口 | 用途 |
|------|------|
| 6379 | Ray 集群通信 |
| 8000 | vLLM OpenAI API |
| 8265 | Ray Dashboard |

### 关键参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `--tensor-parallel-size` | 16 | 张量并行度（双 8 卡） |
| `--pipeline-parallel-size` | 1 | 流水线并行度 |
| `--gpu-memory-utilization` | 0.95 | GPU 显存使用率 |
| `--max-model-len` | 196608 | 最大上下文长度 |
| `--distributed-executor-backend` | ray | 分布式执行后端 |

### 路径

| 路径 | 说明 |
|------|------|
| `/data/models/minimax-m2.5-awq` | 模型文件 |
| `/data/vllm_scripts` | 启动脚本 |
| `/tmp/vllm_run.log` | vLLM 运行日志 |

## Todo

- 采用 `.env` 存储环境变量、常量
- 增加容器管理 sh，控制检测、启、停容器
- `vllm port 8001`
