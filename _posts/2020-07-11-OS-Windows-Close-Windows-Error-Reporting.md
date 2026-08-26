---
layout: post
title: "OS-Windows-Close Windows Error Reporting"
date: 2020-07-11 13:48:00
categories: ["OS"]
tags: ["OS", "Windows"]
---

July 11, 2020 1:44 PM

<!--more-->
当Windows上的应用运行程序崩溃时，windows会弹出崩溃信息窗口，如何才能让系统不再弹出该信息。（以便看门狗或其他操作）

可以通过修改注册表的方式操作 崩溃信息窗口是否显示。
1. 方法：关闭提示信息窗口
```language
Windows Registry Editor Version 5.00 
[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\Windows Error Reporting] 
"DontShowUI"=dword:00000001 
"Disabled"=dword:00000001 
```

2. 方法：显示提示信息窗口
```language
Windows Registry Editor Version 5.00 
[HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\Windows Error Reporting] 
"DontShowUI"=dword:00000000 
"Disabled"=dword:00000000 
```