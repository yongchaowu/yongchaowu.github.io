---

layout: post
title: '从零到一：构建你的 LLM 应用开发知识体系'
summary: 'Learning roadmap for LLM application development, mapping RAG, LangChain, LangGraph, and DeepAgents from fundamentals to production-grade agent workflows.'
lang: zh-CN
date: 2026-09-05 08:44:00
categories:
- AI & LLM
tags:
- LLM
- LangChain
- RAG
---
> **写在前面**：这篇文章是一份精心设计的学习路线图，帮助你从零开始掌握 LangChain、RAG、LangGraph 和 DeepAgents。无论你是想转型做 AI 应用开发的后端工程师，还是想快速上手 LLM 应用的产品经理，这份路线图都能帮你少走弯路。

<!--more-->

## 为什么需要这份路线图？

2024-2025年，大模型应用开发已经从"炫技"走向"落地"。企业不再满足于简单的聊天机器人，而是需要：

- **智能客服**：基于企业知识库的精准问答
- **代码助手**：理解上下文、调用工具、自动修复Bug
- **数据分析**：自然语言查询数据库，自动生成报表
- **自动化流程**：多步骤任务编排，人工审核后执行

这些场景都需要一套成熟的技术栈来实现。本文将带你掌握这套技术栈的核心：**LangChain + RAG + LangGraph + DeepAgents**。

---

## 技术栈全景：一张图看懂

在开始学习之前，先理解这四个技术的定位和关系：

| 技术 | 定位 | 一句话说明 | 学习优先级 |
|------|------|-----------|------------|
| **RAG** | 检索增强生成 | 知识库问答技术（不是框架），解决LLM知识过时/幻觉问题 | ⭐⭐⭐⭐⭐ |
| **LangChain** | 组件工具箱 | 文档加载、切分、向量库封装、prompt、工具调用、LCEL链式调用 | ⭐⭐⭐⭐ |
| **LangGraph** | 状态图编排框架 | 基于LangChain生态，做循环、分支、记忆持久化、人工介入、复杂Agent工作流 | ⭐⭐⭐⭐⭐ |
| **DeepAgents** | 高层封装套件 | 基于LangGraph运行时，封装规划、子Agent、长任务、文件操作 | ⭐⭐⭐ |

**关键认知**：
- RAG 是**技术**，不是框架。它解决的是"如何让LLM基于最新、最准确的知识回答问题"
- LangChain 是**积木**，提供各种组件让你快速搭建应用
- LangGraph 是**蓝图**，解决复杂工作流的编排问题
- DeepAgents 是**高级工具**，适合快速搭建复杂Agent，但不建议初学者直接使用

**学习顺序**：Python基础 → LLM API调用 → Prompt工程 → RAG → LangChain基础 → LangGraph → DeepAgents

---

## 📌 第一阶段：前置基础（1-2周）

> **核心原则**：应用开发，聚焦**调用与编排**，不是造模型。不需要懂 Transformer 训练原理，专注应用层开发。

### 1. Python基础：你的第一行代码

**必备技能清单**：
- 函数定义、字典操作、TypedDict 类型提示、类与继承、异常处理
- 包管理：`pip`、`uv`（推荐，更快）、虚拟环境 `venv`
- 文件操作：读写 txt/json/csv/pdf
- HTTP 调用：requests 库、理解 REST API
- JSON 处理：序列化、反序列化、嵌套结构解析

**开发环境搭建**：
```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 3. 安装基础依赖
pip install python-dotenv requests openai

# 4. 推荐工具
# VS Code + Python插件 + Jupyter Notebook
# 调试技巧：断点调试、print调试、日志logging
```

**为什么选择 uv？**
```bash
# uv 是新一代包管理器，比 pip 快 10-100 倍
# 安装
curl -LsSf https://astral.sh/uv/install.sh | sh

# 使用
uv pip install package-name
uv venv  # 创建虚拟环境
```

### 2. 大模型基础认知：从调用开始

**LLM API 调用（OpenAI 兼容接口）**：

```python
import os
from openai import OpenAI

# 支持OpenAI兼容接口的模型：DeepSeek、Qwen、GLM、Moonshot等
# 以DeepSeek为例
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 基础对话调用
def chat_with_llm(user_message: str) -> str:
    """调用LLM进行对话"""
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手"},
            {"role": "user", "content": user_message}
        ],
        temperature=0.7,  # 控制随机性，0-1
        max_tokens=1000   # 最大输出长度
    )
    return response.choices[0].message.content

# 使用示例
answer = chat_with_llm("什么是RAG？")
print(answer)
```

**流式输出（实时响应）**：
```python
def stream_chat(user_message: str):
    """流式输出 - 实时返回结果"""
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": user_message}],
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()  # 换行

# 流式输出让用户体验更好，不用等待完整响应
stream_chat("解释一下向量数据库")
```

**多轮对话管理**：
```python
def multi_turn_chat():
    """多轮对话 - 保持上下文"""
    messages = [
        {"role": "system", "content": "你是一个有帮助的助手"}
    ]
    
    while True:
        user_input = input("你: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_input})
        
        # 调用LLM
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        
        assistant_message = response.choices[0].message.content
        print(f"助手: {assistant_message}")
        
        # 添加助手回复到历史
        messages.append({"role": "assistant", "content": assistant_message})

# 运行多轮对话
multi_turn_chat()
```

**关键概念详解**：

| 概念 | 说明 | 实际影响 |
|------|------|----------|
| **Token** | 文本被分割成的最小单位，中文约1.5-2个字符/token | 影响成本和上下文长度 |
| **上下文窗口** | 模型能处理的最大token数（如8K、32K、128K） | 决定你能处理多长的文档 |
| **Function Calling** | 模型输出结构化JSON调用工具，不是直接执行代码 | Agent的核心能力 |
| **Temperature** | 控制随机性（0-1），越低越确定 | 0.7适合创意，0.1适合精确任务 |

### 3. Prompt工程：与LLM对话的艺术

**思维链（Chain of Thought）**：
```
请一步一步思考：
1. 首先分析问题的关键信息
2. 然后列出可能的解决方案
3. 最后给出最优答案
```

**为什么有效？** 思维链让LLM展示推理过程，减少跳步错误，特别适合复杂问题。

**Few-shot示例**：
```
请将以下文本分类为正面/负面情感。

文本：这家餐厅的菜很好吃
分类：正面

文本：服务太差了，等了一个小时
分类：负面

文本：环境一般，但味道不错
分类：
```

**ReAct范式（Agent核心）**：
```
思考：用户想查天气，我需要调用天气工具
行动：调用weather_api(city="北京")
观察：北京今天晴，25°C
思考：获取到天气信息，可以回复用户了
回答：北京今天天气晴朗，温度25°C
```

**Prompt模板设计原则**：
1. **明确角色**：告诉LLM它是谁（"你是一个Python专家"）
2. **提供上下文**：给出必要的背景信息
3. **清晰指令**：明确告诉它要做什么
4. **格式要求**：指定输出格式（JSON、Markdown等）
5. **示例引导**：给1-2个示例让它理解

### 4. 必备概念理解

**RAG完整流程**：
```
离线阶段：
文档加载 → 文本切分(chunk) → 向量化(Embedding) → 向量库存储

在线阶段：
用户提问 → 问题向量化 → 相似度检索 → 获取相关文档片段
    ↓
组装Prompt(问题+检索到的上下文) → LLM生成回答
```

**Agent三要素**：
- **记忆(Memory)**：对话历史、长期记忆、工作记忆。决定Agent能"记住"多少信息
- **规划(Planning)**：任务分解、目标设定、策略选择。决定Agent如何完成复杂任务
- **工具(Tool)**：API调用、数据库查询、代码执行、文件操作。扩展LLM的能力边界

**向量数据库选择指南**：

