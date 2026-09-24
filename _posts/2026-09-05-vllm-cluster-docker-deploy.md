---

layout: post
title: '从零搭建 vLLM 多节点推理集群：Docker 部署全流程实战'
summary: '手把手教你用 Docker + Ray + vLLM 在多节点 GPU 集群上部署 70B+ 大模型推理服务，覆盖在线/离线安装、模型选型、性能调优与生产运维。'
lang: zh-CN
date: 2026-09-05 08:28:00
categories:
- AI & LLM
tags:
- vLLM
- LLM
- Docker
- GPU集群
- 大模型部署
- Qwen
- Ray
- 分布式推理
---
## 写在前面

当模型参数量突破 70B，单张 A100 80GB 已经无法装下整个模型。你需要一个**多节点 GPU 集群**，配合高效的分布式推理框架，才能让这些巨型模型真正跑起来。

<!--more-->


本文记录了我在生产环境中使用 **Docker + Ray + vLLM** 搭建多节点推理集群的完整过程。从环境准备到 API 服务上线，覆盖在线/离线两种安装方式，并附上性能调优和故障排查经验。

**你将学到：**
- 如何在多台 GPU 服务器上部署 vLLM 推理集群
- Ray 分布式调度的配置方法
- 张量并行（TP）+ 流水线并行（PP）的实践调优
- 生产环境的安全加固与监控方案

---

## 架构概览

先看一下整体架构：

```
┌─────────────────────────────────────────────────────────────┐
│                      Client (OpenAI API)                    │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP :8000
┌─────────────────────────────▼───────────────────────────────┐
│                   vLLM OpenAI Server                        │
│              (Docker + vllm-openai:latest)                   │
├─────────────────────────────────────────────────────────────┤
│                   Ray Head Node (node1)                      │
│            Ray Dashboard :8265 | Ray GCS :6379              │
├─────────────────────────────────────────────────────────────┤
│    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│    │ GPU 0    │  │ GPU 1    │  │ GPU 2    │  │ GPU 3    │  │
│    │ TP shard │  │ TP shard │  │ TP shard │  │ TP shard │  │
│    └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────┤
│                   Ray Worker Node (node2)                    │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│    │ GPU 4    │  │ GPU 5    │  │ GPU 6    │  │ GPU 7    │  │
│    │ TP shard │  │ TP shard │  │ TP shard │  │ TP shard │  │
│    └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
├─────────────────────────────────────────────────────────────┤
│              NFS Shared Storage (/mnt/models)                │
│         Qwen2-72B-Instruct │ MiniMax-M2.5-AWQ              │
└─────────────────────────────────────────────────────────────┘
```

**关键组件说明：**

| 组件 | 作用 | 为什么选它 |
|------|------|-----------|
| **vLLM** | LLM 推理引擎 | PagedAttention 技术，吞吐量比 HuggingFace 高 14-24 倍 |
| **Ray** | 分布式任务调度 | 原生支持多节点 GPU 资源管理，vLLM 官方推荐 |
| **Docker** | 容器化部署 | 环境隔离，一键迁移，版本管理 |
| **NFS** | 共享存储 | 多节点访问同一份模型文件，节省存储空间 |
| **NCCL** | GPU 通信库 | NVIDIA 官方多卡通信方案，性能最优 |

---

## 第一部分：环境要求

在开始之前，确认你的硬件和软件满足以下条件：

| 类别 | 最低要求 | 推荐配置 | 说明 |
|------|----------|----------|------|
| **GPU** | NVIDIA GPU (显存 ≥ 24GB) | A100 80GB / H100 80GB | 70B 模型至少需要 8×A100 80GB |
| **NVIDIA 驱动** | ≥ 550 | 550.120+ | 驱动版本决定 CUDA 兼容性 |
| **CUDA** | 12.1 | 12.4 | vLLM 0.6+ 要求 CUDA 12.x |
| **Docker** | ≥ 24.0 | 24.0+ | 需要支持 `--gpus` 参数 |
| **nvidia-container-toolkit** | ≥ 1.14 | 最新稳定版 | 容器内访问 GPU 的桥梁 |
| **NCCL** | ≥ 2.18 | 2.20+ | 多卡通信核心 |
| **Ray** | ≥ 2.20 | 2.40+ | 分布式调度框架 |
| **Python** | ≥ 3.9 | 3.10 / 3.12 | Ray 和 vLLM 的运行环境 |
| **网络** | 10GbE | 同网段直连 | NCCL 通信对延迟敏感 |
| **存储** | NFS 共享 | SSD 高速存储 | 模型加载速度影响首 token 延迟 |

