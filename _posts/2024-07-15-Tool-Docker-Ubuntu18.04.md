---
layout: post
title: "Tool-Docker-Ubuntu18.04"
date: 2024-07-15 10:01:00
categories: ["Tool"]
tags: ["Docker", "Tool", "Ubuntu"]
---

在`Ubuntu18.04`的操作系统上安装`Docker`，并实现镜像导入与容器运行。
- [Docker Home](https://www.docker.com/)
- [Docker Download](https://download.docker.com/linux/ubuntu/dists/bionic/pool/stable/)

<!--more-->
---
由于docker官网访问异常，借用阿里云开源镜像站下载安装包。
- [Docker CE镜像](https://mirrors.aliyun.com/docker-ce/)
- [docker-ce镜像下载页](https://mirrors.aliyun.com/docker-ce/?spm=a2c6h.25603864.0.0.32e16744wYuYwR)

---
安装项：
- `containerd.io_1.5.10-1_amd64.deb`
- `docker-ce_18.09.0~3-0~ubuntu-bionic_amd64.deb`
- `docker-ce-cli_18.09.0~3-0~ubuntu-bionic_amd64.deb`

镜像包：`Ubuntu.tar` (Ubuntu:latest)