| 数据库 | 特点 | 适用场景 | 部署难度 |
|--------|------|----------|----------|
| Chroma | 本地、零配置、轻量 | 入门学习、小型项目 | ⭐ |
| Milvus | 分布式、高性能、云原生 | 生产环境、大规模数据 | ⭐⭐⭐⭐ |
| PgVector | PostgreSQL扩展、SQL友好 | 已有PostgreSQL的团队 | ⭐⭐⭐ |
| Pinecone | 全托管、易用 | 快速上线、不想运维 | ⭐ |
| Weaviate | 混合搜索、GraphQL | 需要高级查询功能 | ⭐⭐⭐ |

> **小任务**：写最简单代码调用LLM API，实现单轮、多轮对话，跑通流式输出。

---

## 🚩 第二阶段：RAG完整实现（2-3周）

> RAG是业务最常用，也是Agent的底座能力。**不要直接跳Agent**，先把RAG吃透。

### 为什么RAG如此重要？

**痛点**：LLM的知识有截止日期，且可能产生幻觉（编造事实）。

**RAG的解决方案**：让LLM基于你提供的文档来回答问题，而不是凭"记忆"。

**实际应用场景**：
- 企业知识库问答：员工问"公司的报销流程是什么？"，RAG从公司文档中检索并回答
- 客户支持：用户问"如何重置密码？"，RAG从产品文档中检索步骤
- 学术研究：问"这篇论文的主要贡献是什么？"，RAG从PDF中提取信息

### 学习重点详解

#### 1. 文档加载器：把各种格式变成文本

```python
from langchain_community.document_loaders import (
    PyPDFLoader,           # PDF文件
    TextLoader,            # 纯文本
    UnstructuredMarkdownLoader,  # Markdown
    WebBaseLoader,         # 网页
    CSVLoader,             # CSV
    Docx2txtLoader,        # Word文档
)

# PDF加载示例
loader = PyPDFLoader("document.pdf")
docs = loader.load()
print(f"加载了 {len(docs)} 页文档")

# 查看文档结构
for i, doc in enumerate(docs[:3]):  # 只看前3页
    print(f"第{i+1}页:")
    print(f"  来源: {doc.metadata['source']}")
    print(f"  页码: {doc.metadata.get('page', 'N/A')}")
    print(f"  内容预览: {doc.page_content[:100]}...")
    print()
```

**加载器选择建议**：
- PDF：优先用 `PyPDFLoader`，扫描版PDF用 `UnstructuredPDFLoader`
- 网页：`WebBaseLoader` 会自动处理JavaScript渲染
- 混合格式：`DirectoryLoader` 可以批量加载整个文件夹

#### 2. 文本切分策略：这是RAG质量的关键

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 核心参数详解
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 每个chunk最大字符数
    chunk_overlap=50,      # chunk之间重叠字符数（保持上下文连贯）
    length_function=len,   # 计算长度的函数
    separators=["\n\n", "\n", "。", "！", "？"],  # 中文分隔符
    keep_separator=True    # 保留分隔符
)

# 切分文档
chunks = text_splitter.split_documents(docs)
print(f"切分为 {len(chunks)} 个chunk")

# 查看切分效果
for i, chunk in enumerate(chunks[:3]):
    print(f"Chunk {i+1}: {len(chunk.page_content)} 字符")
    print(f"  内容: {chunk.page_content[:100]}...")
    print()
```

**Chunk调优黄金法则**：
- **一般文档**：chunk_size=300-1000，overlap=10%-20%
- **技术文档**：可适当增大到1000-2000，保持技术术语完整
- **代码文件**：按函数/类切分，保留完整语义
- **对话记录**：按轮次切分，保持上下文连贯

**为什么需要overlap？**
```
文档：LangChain是一个LLM应用开发框架。它提供了各种组件...
Chunk 1: LangChain是一个LLM应用开发框架。它
Chunk 2: 它提供了各种组件...
→ 没有overlap，"它"指代不明

Chunk 1: LangChain是一个LLM应用开发框架。它提供了
Chunk 2: 它提供了各种组件...
→ 有overlap，上下文连贯
```

#### 3. Embedding向量模型：把文本变成数字

```python
from langchain_huggingface import HuggingFaceEmbeddings

# 开源推荐：bge-m3（支持中英文，效果好）
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cuda"},  # GPU加速
    encode_kwargs={"normalize_embeddings": True}
)

# 向量化文本
text = "什么是RAG？"
vector = embeddings.embed_query(text)
print(f"文本: {text}")
print(f"向量维度: {len(vector)}")  # 通常是1024维
print(f"向量前10维: {vector[:10]}")

# 批量向量化
texts = ["什么是RAG？", "LangChain是什么？", "向量数据库如何工作？"]
vectors = embeddings.embed_documents(texts)
print(f"批量向量化: {len(texts)} 个文本 → {len(vectors)} 个向量")
```

**模型选择指南**：

| 模型 | 维度 | 特点 | 适用场景 |
|------|------|------|----------|
| BAAI/bge-m3 | 1024 | 中英文效果好，推荐 | 通用场景 |
| text-embedding-3-small | 1536 | OpenAI官方，效果稳定 | 已有OpenAI API |
| GTE-large-zh | 1024 | 中文特化，速度快 | 纯中文场景 |
| mxbai-embed-large | 1024 | 最佳MRR@10性能 | 追求最高质量 |

**如何评估Embedding效果？**
```python
# 简单评估：计算相关性分数
from sklearn.metrics.pairwise import cosine_similarity

# 向量化查询和文档
query_vector = embeddings.embed_query("什么是RAG？")
doc_vectors = embeddings.embed_documents([
    "RAG是检索增强生成技术",
    "LangChain是LLM应用开发框架",
    "Python是一种编程语言"
])

# 计算相似度
similarities = cosine_similarity([query_vector], doc_vectors)[0]
print("与查询的相似度:")
for i, sim in enumerate(similarities):
    print(f"  文档{i+1}: {sim:.4f}")
# 预期：文档1相似度最高
```

#### 4. 向量库操作：存储和检索

```python
from langchain_community.vectorstores import Chroma

# 创建向量库
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",  # 持久化存储
    collection_name="my_documents"    # 集合名称
)

# 相似度检索
def search_documents(query: str, k: int = 3):
    """检索相关文档"""
    results = vectorstore.similarity_search_with_score(query, k=k)
    
    print(f"查询: {query}")
    print(f"找到 {len(results)} 个相关文档:\n")
    
    for i, (doc, score) in enumerate(results):
        print(f"文档 {i+1} (相似度: {score:.4f}):")
        print(f"  来源: {doc.metadata.get('source', 'N/A')}")
        print(f"  内容: {doc.page_content[:100]}...")
        print()

# 使用示例
search_documents("什么是RAG？")

# MMR检索（最大边际相关性）- 保证相关性的同时增加多样性
results = vectorstore.max_marginal_relevance_search(
    query="RAG技术",
    k=3,
    fetch_k=10  # 先检索10个，再选3个
)
```

**检索策略对比**：
| 策略 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 相似度检索 | 简单快速 | 可能返回重复内容 | 通用场景 |
| MMR检索 | 多样性好 | 计算开销大 | 需要多样化的场景 |
| 混合检索 | 结合关键词和语义 | 实现复杂 | 精确匹配+语义理解 |

#### 5. Prompt组装：把检索结果变成答案

```python
from langchain_core.prompts import ChatPromptTemplate

# RAG标准Prompt模板
template = """你是一个专业的问答助手。请根据以下上下文回答问题。

重要规则：
1. 只根据提供的上下文回答问题
2. 如果上下文中没有相关信息，请说"抱歉，我无法根据现有资料回答这个问题"
3. 不要编造信息
4. 回答要简洁明了

上下文：
{context}

问题：{question}

回答："""

prompt = ChatPromptTemplate.from_template(template)

# 使用示例
context = "RAG是检索增强生成技术，它通过检索相关文档来增强LLM的回答质量。"
question = "什么是RAG？"

