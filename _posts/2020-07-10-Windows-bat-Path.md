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
echo 当前盘符：%~d0
echo 当前路径：%cd%
echo 当前执行命令行：%0
echo 当前bat文件路径：%~dp0
echo 当前bat文件短路径：%~sdp0
pause
```