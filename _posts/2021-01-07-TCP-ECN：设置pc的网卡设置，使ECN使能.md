---
layout: post
title: "TCP-ECN：设置pc的网卡设置，使ECN使能"
date: 2021-01-07 17:28:00
categories: ["TCP"]
tags: ["TCP", "TCP/IP ECN", "Unclassified"]
---

```
//SetEnable.bat
::version1.0.0.1
@echo off
::先延时启动20s
::@ping -n 20 127.1>nul

::设置
netsh interface tcp set global ecncapability=enabled
```

<!--more-->
```
//SetDisabled.bat
::version1.0.0.1
@echo off
::先延时启动20s
::@ping -n 20 127.1>nul

::设置
netsh interface tcp set global ecncapability=disabled
```
