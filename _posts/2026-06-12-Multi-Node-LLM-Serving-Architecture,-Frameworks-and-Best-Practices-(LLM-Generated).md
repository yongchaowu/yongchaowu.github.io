---
layout: post
title: 'Node LLM Serving: Architecture, Frameworks & Best Practices'
date: 2026-06-12 21:13:00
categories:
- AI & LLM
tags:
- Multi
- Model
- LLM
content_origin: ai-assisted
---

{% raw %}
**Use MiMo Code to modify the whole content with MiMo-v2.5.**

<!--more-->
---

## 10 分钟快速部署

如果你已经有一个 2 节点 × 8 GPU 的集群，只需三步即可启动 70B 模型服务：

```bash
# ① 所有节点：安装依赖
pip install vllm ray

# ② 头节点：启动 Ray 集群
ray start --head --port=6379
# 其他节点：ray start --address='10.0.0.1:6379'

# ③ 头节点：启动模型服务
vllm serve meta-llama/Meta-Llama-3-70B-Instruct \
  --tensor-parallel-size 8 \
  --pipeline-parallel-size 2 \
  --max-model-len 8192
```

验证：`curl http://localhost:8000/v1/models` 返回模型信息即成功。

> **注意事项**：确保节点间 NCCL 网络可达（`export NCCL_DEBUG=INFO` 查看），且模型权重在所有节点的同一路径下可访问。详细配置见下文。

---

## 为什么需要多节点部署？

在集群上多节点部署大模型，通常出于两个核心需求：

- **模型太大，单卡装不下** —— 70B+ 参数的模型需要数百GB显存，单节点8卡也放不下
- **需要更高吞吐** —— 生产环境需要同时服务大量并发请求

先看一组数字，直观感受不同规模模型的显存需求：

| 模型规模 | 参数量 | FP16显存（推理） | 最少GPU（A100 80G） | 典型模型 |
|---------|-------|----------------|-------------------|---------|
| 小 | 7B | ~14 GB | 1 | Llama-2-7B, Qwen2-7B |
| 中 | 13B | ~26 GB | 1 | Llama-2-13B, Qwen1.5-14B |
| 大 | 70B | ~140 GB | 2 | Llama-3-70B, Qwen2-72B |
| 超大 | 405B | ~810 GB | 16 | Llama-3.1-405B |

> 显存估算公式：**参数量(B) × 每参数字节数 × 1.2（开销系数）**。FP16 下每参数 2 字节，INT4 量化后约 0.5 字节。1.2 倍系数覆盖了 KV Cache 和激活值的额外开销。

除了单卡装不下，推理场景本身也有吞吐压力。以在线客服为例，假设日均 100 万次对话请求，每次平均 500 token 输出，就是 500B token/天——折合约 580万 tokens/秒 的平均吞吐需求。单节点很难撑住这样的流量。

部署的核心是利用**模型并行**（张量并行、流水线并行）把模型切分到多个GPU，跨节点协同推理。

**多节点部署的本质是把通信和分片做好。** 选对并行策略、配好网络后，剩下的就是启动分布式框架，让它像单机一样服务。

---

## 一、并行策略选择

### 1.1 张量并行（Tensor Parallelism, TP）

把单层矩阵乘法切分到多卡，通信量大，适合**节点内高速NVLink**。

**通信模式**：每一层计算完成后，所有参与 TP 的 GPU 需要执行一次 **AllReduce** 同步结果。对于一个 Transformer 层，每个 TP 步骤通常需要 2 次 AllReduce（前向）+ 2 次（反向，推理时只有前向）。NVLink 的双向带宽通常在 300-900 GB/s（取决于 GPU 型号），能有效支撑这种高频通信。

**适用原则**：TP 度数尽量不超过单节点 GPU 数量。跨节点做 TP 会因网络带宽不足导致严重的性能下降。

### 1.2 流水线并行（Pipeline Parallelism, PP）

按层切分，不同层放不同设备，通信量小，适合**跨节点**。

**通信模式**：相邻 stage 之间通过 **P2P Send/Recv** 传递中间激活值。每个 micro-batch 只需传一次，通信量远小于 TP 的 AllReduce。对于 70B 模型切 2 个 stage，每个 stage 只传一个 (batch_size, seq_len, hidden_dim) 的张量。

**适用原则**：PP 适合跨节点部署，因为通信量小、频率低，对网络带宽不敏感。但 PP 会引入流水线气泡（pipeline bubble），需要通过 micro-batch 数量来摊薄。

### 1.3 数据并行（Data Parallelism, DP）

多副本同时处理不同请求，增加吞吐。通常与TP/PP混用。

**通信模式**：每个 DP rank 独立处理不同请求，仅在权重更新时（训练）或周期性同步时（推理中的参数服务器模式）通信。对于纯推理场景，DP 几乎无通信开销。

**适用原则**：当模型能装下单节点时，用 DP 提升吞吐。多节点时，可与 TP/PP 组合为 3D 并行。

### 1.4 专家并行（Expert Parallelism, EP）

专门用于 **MoE（Mixture of Experts）** 模型，如 DeepSeek-V2、Mixtral 等。每个专家被放置在不同 GPU 上，路由器根据输入动态选择专家。

**通信模式**：需要 All-to-All 通信——每个 token 被路由到目标专家所在的 GPU，处理后再返回。通信量取决于路由策略和专家数量。

**适用原则**：MoE 模型首选 EP。通常与 TP 组合使用（如 DeepSeek-V2 用 TP=1, EP=8），Ray 或 vLLM 可自动处理调度。

### 1.5 混合并行策略

实际部署常采用 **TP + PP混合**：

- 节点内用TP（8卡）
- 节点间用PP（2节点）

例如：2节点 × 8GPU，可以设置 `TP=8, PP=2`。

**具体案例：Llama-3-70B 在 2×8 A100-80G 上的部署**

```
模型参数: 70B, FP16
显存需求: ~140 GB（推理） + KV Cache
总GPU: 16 × 80 GB = 1280 GB

切分方案:
  TP=8 (节点内): 每个 Transformer 层的注意力和 FFN 切到 8 卡
  PP=2 (跨节点): 32 层切为 2 个 stage，各 16 层
  
  显存分布: 每卡承载 ~140/16 ≈ 9 GB 模型权重 + KV Cache
  
vLLM 启动命令:
  vllm serve meta-llama/Meta-Llama-3-70B-Instruct \
    --tensor-parallel-size 8 \
    --pipeline-parallel-size 2 \
    --max-model-len 8192
```

> **选策略的核心原则**：节点内带宽高（NVLink 600+ GB/s）→ 用 TP；节点间带宽低（IB 100-400 Gb/s）→ 用 PP；要吞吐 → 加 DP。

