---
layout: post
title: Gitlab-CICD
display_title: 'GitLab CI/CD'
date: 2023-06-29 19:59:00
categories:
- DevOps & Infrastructure
tags:
- GitLab
- Tool
---

## Attention
- `sudo gitlab-runner register`
- `Linux executor:shell`
- `sudo gitlab-runner verify`
- `sudo gitlab-runner start`

<!--more-->
## Introduction
>https://blog.csdn.net/qq_42001163/article/details/122938040

### 安装Gitlab-runner命令行
- 添加官方 GitLab 存储库： `$ curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash`
- 安装最新版本的 GitLab Runner，或跳到下一步安装特定版本： `$ sudo apt-get install gitlab-runner`
- 要安装特定版本的 GitLab Runner： `$ apt-cache madison gitlab-runner`
- deb文件安装:
    ```
    $ curl -LJO "https://gitlab-runner-downloads.s3.amazonaws.com/latest/deb/gitlab-runner_amd64.deb"
    $ ls -ltr
    # 安装
    $ dpkg -i gitlab-runner_amd64.deb
    ```

### Runner 的配置
- 默认用户:`gitlab-runner`
- 默认工作目录:`/var/lib/gitlab-runner`
- 配置用户与工作目录:`sudo gitlab-runner install --user=username --working-directory=path`

其他方法：[修改gitlab-runner用户权限]
- `vim /etc/sudoers`
- `gitlab-runner ALL=(ALL) NOPASSWD:ALL`:复制root信息
- `sudo`:该用户通过sudo提升权限

### Runner 的注册
- `sudo gitlab-runner register`
- 获取Gitlab实例的URL和Token，这些内容可以通过项目的 Setting –> CI/CD –> Runner 选项来获取
- `gitlab-runner list` //查看当前runner
- `Enter an executor: docker-ssh, shell, ssh, virtualbox, docker+machine, docker-ssh+machine, docker, parallels, kubernetes, custom:
shell` //linux这里选shell
- `gitlab-runner verify `
- `gitlab-runner restart`

### Runner 的使用
`.gitlab-ci.yml` // 创建项目时勾选CICD或按照模板配置