> **选卡建议：** 如果预算有限，4×A100 40GB + 量化模型（AWQ/GPTQ）也是可行方案。FP16 的 70B 模型约需 140GB 显存，AWQ 4bit 量化后约 35GB。

---

## 第二部分：基础软件安装（在线环境）

> 以下操作需在**所有节点**上执行，除非特别标注。

### 2.1 系统预处理

```bash
# 关闭防火墙（生产环境请评估安全风险）
systemctl stop firewalld && systemctl disable firewalld
systemctl stop nftables && systemctl disable nftables

# 关闭 Swap（GPU 推理对内存延迟敏感）
swapoff -a
sed -i '/\sswap\s/d' /etc/fstab

# 内核参数优化
cat > /etc/sysctl.d/99-vllm.conf << 'EOF'
net.ipv4.ip_forward = 1
net.core.somaxconn = 65535
net.ipv4.tcp_syncookies = 1
vm.swappiness = 0
EOF
sysctl -p /etc/sysctl.d/99-vllm.conf
```

**为什么关闭 Swap？** GPU 推理过程中，CPU 需要快速处理 KV Cache 的调度逻辑。如果系统使用 Swap，会导致内存页频繁换入换出，显著增加推理延迟。

### 2.2 NVIDIA 驱动 + CUDA

```bash
# 安装驱动（根据实际文件名修改）
bash NVIDIA-Linux-x86_64-550.120.run -no-x-check -no-nouveau -no-opengl-files

# 安装 CUDA 12.4
rpm -ivh cuda-repo-rhel10-12.4.0-1.x86_64.rpm
yum install -y cuda

# 配置环境变量
cat > /etc/profile.d/cuda.sh << 'EOF'
export PATH=/usr/local/cuda-12.4/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12.4/lib64:$LD_LIBRARY_PATH
EOF
source /etc/profile.d/cuda.sh

# 验证安装
nvidia-smi        # 查看 GPU 列表和驱动版本
nvcc -V           # 查看 CUDA 编译器版本
```

> **版本匹配很重要：** 驱动 550 对应 CUDA 12.4，不要混用不同大版本的驱动和 CUDA，否则会出现 `CUDA driver version is insufficient` 错误。

### 2.3 Docker + NVIDIA Container Toolkit

```bash
# 安装 Docker
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install -y docker-ce docker-ce-cli containerd.io
systemctl enable docker && systemctl start docker

# 安装 nvidia-container-toolkit
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.repo | \
  tee /etc/yum.repos.d/nvidia-container-toolkit.repo
yum install -y nvidia-container-toolkit

# 配置 Docker 使用 NVIDIA 运行时
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker

# 验证：容器内能看到 GPU
docker run --rm --gpus all nvidia/cuda:12.4-base nvidia-smi
```

**原理说明：** nvidia-container-toolkit 在 Docker 层面注入了 NVIDIA 驱动库，让容器内的进程可以透明访问宿主机 GPU。它不是在容器里装驱动，而是把宿主机的驱动"映射"进去。

### 2.4 NCCL + Ray

```bash
# 安装 NCCL（多卡通信库）
yum install -y libnccl-devel libnccl2

# 安装 Ray（分布式调度框架）
pip install ray[default]==2.40.0

# 配置 SSH 免密登录（所有节点互做）
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
ssh-copy-id root@node1
ssh-copy-id root@node2
```

> **为什么需要 Ray？** vLLM 本身只处理单机多卡的张量并行。要实现跨节点的流水线并行，需要 Ray 来协调多个节点上的 vLLM worker 进程。

---

## 第三部分：基础软件安装（离线环境）

> 生产环境往往无法访问外网。以下是在离线环境下安装全部依赖的步骤。

### 3.1 离线资源包清单

在有网的机器上提前下载以下资源：