# 格式化prompt
formatted_prompt = prompt.format(context=context, question=question)
print(formatted_prompt)
```

**高级Prompt技巧**：
```python
# 1. 添加示例（Few-shot）
template_with_examples = """你是一个专业的问答助手。

示例：
问题：Python是什么？
回答：Python是一种高级编程语言，以其简洁易读的语法著称，广泛应用于Web开发、数据科学、人工智能等领域。

问题：什么是机器学习？
回答：机器学习是人工智能的一个分支，它使计算机能够从数据中学习，而无需显式编程。

现在请根据以下上下文回答问题：

上下文：{context}

问题：{question}

回答："""

# 2. 添加置信度提示
template_with_confidence = """你是一个专业的问答助手。请根据以下上下文回答问题，并给出置信度评分。

评分标准：
- 高置信度（0.8-1.0）：上下文中有明确答案
- 中置信度（0.5-0.8）：上下文中有相关信息，但需要推理
- 低置信度（0.0-0.5）：上下文信息不足

上下文：{context}

问题：{question}

请按以下格式回答：
回答：[你的回答]
置信度：[0.0-1.0之间的分数]
理由：[为什么给出这个置信度]"""
```

#### 6. RAG常见坑及解决方案

| 问题 | 原因 | 解决方案 | 代码示例 |
|------|------|----------|----------|
| **幻觉** | LLM凭空生成答案 | 强调"只根据上下文回答"，添加置信度提示 | 见上方Prompt模板 |
| **检索召回差** | embedding效果不好 | 换更好的embedding模型，调整chunk_size | 尝试不同embedding模型 |
| **答案不相关** | prompt设计不当 | 优化prompt模板，添加示例 | 添加Few-shot示例 |
| **重复回答** | 上下文重叠过多 | 减小overlap，去重处理 | 调整chunk_overlap |
| **响应慢** | 向量库检索慢 | 使用GPU加速，优化索引 | 使用FAISS或Milvus |

**性能优化技巧**：
```python
# 1. 使用FAISS加速（比Chroma快10倍）
from langchain_community.vectorstores import FAISS

vectorstore = FAISS.from_documents(chunks, embeddings)

# 2. 使用缓存避免重复计算
from langchain.cache import SQLiteCache
import langchain
langchain.llm_cache = SQLiteCache(database_path=".langchain.db")

# 3. 批量处理
def batch_process(documents, batch_size=100):
    """批量处理文档"""
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i+batch_size]
        vectorstore.add_documents(batch)
```

### 实战项目：从零构建RAG系统

#### 项目1：最简本地RAG（30分钟完成）

```python
# 安装依赖
# pip install langchain langchain-community chromadb sentence-transformers

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama  # 本地模型，无需API

# 1. 加载文档
loader = PyPDFLoader("your_document.pdf")  # 替换为你的PDF
docs = loader.load()
print(f"加载了 {len(docs)} 页文档")

# 2. 切分文档
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "！", "？"]
)
chunks = splitter.split_documents(docs)
print(f"切分为 {len(chunks)} 个chunk")

# 3. 向量化并存储
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
vectorstore = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory="./db"
)

# 4. 创建检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 5. 定义Prompt
prompt = ChatPromptTemplate.from_template("""
基于以下上下文回答问题。如果上下文中没有相关信息，请说不知道。

上下文：{context}
问题：{question}
回答：""")

# 6. 初始化LLM（使用Ollama本地运行）
llm = Ollama(model="qwen2.5:7b")  # 需要先安装Ollama

# 7. 执行RAG
def rag_query(question: str) -> str:
    """执行RAG查询"""
    # 检索相关文档
    docs = retriever.invoke(question)
    context = "\n".join([d.page_content for d in docs])
    
    # 生成回答
    response = llm.invoke(prompt.format(context=context, question=question))
    return response

# 测试
question = "这个文档的主要内容是什么？"
answer = rag_query(question)
print(f"问题: {question}")
print(f"回答: {answer}")
```

#### 项目2：进阶优化（提升质量）

```python
# 1. 优化切分策略
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 按段落切分，保持语义完整
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # 更大的chunk
    chunk_overlap=100,  # 更多的重叠
    separators=["\n\n\n", "\n\n", "\n"],  # 优先按段落切分
)

# 2. 添加Reranker（重排序）
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank

# 使用Cohere重排序（需要API key）
compressor = CohereRerank(model="rerank-v3.5", top_n=3)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)

# 3. 混合检索（向量+关键词）
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# BM25关键词检索
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 3

# 向量检索
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 混合检索（各占50%权重）
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.5, 0.5]
)

# 4. Query改写（提升检索效果）
from langchain_core.prompts import ChatPromptTemplate

rewrite_template = """请将以下用户问题改写为更适合检索的形式。

用户问题：{question}

改写后的检索查询："""

rewrite_prompt = ChatPromptTemplate.from_template(rewrite_template)

def rewrite_query(question: str) -> str:
    """改写用户问题"""
    response = llm.invoke(rewrite_prompt.format(question=question))
    return response  # Ollama.invoke() 直接返回 str；ChatOpenAI 需用 response.content

# 使用改写后的查询进行检索
original_question = "这个系统怎么用？"
rewritten_query = rewrite_query(original_question)
print(f"原始问题: {original_question}")
print(f"改写后: {rewritten_query}")
```

> **重要**：先手写一版简易RAG，彻底看懂完整链路，再用LangChain封装版。

---

## 🚩 第三阶段：LangChain基础（2-3周）

> LangChain核心是一堆组件，不要沉迷各种Chain。重点掌握核心模块，学会用LCEL构建链式调用。

### 为什么选择LangChain？

**LangChain的优势**：
- **标准化接口**：统一的LLM、向量库、工具调用接口
- **丰富的集成**：支持几乎所有主流LLM和向量数据库
- **LCEL表达式语言**：声明式语法，清晰易读
- **生产就绪**：内置重试、缓存、监控、部署工具

**LangChain不是什么**：
- 不是万能的，复杂场景可能需要自己写代码
- 不是最优性能，有些场景直接调用API更快
- 不是唯一选择，LlamaIndex、Haystack也是好选择

### 核心模块详解

#### 1. ChatModel封装：统一的LLM接口

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama  # 注意：用ChatOllama（聊天接口），不是Ollama（补全接口）

# OpenAI兼容模型（推荐）
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
    api_key="your-api-key",
    max_retries=3,  # 自动重试
    request_timeout=30  # 超时时间
)

# Anthropic Claude
llm = ChatAnthropic(
    model="claude-3-sonnet-20240229",
    temperature=0.7,
    max_tokens=1024
)

# 本地Ollama（聊天模型，支持.invoke()返回AIMessage）
llm = ChatOllama(
    model="qwen2.5:7b",
    base_url="http://localhost:11434"
)

# 统一调用接口
response = llm.invoke("你好")
print(response.content)

# 流式输出
for chunk in llm.stream("解释一下Python装饰器"):
    print(chunk.content, end="", flush=True)
```

#### 2. Messages消息体系：结构化的对话

```python
from langchain_core.messages import (
    HumanMessage,      # 用户消息
    AIMessage,         # AI回复
    SystemMessage,     # 系统提示
    ToolMessage,       # 工具调用结果
)

# 构建对话历史
messages = [
    SystemMessage(content="你是一个Python专家，用简洁的语言回答问题"),
    HumanMessage(content="什么是装饰器？"),
    AIMessage(content="装饰器是一种设计模式，允许在不修改原函数代码的情况下为函数添加新功能。"),
    HumanMessage(content="能给个例子吗？")
]

# 查看消息
for msg in messages:
    print(f"{msg.type}: {msg.content}")

# 添加新消息
messages.append(AIMessage(content="当然可以，这里是一个简单的例子..."))
```

#### 3. PromptTemplate：可复用的提示模板

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 简单模板
prompt = ChatPromptTemplate.from_template("请用{language}解释{topic}")

# 消息模板（支持对话历史）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}专家"),
    MessagesPlaceholder(variable_name="chat_history"),  # 对话历史占位符
    ("human", "{question}"),
])

# 使用示例
chat_history = [
    HumanMessage(content="你好"),
    AIMessage(content="你好！我是Python专家，有什么可以帮你的？")
]

