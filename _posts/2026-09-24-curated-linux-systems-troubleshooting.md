---
layout: post
title: "Linux 与 Windows 故障排查：从现象到根因的系统化方法"
display_title: "Linux 与 Windows 故障排查：从现象到根因的系统化方法"
summary: "把命令、进程、服务、动态库、启动、驱动和输入设备等零散笔记整理成一套可复用的故障定位流程。"
lang: zh-CN
date: 2026-09-24 09:10:00
categories:
  - Systems
tags:
  - Linux
  - Ubuntu
  - Windows
  - Troubleshooting
  - System Administration
curated: true
content_origin: curated
curation_level: runbook
version: curated-v1
source_posts:
  - "_posts/2020-07-10-OS-Linux-command.md"
  - "_posts/2023-03-01-OS-Linux-菜鸟教程.md"
  - "_posts/2023-04-05-OS-Linux-Ubuntu.md"
  - "_posts/2023-04-08-OS-Linux-Ubuntu-apt-get.md"
  - "_posts/2020-10-22-OS-Linux-动态链接文件设置环境变量-etcld.so.conf-ldconfig-ldd.md"
  - "_posts/2023-04-09-OS-Linux-端口占用.md"
  - "_posts/2024-08-08-OS-Ubuntu-系统版本信息查询及含义与源配置.md"
  - "_posts/2025-04-29-OS-Ubuntu-Grub-开机后引导丢失.md"
  - "_posts/2026-06-10-OS-Ubuntu-NVIDIA-Driver-Install.md"
  - "_posts/2026-09-05-restart-sogou-input-method.md"
  - "_posts/2026-09-08-kylin-v10-sp1-offline-cpp-development-environment.md"
  - "_posts/2020-07-09-Windows-API-后台服务.md"
  - "_posts/2020-07-11-OS-Windows-bat-不等待当前命令返回继续执行后续指令.md"
---

排查故障时，最容易浪费时间的是“看到一个报错就立刻搜索解决方案”。更可靠的方法是先固定现场，再缩小系统层：用户态进程、服务管理、动态链接、内核/驱动、文件系统和启动链分别有各自的证据。

> 本文是历史 Linux、Windows 和国产 Linux 记录的学习入口。涉及 root、驱动、GRUB、端口和文件系统的操作，请先在可恢复的环境中验证。

> **技术交叉核对（2026-09-25）**：关于 `ldd` 对不可信二进制可能触发执行的风险，已对照 Linux `ldd(1)` 手册；未知文件优先使用 `file`、`readelf` 或 `objdump`。

<!--more-->

## 一个通用的五步法

### 1. 记录可复现条件

至少记录：操作系统版本、发行版/内核、硬件、目标程序版本、启动方式、用户权限、发生时间和完整错误文本。先保存日志，不要只截取最后一行。

### 2. 先做只读检查

只读检查的成本低、风险小，适合作为第一轮：

```bash
uname -a
cat /etc/os-release
id
pwd
df -h
free -h
ps -ef | grep '[p]attern'
ss -lntup
```

Windows 侧则记录系统版本、服务状态、事件查看器中的时间和错误码。命令只是取证工具，关键是把输出和现象放在同一时间线上。

### 3. 画出故障层次

| 层次 | 典型问题 | 优先证据 |
| --- | --- | --- |
| 应用 | 参数、配置、异常退出 | 应用日志、退出码、最小输入 |
| 运行时 | 动态库、解释器、环境变量 | loader 日志、实际解析路径 |
| 服务 | 权限、依赖、启动顺序 | service/journal/事件日志 |
| 内核/驱动 | GPU、网卡、USB、输入设备 | `dmesg`、驱动版本、设备状态 |
| 启动/文件系统 | GRUB、挂载、只读根 | 启动日志、挂载表、恢复环境 |

[Linux 常用命令](#source-note-1)、[Ubuntu 基础整理](#source-note-3) 和 [apt-get 笔记](#source-note-4) 可以作为命令参考，但不要把命令清单当成诊断流程。

## 三个高频问题的定位思路

### 动态库找不到

不要先盲目修改全局环境变量。先确认程序实际需要的库、架构和搜索路径：

```bash
file ./your-program
readelf -d ./your-program | grep NEEDED
objdump -p ./your-program | grep NEEDED
```

对于确认来源可信的二进制，`ldd` 可以作为补充证据；不要对未知或不可信文件直接运行 `ldd`。然后区分三种情况：库根本不存在、库架构不匹配、库存在但不在 loader 搜索路径中。`LD_LIBRARY_PATH` 是局部实验工具，持久化到系统配置前应记录原因、影响范围和回滚方式。相关原理见 [动态链接与 ldconfig/ldd](#source-note-5)。

### 端口被占用

先用 `ss -lntup` 确认监听地址、进程和协议，再判断是服务重复启动、代理配置，还是容器端口映射。终止进程之前确认 PID 和工作目录；不要把“杀掉占用进程”当成长期修复。历史记录见 [Linux 端口占用](#source-note-6)。

### 输入法、显卡或启动异常

驱动和桌面组件问题要分层验证：

1. 内核是否识别设备；
2. 用户会话是否有正确的环境变量和权限；
3. 服务或用户进程是否反复崩溃；
4. 去掉第三方组件后是否仍能复现。

显卡驱动可先看 [Ubuntu NVIDIA Driver 安装记录](#source-note-9)，搜狗输入法可参考 [输入法重启与状态排查](#source-note-10)。对于 GRUB，不要在无法进入系统时直接覆盖分区或重建引导；先准备可启动介质和 [引导恢复记录](#source-note-8) 中的检查顺序。

## 后台运行的额外检查

“终端里能跑，放到后台就失败”通常意味着运行环境发生了变化：工作目录、环境变量、权限、终端信号或相对路径不同。Windows 的 [后台服务](#source-note-12) 和批处理 [异步执行](#source-note-13) 笔记可以作为对照，但生产排查应显式记录工作目录、身份、依赖和退出码。

## 离线环境的做法

内网环境的核心不是“把命令抄下来”，而是建立可验证的软件来源和依赖清单。参考 [银河麒麟 V10 SP1 离线 C/C++ 环境](#source-note-11)，建议为每个包记录版本、来源仓库、校验值、目标架构和安装顺序；导入机器后再次记录 `dpkg`、编译器、动态链接器和运行时验证结果。

## 建议保留的故障记录

```text
现象：
影响范围：
环境与版本：
最小复现：
只读证据：
尝试过的改变：
结果与回滚：
根因：
后续预防：
```

当记录积累起来后，零散命令会变成团队的故障知识库；这比单纯收集“解决方案链接”更有长期价值。
