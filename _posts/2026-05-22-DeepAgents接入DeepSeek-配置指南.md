---
layout: post
title: DeepAgents 接入 DeepSeek 配置指南
summary: >
  Guide for integrating DeepSeek as the LLM backend for DeepAgents, covering
  uv package management, API key setup, and Windows verification.
lang: zh-CN
date: 2026-05-22 02:06:00
categories:
- AI & LLM
tags:
- DeepAgents
- LLM
---

引用[DeepAgents接入DeepSeek 配置指南](https://chat.deepseek.com/share/52ikg61qsi9au9e3wf)

<!--more-->
---

## 环境准备
本次基于Windows进行验证

### 包管理器uv
[uv (An extremely fast Python package and project manager, written in Rust.)](https://docs.astral.sh/uv/)

1. 安装uv
Use irm to download the script and execute it with iex:`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
安装完成后重新启动CMD，键入`uv`识别到相应指令
2. 安装python
`uv install python`
3. 初始化工程
`uv init`
4. 创建虚拟环境
`uv venv`
5. 安装包
`uv pip install deepagents dotenv langchain_deepseek`

## 工程代码

### 定义模型文件
```python
# llm.py
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

load_dotenv()

deepseek_model = ChatDeepSeek(
    model="deepseek-chat", # 模型名称
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # 关键一步：关闭思考模式
    extra_body={"thinking": {"type": "disabled"}}
)
```

### 主程序文件
```python
# main.py
from deepagents import create_deep_agent
from llm import deepseek_model # 导入刚才配置好的模型

# 定义系统提示词，明确 Agent 的角色和任务
research_instructions = """你是一名专业资深研究员..."""

# 创建 Agent
agent = create_deep_agent(
    model=deepseek_model, # 这里直接传入配置好的模型对象
    # tools=[...], # 根据需要添加你的工具
    system_prompt=research_instructions,
)

# 调用 Agent
result = agent.invoke({"messages": [{"role": "user", "content": "什么是 langgraph?"}]})
print(result["messages"][-1].content)
```

## 配置 API Key
[DeepSeek API Keys](https://platform.deepseek.com/api_keys)
```text
# .env
DEEPSEEK_API_KEY="DeepSeek_API_Key"
```

## 运行测试
`uv run main.py`

## 工程结构
主要文件如下：
```shell
.env
llm.py
main.py
```