---
layout: post
title: "Tool-Docker-以ubuntu:latest为例"
date: 2024-08-08 16:48:00
categories: ["Tool"]
tags: ["Docker", "Tool", "Ubuntu"]
---

[Ubuntu-Install](https://docs.docker.com/engine/install/ubuntu/)

<!--more-->
- `docker search ubuntu`:查询镜像
- `docker pull ubuntu[:version]`:拉取镜像
- `docker images`:查看镜像
- `docker ps -a`:查看当前容器状态
- `docker run -itd --name container-name images-name[:version] /bin/bash`:运行容器
  - `-e`:环境变量
  - `-v`:挂载卷
- `docker exec -it container-name|containerID /bin/bash`:进入指定容器
- `docker commit -m="update" -a="yongchao"  container-name|containerID container-name-new:version`:从指定容器提交更新镜像
- `docker save -o xxx.tar images-name[:version]`:导出指定版本镜像
- `docker rmi images-name`:删除指定镜像
- `docker load -i xxx.tar`:导入镜像压缩包
- `docker cp xx container-name:xx ` 或 `docker cp container-name:xx  xx `:拷贝文件
- `docker inspect container-name`:查看信息
- `docker network`:配置网络 `--net  --ip`
  - `list`
  - `create network-name`
    - `--driver bridge`
    - `--subnet 192.168.0.0/24`
    - `--gateway 192.168.0.1`
  - `connect network-name container-name`
    - `--ip 192.168.0.2`
  - `disconnect`
  - `rm network-name`