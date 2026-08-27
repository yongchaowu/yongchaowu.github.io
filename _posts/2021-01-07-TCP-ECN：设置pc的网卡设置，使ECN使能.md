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
::SetEnable.bat
::version1.0.0.1
@echo off
::先延时启动20s
::@ping -n 20 127.1>nul

::设置
netsh interface tcp set global ecncapability=enabled
```

<!--more-->
```
::SetDisabled.bat
::version1.0.0.1
@echo off
::先延时启动20s
::@ping -n 20 127.1>nul

::设置
netsh interface tcp set global ecncapability=disabled
```