| 资源 | 文件/包名 | 用途 |
|------|-----------|------|
| NVIDIA 驱动 | `NVIDIA-Linux-x86_64-550.120.run` | GPU 驱动 |
| CUDA 12.4 | `cuda_12.4.0_550.54.15_linux.run` | CUDA 工具链 |
| Docker CE | `docker-ce`、`docker-ce-cli`、`containerd.io` rpm | 容器运行时 |
| nvidia-container-toolkit | rpm 离线包 | 容器 GPU 支持 |
| NCCL 2.20 | rpm 离线包 | 多卡通信 |
| Python 3.12 | 离线安装包 + pip whl 包 | 运行环境 |
| Ray 2.40 | `ray[default]` whl 包 | 分布式调度 |
| vLLM 镜像 | `vllm-openai.tar` | 推理引擎 |
| 模型文件 | 完整模型目录 | 待部署模型 |
| NFS | `nfs-utils` rpm 包 | 共享存储 |

### 3.2 镜像导出与导入

```bash
# 在有网机器上导出镜像
docker pull vllm/vllm-openai:latest
docker save -o vllm-openai.tar vllm/vllm-openai:latest

# 传输到离线节点后导入
docker load -i vllm-openai.tar
```

### 3.3 Ray 离线安装

vLLM 官方镜像不含 Ray，需要额外安装：

```bash
# 在有网机器上下载 whl 包
mkdir ray_offline_pkgs && cd ray_offline_pkgs
pip download \
  --python-version 312 \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  "ray[default]==2.40.0"

# 在离线节点的容器内安装
docker run --rm \
  -v ./ray_offline_pkgs:/whls \
  -it vllm/vllm-openai:latest \
  pip install --no-index --find-links=/whls "ray[default]==2.40.0"
```

> **提示：** 如果需要持久化安装结果，可以基于原镜像构建自定义镜像：
> ```bash
> docker commit <container_id> my-vllm-with-ray:latest
> ```

### 3.4 完整离线安装步骤

```bash
# 1. NVIDIA 驱动
bash NVIDIA-Linux-x86_64-550.120.run -no-x-check -no-nouveau -no-opengl-files

# 2. CUDA（静默安装）
bash cuda_12.4.0_550.54.15_linux.run --silent --toolkit

# 3. Docker
rpm -ivh containerd.io-*.rpm docker-ce-*.rpm docker-ce-cli-*.rpm
systemctl enable docker && systemctl start docker

# 4. nvidia-container-toolkit
rpm -ivh nvidia-container-toolkit-*.rpm nvidia-container-runtime-*.rpm
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker

# 5. 导入 vLLM 镜像
docker load -i vllm-openai.tar

# 6. Python + Ray
tar -xzf python-3.12.12-linux-x86_64.tar.gz
./python-3.12.12/bin/pip install --no-index --find-links=./whls "ray[default]==2.40.0"
```

---

## 第四部分：共享存储配置

多节点集群需要所有节点访问同一份模型文件。NFS 是最简单直接的方案。

### 4.1 架构

```
node1 (NFS Server)              node2 (NFS Client)
/mnt/models/        ◄──────►    /mnt/models/
  ├── Qwen2-72B-Instruct/        (挂载自 node1)
  └── MiniMax-M2.5-AWQ/
```

### 4.2 主节点配置（NFS Server）

```bash
yum install -y nfs-utils

# 创建共享目录
mkdir -p /mnt/models

# 配置导出规则
# *(rw,sync,no_subtree_check,no_root_squash)
#   │   │     │               │
#   │   │     │               └─ 允许远程 root 以 root 权限访问（容器内通常是 root）
#   │   │     └─ 不检查子目录（提升性能）
#   │   └─ 同步写入（数据安全优先）
#   └─ 所有 IP 可访问（生产环境建议限制 IP 段）
echo "/mnt/models *(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports
exportfs -ra

systemctl enable nfs && systemctl start nfs
```

> **安全建议：** 生产环境应将 `*` 替换为具体 IP 段，如 `192.168.10.0/24`。注意 `no_root_squash` 会赋予远程 root 用户完全权限，仅在容器以 root 运行且必须写入时使用；一般场景建议改为 `root_squash`。