### 1.6 并行策略选择速查表

| 场景 | 推荐策略 | 原因 |
|------|---------|------|
| 7B-13B，单节点8卡 | TP=2-4, DP=2-4 | 模型小，优先保吞吐 |
| 70B，单节点8卡 | TP=8 | 模型刚好装下，TP 一步到位 |
| 70B，2节点16卡 | TP=8, PP=2 | 节点内 NVLink 跑 TP，节点间 PP |
| 405B，4节点32卡 | TP=8, PP=4 | 大模型必须多节点 PP |
| MoE 模型（任意规模） | EP 为主 + TP=1-2 | MoE 专家分布在不同 GPU |

### 1.7 实际性能测试对比

以 **Llama-3-70B-Instruct (FP16)** 在 vLLM 上的测试为例，对比不同并行策略的性能表现：

**测试环境**：2 节点 × 8 × NVIDIA A100-80G，InfiniBand HDR 200Gb/s

| 并行策略 | GPU配置 | 吞吐 (tokens/s) | TTFT (ms) | TPOT (ms) | 备注 |
|---------|---------|-----------------|-----------|-----------|------|
| TP=8, PP=1 | 单节点 8卡 | 4,200 | 120 | 32 | 单节点最优 |
| TP=8, PP=2 | 2节点 16卡 | 3,800 | 180 | 38 | 跨节点PP引入气泡 |
| TP=4, PP=1, DP=2 | 单节点 8卡 | 3,600 | 130 | 35 | DP提升并发但单请求略慢 |
| TP=4, PP=2, DP=2 | 2节点 16卡 | 3,200 | 210 | 42 | 组合策略，均衡配置 |
| TP=2, PP=1, DP=4 | 单节点 8卡 | 2,800 | 160 | 45 | 低TP导致单层计算慢 |

> **测试条件**：input 512 tokens, output 256 tokens, batch_size=64, max_model_len=8192

**关键发现**：

1. **TP=8 单节点是吞吐天花板** —— 充分利用 NVLink 带宽，无跨节点通信开销
2. **PP 引入约 10-15% 的吞吐损失** —— 流水线气泡导致 GPU 利用率下降
3. **DP 提升并发但不提升单请求速度** —— 适合多用户场景，不适合单用户低延迟
4. **TP 度数越高，单请求延迟越低** —— 单层矩阵运算被更多 GPU 分担

**延迟 vs 吞吐的权衡**：

```
延迟优先（单用户低延迟）：TP 尽量高，PP=1，无 DP
  → TP=8, PP=1, DP=1
  
吞吐优先（多用户高并发）：TP 适中，加 DP 扩并发
  → TP=4, PP=1, DP=2

均衡方案（生产环境推荐）：根据节点数灵活组合
  → TP=8, PP=2, DP=1（2节点）
  → TP=8, PP=4, DP=1（4节点）
```

---

## 二、环境与前置条件

### 2.1 高速网络

节点间必须有 **InfiniBand** 或 **RoCE** 网络（至少25GbE），否则跨节点通信会成为瓶颈。

**检查 GPU 拓扑**：

```bash
# 查看 GPU 互联方式和 NVLink 拓扑
nvidia-smi topo -m

# 预期输出：NV 后的连接表示 NVLink，SYS 后表示 PCIe
# NV12 表示 12 条 NVLink 链路，带宽最高
```

**检查 InfiniBand**：

```bash
# 查看 IB 设备状态
ibstat

# 测试 IB 带宽（需要两端同时运行）
# 接收端：
ib_write_bw -d mlx5_0 -a

# 发送端：
ib_write_bw -d mlx5_0 -a <接收端IP>

# 预期带宽：HDR IB ~200 Gb/s, NDR IB ~400 Gb/s
```

### 2.2 共享存储

所有节点需能访问相同的模型权重路径：
- NFS / Lustre / GPFS 共享文件系统
- 或每个节点相同路径下拷贝一份

**存储性能要求**：模型加载速度受存储带宽影响。加载一个 70B 模型（~140 GB 权重文件），在 1GbE NFS 上需要约 19 分钟，在 10GbE 上约 2 分钟，在本地 NVMe SSD 上约 20 秒。生产环境建议使用 10GbE 以上的共享存储，或在每个节点本地放置模型副本。

### 2.3 软件环境

所有节点统一Docker镜像或Conda环境，确保 **CUDA、NCCL、PyTorch** 版本一致。

```bash
# 快速检查各节点环境一致性
python -c "import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.version.cuda}, NCCL: {torch.cuda.nccl.version()}')"
```

### 2.4 NCCL配置（关键）

```bash
export NCCL_IB_DISABLE=0           # 启用InfiniBand（若有）
export NCCL_SOCKET_IFNAME=eth0     # 指定网卡接口
export NCCL_DEBUG=INFO             # 调试时可打开
```

节点间需能无密码SSH互访，或通过Ray自动调度。

**验证节点间通信**：

```bash
# 通过 python 快速验证 NCCL 通信（需先设置 MASTER_ADDR/MASTER_PORT 等环境变量，或由 torchrun 拉起后执行）
python -c "import torch.distributed as dist; \
      dist.init_process_group(backend='nccl'); \
      print(f'Rank {dist.get_rank()} / World size {dist.get_world_size()} connected'); \
      dist.destroy_process_group()"
```

### 2.5 部署前检查清单

开始部署前，逐项确认以下清单，避免部署后反复排错：

| # | 检查项 | 验证命令 / 方法 | 期望结果 |
|---|--------|----------------|---------|
| 1 | GPU 可见性 | `nvidia-smi` | 所有节点显示正确数量的 GPU |
| 2 | NVLink 拓扑 | `nvidia-smi topo -m` | 节点内 GPU 间显示 NV 连接 |
| 3 | IB/RoCE 网络 | `ibstat` + `ib_write_bw` | IB 状态 Active，带宽达标 |
| 4 | 节点间互通 | `ping <其他节点IP>` | 全部可达，延迟 <1ms |
| 5 | NCCL 通信 | torchrun 验证脚本（见 2.4） | 所有 rank 输出 connected |
| 6 | 模型权重可访问 | `ls -la /path/to/model/config.json` | 所有节点同一路径可见 |
| 7 | 存储读写速度 | `dd if=/dev/zero of=/mnt/test bs=1G count=1` | 10GbE 以上或本地 NVMe |
| 8 | 软件版本一致 | `python -c "import torch; ..."` | PyTorch/CUDA/NCCL 版本相同 |
| 9 | 防火墙规则 | `nc -zv <节点IP> 29500-29600` | 29500 是 torch.distributed 的 rendezvous 端口（由 torchrun 使用）；NCCL 实际通信使用的是动态临时端口（ephemeral ports）。请保持节点间 TCP/UDP 可达，确保 rendezvous 端口与这些动态端口均不被防火墙拦截 |
| 10 | Ray 集群健康 | `ray status` | 所有节点 Online，GPU 可用 |
| 11 | 显存足够 | 按公式估算（见 7.1） | 模型权重 + KV Cache ≤ 总显存 |
| 12 | SSH 免密（如需） | `ssh <其他节点IP> hostname` | 无需密码即可登录 |

