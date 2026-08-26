---
layout: post
title: "Model-MiniCPM5-1B-Deploy-llama.cpp(Docker)"
date: 2026-06-10 07:47:00
categories: ["Model"]
tags: ["Model", "OS"]
---

CPU版本
## 必备文件

<!--more-->
- llama.cpp-cpu_image.tar llama-server:cpu镜像
- open-webui_image.tar    Open-WebUI镜像
- Models 模型
    - MiniCPM5-1B-F16.gguf
    - MiniCPM5-1B-Q8_0.gguf
    - MiniCPM5-1B-Q4_K_M.gguf
- docker-compose.yml 
- llama.cpp.zip 源码包，可用于用户编译
- [llama_cpp.md](https://github.com/OpenBMB/MiniCPM/blob/main/docs/deployment/llama_cpp.md)

## 部署步骤

1. 修改docker-compose.yml

    修改挂载的模型路径、名称
    ```shell
    目录结构：
    文件夹/
    ├── docker-compose.yml
    └── models/
        └── MiniCPM5-1B-Q4_K_M.gguf  <-- 把模型放这里
    ```

2. 启动llama-server:cpu容器

    - `docker compose up -d`
    - `docker compose down # 停止服务`

3. 启动Open-WebUI容器

    `docker run -d -p 3000:8080 -v ./open-webui-data:/app/backend/data -v ./embedding_model/all-MiniLM-L6-v2:/app/backend/models/all-MiniLM-L6-v2 -e OPENAI_API_BASE_URL=http://192.168.121.131:8080/v1 -e OPENAI_API_KEY=dummy -e RAG_EMBEDDING_MODEL=/app/backend/models/all-MiniLM-L6-v2 -e USER_AGENT="open-webui-local"  -e HF_HUB_OFFLINE=true -e ENABLE_MODEL_HUB=false --name open-webui-llamacpp --restart always --health-start-period=60s ghcr.io/open-webui/open-webui:main`

    配置open-webui连接地址:`http://ip:8080/v1`(localhost不行)

4. 访问地址

    `http://ip:3000`


## docker-compose.yml

```plaintext
version: '3.8'

services:
  llama-server:
    image: llama-cpp-server:cpu  # 对应你构建的镜像
    container_name: llama-server
    ports:
      - "8080:8080"  # 主机端口:容器端口
    volumes:
      - ./models:/models  # 挂载本地模型目录到容器
    command: >
      ./llama-server
      -m /models/MiniCPM5-1B-Q4_K_M.gguf
      --host 0.0.0.0
      --port 8080
      -ngl 99
      -c 8192
      --jinja
      --alias MiniCPM5-1B-Q4
    restart: unless-stopped  # 异常自动重启
```


## Docker Image:llama-cpp-server:cpu

使用基础镜像`ubuntu:22.04` + llama.cpp源码包制作镜像`llama-cpp-server:cpu`

### llama.cpp Source Code & Compile

```shell
git clone --depth=1 https://github.com/ggerganov/llama.cpp.git
cd llama.cpp
mkdir -p build && cd build

# CPU-only build (sufficient for quantize + sanity check)
cmake .. -DGGML_CUDA=OFF -DLLAMA_CURL=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release -j $(nproc) --target llama-quantize llama-cli llama-server

# Or a CUDA build for high-throughput inference
# cmake .. -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=90 -DCMAKE_BUILD_TYPE=Release
# (set CMAKE_CUDA_ARCHITECTURES to your GPU compute capability, see NVIDIA docs)
```

### Dockerfile

Dockerfile需与llama.cpp.zip同一个文件夹下，构建镜像：`docker build -t llama-cpp-server:cpu .`

```shell

# 基础镜像
FROM ubuntu:22.04

# 工作目录
WORKDIR /app

# 安装编译依赖
RUN apt update && apt install -y --no-install-recommends \
    build-essential \
    cmake \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 复制工程压缩包
COPY llama.cpp.zip /app/

# 解压 + 编译（同时编译 llama-server + llama-quantize）
RUN unzip -q llama.cpp.zip \
    && cd llama.cpp \
    && mkdir -p build && cd build \
    && cmake .. \
        -DGGML_CUDA=OFF \
        -DLLAMA_CURL=OFF \
        -DCMAKE_BUILD_TYPE=Release \
    && cmake --build . --config Release -j $(nproc) \
    && cd ../.. \
    && rm -f llama.cpp.zip

# 工作目录切到可执行文件位置
WORKDIR /app/llama.cpp/build/bin

# 暴露 Web 服务端口
EXPOSE 8080

# 默认启动命令（可挂载模型后覆盖）
CMD ["./llama-server", "--help"]
```

---

## llama-cli & llama-server

```shell
# Download MiniCPM5-1B
huggingface-cli download openbmb/MiniCPM5-1B-GGUF MiniCPM5-1B-Q4_K_M.gguf --local-dir ./minicpm5

# Interactive chat (auto-applies the chat template)
llama-cli -m ./minicpm5/MiniCPM5-1B-Q4_K_M.gguf -n 2048 --temp 0.7 --top-p 0.95 -ngl 99

# server

llama-server -m ./minicpm5/MiniCPM5-1B-Q4_K_M.gguf --host 0.0.0.0 --port 8080 -ngl 0 -c 4096 --jinja -t 6 -b 512 --alias MiniCPM5-1B-Q4

curl http://localhost:8080/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "MiniCPM5-1B-Q4",
        "messages": [{"role": "user", "content": "1+1=?"}],
        "temperature": 0.7, "top_p": 0.95, "max_tokens": 256
    }'
```