### 4.3 从节点配置（NFS Client）

```bash
yum install -y nfs-utils

mkdir -p /mnt/models

# 挂载（替换为实际 node1 IP）
mount -t nfs 192.168.10.10:/mnt/models /mnt/models

# 开机自动挂载
echo "192.168.10.10:/mnt/models /mnt/models nfs defaults,_netdev 0 0" >> /etc/fstab
```

### 4.4 验证

```bash
# node1：创建测试文件
echo "NFS test" > /mnt/models/test.txt

# node2：检查是否可见
cat /mnt/models/test.txt
# 输出: NFS test
```

---

## 第五部分：模型准备

### 5.1 模型选型指南

选择模型时需要考虑三个因素：**显存容量**、**推理速度**、**任务类型**。

| 模型 | 参数量 | FP16 显存 | AWQ 4bit 显存 | 推荐场景 |
|------|--------|-----------|---------------|----------|
| Qwen2-72B-Instruct | 72B | ~144GB | ~36GB | 中文对话、代码生成 |
| Llama-3.1-70B-Instruct | 70B | ~140GB | ~35GB | 英文通用任务 |
| MiniMax-M2.5-AWQ | MoE (456B) | ~200GB+ | ~50GB | 长文本、工具调用 |
| Qwen2-7B-Instruct | 7B | ~14GB | ~4GB | 轻量部署、测试 |

> **量化选择：** 如果显存紧张，优先选择 AWQ 量化版本。AWQ（Activation-aware Weight Quantization）相比 GPTQ 在推理速度和精度上都有优势，是 vLLM 推荐的量化方案。

### 5.2 模型下载

```bash
# 方式一：huggingface-cli（推荐）
pip install huggingface_hub
huggingface-cli download Qwen/Qwen2-72B-Instruct \
  --local-dir /mnt/models/Qwen2-72B-Instruct

# 方式二：私有模型需要 Token
export HF_TOKEN="your-hf-token"
huggingface-cli download meta-llama/Llama-3.1-70B-Instruct \
  --token $HF_TOKEN \
  --local-dir /mnt/models/Llama-3.1-70B-Instruct

# 方式三：国内镜像（速度更快）
pip install modelscope
modelscope download --model Qwen/Qwen2-72B-Instruct \
  --local_dir /mnt/models/Qwen2-72B-Instruct
```

### 5.3 模型目录结构

确保模型文件完整，目录结构如下：

```
/mnt/models/Qwen2-72B-Instruct/
├── config.json              # 模型配置
├── tokenizer.json           # 分词器
├── tokenizer_config.json    # 分词器配置
├── generation_config.json   # 生成配置
├── model-00001-of-00004.safetensors  # 模型权重分片
├── model-00002-of-00004.safetensors
├── model-00003-of-00004.safetensors
└── model-00004-of-00004.safetensors
```

> **常见错误：** 如果缺少 `tokenizer.json`，vLLM 会尝试从 `config.json` 中的 `auto_map` 字段加载，但某些模型可能不支持。建议确保 tokenizer 文件完整。

---

## 第六部分：多节点 vLLM 部署

这是整个流程的核心部分。

### 6.1 环境变量配置（所有节点）

```bash
cat >> ~/.bashrc << 'EOF'
# NCCL 优化（无 InfiniBand 网卡环境）
export NCCL_IB_DISABLE=1           # 禁用 IB，走 TCP
export NCCL_SOCKET_IFNAME=eth0     # 指定通信网卡
export GLOO_SOCKET_IFNAME=eth0     # Ray GLOO 后端也走 eth0
export NCCL_DEBUG=WARN              # 调试时可改为 INFO

# vLLM 分布式后端
export VLLM_DISTRIBUTED_BACKEND=nccl

# HuggingFace Token（用于下载私有模型）
export HF_TOKEN="your-hf-token"
EOF
source ~/.bashrc
```

**参数详解：**

