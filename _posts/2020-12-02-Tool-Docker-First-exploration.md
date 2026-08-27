---
layout: post
title: First exploration
date: 2020-12-02 18:28:00
categories:
- DevOps & Infrastructure
tags:
- Docker
- Tool
---

2020/11/30  00:19:00

<!--more-->
之前工作中接触过Docker，最近在笔记本上想装个Vm虚拟机用，就想着来试试Docker吧。

##  1.Docker Hub Tutorial

[Docker Hub](https://hub.docker.com/)

Get started by downloading Docker Desktop, and learn how you can build, tag and share a sample image on Hub.

1. Download:

   `Docker Desktop installer.exe`

2. Clone:

   `git clone https://github.com/docker/doodle.git`

3. Build:

   `cd doodle\cheers2019 ; docker build -t cain95/cheers2019 .`

   注：实测用了3000+s。

4. Run:

   `docker run -it --rm cain95/cheers2019`

5. Ship:

   `docker login ; docker push cain95/cheers2019`

## 2.Docker 101 Tutorial

[101-Tutorial](https://www.docker.com/101-tutorial)

1. #### Docker Desktop

   ```txt
   Docker Desktop is a native application that delivers all of the Docker tools to your Mac or Windows Computer. 
   
   1.Open Docker Desktop. (Download here if you don't have it).
   2.Type the following command in your terminal: docker run -dp 80:80 docker/getting-started
   3.Open your browser to http://localhost
   4.Have fun!
   ```

2. #### Play with Docker

   ```txt
   Play with Docker is an interactive playground that allows you to run Docker commands on a linux terminal, no downloads required.
   
   1.Log into https://labs.play-with-docker.com/ to access your PWD terminal
   2.Type the following command in your PWD terminal: docker run -dp 80:80 docker/getting-started:pwd
   3.Wait for it to start the container and click the port 80 badge
   4.Have fun!
   ```



## 3. Windows Containers with Docker

[Windows Containers Basics](https://training.play-with-docker.com/windows-containers-basics/)

First, make sure the Docker installation is working:

`docker version`

*我的server是linux/amd64，不支持windows，尴尬。*

**解决方法：任务栏右键whale，可以选择切换server为windows。[默认安装时是linux]**



Next, pull a base image that’s compatible with the evaluation build, re-tag it and do a test-run:

```plain
docker pull microsoft/windowsservercore:10.0.14393.321 
//提示error：xxx i/o timeout。
//替换方案，去hub上找了个镜像：
//[windows-servercore](https://hub.docker.com/_/microsoft-windows-servercore)
//docker pull mcr.microsoft.com/windows/servercore:ltsc2019
//docker run mcr.microsoft.com/windows/servercore:ltsc2019
//拉取超时~，参考[配置Docker镜像加速](https://www.runoob.com/docker/docker-mirror-acceleration.html)
//配置Docker镜像加速：
//-网易：https://hub-mirror.c.163.com/
//-阿里云：https://<你的ID>.mirror.aliyuncs.com  
///阿里云镜像获取地址：https://cr.console.aliyun.com/cn-hangzhou/instances/mirrors
//-七牛云加速器：https://reg-mirror.qiniu.com
//-Docker 官方加速器 https://registry.docker-cn.com (可能不能用了)
//回到原有指令，3.738GB
//2020/12/02 最后还是没下下来，真的放弃了，这是要让人用AWS来实现啊
```



```bash
docker tag microsoft/windowsservercore:10.0.14393.321 microsoft/windowsservercore
docker run microsoft/windowsservercore hostname
```



### Building and pushing Windows container images

Pushing images to Docker Cloud requires a [free Docker ID](https://cloud.docker.com/). Storing images on Docker Cloud is a great way to save build artifacts for later use, to share base images with co-workers or to create build-pipelines that move apps from development to production with Docker.

Docker images are typically built with [docker build](https://docs.docker.com/engine/reference/commandline/build/) from a [Dockerfile](https://docs.docker.com/engine/reference/builder/) recipe, but for this example, we’re going to just create an image on the fly in PowerShell.

```
"FROM microsoft/windowsservercore `n CMD echo Hello World!" | docker build -t <docker-id>/windows-test-image -
```

Test the image:

```bash
docker run <docker-id>/windows-test-image
Hello World!
```

Login with `docker login` and then push the image:

```bash
docker push <docker-id>/windows-test-image
```

Images stored on Docker Cloud are available in the web interface and public images can be pulled by other Docker users in the [Docker Store](https://store.docker.com/).



## 4.Docker 命令大全

转自[runoobDocker-命令大全](https://www.runoob.com/docker/docker-command-manual.html)

### 容器生命周期管理

- [run](https://www.runoob.com/docker/docker-run-command.html)
- [start/stop/restart](https://www.runoob.com/docker/docker-start-stop-restart-command.html)
- [kill](https://www.runoob.com/docker/docker-kill-command.html)
- [rm](https://www.runoob.com/docker/docker-rm-command.html)
- [pause/unpause](https://www.runoob.com/docker/docker-pause-unpause-command.html)
- [create](https://www.runoob.com/docker/docker-create-command.html)
- [exec](https://www.runoob.com/docker/docker-exec-command.html)

### 容器操作

- [ps](https://www.runoob.com/docker/docker-ps-command.html)
- [inspect](https://www.runoob.com/docker/docker-inspect-command.html)
- [top](https://www.runoob.com/docker/docker-top-command.html)
- [attach](https://www.runoob.com/docker/docker-attach-command.html)
- [events](https://www.runoob.com/docker/docker-events-command.html)
- [logs](https://www.runoob.com/docker/docker-logs-command.html)
- [wait](https://www.runoob.com/docker/docker-wait-command.html)
- [export](https://www.runoob.com/docker/docker-export-command.html)
- [port](https://www.runoob.com/docker/docker-port-command.html)

### 容器rootfs命令

- [commit](https://www.runoob.com/docker/docker-commit-command.html)
- [cp](https://www.runoob.com/docker/docker-cp-command.html)
- [diff](https://www.runoob.com/docker/docker-diff-command.html)

### 镜像仓库

- [login](https://www.runoob.com/docker/docker-login-command.html)
- [pull](https://www.runoob.com/docker/docker-pull-command.html)
- [push](https://www.runoob.com/docker/docker-push-command.html)
- [search](https://www.runoob.com/docker/docker-search-command.html)

### 本地镜像管理

- [images](https://www.runoob.com/docker/docker-images-command.html)
- [rmi](https://www.runoob.com/docker/docker-rmi-command.html)
- [tag](https://www.runoob.com/docker/docker-tag-command.html)
- [build](https://www.runoob.com/docker/docker-build-command.html)
- [history](https://www.runoob.com/docker/docker-history-command.html)
- [save](https://www.runoob.com/docker/docker-save-command.html)
- [load](https://www.runoob.com/docker/docker-load-command.html)
- [import](https://www.runoob.com/docker/docker-import-command.html)

### info|version

- [info](https://www.runoob.com/docker/docker-info-command.html)
- [version](https://www.runoob.com/docker/docker-version-command.html)

## 5.Docker 资源

转自[runoobDocker-资源汇总](https://www.runoob.com/docker/docker-resources.html)

- Docker 官方主页: [https://www.docker.com](https://www.docker.com/)
- Docker 官方博客: https://blog.docker.com/
- Docker 官方文档: https://docs.docker.com/
- Docker Store: [https://store.docker.com](https://store.docker.com/)
- Docker Cloud: [https://cloud.docker.com](https://cloud.docker.com/)
- Docker Hub: [https://hub.docker.com](https://hub.docker.com/)
- Docker 的源代码仓库: https://github.com/moby/moby
- Docker 发布版本历史: https://docs.docker.com/engine/release-notes/
- Docker 常见问题: https://docs.docker.com/
- Docker 远端应用 API: https://docs.docker.com/develop/sdk/

- Docker 国内镜像

  阿里云的加速器：https://help.aliyun.com/document_detail/60750.html

  网易加速器：http://hub-mirror.c.163.com

  官方中国加速器：https://registry.docker-cn.com

  ustc 的镜像：https://docker.mirrors.ustc.edu.cn

  daocloud：https://www.daocloud.io/mirror#accelerator-doc（注册后使用）