formatted = prompt.format_messages(
    role="Python",
    chat_history=chat_history,
    question="什么是装饰器？"
)

# 查看格式化结果
for msg in formatted:
    print(f"{msg.type}: {msg.content}")
```

#### 4. LCEL表达式语言：官方主推的链式调用

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

# 基础LCEL链
prompt = ChatPromptTemplate.from_template("请用{language}解释{topic}")
llm = ChatOpenAI(model="gpt-4o")
parser = StrOutputParser()

# 管道语法 - 清晰易读
chain = prompt | llm | parser

# 执行
result = chain.invoke({
    "language": "中文",
    "topic": "Python装饰器"
})
print(result)

# 高级LCEL：带中间处理步骤
def format_docs(docs):
    """格式化检索到的文档"""
    return "\n\n".join([doc.page_content for doc in docs])

# RAG链
rag_chain = (
    {
        "context": retriever | format_docs,  # 检索并格式化
        "question": RunnablePassthrough()     # 直接传递问题
    }
    | prompt
    | llm
    | parser
)

# 执行
answer = rag_chain.invoke("什么是RAG？")
```

**LCEL优势详解**：
- **声明式语法**：代码即文档，清晰易读
- **自动流式**：`chain.stream()` 自动支持流式输出
- **自动异步**：`chain.ainvoke()` 自动支持异步
- **自动批处理**：`chain.batch()` 自动并行处理
- **内置重试**：`.with_retry(retries=3)` 自动重试
- **易于测试**：每个组件都可以单独测试

#### 5. Document和Retriever：标准化的检索接口

```python
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

# Document对象 - LangChain的核心数据结构
doc = Document(
    page_content="这是文档内容",
    metadata={
        "source": "file.pdf",
        "page": 1,
        "chapter": "第一章",
        "custom_field": "自定义数据"  # 可以添加任意元数据
    }
)

# Retriever接口 - 标准化的检索接口
retriever = vectorstore.as_retriever(
    search_type="similarity",  # 或 "mmr"（最大边际相关性）
    search_kwargs={
        "k": 3,  # 返回3个结果
        "score_threshold": 0.7  # 相似度阈值
    }
)

# 检索
docs = retriever.invoke("查询内容")
print(f"检索到 {len(docs)} 个文档")

# 带分数的检索
docs_with_scores = vectorstore.similarity_search_with_score("查询内容", k=3)
for doc, score in docs_with_scores:
    print(f"相似度: {score:.4f}, 内容: {doc.page_content[:50]}...")
```

#### 6. Tool工具封装：扩展LLM的能力

```python
from langchain_core.tools import tool
import math
import requests

# 定义工具 - 使用@tool装饰器
@tool
def calculate(expression: str) -> str:
    """计算数学表达式。输入应该是有效的Python数学表达式。
    
    示例：
    - "2 + 2" 返回 "4"
    - "sqrt(16)" 返回 "4.0"
    - "sin(3.14)" 返回 "0.0015926529164868282"
    """
    try:
        # 安全计算（生产环境应使用更安全的评估方式）
        result = eval(expression, {"__builtins__": {}}, {
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "pi": math.pi,
            "e": math.e
        })
        return str(result)
    except Exception as e:
        return f"计算错误：{str(e)}"

@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息。
    
    Args:
        city: 城市名称，如"北京"、"上海"
    
    Returns:
        天气信息字符串
    """
    # 这里调用实际天气API
    # 示例返回
    weather_data = {
        "北京": "北京今天天气晴朗，温度25°C，湿度40%",
        "上海": "上海今天多云，温度28°C，湿度65%",
        "广州": "广州今天有雨，温度30°C，湿度80%"
    }
    return weather_data.get(city, f"暂时无法获取{city}的天气信息")

# 工具列表
tools = [calculate, get_weather]

# 查看工具信息
for t in tools:
    print(f"工具名: {t.name}")
    print(f"描述: {t.description}")
    print(f"参数: {t.args}")
    print()
```

#### 7. Memory记忆系统：让对话有连续性

```python
from langchain.memory import (
    ConversationBufferMemory,      # 完整对话历史
    ConversationBufferWindowMemory, # 滑动窗口（只保留最近K轮）
    ConversationSummaryMemory,     # 对话摘要
    ConversationEntityMemory,      # 实体记忆（记住人名、地点等）
)

# 完整记忆 - 保留所有对话历史
memory = ConversationBufferMemory(return_messages=True)
memory.save_context(
    {"input": "你好，我叫小明"},
    {"output": "你好小明！我是AI助手，有什么可以帮你的？"}
)
memory.save_context(
    {"input": "我是一名Python开发者"},
    {"output": "太好了！作为Python开发者，你可能对装饰器、生成器等高级特性很熟悉。"}
)

# 获取记忆
history = memory.load_memory_variables({})
print("对话历史:")
for msg in history["messages"]:
    print(f"{msg.type}: {msg.content}")

# 滑动窗口记忆 - 只保留最近3轮对话
window_memory = ConversationBufferWindowMemory(k=3, return_messages=True)

# 摘要记忆 - 用摘要代替完整历史（节省token）
summary_memory = ConversationSummaryMemory(
    llm=llm,  # 需要LLM来生成摘要
    return_messages=True
)
```

### 调试工具：LangSmith

> **极其重要**：每一个项目都打开trace，看每一步流转，这是排错最重要手段。

```python
# 安装
# pip install langsmith

# 设置环境变量
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-api-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# 现在所有LangChain调用都会自动追踪
# 打开 https://smith.langchain.com/ 查看trace
```

**LangSmith能做什么**：
- **查看每一步的输入/输出**：看到LLM收到了什么，返回了什么
- **追踪token使用量和成本**：精确计算每个调用的花费
- **定位错误发生的具体环节**：是检索错了？还是LLM理解错了？
- **比较不同版本的效果**：A/B测试不同的prompt或模型
- **监控生产环境**：实时查看线上调用情况

### 实战任务

#### 任务1：LCEL重写RAG

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 定义组件
llm = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_template("""
基于以下上下文回答问题。如果上下文中没有相关信息，请说不知道。

上下文：{context}
问题：{question}
回答：""")
parser = StrOutputParser()

# 格式化检索结果
def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

# LCEL RAG链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | parser
)

# 执行
answer = rag_chain.invoke("什么是RAG？")
print(answer)

# 流式输出
for chunk in rag_chain.stream("解释一下向量数据库"):
    print(chunk, end="", flush=True)
```

#### 任务2：简单工具Agent

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor

# 创建Agent
llm = ChatOpenAI(model="gpt-4o")
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 执行
result = executor.invoke({
    "input": "北京今天天气怎么样？帮我计算一下25度转换成华氏度是多少？"
})
print(result["output"])

# 查看详细过程
print("\n详细过程:")
for step in result.get("intermediate_steps", []):
    action, observation = step
    print(f"工具调用: {action.tool}")
    print(f"参数: {action.tool_input}")
    print(f"结果: {observation}")
    print()
```

#### 任务3：观察trace