| 变量 | 说明 |
|------|------|
| `NCCL_IB_DISABLE=1` | 禁用 InfiniBand，改用 TCP Socket 通信。大多数以太网环境必须设置 |
| `NCCL_SOCKET_IFNAME=eth0` | 指定 NCCL 使用哪个网卡通信，避免走错网卡 |
| `GLOO_SOCKET_IFNAME=eth0` | Ray 的 GLOO 后端也需要指定网卡 |
| `NCCL_DEBUG=WARN` | 设置为 INFO 可看到详细的 NCCL 通信日志，排查问题时很有用 |
| `VLLM_DISTRIBUTED_BACKEND=nccl` | 指定 vLLM 使用 NCCL 作为分布式通信后端 |

### 6.2 拉取镜像（所有节点）

```bash
docker pull vllm/vllm-openai:latest
```

> **重要：** 所有节点必须使用**完全相同版本**的镜像，否则可能导致 NCCL 通信不兼容。

### 6.3 启动 Ray 集群

**头节点（node1，IP: 192.168.10.10）：**

```bash
ray start --head --port=6379 --dashboard-host=0.0.0.0
```

**工作节点（node2，IP: 192.168.10.11）：**

```bash
ray start --address=192.168.10.10:6379
```

**验证集群状态：**

```bash
ray status
```

输出应类似：

```
======== Resources ========
Total GPU: 8
Total object store memory: 10.74 GiB
```

如果只看到 4 张 GPU，说明工作节点没有正确加入。检查：
1. SSH 免密是否配置
2. Ray 版本是否一致
3. 端口 6379 是否可达

### 6.4 启动 vLLM 服务

在**头节点**执行：

```bash
docker run -d \
  --name vllm-service \
  --runtime nvidia \
  --gpus all \
  -v /mnt/models:/mnt/models \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  --env "HF_TOKEN=$HF_TOKEN" \
  --env "NCCL_IB_DISABLE=1" \
  --env "NCCL_SOCKET_IFNAME=eth0" \
  --env "GLOO_SOCKET_IFNAME=eth0" \
  -p 8000:8000 \
  --ipc=host \
  --restart unless-stopped \
  vllm/vllm-openai:latest \
  --model /mnt/models/Qwen2-72B-Instruct \
  --served-model-name Qwen2-72B \
  --tensor-parallel-size 4 \
  --pipeline-parallel-size 2 \
  --gpu-memory-utilization 0.9 \
  --max-model-len 16384 \
  --max-num-seqs 32 \
  --enable-chunked-prefill \
  --host 0.0.0.0 \
  --port 8000
```

**核心参数详解：**

| 参数 | 值 | 说明 | 调优建议 |
|------|-----|------|----------|
| `--tensor-parallel-size` | 4 | 张量并行度，模型拆分到 4 张 GPU | 单节点设为 GPU 数，跨节点需配合 PP |
| `--pipeline-parallel-size` | 2 | 流水线并行度，模型拆分到 2 个阶段 | 跨节点时使用，同节点设为 1 |
| `--gpu-memory-utilization` | 0.9 | GPU 显存利用率 | 0.85-0.95，过高易 OOM |
| `--max-model-len` | 16384 | 最大上下文长度 | 根据显存调整，越大 KV 缓存占用越多 |
| `--max-num-seqs` | 32 | 最大并发请求数 | 影响吞吐量，需测试找到最优值 |
| `--enable-chunked-prefill` | - | 分块 Prefill | 长文本场景必开，减少首 token 等待 |
| `--ipc=host` | - | 宿主机 IPC 命名空间 | 多卡通信必需，否则 NCCL 走 socket 更慢 |

> **并行策略选择：**
> - **同节点多卡：** 只用 `--tensor-parallel-size`，设为 GPU 数量
> - **跨节点：** TP + PP 组合。如 8 卡分 2 节点，TP=4, PP=2
> - **超大模型：** TP=8, PP=2（16 卡环境：每 8 卡一组做 TP，2 组做流水线）

### 6.5 验证服务

```bash
# 等待模型加载完成（观察日志）
docker logs -f vllm-service

# 看到以下日志表示启动成功
# INFO:     Uvicorn running on http://0.0.0.0:8000

# 测试 API
curl http://localhost:8000/v1/models
```

---

## 第七部分：单节点部署示例

用于调试或单机多卡场景。以 MiniMax-M2.5-AWQ 为例：

