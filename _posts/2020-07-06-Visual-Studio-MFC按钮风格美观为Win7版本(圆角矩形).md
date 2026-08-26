---
layout: post
title: "Visual Studio-MFC按钮风格美观为Win7版本(圆角矩形)"
date: 2020-07-06 22:51:00
categories: ["Visual Studio"]
tags: ["Visual Studio", "IDE"]
---

July 6, 2020 10:48 PM
参考 [VS2010 MFC的按钮风格改变](https://www.cnblogs.com/woniu201/p/11694648.html)

<!--more-->
VS2010建的MFC工程按钮默认的风格类似VC6.0（直角矩形），如想美观按钮改为WIN7的按钮风格（圆角矩形），只需在代码中找到头文件“stdafx.h”，在里面添加如下代码即可：
```language
#pragma comment(linker,"/manifestdependency:\"type='win32' name='Microsoft.Windows.Common-Controls' version='6.0.0.0' processorArchitecture='x86' publicKeyToken='6595b64144ccf1df' language='*'\"")
```