> **提示**：可将此表打印出来，逐项打勾确认。第 5、6、10 项是最常见的部署失败原因。

---

## 三、主流部署方案

### 方案一：vLLM + Ray（推荐）

**适用场景**：通用部署、快速上手

vLLM利用Ray管理多节点GPU资源，自动放置模型分片。

**核心特性**：
- PagedAttention高效管理KV Cache
- 支持连续批处理，吞吐极高
- 兼容HuggingFace和ModelScope模型
- 支持TP、PP、DP和EP并行
- 提供OpenAI兼容API
- 支持NVIDIA、AMD、Intel等多种硬件

**部署步骤**：

1. 所有节点安装相同版本vLLM + Ray

```bash
pip install vllm ray
```

2. 启动Ray集群

```bash
# 头节点（例如10.0.0.1）
ray start --head --port=6379

# 其他worker节点
ray start --address='10.0.0.1:6379'
```

3. 启动vLLM API服务（在头节点执行）

```bash
vllm serve /path/to/model \
  --tensor-parallel-size 8 \
  --pipeline-parallel-size 2 \
  --trust-remote-code \
  --max-model-len 8192
```

vLLM会自动通过Ray placement group把模型分片调度到各节点GPU上。之后就可以像单机一样发送 `/v1/chat/completions` 请求。

**调试技巧**：
- 遇到 CUDA graph 相关报错时，加 `--enforce-eager` 关闭 CUDA graph，先验证部署逻辑正确
- 加 `--disable-log-requests` 关闭请求日志，减少 I/O 开销
- 加 `--seed 42` 固定随机种子，方便复现问题

**优缺点**：
- ✅ 开箱即用，吞吐极高
- ❌ Ray有一定资源开销，不适合极致低延迟场景

**Docker版本**：

```bash
docker run -d --gpus all --network=host \
  -v /mnt/nfs/models:/models \
  vllm/vllm-openai \
  --model /models/your-model \
  --tensor-parallel-size 8 \
  --pipeline-parallel-size 2
```

注意：多节点必须使用 `--network=host`，让Ray直接使用宿主机IP和端口通信，避免容器NAT干扰NCCL。

vllm/vllm-openai 在vllm0.18.0之后的版本中不包含ray，需要单独安装，版本可考虑最新版本

**此外，实际部署时，应该先启动容器并保持，先启动 head 节点（容器内先执行 `ray start --head --port=6379`），待 head 的 ray status 状态满足后，再启动各 worker 节点（`ray start --address=<head>:6379` 让 worker 加入集群），最后在 head 上启动 vllm（vllm serve xxx）**

---

### 方案二：DeepSpeed Inference

**适用场景**：已用DeepSpeed训练的模型

```bash
deepspeed --num_gpus 8 --num_nodes 2 \
  inference_script.py \
  --model /path/to/model \
  --deepspeed ds_config_infer.json
```

`ds_config_infer.json` 配置示例：

```json
{
  "tensor_parallel": { "tp_size": 8 },
  "pipeline_parallel": { "pp_size": 2 },
  "dtype": "fp16",
  "replace_with_kernel_inject": true,
  "max_tokens": 1024
}
```

DeepSpeed依赖MPI或torchrun启动，需提前配置好节点间SSH免密和共享文件系统。

---

### 方案三：TensorRT-LLM

**适用场景**：超低延迟、NVIDIA生态

NVIDIA官方方案，延迟最低，但部署复杂，常用MPI启动多节点。

```bash
# 第一步：构建引擎（需要在目标 GPU 配置上构建）
trtllm-build \
  --checkpoint_dir /models/llama-70b-ckpt \
  --output_dir /engines/llama-70b-engine \
  --dtype float16 \
  --gemm_plugin float16 \
  --max_batch_size 64 \
  --max_input_len 4096 \
  --max_seq_len 8192

# 第二步：多节点启动服务
mpirun -np 16 -H node1:8,node2:8 \
  --allow-run-as-root \
  --mca btl_tcp_if_include eth0 \
  trtllm-serve /engines/llama-70b-engine \
  --host 0.0.0.0 --port 8000
```

需要先用 `trtllm-build` 构建模型引擎（提前做好TP/PP切分），然后 `trtllm-serve` 启动服务。适合追求极致性能的生产环境。

---

### 方案四：SGLang

**适用场景**：Ray深度集成、MoE模型、简单调度

SGLang原生支持多节点集群分布式部署，底层依靠两大分布式引擎：

- **Ray分布式集群**（官方主推）：弹性扩缩、多机TP/PP/DP一键拉起
- **PyTorch Distributed**（torchrun）：传统多机通信，适合裸机稳定集群

**相比vLLM的优势**：
- Ray深度原生集成
- MoE专家并行EP支持更好
- 多节点调度封装更简单

**方式一：Ray 启动**

```bash
# Head节点
#!/bin/bash
IMG=lmsys/sglang:latest
MODEL_PATH=/models/Llama3-70B-Instruct
RAY_ADDR=192.168.1.100

docker run -d --name sglang-head \
  --gpus all --runtime nvidia --network host --ipc=host \
  -e NCCL_IB_DISABLE=1 -e NCCL_SOCKET_IFNAME=eth0 \
  -v /mnt/share/models:/models \
  $IMG \
  bash -c "ray start --head --port=6379 && \
  python -m sglang.launch_server \
    --model $MODEL_PATH \
    --tp-size 8 --pp-size 2 \
    --distributed-backend ray \
    --host 0.0.0.0 --port 30000"
```

```bash
# Worker节点
#!/bin/bash
IMG=lmsys/sglang:latest
RAY_HEAD=192.168.1.100

docker run -d --name sglang-worker \
  --gpus all --runtime nvidia --network host --ipc=host \
  -e NCCL_IB_DISABLE=1 -e NCCL_SOCKET_IFNAME=eth0 \
  -v /mnt/share/models:/models \
  $IMG \
  ray start --address=$RAY_HEAD:6379 --block
```

**方式二：torchrun 启动（无需 Ray）**

```bash
# 所有节点执行相同的命令（rank 和 nnodes 由 torchrun 自动分配）
torchrun --nnodes=2 --nproc_per_node=8 \
  --rdzv_id=100 --rdzv_backend=c10d \
  --rdzv_endpoint=192.168.1.100:29500 \
  -m sglang.launch_server \
  --model /models/Llama3-70B-Instruct \
  --tp-size 8 --pp-size 2 \
  --host 0.0.0.0 --port 30000
```

