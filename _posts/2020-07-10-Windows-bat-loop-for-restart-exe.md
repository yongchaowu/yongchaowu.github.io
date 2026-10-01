---
layout: post
title: Windows-bat-loop for restart exe
date: 2020-07-10 02:10:00
categories:
- Systems
tags:
- Windows
- Windows批处理 (cmd/bat)
- OS
---
July 10, 2020 2:09 AM
## 周期重启某个指定的程序
```language
@echo off
:start
choice /t 10 /d y /n >nul
start "" "C:\Users\Administrator\Desktop\XXXX.exe"
choice /t 10 /d y /n >nul
taskkill /F /IM XXXX.exe
goto start
```

参考：[Microsoft Learn：`start`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/start) 和 [`cd`](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/cd)。

<!--more-->

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 02:41（UTC+08:00）。
