---
layout: post
title: 'Sentence Transformers: Sentence-BERT'
summary: >
  Notes on using Sentence Transformers for semantic search and text similarity,
  covering embedding generation, reranking, and integration with vector stores.
lang: en
date: 2026-06-01 21:39:00
categories:
- AI & LLM
tags:
- Model
- Sentence-BERT
---
背景：某项目中涉及Sentence-BERT 模型

---

<!--more-->

- [Sentence Transformers ](https://www.sbert.net/index.html)

Sentence Transformers (a.k.a. SBERT) is the go-to Python module for using and training state-of-the-art embedding and reranker models. It can be used to compute embeddings from text, images, audio, or video using Sentence Transformer models (quickstart), to calculate similarity scores using Cross-Encoder (a.k.a. reranker) models (quickstart), or to generate sparse embeddings using Sparse Encoder models (quickstart). This unlocks a wide range of applications, including semantic search, semantic textual similarity, and paraphrase mining.

Sentence Transformers was created by UKP Lab and is being maintained by 🤗 Hugging Face. 

## Installation

`pip install -U sentence-transformers # Python 3.10+ and PyTorch 1.11.0+`

## Pretrained Models
- [Pretrained Models](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html)

via Sentence Transformers Hugging Face organization

```python
from sentence_transformers import SentenceTransformer

# Load https://huggingface.co/sentence-transformers/all-mpnet-base-v2
model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
embeddings = model.encode([
    "The weather is lovely today.",
    "It's so sunny outside!",
    "He drove to the stadium.",
])
similarities = model.similarity(embeddings, embeddings)
```

### 离线使用模型,例如:`all-MiniLM-L6-v2`

- 使用 `huggingface-cli`
```shell
#国内网络加速（镜像站）
uv pip install huggingface_hub

# 手动下载时，把文件 URL 中的 huggingface.co 替换为 hf-mirror.com
export HF_ENDPOINT=https://hf-mirror.com

# huggingface-cli download sentence-transformers/all-MiniLM-L6-v2 --local-dir ./all-MiniLM-L6-v2
uvx hf download sentence-transformers/all-MiniLM-L6-v2 --local-dir ./all-MiniLM-L6-v2
```

- 手动从 Hugging Face 网页下载
- [**未验证**]用 sentence-transformers 自动下载（需联网一次）
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
# 下载后模型会自动存放在 ~/.cache/torch/sentence_transformers/ 下

# 在离线代码中加载时，直接传入本地路径即可：
model = SentenceTransformer('/your/path/all-MiniLM-L6-v2')
```

本文修订依据：Hugging Face 官方模型仓库 [`sentence-transformers/all-MiniLM-L6-v2` model card revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/README.md)。官方示例使用完整模型 ID `sentence-transformers/all-MiniLM-L6-v2`；本文仅修正该 ID，缓存路径说明因版本依赖保持不变。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 10:50（UTC+08:00）。修订仅将 `all-MiniLM-L6-v2` 改为官方完整模型 ID。