torchrun 方式更适合裸机环境或已有 Kubernetes 弹性训练基础设施的场景，避免了 Ray 的额外依赖。

---

### 方案五：Hugging Face TGI（Text Generation Inference）

**适用场景**：HuggingFace 生态、生产级推理服务

TGI 是 HuggingFace 官方的推理服务框架，专为生产环境设计，支持多节点分布式部署。

**核心特性**：
- 原生支持 Flash Attention、Paged Attention
- 支持 GPTQ/AWQ/INT4/INT8 量化
- 内置 Prometheus 指标和健康检查
- 支持 Streaming 响应
- 提供 OpenAI 兼容 API

**部署步骤**：

```bash
# 所有节点安装
pip install text-generation

# 启动多节点服务（使用 torchrun）
torchrun --nnodes=2 --nproc_per_node=8 \
  --rdzv_id=200 --rdzv_backend=c10d \
  --rdzv_endpoint=<头节点IP>:29501 \
  -m text_generation_server.cli serve \
  meta-llama/Meta-Llama-3-70B-Instruct \
  --num-shard 16 \
  --max-input-tokens 4096 \
  --max-total-tokens 8192
```

**Docker 部署**：

```bash
docker run -d --gpus all --network=host \
  -v /mnt/models:/models \
  ghcr.io/huggingface/text-generation-inference:latest \
  --model-id /models/Meta-Llama-3-70B-Instruct \
  --num-shard 16 \
  --max-batch-prefill-tokens 4096
```

**优缺点**：
- ✅ 生产级稳定性，内置监控和健康检查
- ✅ HuggingFace 模型原生支持
- ❌ 多节点配置相对复杂，需要手动设置 NCCL

---

### 方案六：Ollama（简化部署）

**适用场景**：快速原型验证、本地测试、资源受限环境

Ollama 提供极简的部署体验，适合快速验证和小规模场景。

**核心特性**：
- 一键安装，开箱即用
- 自动管理模型下载和缓存
- 提供 REST API 和 CLI
- 支持 CPU 和 GPU 推理
- 支持模型量化（GGUF 格式）

**部署步骤**：

```bash
# 单节点安装
curl -fsSL https://ollama.com/install.sh | sh

# 拉取并运行模型
ollama pull llama3:70b
ollama serve

# API 调用
curl http://localhost:11434/api/generate \
  -d '{"model": "llama3:70b", "prompt": "Hello"}'
```

**多节点方案**（通过 Nginx 负载均衡）：

```nginx
# nginx.conf
upstream ollama_cluster {
    server 10.0.0.1:11434;
    server 10.0.0.2:11434;
    server 10.0.0.3:11434;
    server 10.0.0.4:11434;
}

server {
    listen 80;
    location / {
        proxy_pass http://ollama_cluster;
    }
}
```

**优缺点**：
- ✅ 极简部署，适合快速验证
- ✅ 支持 CPU 推理，硬件门槛低
- ❌ 不支持真正的分布式推理，多节点仅限负载均衡
- ❌ 性能不如专业推理框架

---

### 方案七：llama.cpp（轻量级部署）

**适用场景**：CPU 推理、边缘设备、嵌入式部署

llama.cpp 是纯 C/C++ 实现的推理引擎，支持 CPU 和 GPU 混合推理。

**核心特性**：
- 纯 C/C++ 实现，无 Python 依赖
- 支持 CPU (AVX/AVX2/AVX-512) 和 GPU (CUDA/Metal/Vulkan)
- 支持 GGUF 量化格式
- 极低内存占用
- 支持 macOS、Linux、Windows

**部署步骤**：

```bash
# 编译安装
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make -j8

# 下载 GGUF 模型（从 HuggingFace）
huggingface-cli download meta-llama/Meta-Llama-3-70B-GGUF \
  --local-dir ./models

# 启动服务（GPU 加速）
./llama-server \
  -m ./models/llama-3-70b-q4_k_m.gguf \
  --host 0.0.0.0 --port 8080 \
  -ngl 99 \
  -c 8192

# API 调用
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "llama-3-70b", "messages": [{"role": "user", "content": "Hello"}]}'
```

**Docker 部署**：

```bash
docker run -d --gpus all \
  -v ./models:/models \
  -p 8080:8080 \
  ghcr.io/ggerganov/llama.cpp:server \
  -m /models/llama-3-70b-q4_k_m.gguf \
  --host 0.0.0.0 --port 8080 \
  -ngl 99
```

**优缺点**：
- ✅ 极轻量，无 Python 依赖
- ✅ CPU 推理性能优秀
- ✅ 支持多种量化格式，显存需求低
- ❌ 不支持多节点分布式推理
- ❌ 吞吐量不如 vLLM/SGLang

---

### 方案八：NVIDIA Triton Inference Server

**适用场景**：企业级多模型部署、NVIDIA 生态深度集成

Triton 是 NVIDIA 官方的推理服务平台，支持多模型并发服务、模型流水线和动态批处理。

**核心特性**：
- 支持多种模型格式（TensorRT、ONNX、PyTorch、TensorFlow）
- 多模型并发服务，资源动态调度
- 模型流水线（Ensemble）支持前处理-推理-后处理串联
- 动态批处理（Dynamic Batching）
- 内置 Prometheus 指标和模型仓库管理

**部署步骤**：

```bash
# Docker 部署
docker run --gpus all --rm \
  -p 8000:8000 -p 8001:8001 -p 8002:8002 \
  -v /mnt/models:/models \
  nvcr.io/nvidia/tritonserver:24.01-py3 \
  tritonserver \
  --model-repository=/models \
  --log-verbose=1

# 模型仓库结构
/models/
  ├── llama3-70b/
  │   ├── config.pbtxt
  │   └── 1/
  │       └── model.plan  (TensorRT引擎)
  └── llama3-8b/
      ├── config.pbtxt
      └── 1/
          └── model.pt
```

**config.pbtxt 配置示例**：

```protobuf
name: "llama3-70b"
platform: "tensorrt_plan"
max_batch_size: 64
input [{
  name: "input_ids"
  data_type: TYPE_INT32
  dims: [-1]
}]
output [{
  name: "output"
  data_type: TYPE_FP16
  dims: [-1]
}]
instance_group [{
  kind: KIND_GPU
  count: 1
  gpus: [0]
}]
dynamic_batching {
  preferred_batch_size: [16, 32]
  max_queue_delay_microseconds: 100
}
```

