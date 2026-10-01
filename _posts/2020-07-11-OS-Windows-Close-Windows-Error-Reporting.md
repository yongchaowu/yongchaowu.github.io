---
layout: post
title: Windows-Close Windows Error Reporting
date: 2020-07-11 13:48:00
categories:
- Systems
tags:
- OS
- Windows
---
July 11, 2020 1:44 PM

当Windows上的应用运行程序崩溃时，windows会弹出崩溃信息窗口，如何才能让系统不再弹出该信息。（以便看门狗或其他操作）

<!--more-->

可以通过修改注册表的方式操作 崩溃信息窗口是否显示。
1. 方法：关闭提示信息窗口
```language
Windows Registry Editor Version 5.00 
[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\Windows Error Reporting] 
"DontShowUI"=dword:00000001 
"Disabled"=dword:00000001 
```

2. 方法：开启提示信息窗口
```language
Windows Registry Editor Version 5.00 
[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\Windows Error Reporting] 
"DontShowUI"=dword:00000000 
"Disabled"=dword:00000000 
```

本文修订依据：Microsoft Learn [`WER settings`](https://learn.microsoft.com/en-us/windows/win32/wer/wer-settings#windows-error-reporting-subkey)，源文档提交 `69abdafd76e6a85088ba2508485d974b853783c2`（页面更新 2025-04-15）。文档规定 `Disabled=0` 为启用 WER，`DontShowUI=0` 为显示 WER UI；本文仅将第二组设置标签改为“开启提示信息窗口”。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 11:30（UTC+08:00）。修订仅纠正 Windows Error Reporting 启用设置的标签。