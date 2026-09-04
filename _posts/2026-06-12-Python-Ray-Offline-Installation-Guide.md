---
layout: post
title: Python Ray Offline Installation Guide
summary: >
  Step-by-step guide for installing Ray in air-gapped environments using
  pre-downloaded wheel packages, with pip configuration and verification steps.
lang: en
tested:
  Python: "3.12"
  Package Manager: "pip >= 21.0"
  Environment: "Air-gapped / offline"
date: 2026-06-12 22:17:00
categories:
- Programming
tags:
- Python
- Ray
---

## Prerequisites

<!--more-->
- Python 3.12
- pip >= 21.0

## Steps

1. Create ray offline packages folder:
   ```bash
   mkdir ray_offline_pkgs && cd ray_offline_pkgs
   ```

2. Download all dependencies (specify Python 3.12, manylinux2014_x86_64 platform, binary-only):
   ```bash
   pip download --python-version 312 --platform manylinux2014_x86_64 --only-binary :all: ray[default]==2.40.0
   ```

   ```bash
   # 临时加镜像执行下载
   pip download \
   --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
   --retries 10 \
   --timeout 120 \
   --python-version 312 \
   --platform manylinux2014_x86_64 \
   --only-binary :all: \
   ray[default]==2.40.0
   ```

3. Offline install:
   ```bash
   pip install --no-index --find-links=./ray_offline_pkgs ray[default]==2.40.0
   ```

## Next Steps

After installing Ray, you can proceed to:

- [Multi-Node LLM Serving: vLLM + Ray]({% post_url 2026-06-12-Multi-Node-LLM-Serving-vLLM+Ray(Docker) %}) — Deploy vLLM across multiple nodes using Ray
- [Multi-Node LLM Serving: Architecture, Frameworks & Best Practices]({% post_url 2026-06-12-Multi-Node-LLM-Serving-Architecture,-Frameworks-and-Best-Practices-(LLM-Generated) %}) — Compare multi-node serving frameworks