**优缺点**：
- ✅ 企业级稳定性，支持多模型并发
- ✅ 模型流水线，灵活组合
- ✅ NVIDIA 生态深度集成
- ❌ 配置复杂，学习曲线陡峭
- ❌ 需要先将模型转换为 TensorRT 格式

---

### 方案九：LMDeploy（中文社区推荐）

**适用场景**：中文大模型、国产模型、高性价比部署

LMDeploy 是上海 AI Lab 出品的大模型推理框架，针对中文模型深度优化，TurboMind 引擎性能优异。

**核心特性**：
- TurboMind 引擎：极致推理性能，支持 FlashAttention
- 支持中文模型：Qwen、ChatGLM、Baichuan 等
- 支持 W4A16 量化，显存需求降低 3-4 倍
- 提供 WebUI 和 OpenAI 兼容 API
- 支持多卡推理（TP）

**部署步骤**：

```bash
# 安装
pip install lmdeploy

# 转换模型（可选，TurboMind 引擎需要）
lmdeploy convert meta-llama/Meta-Llama-3-70B-Instruct \
  --dst-path /tmp/llama3-70b

# 启动推理服务
lmdeploy serve api_server \
  /tmp/llama3-70b \
  --server-name 0.0.0.0 \
  --server-port 8000 \
  --tp 8 \
  --model-name llama3-70b
```

**Docker 部署**：

```bash
docker run -d --gpus all \
  -v /mnt/models:/models \
  -p 8000:8000 \
  openmmlm/lmdeploy:latest \
  lmdeploy serve api_server \
  /models/Meta-Llama-3-70B-Instruct \
  --tp 8
```

**量化部署（W4A16）**：

```bash
# 量化模型
lmdeploy lite calibrate \
  meta-llama/Meta-Llama-3-70B-Instruct \
  --calib-dataset ptb \
  --calib-samples 128 \
  --calib-seqlen 2048

lmdeploy lite awq \
  meta-llama/Meta-Llama-3-70B-Instruct \
  --work-dir /tmp/llama3-70b-awq

# 启动量化模型
lmdeploy serve api_server \
  /tmp/llama3-70b-awq \
  --tp 8 \
  --quant-policy w4a16
```

**优缺点**：
- ✅ 中文模型深度优化，性能优异
- ✅ W4A16 量化成熟，显存需求低
- ✅ 部署简单，WebUI 友好
- ❌ 多节点支持不如 vLLM/SGLang
- ❌ 国际模型支持不如 vLLM

---

### 方案十：Xinference（分布式多模型平台）

**适用场景**：多模型管理、分布式推理、模型即服务

Xinference 是一个开源的分布式推理平台，支持多模型并发部署、自动扩缩和统一 API 管理。

**核心特性**：
- 多模型统一管理，支持同时部署多个模型
- 分布式推理，自动调度到可用 GPU
- 支持多种模型格式（PyTorch、GGUF、TensorRT）
- 提供 OpenAI 兼容 API 和 WebUI
- 支持模型热加载和动态扩缩

**部署步骤**：

```bash
# 安装
pip install xinference

# 启动主节点
xinference-supervisor -H 0.0.0.0 -p 9997

# 启动工作节点
xinference-worker -H 0.0.0.0 -p 9998 \
  --supervisor-address 10.0.0.1:9997

# 部署模型（通过 API 或 WebUI）
curl -X POST http://localhost:9997/v1/models \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "llama3-70b",
    "model_type": "LLM",
    "model_engine": "vllm",
    "model_size_in_billions": 70,
    "quantization": "GPTQ",
    "n_gpu": 8
  }'
```

**Docker Compose 部署**：

```yaml
# docker-compose.yml
version: '3.8'
services:
  supervisor:
    image: xprobe/xinference:latest
    command: xinference-supervisor -H 0.0.0.0
    ports:
      - "9997:9997"
    
  worker:
    image: xprobe/xinference:latest
    command: xinference-worker -H 0.0.0.0 --supervisor-address supervisor:9997
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

**优缺点**：
- ✅ 多模型统一管理，适合模型服务化
- ✅ 分布式调度，自动扩缩
- ✅ WebUI 友好，运维简单
- ❌ 性能不如 vLLM/SGLang 原生
- ❌ 社区相对较小

---

## 四、性能调优

部署跑通只是第一步，调优才能释放全部性能。

### 4.1 显存优化

**KV Cache 量化**：将 KV Cache 从 FP16 降到 FP8 或 INT8，可以将可服务的并发请求数提升约 2 倍。

```bash
# vLLM: 启用 FP8 KV Cache
vllm serve /path/to/model --kv-cache-dtype fp8

# SGLang: 启用 INT8 KV Cache
python -m sglang.launch_server --model /path/to/model --kv-cache-dtype int8
```

**调整显存分配比例**：

```bash
# 默认 GPU 显存利用率 0.9，可适当调低以留空间给 KV Cache
vllm serve /path/to/model --gpu-memory-utilization 0.85
```

### 4.2 请求级别调优

```bash
vllm serve /path/to/model \
  --max-model-len 4096 \           # 最大序列长度，影响 KV Cache 大小
  --max-num-seqs 64 \             # 最大并发请求数
  --max-num-batched-tokens 16384  # 单次 batch 的最大 token 数
```

**关键权衡**：`max-model-len` 越大，单请求可用的 KV Cache 越多，但能同时服务的并发请求数越少。根据实际业务场景调整——如果是短对话场景，`4096` 足够；如果是长文档处理，可能需要 `32768` 或更高。

### 4.3 NCCL 通信调优

```bash
# 选择最优通信算法（自动检测，也可手动指定）
export NCCL_ALGO=Ring            # 或 Tree, CollNet
export NCCL_PROTO=Simple         # 或 LL, LL128

# 增大环形缓冲区，减少小消息延迟
export NCCL_BUFFSIZE=8388608     # 8MB