```bash
docker run -d \
  --name vllm-minimax \
  --runtime nvidia \
  --gpus all \
  --ipc=host \
  --ulimit memlock=-1 \
  --ulimit stack=67108864 \
  -p 8000:8000 \
  -v /root/models:/models/MiniMax-M2.5-AWQ:ro \
  -e VLLM_USE_DEEP_GEMM=0 \
  -e VLLM_USE_FLASHINFER_MOE_FP16=1 \
  -e VLLM_USE_FLASHINFER_SAMPLER=0 \
  -e OMP_NUM_THREADS=4 \
  --restart unless-stopped \
  vllm/vllm-openai:latest \
  --model /models/MiniMax-M2.5-AWQ \
  --served-model-name MiniMax-M2.5-AWQ \
  --max-num-seqs 32 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --tensor-parallel-size 8 \
  --enable-expert-parallel \
  --enable-auto-tool-choice \
  --tool-call-parser minimax_m2 \
  --reasoning-parser minimax_m2_append_think \
  --trust-remote-code \
  --host 0.0.0.0 \
  --port 8000 \
  --enable-chunked-prefill \
  -q awq
```

**MoE 模型专用参数说明：**

| 参数 | 说明 |
|------|------|
| `--enable-expert-parallel` | 将 MoE 的专家层分布到多张 GPU，减少单卡显存压力 |
| `--enable-auto-tool-choice` | 启用工具调用（Function Calling）能力 |
| `--tool-call-parser minimax_m2` | 适配 MiniMax-M2 的工具调用格式 |
| `--reasoning-parser minimax_m2_append_think` | 自动处理模型的思考链输出 |
| `-q awq` | 以 AWQ 量化格式加载模型 |

**环境变量说明：**

| 变量 | 说明 |
|------|------|
| `VLLM_USE_DEEP_GEMM=0` | 禁用 DeepGEMM，避免兼容性问题 |
| `VLLM_USE_FLASHINFER_MOE_FP16=1` | 启用 FlashInfer 的 MoE FP16 优化 |
| `VLLM_USE_FLASHINFER_SAMPLER=0` | 禁用 FlashInfer 采样器，使用 vLLM 原生逻辑 |
| `OMP_NUM_THREADS=4` | 限制 CPU 并行线程数，避免抢占资源 |

---

## 第八部分：API 调用示例

vLLM 提供 OpenAI 兼容的 API 接口，可以直接替换 OpenAI SDK 的 `base_url`。

### 8.1 非流式调用

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen2-72B",
    "messages": [
      {"role": "system", "content": "你是一个有帮助的助手。"},
      {"role": "user", "content": "请解释什么是 PagedAttention？"}
    ],
    "max_tokens": 1024,
    "temperature": 0.7,
    "top_p": 0.9
  }'
```

### 8.2 流式调用

```bash
curl -N http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen2-72B",
    "messages": [
      {"role": "user", "content": "写一首关于人工智能的诗"}
    ],
    "max_tokens": 1024,
    "stream": true
  }'
```

### 8.3 Python 调用

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://your-vllm-server:8000/v1",
    api_key="not-needed"  # vLLM 默认不需要 API Key
)

# 非流式
response = client.chat.completions.create(
    model="Qwen2-72B",
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "用 Python 实现快速排序"}
    ],
    max_tokens=1024,
    temperature=0.7
)
print(response.choices[0].message.content)

# 流式
stream = client.chat.completions.create(
    model="Qwen2-72B",
    messages=[{"role": "user", "content": "解释量子计算"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### 8.4 多模型切换

vLLM 支持同时加载多个模型（需足够显存）：

```bash
# 启动时指定多个模型
docker run -d --name vllm-multi \
  --runtime nvidia --gpus all \
  -v /mnt/models:/mnt/models \
  -p 8000:8000 --ipc=host \
  vllm/vllm-openai:latest \
  --model /mnt/models/Qwen2-72B-Instruct /mnt/models/Qwen2-7B-Instruct \
  --served-model-name Qwen2-72B Qwen2-7B \
  --tensor-parallel-size 4 \
  --host 0.0.0.0 --port 8000
```

然后通过 API 的 `model` 参数切换：

```python
# 使用 Qwen2-72B
response = client.chat.completions.create(
    model="Qwen2-72B",
    messages=[...]
)

