---
layout: post
title: "Windows-bat-loop for restart exe"
date: 2020-07-10 02:10:00
categories: ["Windows"]
tags: ["Windows", "Windows批处理 (cmd/bat)", "OS"]
---

July 10, 2020 2:09 AM
## 周期重启某个指定的程序
```bash
@echo off
:start
choice /t 10 /d y /n >nul
cd C:\Users\Administrator\Desktop\XXXX.exe
choice /t 10 /d y /n >nul
taskkill /F /IM XXXX.exe
goto start
```

<!--more-->