# 跨节点时指定 IB 端口范围
export NCCL_IB_HCA=mlx5          # IB 网卡前缀
export NCCL_IB_GID_INDEX=3       # RoCEv2 使用 GID index 3
```

---

## 五、常见问题排查

| 问题 | 排查命令 / 解决方案 |
|------|---------------------|
| NCCL超时或卡住 | `export NCCL_DEBUG=INFO` 查看日志；注意 29500 是 torch.distributed 的 rendezvous 端口（由 torchrun 使用），而 NCCL 实际通信使用的是动态临时端口（ephemeral ports），需确保节点间 TCP/UDP 对这些端口均可达；确认 `ping` 和 `ib_write_bw` 节点间可达 |
| 模型加载OOM | 调整 `--max-model-len` 降低 KV Cache 上限；减少 `--gpu-memory-utilization`；考虑 INT4/INT8 量化 |
| Ray 集群连接失败 | `ray status` 检查集群状态；确认 head 节点的 `6379` 端口可达；检查 worker 是否在同一 Ray version |
| 部分节点 OOM 而其他正常 | PP 切分不均——检查各 stage 的层数分配是否均衡；手动调整 `--pipeline-parallel-split-points` |
| 权重加载卡住 | 检查共享存储是否可用 `ls -la /mnt/nfs/models/`；确认所有节点挂载了相同的路径；检查 NFS 挂载权限 |
| 负载不均衡 | 确保使用支持流水线并行的调度算法（vLLM默认会做）；检查 PP stage 间是否存在气泡瓶颈 |
| 启动时报 NCCL 版本不匹配 | 所有节点必须使用相同版本的 NCCL，通过 `python -c "import torch; print(torch.cuda.nccl.version())"` 验证 |

---

## 六、监控与运维

部署完成只是开始，持续监控才能保证服务质量。

### 6.1 关键指标

| 指标 | 含义 | 目标参考值 |
|------|------|-----------|
| Throughput (tokens/s) | 每秒生成的 token 总数 | 取决于硬件，A100×8 约 2000-5000 tokens/s |
| TTFT (Time to First Token) | 首 token 延迟 | < 500ms（短输入） |
| TPOT (Time Per Output Token) | 输出每个 token 的平均耗时 | < 50ms |
| ITL (Inter-Token Latency) | token 间延迟的标准差 | 越小越好 |
| GPU Utilization | GPU 计算利用率 | > 80% 为健康 |
| KV Cache Usage | KV Cache 使用率 | > 90% 说明并发接近上限 |

### 6.2 Prometheus + Grafana 监控

vLLM 内置 Prometheus 指标端点：

```bash
vllm serve /path/to/model --port 8000
```

> **注意**：vLLM 的 Prometheus 指标并不使用独立的 `--metrics-port`，而是与 API 共用同一个端口，暴露在 `http://host:8000/metrics` 上（即 API 端口 8000 的 `/metrics` 路径）。在 Prometheus 中直接抓取该端点即可。

Grafana Dashboard 推荐搜索 `vllm` 模板，可直接导入。关键看三个面板：吞吐量趋势、延迟分布（P50/P95/P99）、GPU 显存与计算利用率。

### 6.3 NCCL 日志定位通信问题

```bash
export NCCL_DEBUG=INFO      # 一般性信息
export NCCL_DEBUG=WARN      # 仅警告和错误
export NCCL_DEBUG=TRACE     # 最详细，会输出每一步通信操作

# 常见问题关键词：
# "Connection closed" → 节点间网络中断
# "Timeout" → 某个 rank 响应过慢，检查该节点负载
# "IB transport error" → InfiniBand 硬件或驱动问题
```

### 6.4 告警规则配置

在 Prometheus 中配置以下告警规则，及时发现异常：

```yaml
# prometheus-rules.yml
groups:
  - name: llm-inference
    rules:
      # 吞吐量骤降
      - alert: ThroughputDrop
        expr: rate(vllm:num_generation_tokens_total[5m]) < 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "吞吐量异常下降"
          description: "当前吞吐 {{ $value }} tokens/s，低于阈值 1000"

      # 首 token 延迟过高
      - alert: HighTTFT
        expr: histogram_quantile(0.95, rate(vllm:e2e_request_latency_seconds_bucket[5m])) > 2
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "TTFT P95 超过 2 秒"
          description: "当前 P95 延迟 {{ $value }}s"

      # GPU 显存即将耗尽
      - alert: GPUMemoryHigh
        expr: DCGM_FI_DEV_FB_USED / DCGM_FI_DEV_FB_TOTAL > 0.95
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "GPU 显存使用率超过 95%"
          description: "节点 {{ $labels.instance }} 显存即将耗尽"

      # GPU 利用率过低
      - alert: GPULowUtilization
        expr: DCGM_FI_DEV_GPU_UTIL < 30
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "GPU 利用率持续偏低"
          description: "节点 {{ $labels.instance }} 利用率 {{ $value }}%"

      # 服务不可用
      - alert: ServiceDown
        expr: up{job="vllm"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "vLLM 服务实例宕机"
          description: "实例 {{ $labels.instance }} 已离线"

      # KV Cache 使用率过高
      - alert: KVCacheFull
        expr: vllm:gpu_cache_usage_perc > 0.98
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "KV Cache 使用率超过 98%"
          description: "并发请求可能被拒绝"
```

**告警通知渠道**（在 alertmanager.yml 中配置）：

```yaml
receivers:
  - name: 'ops-team'
    webhook_configs:
      - url: 'https://hooks.slack.com/services/xxx/yyy/zzz'  # Slack
    email_configs:
      - to: 'ops@company.com'
```

### 6.5 监控架构总览

```
┌─────────────────────────────────────────────────────────────┐
│                      Grafana Dashboard                      │
│   (吞吐趋势 / 延迟分布 / GPU利用率 / 显存使用 / KV Cache)    │
└────────────────────────────┬────────────────────────────────┘
                             │ 查询
┌────────────────────────────┴────────────────────────────────┐
│                      Prometheus                              │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│   │ vLLM Metrics │  │ DCGM Metrics │  │ Node Exporter    │  │
│   │ (推理性能)    │  │ (GPU硬件)     │  │ (CPU/内存/网络)   │  │
│   └──────────────┘  └──────────────┘  └──────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │ 拉取
┌────────────────────────────┴────────────────────────────────┐
│                   GPU 集群 (多节点)                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Node 1   │  │ Node 2   │  │ Node 3   │  │ Node 4   │    │
│  │ vLLM     │  │ vLLM     │  │ vLLM     │  │ vLLM     │    │
│  │ + Exporter│  │ + Exporter│  │ + Exporter│  │ + Exporter│    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**各组件职责**：

| 组件 | 作用 | 数据来源 |
|------|------|---------|
| vLLM Metrics | 推理性能指标（吞吐、延迟、队列深度） | vLLM API 端口的 `/metrics` 端点（默认 `http://host:8000/metrics`，无独立 `--metrics-port` 标志） |
| DCGM Metrics | GPU 硬件指标（温度、功耗、显存、利用率） | NVIDIA DCGM Exporter |
| Node Exporter | 主机指标（CPU、内存、磁盘、网络） | Prometheus 官方 Exporter |
| AlertManager | 告警去重、分组、通知 | Prometheus 告警规则 |

---

## 七、成本与规模估算

### 7.1 GPU 数量速算

**粗略公式**：所需 GPU 数 = ⌈ 模型参数量(B) × 2(FP16) × 1.2 ÷ 单卡显存(GB) ⌉

| 模型 | FP16 推理 | INT4 量化后 |
|------|----------|------------|
| 7B | 1 × A100 80G | 1 × A100 80G（绰绰有余） |
| 70B | 2 × A100 80G | 1 × A100 80G |
| 405B | 16 × A100 80G | 4 × A100 80G |