1. 打开LangSmith控制台 (https://smith.langchain.com/)
2. 找到你的项目
3. 点击任意trace查看：
   - **输入**：LLM收到了什么消息
   - **输出**：LLM返回了什么内容
   - **工具调用**：调用了哪些工具，参数是什么
   - **耗时**：每一步花了多长时间
   - **Token使用**：消耗了多少token，花了多少钱

> **注意**：此时普通AgentExecutor够用，但复杂多轮、循环、中断会很难写，这时就该学LangGraph。

---

## 🚩 第四阶段：LangGraph（3-4周）

> LangGraph解决LangChain原生Agent短板：**状态持久化、循环、条件分支、断点恢复、人工介入、多Agent协作**。
> 
> LangGraph不是替代LangChain，而是**复用LangChain组件，做流程编排**。

### 为什么需要LangGraph？

**LangChain Agent的局限**：
- 难以处理复杂的循环逻辑
- 无法优雅地处理中断和恢复
- 多Agent协作困难
- 状态管理混乱

**LangGraph的解决方案**：
- 基于**有限状态机**的思想
- 所有数据流转通过**State状态对象**
- 支持**条件分支**和**循环**
- 内置**Checkpoint**持久化
- 原生支持**Human-in-the-loop**

### 必学核心概念详解

#### 1. State全局状态：所有节点共享的数据

```python
from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """Agent状态定义"""
    messages: Annotated[List, add_messages]  # 消息历史（自动追加）
    current_step: str                         # 当前步骤
    context: Optional[str]                    # 检索到的上下文
    tool_results: Optional[dict]              # 工具调用结果
    user_id: str                              # 用户ID
    session_id: str                           # 会话ID

# 所有节点共享这份状态，读写都通过state
# Annotated[List, add_messages] 表示消息会自动追加，而不是覆盖
```

**State设计原则**：
- **单一数据源**：所有数据都放在State中，不要用全局变量
- **不可变性**：节点返回新的State，不直接修改传入的State
- **类型安全**：使用TypedDict确保类型正确

#### 2. Node节点：执行逻辑的单元

```python
from langgraph.graph import StateGraph
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 初始化LLM
llm = ChatOpenAI(model="gpt-4o")

def research_node(state: AgentState):
    """研究节点 - 检索信息"""
    # 从state读取问题
    question = state["messages"][-1].content
    
    # 执行检索
    docs = retriever.invoke(question)
    context = "\n".join([d.page_content for d in docs])
    
    # 返回更新的状态（注意：不直接修改state）
    return {
        "context": context,
        "current_step": "research_complete"
    }

def answer_node(state: AgentState):
    """回答节点 - 生成答案"""
    # 从state读取
    question = state["messages"][-1].content
    context = state.get("context", "")
    
    # 定义RAG提示模板
    rag_prompt = ChatPromptTemplate.from_template("""
基于以下上下文回答问题。如果上下文中没有相关信息，请说不知道。

上下文：{context}
问题：{question}
回答：""")
    
    # 生成回答
    if context:
        response = llm.invoke(rag_prompt.format(context=context, question=question))
    else:
        response = llm.invoke(question)
    
    return {
        "messages": [response],  # 自动追加到messages
        "current_step": "answer_complete"
    }

def validate_node(state: AgentState):
    """验证节点 - 检查答案质量"""
    answer = state["messages"][-1].content
    
    # 简单验证逻辑
    if len(answer) < 10:
        return {"current_step": "needs_improvement"}
    else:
        return {"current_step": "valid"}
```

#### 3. Edge边：节点之间的连接

```python
from langgraph.graph import END
from langgraph.graph import StateGraph

# 示例：创建图并添加边
graph = StateGraph(AgentState)

# 普通边 - 无条件跳转
graph.add_edge("research_node", "answer_node")

# 条件边 - 根据状态决定跳转
def should_continue(state: AgentState):
    """决定是否继续"""
    step = state.get("current_step", "")
    
    if step == "needs_improvement":
        return "research_node"  # 重新研究
    elif step == "valid":
        return END  # 结束
    else:
        return "answer_node"  # 继续回答

# 添加条件边
graph.add_conditional_edges(
    "validate_node",        # 从哪个节点出发
    should_continue,        # 条件函数
    {
        "research_node": "research_node",  # 条件1
        "answer_node": "answer_node",      # 条件2
        END: END                           # 条件3
    }
)
```

#### 4. Checkpoint持久化：保存和恢复状态

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

# 初始化LLM
llm = ChatOpenAI(model="gpt-4o")

# 内存存储（开发测试用）
checkpointer = MemorySaver()

# SQLite存储（生产环境用）
checkpointer = SqliteSaver.from_conn_string("./checkpoints.db")

# 编译时添加checkpointer
app = graph.compile(checkpointer=checkpointer)

# 执行时指定thread_id（每个用户/会话一个ID）
config = {"configurable": {"thread_id": "user-123"}}

# 第一次对话
result1 = app.invoke(
    {"messages": [HumanMessage(content="你好")]},
    config
)

# 第二次对话（会记住之前的内容）
result2 = app.invoke(
    {"messages": [HumanMessage(content="我叫什么名字？")]},
    config
)

# 查看当前状态
state = app.get_state(config)
print("当前状态:", state.values)

# 查看历史状态（需要使用MemorySaver）
history = list(app.get_state_history(config))
print(f"历史状态数量: {len(history)}")
```

#### 5. Human-in-the-loop：人工介入

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# 初始化LLM
llm = ChatOpenAI(model="gpt-4o")

# 定义工具
@tool
def delete_file(filename: str) -> str:
    """删除指定文件"""
    return f"已删除文件: {filename}"

tools = [delete_file]

# 创建带人工介入的Agent
agent = create_react_agent(
    llm,
    tools,
    checkpointer=MemorySaver(),
    interrupt_before=["tools"]  # 在调用工具前暂停
)

# 执行
config = {"configurable": {"thread_id": "user-123"}}
result = agent.invoke(
    {"messages": [HumanMessage(content="帮我删除文件config.json")]},
    config
)

# 检查是否暂停
if result.get("__interrupt__"):
    print("等待人工确认...")
    print(f"即将调用的工具: {result['__interrupt__'].value}")
    
    # 人工审核后继续
    # 如果确认，传入None继续执行
    result = agent.invoke(None, config)
    
    # 如果拒绝，可以修改状态或终止
    # app.update_state(config, {"messages": [AIMessage(content="操作已取消")]})
```

**Human-in-the-loop使用场景**：
- **敏感操作审核**：删除文件、发送邮件、转账等
- **质量检查**：AI生成内容后，人工审核再发布
- **决策确认**：AI提出方案，人工确认后执行
- **数据标注**：AI预标注，人工修正

### 循序渐进实战项目

#### 项目1：简单聊天Graph

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated, List
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# 初始化LLM
llm = ChatOpenAI(model="gpt-4o")

class ChatState(TypedDict):
    messages: Annotated[List, add_messages]

def chat_node(state: ChatState):
    """聊天节点"""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 构建图
graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.set_entry_point("chat")
graph.add_edge("chat", END)

# 编译
app = graph.compile(checkpointer=MemorySaver())

# 多轮对话
config = {"configurable": {"thread_id": "session-1"}}

# 第1轮
app.invoke({"messages": [HumanMessage(content="你好")]}, config)

# 第2轮（会记住第1轮）
app.invoke({"messages": [HumanMessage(content="我叫小明")]}, config)

# 第3轮（会记住所有历史）
result = app.invoke(
    {"messages": [HumanMessage(content="我叫什么名字？")]},
    config
)
print(result["messages"][-1].content)  # 应该回答"小明"
```

#### 项目2：带工具调用Agent Graph（ReAct循环）

```python
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

# 初始化LLM
llm = ChatOpenAI(model="gpt-4o")

# 定义工具
@tool
def search_web(query: str) -> str:
    """搜索互联网获取信息"""
    # 这里调用实际搜索API
    return f"搜索结果：关于'{query}'的信息..."

@tool
def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        return str(eval(expression))
    except (SyntaxError, NameError, TypeError, ZeroDivisionError) as e:
        return f"计算错误：{e}"

tools = [search_web, calculator]

# 使用LangGraph预置的ReAct Agent
agent = create_react_agent(
    llm,
    tools,
    prompt="你是一个有帮助的助手，可以使用工具回答问题。请用中文回答。"
)

# 执行
result = agent.invoke({
    "messages": [HumanMessage(content="北京天气怎么样？帮我计算一下25度转换成华氏度是多少？")]
})

# 查看工具调用过程
print("对话过程:")
for msg in result["messages"]:
    if msg.type == "human":
        print(f"\n用户: {msg.content}")
    elif msg.type == "ai":
        if msg.content:
            print(f"\n助手: {msg.content}")
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  调用工具: {tc['name']}")
                print(f"  参数: {tc['args']}")
    elif msg.type == "tool":
        print(f"  工具结果: {msg.content}")
```

#### 项目3：RAG + LangGraph工作流

```python
from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 初始化LLM
llm = ChatOpenAI(model="gpt-4o")

class RAGState(TypedDict):
    messages: Annotated[List, add_messages]
    context: Optional[str]
    use_rag: bool
    confidence: float
    current_step: Optional[str]

def classify_node(state: RAGState):
    """分类节点 - 判断是否需要检索"""
    question = state["messages"][-1].content
    
    # 简单规则判断（也可以用LLM判断）
    use_rag = len(question) > 10 or "?" in question or "？" in question
    
    return {
        "use_rag": use_rag,
        "current_step": "classified"
    }

def retrieval_node(state: RAGState):
    """检索节点 - 从知识库检索"""
    question = state["messages"][-1].content
    
    # 检索相关文档
    docs = retriever.invoke(question)
    context = "\n".join([d.page_content for d in docs])
    
    # 计算置信度（简单版本）
    confidence = min(1.0, len(docs) / 3)  # 文档越多，置信度越高
    
    return {
        "context": context,
        "confidence": confidence,
        "current_step": "retrieved"
    }

def generate_node(state: RAGState):
    """生成节点 - 生成回答"""
    question = state["messages"][-1].content
    context = state.get("context", "")
    confidence = state.get("confidence", 0.0)
    
    # 定义RAG提示模板
    rag_prompt = ChatPromptTemplate.from_template("""
基于以下上下文回答问题。如果上下文中没有相关信息，请说不知道。

上下文：{context}
问题：{question}
回答：""")
    
    # 根据是否有上下文选择不同的prompt
    if context and confidence > 0.5:
        response = llm.invoke(rag_prompt.format(
            context=context,
            question=question
        ))
    else:
        # 没有足够上下文，直接回答
        response = llm.invoke(f"请回答以下问题：{question}")
    
    # 添加置信度信息
    answer = response.content
    if confidence < 0.5:
        answer += "\n\n[注意：此回答基于有限信息，置信度较低]"
    
    return {
        "messages": [AIMessage(content=answer)],
        "current_step": "generated"
    }

# 构建图
graph = StateGraph(RAGState)
graph.add_node("classify", classify_node)
graph.add_node("retrieve", retrieval_node)
graph.add_node("generate", generate_node)

# 设置入口
graph.set_entry_point("classify")

# 添加条件边
graph.add_conditional_edges(
    "classify",
    lambda state: "retrieve" if state["use_rag"] else "generate"
)

# 添加普通边
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

# 编译
app = graph.compile(checkpointer=MemorySaver())

# 使用
config = {"configurable": {"thread_id": "rag-session-1"}}
result = app.invoke(
    {"messages": [HumanMessage(content="什么是RAG？")]},
    config
)
print(result["messages"][-1].content)
```

#### 项目4：Human-in-the-loop审核

```python
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# 初始化LLM
llm = ChatOpenAI(model="gpt-4o")

class ReviewState(TypedDict):
    messages: Annotated[List, add_messages]
    draft: str
    approved: bool
    reviewer_comment: str

def draft_node(state: ReviewState):
    """草拟节点 - 生成草稿"""
    question = state["messages"][-1].content
    response = llm.invoke(f"请草拟以下内容的回复：{question}")
    return {"draft": response.content}

def review_node(state: ReviewState):
    """审核节点 - 人工审核（会暂停）"""
    # 这个节点会被interrupt_before暂停
    # 等待人工输入审核结果
    return {"approved": True}  # 实际会从外部输入

def publish_node(state: ReviewState):
    """发布节点 - 发布审核通过的内容"""
    if state.get("approved"):
        return {
            "messages": [AIMessage(content=f"已发布：{state['draft']}")]
        }
    else:
        return {
            "messages": [AIMessage(content=f"已拒绝：{state.get('reviewer_comment', '无评论')}")]
        }

# 构建图
graph = StateGraph(ReviewState)
graph.add_node("draft", draft_node)
graph.add_node("review", review_node)
graph.add_node("publish", publish_node)

graph.set_entry_point("draft")
graph.add_edge("draft", "review")
graph.add_edge("review", "publish")
graph.add_edge("publish", END)

# 编译时添加interrupt
app = graph.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["review"]  # 在审核前暂停
)

