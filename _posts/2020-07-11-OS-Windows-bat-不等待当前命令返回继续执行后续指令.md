---
layout: post
title: Windows-bat-不等待当前命令返回继续执行后续指令
date: 2020-07-11 17:29:00
categories:
- Systems
tags:
- Windows
- OS
- Windows批处理 (cmd/bat)
---

`start 程序名` 使用start调用的程序，批处理是不会等待程序运行结束的，这样才能在启动一个程序后，不用等到该程序结束，就可以执行之后的语句。