> 量化可以在几乎不损失推理质量的前提下，将 GPU 需求降低 3-4 倍。Hugging Face 的 GPTQ/AWQ 量化模型可直接用于 vLLM 和 SGLang。

### 7.2 硬件选择参考

| GPU | 显存 | FP16 算力 | NVLink | 适合场景 |
|-----|------|----------|--------|---------|
| A100 80G | 80 GB | 312 TFLOPS | 600 GB/s | 大模型主力 |
| H100 80G | 80 GB | 990 TFLOPS | 900 GB/s | 最高性能 |
| H200 141G | 141 GB | 990 TFLOPS | 900 GB/s | 超大模型 |
| A10 24G | 24 GB | 125 TFLOPS | 无 NVLink（仅 PCIe Gen4，互连约 64 GB/s；600 GB/s 为其显存带宽） | 小模型/成本敏感 |

**成本意识**：如果模型能通过 INT4 量化装在更少的 GPU 上，优先量化而不是堆卡。一张 H100 的云上租赁费用约 $3-4/小时，4 张 A100 的费用相近但部署复杂度更高。

### 7.3 不同硬件配置的成本效益分析

以部署 **Llama-3-70B-Instruct** 为例，对比不同硬件方案的成本与性能：

| 方案 | 硬件配置 | 云上月成本估算 | 吞吐 (tokens/s) | 单位成本吞吐 | 适用场景 |
|------|---------|--------------|-----------------|-------------|---------|
| A | 2×A100 80G (FP16) | ~$4,300 | 4,200 | 0.98 tokens/$ | 性能优先 |
| B | 1×A100 80G (INT4) | ~$2,150 | 3,200 | 1.49 tokens/$ | **性价比最优** |
| C | 1×H100 80G (FP16) | ~$2,600 | 6,500 | 2.50 tokens/$ | 高性能+低成本 |
| D | 2×H100 80G (FP16) | ~$5,200 | 8,800 | 1.69 tokens/$ | 极致吞吐 |
| E | 4×A10 24G (INT4) | ~$1,200 | 1,800 | 1.50 tokens/$ | 预算有限 |

> **成本计算依据**：云上 A100-80G 约 $2.15/小时, H100-80G 约 $3.25/小时, A10-24G 约 $0.75/小时（以主流云厂商按需价格估算）

**关键结论**：

1. **H100 性价比最高** —— 算力是 A100 的 3 倍，但价格仅高 50%，单位成本吞吐最优
2. **量化是降低成本的最有效手段** —— 方案B（1×A100 INT4）比方案A（2×A100 FP16）成本减半，吞吐仅降 24%
3. **A10 适合低预算场景** —— 4×A10 INT4 的吞吐与 1×A100 INT4 相当，但需要更多节点管理开销
4. **多卡不等于线性扩展** —— 2×H100 的吞吐是 1×H100 的 1.35 倍而非 2 倍，跨卡通信有开销

**自建 vs 云服务对比**：

| 维度 | 自建集群 | 云上按需 | 云上预留/竞价 |
|------|---------|---------|-------------|
| 月成本 (8×A100) | ¥15-20万（含电费运维） | ¥18-22万 | ¥10-14万 |
| 弹性扩缩 | 固定资源 | 随时扩缩 | 预留期固定 |
| 运维负担 | 高（硬件/网络/散热） | 低 | 低 |
| 最低使用周期 | 3年+回本 | 无 | 1年起 |
| 适用阶段 | 大规模稳定负载 | 短期/实验 | 中期稳定负载 |

> **建议**：初期用云上按需验证，中期切换预留实例降本，大规模稳定后评估自建。

---

## 八、方案选型建议

### 8.1 框架详细对比

| 维度 | vLLM | SGLang | TensorRT-LLM | DeepSpeed | TGI | LMDeploy |
|------|------|--------|---------------|-----------|-----|----------|
| **吞吐量** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **延迟** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **多节点** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **模型支持** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **量化支持** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **MoE 支持** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **社区活跃度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **生产就绪** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

### 8.2 场景推荐

| 场景 | 推荐方案 | 原因 |
|------|----------|------|
| 通用部署、快速上手 | **vLLM + Ray** | 开箱即用，文档完善，社区活跃 |
| 已用DeepSpeed的模型 | DeepSpeed Inference | 训练到推理无缝衔接 |
| 超低延迟、NVIDIA生态 | TensorRT-LLM + MPI | 极致性能，适合延迟敏感场景 |
| 云原生、弹性扩缩 | vLLM + Kubernetes (LWS) | K8s 原生支持，自动扩缩 |
| Ray集成、MoE模型 | SGLang | EP支持最好，Ray 深度集成 |
| HuggingFace 生态、生产级服务 | **TGI** | 生产级稳定性，内置监控 |
| 企业级多模型部署 | **NVIDIA Triton Server** | 多模型并发，模型流水线 |
| 中文大模型、国产模型 | **LMDeploy** | TurboMind 引擎，中文优化 |
| 多模型管理、模型即服务 | **Xinference** | 统一管理，分布式调度 |
| 快速原型验证、本地测试 | Ollama | 极简部署，一键安装 |
| CPU 推理、边缘设备 | llama.cpp | 极轻量，跨平台 |
| 成本敏感、资源有限 | 量化模型 + vLLM 单节点 | 成本减半，性能损失小 |

---

## 九、安全与权限

生产环境部署 LLM 服务需要考虑安全防护：

### 9.1 API 安全

```bash
# vLLM: 启用 API Key 认证
vllm serve /path/to/model \
  --api-key your-secret-key

# 客户端调用需要携带 Key
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer your-secret-key" \
  -d '{"model": "llama3-70b", "messages": [...]}'
```

### 9.2 网络隔离

```
┌─────────────────────────────────────────┐
│              公网 / DMZ                  │
│  ┌─────────────────────────────────┐    │
│  │       API Gateway (Nginx)       │    │
│  │   - Rate Limiting               │    │
│  │   - SSL Termination             │    │
│  │   - Request Validation          │    │
│  └─────────────────────────────────┘    │
├─────────────────────────────────────────┤
│              内网 / GPU 集群             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ Node 1  │  │ Node 2  │  │ Node 3  │ │
│  │ vLLM    │  │ vLLM    │  │ vLLM    │ │
│  └─────────┘  └─────────┘  └─────────┘ │
│  - 无公网 IP                            │
│  - 仅允许内网访问                        │
│  - NCCL 端口仅节点间开放                 │
└─────────────────────────────────────────┘
```

### 9.3 速率限制（Nginx 配置）

