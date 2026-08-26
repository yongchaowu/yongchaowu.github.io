---
layout: post
title: "Multi-Node LLM Serving-vLLM+Ray(Docker)"
date: 2026-06-12 22:04:00
categories: ["Multi"]
tags: ["Multi", "LLM", "Model", "Agent"]
---

vLLM+Ray(Docker) 双节点离线一键部署完整方案

<!--more-->
适配：vllm/vllm-openai镜像、离线禁 HF 联网、双 8 卡 = 16 张量并行、MiniMax-M2.5-AWQ、脚本挂载启动、自动等待 Worker 就绪再拉起 vLLM

## 环境预设

- Head 节点 IP：`192.168.1.10`
- Worker 节点 IP：`192.168.1.11`
- 宿主机模型路径：`/data/models/minimax-m2.5-awq`
- 宿主机脚本目录：`/data/vllm_scripts`
- 网卡名称替换为你实际网卡（示例ens160）
- Ray 端口：`6379`；vLLM 服务端口：`8000`；Ray Dashboard：`8265`

## 两台宿主机统一准备脚本文件

1. 创建脚本目录

    `mkdir -p /data/vllm_scripts && cd /data/vllm_scripts`

2. Ray Head 启动脚本 `start_ray_head.sh`

```bash
#!/bin/bash
set -e

# 基础环境变量
export VLLM_HOST_IP=192.168.1.10
#export NCCL_SOCKET_IFNAME=ens160
#export GLOO_SOCKET_IFNAME=ens160

# 启动Ray Head
echo "=== 启动Ray Head节点 ==="
ray start --head \
  --node-ip-address=192.168.1.10 \
  --port=6379 \
  --dashboard-host=0.0.0.0 \
  --num-gpus=8 \
  --num-cpus=128

# 轮询等待2个Active节点（适配新版ray status无Total Nodes行）
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

# 等待超时退出
if [ $COUNT -ge $MAX_WAIT ]; then
  echo "❌ 等待超时，Worker未接入，终止启动"
  exit 1
fi

# 后台启动vLLM离线推理服务
# 注：也可使用 `vllm serve` 简写命令启动，等价于下面 python -m 方式
echo "=== 启动vLLM OpenAI服务 ==="
python -m vllm.entrypoints.openai.api_server \
  --model /data/models/minimax-m2.5-awq \
  --local-files-only \
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

# 容器常驻不退出
echo "=== 所有服务启动完成，容器持续运行 ==="
tail -f /dev/null
```

3. Ray Worker 启动脚本 `start_ray_worker.sh`

```bash
#!/bin/bash
set -e

# 基础环境变量
export VLLM_HOST_IP=192.168.1.11
#export NCCL_SOCKET_IFNAME=ens160
#export GLOO_SOCKET_IFNAME=ens160

# 等待Head节点Ray服务就绪
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

# 接入Head Ray集群
echo "=== Worker节点连接Ray集群 ==="
ray start --address=192.168.1.10:6379 \
  --node-ip-address=192.168.1.11 \
  --num-gpus=8 \
  --num-cpus=128

# 验证Worker已加入集群
echo "=== 验证Worker节点状态 ==="
ray status

# 容器常驻，持续保活Ray Worker进程
echo "=== Ray Worker就绪，进入常驻状态 ==="
tail -f /dev/null
```

4. 赋予脚本执行权限
    `chmod +x /data/vllm_scripts/*.sh`


## 节点容器启动命令（一键拉起）

1. Ray Worker 节点 先执行（必须优先启动）

```bash
# Ray Worker 节点（必须优先启动）
docker run -d \
  --name vllm-ray-worker \
  --privileged \
  --net=host \
  --shm-size=64g \
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

```bash
# Ray Head 节点（自动等待 Worker 再启 vLLM）
docker run -d \
  --name vllm-ray-head \
  --privileged \
  --net=host \
  --shm-size=64g \
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

## 校验 & 运维操作集

1. 查看 Ray 集群状态

```shell
# Head容器内查看双节点
docker exec vllm-ray-head ray status
```

Active 列表出现 2 个 node_id、资源总量 16GPU 即集群正常。


2. 查看启动全流程日志

```shell
# Head完整启动日志（Ray+等待+vLLM启动）
docker logs -f vllm-ray-head
# Worker Ray日志
docker logs -f vllm-ray-worker
```

3. 查看 vLLM 推理实时日志

`docker exec -it vllm-ray-head tail -f /tmp/vllm_run.log`

4. 接口测试验证服务

```shell
curl http://192.168.1.10:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
"model":"minimax-m2.5-awq",
"messages":[{"role":"user","content":"测试多节点长上下文推理"}]
}'

curl http://192.168.1.10:8000/v1/models

```

5. 启停销毁命令

```shell
# 停止容器服务
docker stop vllm-ray-head vllm-ray-worker
# 彻底删除容器重建
docker rm -f vllm-ray-head vllm-ray-worker
```

6. 手动进入容器调试

```shell
# Head进入交互终端
docker exec -it vllm-ray-head bash
# Worker进入交互终端
docker exec -it vllm-ray-worker bash

```

## 关键配置说明

1. 显存与 Token 最大化
`--gpu-memory-utilization 0.95` 极限榨取显存，搭配`196608`模型原生最大上下文；若出现 OOM，下调至 0.90 稳定生产。

2. 离线保障
容器环境变量 + vLLM `--local-files-only` 双重锁死，完全不会访问 huggingface 外网。

3. 常驻原理
Worker 用`tail -f /dev/null`保活 Ray 进程；Head 同方式保活，vLLM 后台异步运行不阻塞常驻 PID1。

4. 通信兼容
NCCL/GLOO 双通信网卡绑定，解决跨节点多卡张量并行通信超时问题。

5. Ray 适配修复
脚本改用统计node_行数判断节点数，兼容无Total Nodes输出的 Ray 新版本。

## Todo

- 采用`.env`存储环境变量、常量
- 增加容器管理sh，控制检测、启、停容器
- `vllm port 8001`