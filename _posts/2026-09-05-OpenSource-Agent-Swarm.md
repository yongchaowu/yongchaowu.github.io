---

layout: post
title: 'Agent Swarm: 部署一个自主协作的 AI 编程团队'
summary: 'Introduction to Agent Swarm, an open-source multi-agent AI operating system, with a step-by-step focus on offline deployment of its Docker-based Lead and Worker architecture.'
lang: zh-CN
date: 2026-09-05 09:32:00
categories:
- AI & LLM
tags:
- Open Source
- AI Coding Agent
- Docker
---
{% raw %}
[GitHub: desplega-ai/agent-swarm](https://github.com/desplega-ai/agent-swarm) · [官网](https://www.agent-swarm.dev/) · [文档](https://docs.agent-swarm.dev/docs)

---

Agent Swarm 是一个开源的「AI 操作系统」——它让你拥有一支自主协作的 AI 编程团队。一个 Lead Agent 接收任务（来自 Slack、GitHub 或 API），拆解为子任务，分发给运行在 Docker 容器中的 Worker Agent。Worker 独立执行、汇报进度、提交代码——全程无需人工干预。

这篇文章聚焦一个实用场景：**在离线/气隙环境中部署 Agent Swarm**。无论你是需要在内网服务器上运行，还是出于安全考虑不能连接外网，这套方案都能帮你把 AI Agent 跑起来。

{% endraw %}

<!--more-->
{% raw %}

## 架构概览

Agent Swarm 采用 Hub-and-Spoke 架构：

```
┌───────────────────────────────────────────────────────────────┐
│                       Docker Compose                          │
│                                                               │
│  ┌───────────────┐    ┌──────────────────────────────────┐   │
│  │  API Server    │    │  Worker Agent                     │   │
│  │  :3013         │◄───│  - Claude Code CLI                │   │
│  │  SQLite        │    │  - Codex CLI                      │   │
│  │  Lead Agent    │    │  - Pi-mono CLI                    │   │
│  │  (协调者)      │    │  - DeepSeek (Anthropic API)       │   │
│  └───────────────┘    └──────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
```

核心组件：

- **API Server**：中心协调节点，基于 MCP 协议暴露工具，管理任务分发，所有状态存储在 SQLite 中
- **Worker Agent**：执行层，每个 Worker 运行在独立的 Docker 容器中，拥有完整的开发环境（Python、Node.js、Git 等）
- **Lead Agent**：协调者，接收任务、拆解、分配给 Worker，监控进度

## 离线部署完整指南

### Step 1: 构建 API 镜像

在一台联网的机器上构建：

```bash
cd /path/to/agent-swarm

# 构建 API 镜像
sudo docker build -f Dockerfile -t agent-swarm-api:local .
```

> **Note**：如果 Archil 下载失败，构建会自动跳过它（可选组件）。

### Step 2: 构建 Worker 镜像

```bash
# 构建 Worker 镜像
sudo docker build --no-cache -f Dockerfile.worker --build-arg INSTALL_ARCHIL=false -t agent-swarm-worker:local .
```

### Step 3: 导出镜像

```bash
# 将两个镜像打包为 tar 文件
sudo docker save agent-swarm-api:local agent-swarm-worker:local > agent-swarm-images.tar

# 检查文件大小
ls -lh agent-swarm-images.tar
```

### Step 4: 传输到目标机器

根据你的环境选择传输方式：

```bash
# 通过 SSH 传输
scp agent-swarm-images.tar user@target-machine:/path/to/offline-deploy/

# 或者通过 USB 拷贝
cp agent-swarm-images.tar /mnt/usb/
```

### Step 5: 在目标机器上加载镜像

```bash
# 加载镜像
sudo docker load < agent-swarm-images.tar

# 验证
sudo docker images | grep agent-swarm
```

### Step 6: 配置环境

在目标机器上创建部署目录，并编写 `docker-compose.yml`：

```bash
mkdir -p /path/to/offline-deploy
cd /path/to/offline-deploy
```

以下是单 Worker 的配置示例：

```yaml
services:
  api:
    image: agent-swarm-api:local
    ports:
      - "3013:3013"
    environment:
      API_KEY: "your-secret-key"
    volumes:
      - api-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3013/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  worker:
    image: agent-swarm-worker:local
    depends_on:
      api:
        condition: service_healthy
    environment:
      API_KEY: "your-secret-key"
      MCP_BASE_URL: http://api:3013
      HARNESS_PROVIDER: claude
      # DeepSeek 作为 Anthropic 兼容 Provider
      ANTHROPIC_API_KEY: "sk-your-deepseek-api-key"
      ANTHROPIC_BASE_URL: "https://api.deepseek.com/anthropic"
      # 禁用在线集成
      SLACK_DISABLE: "true"
      GITHUB_DISABLE: "true"
      LINEAR_DISABLE: "true"
      JIRA_DISABLE: "true"
    volumes:
      - ./workspace:/workspace
      - ./logs:/logs
    restart: unless-stopped

volumes:
  api-data:
```

### Step 7: 启动服务

```bash
sudo docker compose up -d
```

检查状态：

```bash
sudo docker compose ps
sudo docker compose logs -f
```

### Step 8: 验证

```bash
# 健康检查
curl http://localhost:3013/health

# 提交一个测试任务
curl -X POST http://localhost:3013/api/tasks \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"task": "Write a hello world program in Python", "priority": 50}'
```

## 多种 Provider 配置方案

Agent Swarm 支持多种 AI Provider。以下是 worker 服务的配置片段，需与 Step 6 中的 api 服务组合使用：

### 使用 OpenCode + DeepSeek（OpenAI 格式）

```yaml
worker:
  image: agent-swarm-worker:local
  depends_on:
    api:
      condition: service_healthy
  environment:
    API_KEY: "your-secret-key"
    MCP_BASE_URL: http://api:3013
    AGENT_ROLE: worker
    HARNESS_PROVIDER: opencode
    DISABLE_AUTOUPDATER: "1"
    SLACK_DISABLE: "true"
    GITHUB_DISABLE: "true"
    LINEAR_DISABLE: "true"
    JIRA_DISABLE: "true"
    # DeepSeek via OpenAI-compatible endpoint
    OPENAI_API_KEY: "sk-your-deepseek-api-key"
    # OPENAI_BASE_URL: "https://api.deepseek.com/v1"
    # MODEL_OVERRIDE: "vllm/deepseek-v4-flash"
    CONTEXT_MODE_DISABLED: "true"  # 修复 Qwen system message 顺序问题
  volumes:
    - ./workspace:/workspace
    - ./logs:/logs
    - ./opencode.json:/home/worker/.config/opencode/opencode.json
  restart: unless-stopped
```

### 使用 Claude（Anthropic 兼容格式）

```yaml
worker:
  image: agent-swarm-worker:local
  depends_on:
    api:
      condition: service_healthy
  environment:
    API_KEY: "your-secret-key"
    MCP_BASE_URL: http://api:3013
    AGENT_ROLE: worker
    HARNESS_PROVIDER: claude
    DISABLE_AUTOUPDATER: "1"
    SLACK_DISABLE: "true"
    GITHUB_DISABLE: "true"
    LINEAR_DISABLE: "true"
    JIRA_DISABLE: "true"
    ANTHROPIC_API_KEY: "sk-your-deepseek-api-key"
    ANTHROPIC_BASE_URL: "https://api.deepseek.com/anthropic"
  volumes:
    - ./workspace:/workspace
    - ./logs:/logs
  restart: unless-stopped
```

### 使用 DeepSeek 原生 Provider

```yaml
worker:
  image: agent-swarm-worker:local
  depends_on:
    api:
      condition: service_healthy
  environment:
    API_KEY: "your-secret-key"
    MCP_BASE_URL: http://api:3013
    AGENT_ROLE: worker
    HARNESS_PROVIDER: opencode
    DISABLE_AUTOUPDATER: "1"
    SLACK_DISABLE: "true"
    GITHUB_DISABLE: "true"
    LINEAR_DISABLE: "true"
    JIRA_DISABLE: "true"
    # DeepSeek via native provider
    DEEPSEEK_API_KEY: "sk-your-deepseek-api-key"
    MODEL_OVERRIDE: "deepseek/deepseek-chat"
  volumes:
    - ./workspace:/workspace
    - ./logs:/logs
  restart: unless-stopped
```

## OpenCode 配置文件详解

通过挂载 `opencode.json`，可以精确控制 Worker 使用的 Provider 和模型。在宿主机上创建该文件，然后通过 Docker volume 挂载到容器内 `/home/worker/.config/opencode/opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "vllm": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "vLLM 本地模型",
      "options": {
        "baseURL": "https://api.deepseek.com/v1",
        "apiKey": "sk-your-api-key"
      },
      "transform": {
        "reorderSystemMessage": true
      },
      "models": {
        "deepseek-v4-flash": {
          "name": "deepseek-v4-flash"
        }
      }
    }
  },
  "model": "vllm/deepseek-v4-flash"
}
```

关键点：

- `provider` 定义了可用的 AI 提供商
- `model` 字段激活默认配置
- `transform.reorderSystemMessage: true` 解决部分模型的 system message 顺序问题

## 快速验证

创建以下 `demo.sh` 脚本用于验证部署：

```bash
#!/bin/bash
# demo.sh - Agent Swarm 本地演示

API="http://localhost:3013"
API_KEY="your-secret-key"

echo "=== Agent Swarm Demo ==="
echo ""

# 检查运行模式
if sudo docker ps --format '{{.Names}}' | grep -q "worker-2"; then
  echo "Running: Multi-worker setup (3 workers)"
elif sudo docker ps --format '{{.Names}}' | grep -q "worker"; then
  echo "Running: Single worker setup"
else
  echo "No services running. Start with:"
  echo "  sudo docker compose up -d"
  exit 1
fi
echo ""

# 1. 健康检查
echo "1. Checking API health..."
HEALTH=$(curl -s "$API/health" 2>/dev/null)
if [ -z "$HEALTH" ]; then
  echo "API not running."
  exit 1
fi
echo "API is running"
echo ""

# 2. 创建任务
echo "2. Creating a task..."
RESPONSE=$(curl -s -X POST "$API/api/tasks" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Write a simple Python function that calculates the Fibonacci sequence up to n terms. Include docstring and type hints.",
    "priority": 50,
    "tags": ["demo", "python"]
  }')
echo "Response: $RESPONSE"
echo ""

# 3. 等待并检查
echo "3. Waiting 10s for worker to pick up task..."
sleep 10

echo "4. Current tasks:"
curl -s -H "Authorization: Bearer $API_KEY" "$API/api/tasks" 2>/dev/null
echo ""
echo ""
echo "=== Done ==="
```

运行方式：

```bash
chmod +x demo.sh
./demo.sh
```

运行后，Worker 生成的文件会通过 volume 挂载保存到宿主机的 `./workspace/personal/` 目录下。

## 常用运维命令

| 操作 | 命令 |
|------|------|
| 启动服务 | `sudo docker compose up -d` |
| 停止服务 | `sudo docker compose down` |
| 查看日志 | `sudo docker compose logs -f` |
| 检查状态 | `sudo docker compose ps` |
| 进入 Worker 容器 | `sudo docker compose exec worker bash`（多 Worker 时改为 `worker-1` 等） |
| 清除数据和挂载 | `sudo docker compose down -v` |

查看生成的文件：

```bash
ls -la workspace/personal/
cat workspace/personal/fibonacci.py
```

## 踩坑记录与最佳实践

在实际部署中总结的几条经验：

**1. Qwen 模型的 system message 问题**

使用 vLLM + Qwen3.5-397B 时，会遇到 `system message must be at the beginning` 错误。在环境变量中设置 `CONTEXT_MODE_DISABLED: "true"` 可以规避。

**2. docker compose 命令的一致性**

`docker compose up` 默认使用 `docker-compose.yml`，对应的 `docker compose ps` 也使用同一个文件。如果通过 `-f xx.yml` 指定了配置文件，后续所有命令都需要加上 `-f xx.yml`。

**3. OpenCode Provider 配置层级**

配置可以叠加，优先级从高到低：
1. 环境变量 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`MODEL_OVERRIDE`
2. 挂载的 `opencode.json` 配置文件
3. 默认配置

**4. 文件挂载技巧**

通过 Docker Volume 可以替换 Worker 容器内的任意配置文件：

```yaml
volumes:
  - ./opencode.json:/home/worker/.config/opencode/opencode.json
```

**5. 多 Worker 扩展**

需要并行处理多个任务时，可以启动多个 Worker：

```yaml
services:
  api:
    image: agent-swarm-api:local
    ports:
      - "3013:3013"
    environment:
      API_KEY: "your-secret-key"
    volumes:
      - api-data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3013/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  worker-1:
    image: agent-swarm-worker:local
    depends_on:
      api:
        condition: service_healthy
    environment:
      API_KEY: "your-secret-key"
      MCP_BASE_URL: http://api:3013
      HARNESS_PROVIDER: opencode
      OPENAI_API_KEY: "sk-your-api-key"
    volumes:
      - ./workspace:/workspace
      - ./logs:/logs
    restart: unless-stopped

  worker-2:
    image: agent-swarm-worker:local
    depends_on:
      api:
        condition: service_healthy
    environment:
      API_KEY: "your-secret-key"
      MCP_BASE_URL: http://api:3013
      HARNESS_PROVIDER: opencode
      OPENAI_API_KEY: "sk-your-api-key"
    volumes:
      - ./workspace:/workspace
      - ./logs:/logs
    restart: unless-stopped

volumes:
  api-data:
```

## 总结

Agent Swarm 提供了一套完整的多 Agent 协作方案。通过 Docker 容器化部署，即使是离线环境也能快速搭建起 AI 编程团队。它的核心价值在于：

- **自主协作**：Lead Agent 自动拆解任务，分发给 Worker
- **隔离执行**：每个 Worker 运行在独立容器中，互不干扰
- **可扩展**：支持多种 AI Provider，可以通过增加 Worker 水平扩展
- **持久记忆**：Agent 会学习并积累经验，越用越聪明

如果你对多 Agent 协作、AI Native 开发流程感兴趣，Agent Swarm 值得一试。
{% endraw %}
