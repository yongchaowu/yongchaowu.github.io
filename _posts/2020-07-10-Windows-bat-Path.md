---
layout: post
title: Windows-bat-Path
display_title: 'Windows bat Path'
date: 2020-07-10 08:18:00
categories:
- Systems
tags:
- Windows
- Windows批处理 (cmd/bat)
- OS
---
```language
@echo off
echo 批处理文件所在盘符：%~d0
echo 当前工作目录：%cd%
echo 批处理文件名/路径：%0
echo 当前bat文件路径：%~dp0
echo 当前bat文件短路径：%~sdp0
pause
```

本文修订依据：Microsoft Learn 当前 Windows 命令参考中的 [`call`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/call)、[`cd`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cd) 和批处理参数说明。`%~d0` 展开 `%0` 参数的驱动器，`%cd%` 是当前工作目录，`%0` 是批处理文件名及调用时提供的路径；本文仅修正三个标签。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 13:00（UTC+08:00）。修订仅纠正 `%~d0`、`%cd%` 和 `%0` 的说明标签。