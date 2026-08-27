---
layout: post
title: Software-DM8-docker镜像
display_title: 'DM8 Docker 镜像'
date: 2024-07-24 16:59:00
categories:
- DevOps & Infrastructure
tags:
- Software
- DB
- Tool
- Docker
---

- [达梦数据库](https://www.dameng.com/)
- [达梦数据库管理系统DM8 Docker镜像](https://www.dameng.com/list_103.html)

<!--more-->
## 安装
- [Docker安装](https://eco.dameng.com/document/dm/zh-cn/start/dm-install-docker)
- `dm8_20240613_x86_rh6_64_rq_ent_8.1.3.140_pack5.tar`


注意
1. 如果使用 docker 容器里面的 disql，进入容器后，先执行 `source /etc/profile` 防止中文乱码。
2. 新版本 Docker 镜像中数据库默认用户名/密码为 `SYSDBA/SYSDBA001`。