# 切换到 Qwen2-7B
response = client.chat.completions.create(
    model="Qwen2-7B",
    messages=[...]
)
```

---

## 第九部分：性能调优

### 9.1 吞吐量优化

```bash
# 增大并发数（需要足够显存）
--max-num-seqs 64

# 启用 Prefix Caching（相同前缀的请求复用 KV Cache）
--enable-prefix-caching

# 启用 Chunked Prefill
--enable-chunked-prefill

# 增大 Chunk 大小
--max-num-batched-tokens 16384
```

### 9.2 延迟优化

```bash
# 减小最大上下文长度（减少 KV Cache 分配）
--max-model-len 4096

# 减小 GPU 显存利用率（减少内存分配开销）
--gpu-memory-utilization 0.85

# 使用 AWQ 量化模型（计算量更小）
-q awq
```

### 9.3 关键指标监控

| 指标 | 正常范围 | 异常处理 |
|------|----------|----------|
| GPU 显存使用率 | 85-95% | 低于 80% 可增大并发，高于 95% 需减小 |
| GPU 利用率 | 60-90% | 低于 50% 可能是 CPU 瓶颈或模型加载中 |
| 首 Token 延迟 (TTFT) | < 500ms | 过高可减小 `--max-model-len` |
| 吞吐量 (tokens/s) | 视模型而定 | 通过 `--max-num-seqs` 调整并发 |
| 排队请求 | 0-5 | 持续积压需增加节点或降低请求速率 |

---

## 第十部分：监控与运维

### 10.1 Ray Dashboard

访问 `http://<node1-ip>:8265`，可以看到：
- 集群节点状态和资源使用率
- GPU/CPU/内存实时监控
- 任务调度和执行情况

### 10.2 GPU 监控

```bash
# 实时监控
watch -n 1 nvidia-smi

# 查看 GPU 进程详情
nvidia-smi --query-compute-apps=pid,name,used_memory --format=csv

# 持续记录 GPU 使用情况（每 5 秒）
nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu \
  --format=csv -l 5 > gpu_monitor.log
```

### 10.3 日志管理

```bash
# 查看 vLLM 容器日志
docker logs -f vllm-service

# 查看最近 100 行
docker logs --tail 100 vllm-service

# 导出日志到文件
docker logs vllm-service > vllm.log 2>&1
```

### 10.4 常用运维命令

```bash
# 停止/重启服务
docker stop vllm-service
docker restart vllm-service

# 查看 Ray 集群状态
ray status

# 停止 Ray（工作节点执行）
ray stop

# 强制清理残留进程
ray stop --force

# 清理 Docker 悬空镜像
docker image prune -f
```

---

## 第十一部分：常见问题排查

### 问题 1：`nvidia-smi` 报错

```
NVIDIA-SMI has failed because it couldn't communicate with the NVIDIA driver.
```

**原因：** 驱动未安装或内核模块未加载

**解决：**
```bash
# 检查驱动是否安装
lsmod | grep nvidia

# 如果没有输出，重新加载模块
modprobe nvidia

# 如果仍然不行，重新安装驱动
bash NVIDIA-Linux-x86_64-550.120.run -no-x-check -no-nouveau -no-opengl-files
```

### 问题 2：Docker 容器内无法访问 GPU

```
docker: Error response from daemon: could not select device driver "" with capabilities: [[gpu]].
```

**原因：** nvidia-container-toolkit 未安装或未配置

**解决：**
```bash
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker
```

### 问题 3：NCCL 通信超时

```
RuntimeError: NCCL communicator was aborted on rank 0
```

**原因：** 网络不通或网卡配置错误

**解决：**
```bash
# 检查节点间网络连通性
ping 192.168.10.11

# 检查 NCCL 网卡配置
echo $NCCL_SOCKET_IFNAME

# 调试 NCCL 通信
export NCCL_DEBUG=INFO
```

### 问题 4：模型加载 OOM

```
torch.cuda.OutOfMemoryError: CUDA out of memory
```

**原因：** GPU 显存不足

**解决：**
```bash
# 方案一：增加张量并行度（需要更多可用 GPU）
--tensor-parallel-size 8

# 方案二：减小上下文长度
--max-model-len 4096  # 从 16384 减小

# 方案三：使用量化模型
-q awq  # 加载 AWQ 量化版本
```