# 执行
config = {"configurable": {"thread_id": "review-1"}}
result = app.invoke(
    {"messages": [HumanMessage(content="写一篇关于AI发展趋势的文章")]},
    config
)

# 检查是否暂停
if result.get("__interrupt__"):
    print("等待人工审核...")
    print(f"草稿内容: {result.get('draft', '')[:100]}...")
    
    # 人工审核后继续
    # 方式1：直接继续（默认approved=True）
    result = app.invoke(None, config)
    
    # 方式2：修改状态后再继续
    # app.update_state(config, {"approved": False, "reviewer_comment": "需要更多细节"})
    # result = app.invoke(None, config)
    
    print("审核结果:", result["messages"][-1].content)
```

> **重要**：官方Cookbook示例一定要跑一遍，全部可在colab直接运行。

---

## 🚩 第五阶段：DeepAgents（1-2周）

> DeepAgents是LangChain团队提出的**高层Agent设计范式**，基于LangGraph运行时，封装了规划、子Agent调度、长任务管理等能力。**注意**：DeepAgents不是一个独立的pip包，而是一套设计模式和最佳实践，需要基于LangGraph自己实现。
> 
> **适合场景**：写调研报告、复杂多步骤任务
> 
> **不适合入门理解底层原理，所以放最后**

### 核心能力

- **任务规划**：自动分解复杂任务为子任务
- **并行子Agent**：多个Agent同时执行不同子任务
- **文件读写工具**：读取文档、写入报告
- **错误重试**：自动处理失败，重试机制
- **状态管理**：基于LangGraph的状态持久化
- **长上下文处理**：自动处理超过上下文窗口的长文档

### 快速上手：基于LangGraph实现DeepAgents模式

```python
from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

# 定义DeepAgent状态
class DeepAgentState(TypedDict):
    messages: Annotated[List, add_messages]
    task: str
    subtasks: List[str]
    results: List[str]
    current_subtask_index: int  # 当前执行到第几个子任务

# 初始化LLM
llm = ChatOpenAI(model="gpt-4o")

# 任务分解节点
def planner_node(state: DeepAgentState):
    """将复杂任务分解为子任务"""
    task = state["messages"][-1].content
    
    response = llm.invoke(f"""请将以下任务分解为3-5个子任务，每个子任务一行：

任务：{task}

子任务：""")
    
    subtasks = [s.strip() for s in response.content.split("\n") if s.strip()]
    return {"task": task, "subtasks": subtasks, "current_subtask_index": 0}

# 执行节点
def executor_node(state: DeepAgentState):
    """执行当前子任务"""
    idx = state.get("current_subtask_index", 0)
    subtasks = state.get("subtasks", [])
    subtask = subtasks[idx] if idx < len(subtasks) else ""
    context = "\n".join(state.get("results", []))
    
    response = llm.invoke(f"""基于以下上下文，执行当前子任务：

上下文：{context}

当前子任务：{subtask}

执行结果：""")
    
    return {
        "results": state.get("results", []) + [response.content],
        "current_subtask_index": idx + 1
    }

# 汇总节点
def summarizer_node(state: DeepAgentState):
    """汇总所有子任务结果"""
    results = "\n\n".join([f"子任务{i+1}结果：{r}" for i, r in enumerate(state.get("results", []))])
    
    response = llm.invoke(f"""请汇总以下子任务结果，生成完整报告：

{results}

报告：""")
    
    return {"messages": [AIMessage(content=response.content)]}

# 构建DeepAgent图
graph = StateGraph(DeepAgentState)
graph.add_node("planner", planner_node)
graph.add_node("executor", executor_node)
graph.add_node("summarizer", summarizer_node)

