---
layout: post
title: "DevOps 交付手册：Git、GitLab、Docker 与可恢复的发布流程"
display_title: "DevOps 交付手册：Git、GitLab、Docker 与可恢复的发布流程"
summary: "把版本控制、CI/CD、容器、GitLab 运维、备份恢复和常见故障整理成一条适合小团队落地的交付与回滚路径。"
lang: zh-CN
date: 2026-09-24 10:00:00
categories:
  - DevOps & Infrastructure
tags:
  - Git
  - GitLab
  - Docker
  - CI/CD
  - Backup
  - Operations
curated: true
content_origin: curated
curation_level: runbook
version: curated-v1
source_posts:
  - "_posts/2023-02-27-Tool-Git.md"
  - "_posts/2023-04-14-Tool-GitLab.md"
  - "_posts/2023-06-29-Tool-Gitlab-CICD.md"
  - "_posts/2023-07-24-Tool-Gitlab-502-端口占用.md"
  - "_posts/2023-07-24-Tool-Gitlab-备份恢复-迁移.md"
  - "_posts/2024-04-23-Tool-Gitlab-重置root账户密码.md"
  - "_posts/2024-07-20-Tool-Gitlab-CICD-jobs-删除或清空.md"
  - "_posts/2024-07-20-Tool-Gitlab-禁止开机自启动.md"
  - "_posts/2020-12-02-Tool-Docker-First-exploration.md"
  - "_posts/2024-07-15-Tool-Docker-Ubuntu18.04.md"
  - "_posts/2024-08-08-Tool-Docker-以ubuntulatest为例.md"
  - "_posts/2024-07-24-Software-DM8-docker镜像.md"
---

交付能力的核心不是记住某条 GitLab 或 Docker 命令，而是让每次变更都能回答四个问题：改了什么、谁批准、在哪里验证、失败后如何回到上一版本。下面的路线把站内零散笔记串成一个小型交付闭环。

> 本文是 DevOps 历史文章的重组稿。涉及删除数据、重置账户、清理任务和修改开机服务的操作，都应先确认备份、权限和影响范围。

<!--more-->

## 1. 版本控制：先保证可回退

[Git](#source-posts-title) 的基本价值是建立可审计的变更轨迹。小团队可以从下面的最小约定开始：

- 主分支始终保持可发布；
- 功能通过短生命周期分支和合并请求进入主分支；
- 提交说明说明动机和影响，不只写“fix bug”；
- 发布前打不可变版本，镜像和二进制都带版本号；
- 禁止把密钥、密码和临时凭据提交到仓库。

冲突解决不是简单的“接受一边”。先理解两边的意图，再决定是否重放提交或重新组织变更。

## 2. CI/CD：让流水线成为质量门

[GitLab CI/CD](#source-posts-title) 适合把检查分成三个阶段：

```text
提交检查 → 构建检查 → 发布检查
 lint/test   image/job   staging/canary
```

每个阶段都应有超时、重试上限和清晰的失败日志。Runner 的标签、网络、缓存和权限是环境的一部分，不能只依赖“在本机能跑”。发布前至少保留：测试报告、构建产物摘要、镜像 digest、配置快照和审批记录。

## 3. 容器：镜像可复现，运行配置外置

[Docker 入门记录](#source-posts-title) 和 [以 ubuntu:latest 为例](#source-posts-title) 提醒我们：标签不是版本。生产镜像应尽量固定基础镜像和依赖，数据、密钥、端口和日志目录通过运行时配置注入。

上线前检查：

- 容器以什么用户运行？
- 挂载了哪些目录，是否包含不必要的敏感路径？
- 网络是否需要出站访问，能否限制？
- 依赖服务是否有健康检查和启动顺序？
- 删除容器后，持久化数据是否仍然存在？

## 4. 故障处理：先恢复，再定位

[GitLab 502](#source-posts-title) 只是一个表象，可能来自反向代理、端口、容器、服务进程或资源耗尽。排查顺序应是：入口是否可达 → 反代后端是否健康 → 应用是否监听正确地址 → 日志是否有启动/权限错误 → 资源是否耗尽。

对于 [重置 root 账户](#source-posts-title)、[清理 CI/CD jobs](#source-posts-title) 和 [禁止开机自启动](#source-posts-title)，先导出配置和备份，再执行破坏性操作，并记录执行人、时间和回滚命令。

## 5. 备份恢复：恢复演练比备份文件更重要

[GitLab 备份、恢复与迁移](#source-posts-title) 的核心不是“压缩成功”，而是在干净环境中恢复成功。每次备份应记录：

```text
版本与实例：
备份范围：
开始/结束时间：
文件校验值：
依赖和权限：
恢复目标：
演练结果：
```

数据库、仓库、配置和密钥应分开管理。不要把“数据库备份”和“应用目录压缩包”混为一个恢复方案，也不要把唯一备份放在与生产相同的故障域。

## 6. 一次发布的标准模板

```text
变更单：
影响服务：
代码/镜像版本：
配置差异：
数据库迁移：
测试与回滚证据：
发布窗口：
监控指标：
回滚负责人：
```

当发布流程能够被另一个人根据记录复现，DevOps 才真正从个人经验变成团队能力。