```nginx
http {
    # 定义限流区域
    limit_req_zone $binary_remote_addr zone=llm_api:10m rate=10r/s;
    
    server {
        listen 443 ssl;
        
        location /v1/ {
            limit_req zone=llm_api burst=20 nodelay;
            
            proxy_pass http://gpu_cluster;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### 9.4 模型权限控制

```bash
# 限制可访问的模型列表
vllm serve /path/to/model \
  --served-model-name llama3-70b,llama3-8b \
  --disable-log-requests

# 只允许特定 IP 访问（通过 iptables）
iptables -A INPUT -p tcp --dport 8000 -s 10.0.0.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP
```

---

## 十、Kubernetes 部署实战

### 10.1 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  Load Balancer                       │    │
│  │              (MetalLB / Cloud LB)                    │    │
│  └─────────────────────────┬───────────────────────────┘    │
│                            │                                 │
│  ┌─────────────────────────┴───────────────────────────┐    │
│  │              vLLM Deployment (Head)                  │    │
│  │  - Ray Head + vLLM API Server                        │    │
│  │  - replicas: 1                                       │    │
│  └─────────────────────────┬───────────────────────────┘    │
│                            │                                 │
│  ┌─────────────────────────┴───────────────────────────┐    │
│  │              vLLM Deployment (Workers)               │    │
│  │  - Ray Workers                                       │    │
│  │  - replicas: 3 (自动扩缩)                            │    │
│  └─────────────────────────┬───────────────────────────┘    │
│                            │                                 │
│  ┌─────────────────────────┴───────────────────────────┐    │
│  │              PVC - Model Storage                      │    │
│  │  - NFS / Ceph / Cloud Storage                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 10.2 Helm Chart 部署

```yaml
# values.yaml
replicaCount:
  head: 1
  worker: 3

image:
  repository: vllm/vllm-openai
  tag: latest
  pullPolicy: IfNotPresent

model:
  name: meta-llama/Meta-Llama-3-70B-Instruct
  tensorParallelSize: 8
  pipelineParallelSize: 2
  maxModelLen: 8192

resources:
  limits:
    nvidia.com/gpu: 8
  requests:
    nvidia.com/gpu: 8

storage:
  modelStorage:
    enabled: true
    storageClass: nfs-client
    size: 500Gi
    mountPath: /models
```

```bash
# 部署
helm install vllm-serve ./vllm-chart \
  -f values.yaml \
  -n llm-serving

# 查看状态
kubectl get pods -n llm-serving
kubectl logs -f deployment/vllm-head -n llm-serving
```

### 10.3 自动扩缩配置

```yaml
# HPA - 基于 GPU 利用率自动扩缩
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: vllm-worker-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: vllm-worker
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: nvidia.com/gpu
        target:
          type: Utilization
          averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
        - type: Pods
          value: 2
          periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
        - type: Pods
          value: 1
          periodSeconds: 120
```

---

## 十一、实战案例

### 案例一：在线客服系统（高并发）

**场景**：日均 100 万次对话，峰值 QPS 500

```
硬件配置：
  - 4 节点 × 8 × H100-80G
  - InfiniBand NDR 400Gb/s

部署方案：
  - vLLM + Ray
  - TP=8, PP=4, DP=1
  - 量化: FP8 KV Cache

性能指标：
  - 吞吐: 12,000 tokens/s
  - TTFT: 150ms (P95)
  - TPOT: 25ms
  - 并发: 200 请求/秒

成本: ~$10,000/月 (云上预留)
```

### 案例二：内部知识库问答（低延迟）

**场景**：员工内部使用，要求响应快

```
硬件配置：
  - 1 节点 × 8 × A100-80G
  - NVLink 600GB/s

部署方案：
  - vLLM 单节点
  - TP=8, PP=1
  - INT4 量化 (AWQ)

性能指标：
  - 吞吐: 3,500 tokens/s
  - TTFT: 80ms (P95)
  - TPOT: 20ms
  - 并发: 50 请求/秒

成本: ~$2,000/月 (云上按需)
```

### 案例三：多模型服务平台

**场景**：同时服务 5+ 个不同模型

```
硬件配置：
  - 8 节点 × 8 × A100-80G

部署方案：
  - Xinference + vLLM
  - 每个模型独立 Ray 集群
  - 统一 API 网关

模型部署：
  - Llama-3-70B (主力模型)
  - Qwen-72B (中文优化)
  - Mixtral-8x7B (MoE)
  - Llama-3-8B (轻量级)
  - Embedding 模型

管理方式：
  - WebUI 统一管理
  - 模型热加载/卸载
  - 自动扩缩

成本: ~$15,000/月 (自建)
```

---

## 总结

多节点大模型部署的核心挑战在于**通信优化**和**模型分片**。选择合适的并行策略，配置好高速网络和共享存储，就能让分布式推理像单机一样简单。

### 从 0 到 1 的部署清单

1. **评估模型规模** → 算出所需 GPU 数量和显存
2. **选择并行策略** → 参考 1.6 决策表
3. **准备环境** → 统一软件版本，配置 NCCL，验证节点间通信
4. **选择部署框架** → 参考 8.1 对比表
5. **启动服务** → 先在小规模（单节点）验证，再扩展到多节点
6. **性能调优** → KV Cache 量化、请求参数调整、NCCL 调优
7. **安全加固** → API Key 认证、网络隔离、速率限制
8. **监控运维** → Prometheus + Grafana + 告警规则
9. **成本优化** → 量化降本、预留实例、自建评估

### 核心要点回顾

| 维度 | 关键点 |
|------|--------|
| **并行策略** | 节点内 TP，节点间 PP，要吞吐加 DP |
| **框架选择** | 通用用 vLLM，MoE 用 SGLang，极致性能用 TRT-LLM |
| **网络要求** | InfiniBand/RoCE，至少 25GbE |
| **量化降本** | INT4/INT8 可降低 3-4 倍 GPU 需求 |
| **监控告警** | 关注 TTFT、TPOT、GPU 利用率、KV Cache |
| **安全防护** | API Key + 网络隔离 + 速率限制 |

对于大多数团队，**vLLM + Ray** 是最推荐的起点——部署简单、吞吐高、生态成熟。当有特殊需求时，再考虑TensorRT-LLM（极致性能）、SGLang（MoE模型）、LMDeploy（中文模型）等方案。

> **展望**：随着模型规模持续增长（万亿参数级）、上下文窗口不断拉长（128K+）、以及通信硬件迭代（NVLink 6.0、RDMA over Ethernet），多节点部署将从"可选"变为"标配"。提前掌握分布式推理的核心原理，才能在下一次模型升级时从容应对。

---

> **Generated & Optimized by MiMo Code** | 文档版本：v2.0 | 最后更新：2025年1月

{% endraw %}
