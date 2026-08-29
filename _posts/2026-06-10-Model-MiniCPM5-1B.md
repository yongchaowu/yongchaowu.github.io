---
layout: post
title: MiniCPM5 1B
display_title: 'MiniCPM5-1B Overview'
summary: >
  Overview of MiniCPM5-1B, a 1B-parameter on-device language model from
  面壁智能, with benchmarks, architecture details, and deployment considerations.
lang: zh-CN
date: 2026-06-10 19:56:00
categories:
- AI & LLM
tags:
- Model
---

本节内容参考引用 [微信文章](https://mp.weixin.qq.com/s/2tdHV01FL_YGUmZQ12DS2A)

<!--more-->
5 月 25 日，面壁开源最新一代端侧文本基座大模型 `MiniCPM5-1B`。这是一款面向开发者和终端设备的 1B 级「小钢炮」模型，主打`低成本部署、高效运行和端侧友好`。

基于面壁 MiniCPM 系列端侧模型开发的 AI 桌宠交互演示。项目地址：`https://github.com/OpenBMB/MiniCPM-Desk-Pet（本项目基于 clawd-on-desk 项目二次开发）`

优势：
- 它小到可以被放进普通终端，支持本地运行，可以减少对云端 API 的依赖；
- 还保留了对话、理解、推理和工具调用等基础能力，足以支撑一类轻量但高频的本地 AI 应用。

MiniCPM5-1B 不仅能聊天，更拥有深入系统底层的端侧 Agent 自主执行能力

- [Github](https://github.com/OpenBMB/MiniCPM)

Generation parameters
|Mode	|--temp	|--top-p|When to use|
|-------|-------|-------|-------|
|Think|0.9|0.95|reasoning, math, code, multi-step|
|No-think|0.7|0.95|fast assistant, latency-bound|


## 部署
从精度选择上看:
- FP16 精度权重约 2GB，适合 GPU 和高端笔记本以及服务器；
- INT8 量化后约 1GB，几乎无性能损失，覆盖主流笔电和边缘计算盒子；
- INT4 / Q4 量化后仅 0.5GB，手机、平板、车机都能跑。也就是说，一张半张 SD 卡的空间，就能装进一个达到同级全球最优水平的语言模型。
- 支持纯 CPU 环境运行，也可以在浏览器中部署

模型列表(根据运行环境选择合适的模型格式)
|  Name | Description  |
|-------|-------|
|  MiniCPM5-1B      | BF16 最终发布版（经过 RL + OPD 后训练） |
|  MiniCPM5-1B-SFT  | BF16 仅监督微调（SFT）检查点（RL / OPD 之前）  |
|  MiniCPM5-1B-Base | BF16 基础检查点（仅预训练）  |
|  MiniCPM5-1B-GGUF | 适用于 llama.cpp / Ollama / LM Studio 的 GGUF 格式  |
|  MiniCPM5-1B-MLX  | 适用于 Apple Silicon 的 MLX / 4bit 格式  |


## 微调侧
微调侧支持 `LlamaFactory`、`ms-swift`

## 推理侧
推理侧支持 `SGLang、vLLM、llama.cpp、Ollama、Hugging Face、ArcLight` 等工具和框架

### Deployment Guides

Ready to deploy? Choose your preferred method:

- [Deploying MiniCPM5-1B with Ollama]({% post_url 2026-06-10-Model-MiniCPM5-1B-Deploy-Ollama(Docker) %}) — Docker-based deployment with Open-WebUI
- [Deploying MiniCPM5-1B with llama.cpp]({% post_url 2026-06-10-Model-MiniCPM5-1B-Deploy-llama.cpp(Docker) %}) — CPU inference with llama.cpp server

## Skills
面壁还提供了安装部署相关的 skills
Skills 链接：`https://github.com/OpenBMB/MiniCPM/tree/minicpm5#agent-skills--one-click-deploy--finetune`

## 数据治理相关成果
包括开源高质量预训练数据集 UltraData（含最新版本 Ultra-FineWeb-L3）。


## 参考链接

- Hugging Face 链接：https://huggingface.openbmb.com/model/openbmb/MiniCPM5-1B
- GitHub 链接：https://github.com/OpenBMB/MiniCPM
- ModelScope 链接：https://modelscope.cn/models/OpenBMB/MiniCPM5-1B
- AtomGit：https://ai.gitcode.com/OpenBMB/MiniCPM5-1B
- 魔乐社区：https://modelers.cn/models/OpenBMB/MiniCPM5-1B
- ForgeTrain开源链接：https://github.com/OpenBMB/ForgeTrain


## MiniCPM5-1B--modelscope
- [modelscope](https://www.modelscope.cn/models/OpenBMB/MiniCPM5-1B)

支持多种后端部署方式(其中部分)

| 后端 | 模型格式 | 使用场景 | 部署指南 | Agent 技能 |
|-------|-------|-------|-------|-------|
| Transformers | BF16 / FP16 | 本地 Python 推理，支持 GPU + CPU |  transformers.md   |  minicpm5-deploy-transformers   |
| vLLM         | BF16 / FP16 | OpenAI 服务器  | vllm.md | minicpm5-deploy-vllm  |
| llama.cpp    | GGUF     | 本地推理，支持 CPU/GPU | llama_cpp.md      | minicpm5-deploy-llama-cpp  |
| Ollama       | GGUF     | 本地设备运行时  | ollama.md | minicpm5-deploy-ollama  |
