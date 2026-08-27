---
layout: post
title: Python Ray Offline Installation Guide
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
   ray[default]==2.56.0
   ```

3. Offline install:
   ```bash
   pip install --no-index --find-links=./ray_offline_pkgs ray[default]==2.40.0
   ```