### 问题 5：Ray 集群连不上

```
raylet (pid=12345): This node has an IP address of 192.168.10.11, while
the GCS address is 192.168.10.10:6379. This is likely because the
node is behind a NAT.
```

**原因：** SSH 免密未配置或网络不通

**解决：**
```bash
# 配置 SSH 免密
ssh-copy-id root@192.168.10.10
ssh-copy-id root@192.168.10.11

# 检查 Ray 进程
ps aux | grep ray

# 重新启动 Ray
ray stop --force
ray start --head --port=6379
```

### 问题 6：NFS 挂载失败

```
mount.nfs: Connection timed out
```

**原因：** NFS 服务未启动或防火墙拦截

**解决：**
```bash
# 检查 NFS 服务状态
systemctl status nfs

# 检查导出配置
exportfs -v

# 如果是防火墙问题（生产环境请评估安全风险）
systemctl stop firewalld
```

---

## 第十二部分：安全加固

生产环境需要额外的安全措施：

### 12.1 API Key 认证

```bash
# 启用 API Key
docker run -d \
  --name vllm-secure \
  --runtime nvidia --gpus all \
  -v /mnt/models:/mnt/models \
  -e VLLM_API_KEY="your-secret-key" \
  -p 8000:8000 --ipc=host \
  vllm/vllm-openai:latest \
  --model /mnt/models/Qwen2-72B-Instruct \
  --host 0.0.0.0 --port 8000
```

调用时需要携带 API Key：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "Qwen2-72B", "messages": [{"role": "user", "content": "hello"}]}'
```

### 12.2 限制访问 IP

```bash
# 只允许特定 IP 段访问
iptables -A INPUT -p tcp --dport 8000 -s 192.168.10.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP
```

### 12.3 HTTPS 加密

```bash
# 使用 nginx 反向代理 + SSL
# nginx.conf
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    location /v1/ {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

## 第十三部分：最终检查清单

部署前逐项确认：

- [ ] **系统：** 防火墙已关闭（或已配置规则），Swap 已禁用，内核参数已优化
- [ ] **驱动：** NVIDIA 驱动 ≥ 550，CUDA 12.1+ 已安装，`nvidia-smi` 正常
- [ ] **容器：** Docker ≥ 24.0，nvidia-container-toolkit 已安装，`docker run --gpus all` 正常
- [ ] **通信：** NCCL ≥ 2.18，Ray ≥ 2.40，SSH 免密已配置
- [ ] **网络：** 万兆静态 IP，同网段，NCCL 环境变量已设置
- [ ] **存储：** NFS 共享盘已挂载，所有节点模型路径一致
- [ ] **模型：** 模型文件完整，路径正确，HF_TOKEN 已设置
- [ ] **镜像：** 所有节点 vllm-openai 镜像版本一致
- [ ] **Ray：** `ray status` 显示所有节点 GPU 资源正常
- [ ] **服务：** API 可正常调用，响应正确，延迟在可接受范围内

---

## 总结

搭建一个生产级的 vLLM 多节点推理集群，涉及的组件和配置确实不少。但一旦跑通，你就能获得：

- **高吞吐：** PagedAttention + 连续批处理，单节点轻松达到数百 tokens/s
- **低延迟：** 分块 Prefill + Prefix Caching，首 token 延迟控制在毫秒级
- **高可用：** Docker 容器化 + Ray 分布式调度，支持滚动更新和故障恢复
- **易扩展：** 新增节点只需加入 Ray 集群，无需修改代码

**后续优化方向：**
- 使用 TensorRT-LLM 替代 vLLM 获得更高性能（但灵活性降低）
- 部署 Prometheus + Grafana 实现精细化监控
- 使用 Kubernetes + Ray Operator 实现自动化运维
- 探索 FP8 量化在 H100 上的性能收益

---

## 参考资料

- [vLLM 官方文档](https://docs.vllm.ai/)
- [Ray 分布式计算框架](https://docs.ray.io/)
- [NVIDIA NCCL 文档](https://docs.nvidia.com/deeplearning/nccl/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
