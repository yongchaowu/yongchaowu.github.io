---
layout: post
title: MiniCPM5 1B Deploy Ollama
display_title: 'Deploying MiniCPM5-1B with Ollama'
date: 2026-06-10 07:45:00
categories:
- AI & LLM
tags:
- Model
- OS
- Docker
---

CPU版本
## 必备文件

<!--more-->
- ollama_docker_image.tar Ollama镜像
- open-webui_image.tar    Open-WebUI镜像
- Models 模型
    - MiniCPM5-1B-F16.gguf
    - MiniCPM5-1B-Q8_0.gguf
    - MiniCPM5-1B-Q4_K_M.gguf
- Modelfile Ollama模型配置文件
- [ollama.md](https://github.com/OpenBMB/MiniCPM/blob/main/docs/deployment/ollama.md)

## 部署步骤

1. 导入镜像

    - `docker load -i ollama_docker_image.tar`
    - `docker load -i open-webui_image.tar`

2. 启动并导入模型

    `docker run -d -v ./ollama:/root/.ollama -p 11434:11434 --name ollama --restart always ollama/ollama`

    可增加参数
    - `--memory=11g` 限制内存11GB
    - `--cpus=6`     限制核心6个 

3. 创建自定义模型文件Modelfile或使用现有文件修改模型路径

    `FROM /path/to/MiniCPM5-1B-F16.gguf  # 从本机路径加载模型文件`

4. 进入容器

    - `docker exec -it ollama /bin/bash`
    - `cd /root/.ollama #model_data`

5. 导入模型

    `ollama create MiniCPM5-1B-Q4_K_M -f ./Modelfile`
    MiniCPM5-1B-Q4_K_M为管理列表中模型名称
6. 运行模型

    `ollama run MiniCPM5-1B-Q4_K_M`

7. 验证模型

    - `ollama list`
    - `curl http://localhost:11434`
    - `curl http://localhost:11434/api/tags #查看模型列表`

    注意：windows系统powershell中使用`curl.exe`

8. API Access

    - OpenAI-compatible REST endpoint
    ```shell
    curl http://localhost:11434/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
            "model": "MiniCPM5-1B-Q4_K_M",
            "messages": [{"role": "user", "content": "用一句话解释 GQA。"}],
            "temperature": 0.9, "top_p": 0.95, "max_tokens": 1024
        }'
    ```

    - Ollama-native API
    ```shell
    curl http://localhost:11434/api/chat -d '{
            "model": "MiniCPM5-1B-Q4_K_M",
            "messages": [{"role":"user","content":"1+1=?"}],
            "stream": false,
            "options": {"temperature": 0.7, "top_p": 0.95}
        }'
    ```

9. 前端可视化配置，配置Open-WebUI

    - 启动命令：
    `docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main`
    - 首次登录配置管理员用户
    - 登录页面：`ip:3000`

10. 虚拟机网络配置
    - 可通过虚拟机ip直接访问
    - Nat模式配置端口转发
    - 桥接模式


## GPU版本
以NVIDIA显卡,Ubuntu22.04系统为例

1. 前置依赖：安装NVIDIA容器工具
```shell
# 导入密钥与源
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 安装工具包
sudo apt update
sudo apt install -y nvidia-container-toolkit

# 配置Docker使用NVIDIA运行时
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

```

2. 一键启动 Ollama（N 卡 GPU 直通）

- 命令行方式
```shell
# 全部GPU
docker run -d \
  --gpus=all \
  -v ollama_data:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama

# 只指定GPU0、GPU1（多显卡）
docker run -d \
  --gpus '"device=0,1"' \
  -v ollama_data:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama

```

- docker-compose.yml `docker compose up -d`
```shell
version: "3.8"
services:
  ollama:
    image: ollama/ollama
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped

volumes:
  ollama_data:

```

3. 验证 GPU 是否生效
- 查看容器内识别显卡:`docker exec -it ollama nvidia-smi`
- 运行模型看是否调用 GPU