graph.set_entry_point("planner")
graph.add_edge("planner", "executor")
graph.add_conditional_edges(
    "executor",
    lambda state: "summarizer" if state.get("current_subtask_index", 0) >= len(state.get("subtasks", [])) else "executor"
)
graph.add_edge("summarizer", END)

app = graph.compile()

# 执行任务
result = app.invoke({
    "messages": [HumanMessage(content="分析RAG技术的优缺点，并给出实践建议")]
})
print(result["messages"][-1].content)
```

### 源码学习重点

1. **理解内部组装**：看它如何将任务转换为LangGraph节点
   - 任务分解逻辑
   - Agent调度策略
   - 状态流转机制

2. **学习调度策略**：子Agent如何分配和协调
   - 负载均衡
   - 依赖管理
   - 并行执行

3. **状态流转**：全局状态如何在各节点间传递
   - 状态合并策略
   - 冲突解决
   - 持久化机制

### 实战项目：文档研究Agent

```python
from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 定义研究Agent状态
class ResearchAgentState(TypedDict):
    messages: Annotated[List, add_messages]
    documents: List[str]
    analysis_results: List[str]
    current_doc_index: int
    final_report: Optional[str]

# 初始化组件
llm = ChatOpenAI(model="gpt-4o")
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

# 文档加载节点
def load_docs_node(state: ResearchAgentState):
    """加载并索引文档"""
    # 这里可以从文件路径加载PDF
    # docs = PyPDFLoader("paper.pdf").load()
    # chunks = RecursiveCharacterTextSplitter(chunk_size=500).split_documents(docs)
    # vectorstore = Chroma.from_documents(chunks, embeddings)
    
    return {"documents": ["文档1内容", "文档2内容", "文档3内容"]}

# 分析节点
def analyze_node(state: ResearchAgentState):
    """分析当前文档"""
    docs = state.get("documents", [])
    idx = state.get("current_doc_index", 0)
    
    if idx >= len(docs):
        return {"current_doc_index": idx}
    
    doc_content = docs[idx]
    response = llm.invoke(f"请分析以下文档的关键内容：\n{doc_content}")
    
    return {
        "analysis_results": state.get("analysis_results", []) + [response.content],
        "current_doc_index": idx + 1
    }

# 报告生成节点
def report_node(state: ResearchAgentState):
    """生成最终报告"""
    results = "\n\n".join([
        f"文档{i+1}分析：{r}" 
        for i, r in enumerate(state.get("analysis_results", []))
    ])
    
    response = llm.invoke(f"请基于以下分析结果，生成一份完整的研究报告：\n{results}")
    return {"final_report": response.content}

# 构建研究Agent图
graph = StateGraph(ResearchAgentState)
graph.add_node("load_docs", load_docs_node)
graph.add_node("analyze", analyze_node)
graph.add_node("report", report_node)

graph.set_entry_point("load_docs")
graph.add_edge("load_docs", "analyze")
graph.add_conditional_edges(
    "analyze",
    lambda state: "report" if state.get("current_doc_index", 0) >= len(state.get("documents", [])) else "analyze"
)
graph.add_edge("report", END)

app = graph.compile()

# 执行研究任务
result = app.invoke({
    "messages": [HumanMessage(content="研究RAG技术的最佳实践")]
})
print("研究报告：")
print(result.get("final_report", "未生成报告"))
```

---

## 🎯 完整学习项目清单

| 序号 | 项目 | 难度 | 时间 | 关键技能 | 产出物 |
|------|------|------|------|----------|--------|
| 1 | 调用LLM原生API实现多轮对话 | ⭐ | 1天 | API调用、消息管理 | 多轮对话程序 |
| 2 | 手写简易RAG（不使用LangChain） | ⭐⭐ | 3天 | 向量检索、Prompt组装 | 基础RAG系统 |
| 3 | LangChain+LCEL实现RAG知识库问答 | ⭐⭐ | 2天 | LCEL链式调用 | LCEL RAG应用 |
| 4 | LangChain简单工具Agent（搜索+计算器） | ⭐⭐⭐ | 2天 | Function Calling | 工具Agent |
| 5 | LangGraph手写ReAct工具Agent循环 | ⭐⭐⭐ | 3天 | State、Node、Edge | ReAct Agent |
| 6 | LangGraph实现带RAG检索分支的问答系统 | ⭐⭐⭐⭐ | 3天 | 条件边、分支逻辑 | 智能RAG系统 |
| 7 | LangGraph实现Human-in-loop人工审核Agent | ⭐⭐⭐⭐ | 2天 | Checkpoint、中断恢复 | 审核Agent |
| 8 | DeepAgents做文档调研报告Agent | ⭐⭐⭐⭐⭐ | 3天 | 多Agent协作 | 研究报告系统 |

**学习建议**：
1. **循序渐进**：按照顺序完成，不要跳跃
2. **动手实践**：每个项目都要亲手敲代码
3. **记录笔记**：记录遇到的问题和解决方案
4. **寻求帮助**：遇到困难时，查阅官方文档或社区

---

## 📚 官方优先参考资料

> **不要看太多过时博客**，以官方文档为准。

| 资源 | 链接 | 用途 | 优先级 |
|------|------|------|--------|
| LangChain Python官方文档 | https://python.langchain.com/ | 核心API参考 | ⭐⭐⭐⭐⭐ |
| LangGraph官方文档 | https://langchain-ai.github.io/langgraph/ | 图编排指南 | ⭐⭐⭐⭐⭐ |
| LangGraph Cookbook | https://github.com/langchain-ai/langgraph/tree/main/docs/cookbook | 实战示例 | ⭐⭐⭐⭐ |
| LangSmith | https://smith.langchain.com/ | 调试追踪 | ⭐⭐⭐⭐⭐ |
| OpenAI Cookbook | https://cookbook.openai.com/ | API使用示例 | ⭐⭐⭐⭐ |

**学习资源使用建议**：
1. **官方文档为主**：API参考、教程、示例代码
2. **Cookbook必跑**：每个示例都亲手运行一遍
3. **LangSmith必用**：每个项目都打开trace
4. **社区为辅**：Stack Overflow、GitHub Issues、Reddit

> **关键习惯**：每一个项目都打开LangSmith trace，看每一步流转，这是排错最重要手段。

---

## ⚠️ 新手高频踩坑提醒

### 1. 不要上来直接DeepAgents
**问题**：高层封装会掩盖底层细节，遇到bug看不懂。

**解决方案**：必须先掌握LangGraph，理解State、Node、Edge的核心概念。

### 2. 不要只复制代码跑通
**问题**：不理解代码逻辑，遇到问题无法调试。

**解决方案**：一定要看懂每一步输入输出；利用LangSmith看trace，理解数据流转。

### 3. 模型必须支持Function-Calling
**问题**：国产模型要确认工具调用能力，很多小模型工具调用不稳定。

**推荐模型**：
- **首选**：DeepSeek-V3、Qwen2.5、GLM-4
- **备选**：GPT-4o、Claude-3.5 Sonnet
- **避免**：小模型（7B以下）的工具调用通常不稳定

### 4. RAG不要迷信大chunk
**问题**：chunk_size越大不一定越好，调优chunk大小、overlap、rerank是重点。

**建议**：
- 从chunk_size=500开始实验
- overlap设为10%-20%
- 添加Reranker提升精度

### 5. LangGraph核心是State状态
**问题**：所有数据流转尽量走状态对象，不要用全局变量。

**原则**：State是唯一的"真相来源"，所有节点都通过State读写数据。

### 6. 不要沉迷各种花哨Agent框架
**问题**：CrewAI、AutoGen等框架分散精力，学不精。

**建议**：把RAG+LangGraph吃透，绝大多数业务需求都能覆盖。其他框架可以了解，但不要深入。

### 7. 生产环境注意成本
**问题**：每次调用LLM都有token成本，容易超预算。

**解决方案**：
- 使用缓存避免重复调用
- 设置max_tokens限制输出长度
- 监控token使用量
- 考虑使用更便宜的模型

### 8. 异步处理很重要
**问题**：同步调用会阻塞，影响用户体验。

**解决方案**：生产环境务必使用异步调用（`ainvoke`、`astream`）。

### 9. 错误处理不可忽视
**问题**：网络超时、API限流、模型错误等异常情况。

**解决方案**：
- 添加重试机制
- 设置超时时间
- 记录错误日志
- 实现降级策略

### 10. 测试驱动开发
**问题**：没有测试，bug难以发现。

**解决方案**：
- 为每个组件编写单元测试
- 使用LangSmith进行A/B测试
- 建立评估指标

---

## 可选补充方向（学完主线之后）

| 方向 | 内容 | 推荐资源 | 学习时间 |
|------|------|----------|----------|
| **向量库进阶** | Milvus、PgVector、Pinecone | 各数据库官方文档 | 1-2周 |
| **Agent评估** | 用LangSmith做评测集，评测RAG/Agent效果 | LangSmith评测指南 | 1周 |
| **部署上线** | LangServe封装API、Docker容器化、云服务部署 | FastAPI + LangServe | 1-2周 |
| **性能优化** | 流式输出、缓存机制、批量处理 | LangChain高级特性 | 1周 |
| **多模态** | 图片、音频、视频理解与生成 | 多模态模型API | 2-3周 |
| **对比框架** | CrewAI、AutoGen、MetaGPT | 各框架GitHub | 1周 |
| **监控 observability** | LangSmith、Langfuse、Phoenix | 各平台文档 | 1周 |
| **安全** | Prompt注入防护、内容过滤、权限控制 | 安全最佳实践 | 1周 |

---

## 学习路线图（可视化）

```
Week 1-2: 前置基础
├── Python语法与工具
│   ├── 函数、类、异常处理
│   ├── 包管理（pip/uv）
│   └── 调试技巧
├── LLM API调用（单轮/多轮/流式）
│   ├── OpenAI兼容接口
│   ├── 流式输出
│   └── 多轮对话管理
├── Prompt工程（CoT/Few-shot/ReAct）
│   ├── 思维链
│   ├── Few-shot示例
│   └── ReAct范式
└── 基础概念（RAG/Agent/向量数据库）
    ├── RAG流程
    ├── Agent三要素
    └── 向量数据库选择

