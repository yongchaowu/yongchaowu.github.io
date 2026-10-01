---
layout: post
title: TCP-ECN：设置pc的网卡设置，使ECN使能
display_title: 'TCP-ECN 设置 PC 的网卡设置使 ECN 使能'
date: 2021-01-07 17:28:00
categories:
- Security & Networking
tags:
- TCP
- TCP/IP ECN
---
```
rem SetEnable.bat
::version1.0.0.1
@echo off
::先延时启动20s
::@ping -n 20 127.1>nul

::设置
netsh interface tcp set global ecncapability=enabled
```

```
rem SetDisabled.bat
::version1.0.0.1
@echo off
::先延时启动20s
::@ping -n 20 127.1>nul

<!--more-->

::设置
netsh interface tcp set global ecncapability=disabled
```

本文修订依据：Microsoft Learn [`rem` command](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/rem)，源文档提交 `48fd05321fd0fe328b1977597b554d884ca5e35d`。该命令是 Windows `cmd.exe` 批处理文件中的注释命令；本文仅将两个 `//` 文件标签改为 `rem`，不改变其余 `::` 注释或 `netsh` 命令。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 10:22（UTC+08:00）。修订仅纠正两个 Windows 批处理文件的注释语法。