Week 3-5: RAG完整实现
├── 文档加载与切分
│   ├── 各种加载器
│   ├── 切分策略
│   └── Chunk调优
├── Embedding向量化
│   ├── 模型选择
│   ├── 批量处理
│   └── 效果评估
├── 向量库操作
│   ├── Chroma/FAISS
│   ├── 检索策略
│   └── 性能优化
├── Prompt组装与生成
│   ├── 模板设计
│   ├── Few-shot
│   └── 置信度提示
└── 优化：Reranker/混合检索
    ├── 重排序
    ├── 混合检索
    └── Query改写

Week 6-8: LangChain基础
├── ChatModel与Messages
│   ├── 统一接口
│   ├── 消息体系
│   └── 流式输出
├── PromptTemplate
│   ├── 模板设计
│   ├── 消息占位符
│   └── 格式化
├── LCEL表达式语言
│   ├── 管道语法
│   ├── 自动流式/异步
│   └── 重试机制
├── Tool封装与Function Calling
│   ├── 工具定义
│   ├── 参数验证
│   └── 错误处理
├── Memory记忆系统
│   ├── 缓冲记忆
│   ├── 窗口记忆
│   └── 摘要记忆
└── LangSmith调试
    ├── 环境配置
    ├── Trace查看
    └── 成本监控

Week 9-12: LangGraph核心
├── State状态管理
│   ├── TypedDict定义
│   ├── 状态更新
│   └── 类型安全
├── Node节点开发
│   ├── 节点函数
│   ├── 输入输出
│   └── 错误处理
├── Edge条件分支
│   ├── 普通边
│   ├── 条件边
│   └── 分支逻辑
├── Checkpoint持久化
│   ├── 内存存储
│   ├── SQLite存储
│   └── 状态恢复
├── Human-in-the-loop
│   ├── 中断机制
│   ├── 人工审核
│   └── 状态修改
└── 多Agent协作
    ├── Agent定义
    ├── 任务分配
    └── 结果汇总

Week 13-14: DeepAgents高层封装
├── 任务规划与分解
│   ├── 任务定义
│   ├── 子任务分解
│   └── 依赖管理
├── 并行子Agent
│   ├── Agent创建
│   ├── 并行执行
│   └── 结果合并
├── 文件读写工具
│   ├── 文档读取
│   ├── 报告生成
│   └── 格式转换
└── 源码学习
    ├── 内部组装
    ├── 调度策略
    └── 状态流转
```

---

## 常见问题解答（FAQ）

### Q1: 我应该选择哪个LLM？
**A**: 
- **预算充足**：GPT-4o 或 Claude-3.5 Sonnet（效果最好）
- **性价比**：DeepSeek-V3 或 Qwen2.5（国内访问快，价格便宜）
- **本地部署**：Ollama + Qwen2.5:7b（无需API，隐私安全）

### Q2: 向量数据库怎么选？
**A**:
- **入门学习**：Chroma（零配置，本地运行）
- **生产环境**：Milvus（高性能，可扩展）
- **已有PostgreSQL**：PgVector（无需额外部署）

### Q3: LangChain和LlamaIndex有什么区别？
**A**:
- **LangChain**：通用的LLM应用开发框架，适合各种场景
- **LlamaIndex**：专注于数据索引和检索，RAG场景更专业
- **建议**：先学LangChain，需要时再学LlamaIndex

### Q4: 如何处理长文档？
**A**:
- **切分**：将长文档切分成小chunk
- **摘要**：先生成摘要，再基于摘要检索
- **层级索引**：建立文档-段落-句子的层级索引
- **MapReduce**：并行处理多个chunk，再汇总

### Q5: 如何评估RAG系统效果？
**A**:
- **检索精度**：检索到的文档是否相关
- **召回率**：是否检索到了所有相关文档
- **回答准确性**：生成的答案是否正确
- **用户满意度**：用户对回答的评价
- **工具**：LangSmith评测、RAGAS框架

### Q6: 生产环境需要注意什么？
**A**:
- **错误处理**：网络超时、API限流、模型错误
- **性能优化**：缓存、异步、批量处理
- **成本控制**：token监控、模型选择、缓存策略
- **安全**：Prompt注入防护、内容过滤、权限控制
- **监控**：日志、指标、告警

### Q7: 如何持续学习？
**A**:
- **官方文档**：定期查看更新
- **社区动态**：关注GitHub、Twitter、Reddit
- **实践项目**：不断做新项目
- **分享交流**：写博客、参加社区活动
- **源码阅读**：理解框架内部原理

---

## 下一步行动

1. **立即开始**：从Week 1开始，每天投入2-3小时
2. **动手实践**：每完成一个项目，在LangSmith查看trace
3. **记录学习**：建立自己的笔记系统，记录问题和解决方案
4. **寻求帮助**：遇到问题先查官方文档，再搜索社区
5. **分享交流**：写学习博客，参与社区讨论
6. **持续迭代**：根据实际需求，不断优化和扩展

**学习建议**：
- 不要急于求成，扎实基础比追求速度更重要
- 遇到问题不要慌，这是学习的必经之路
- 多动手实践，代码写多了自然就熟练了
- 保持好奇心，不断探索新技术和新场景
- 可以参考官方Cookbook中的示例代码，从最简单RAG开始，逐步实现LangGraph工具Agent

---

## 结语

从零到一掌握LLM应用开发是一个循序渐进的过程。这份路线图为你指明了方向，但真正的学习在于实践。

记住：
- **RAG是基础**，解决知识问答的核心问题
- **LangChain是工具**，提供标准化的开发接口
- **LangGraph是核心**，解决复杂工作流编排
- **DeepAgents是进阶**，掌握后可以快速搭建复杂Agent

不要急于求成，扎实基础，一步步来。当你完成所有项目时，你将具备构建生产级LLM应用的能力。

祝你学习顺利！🚀
