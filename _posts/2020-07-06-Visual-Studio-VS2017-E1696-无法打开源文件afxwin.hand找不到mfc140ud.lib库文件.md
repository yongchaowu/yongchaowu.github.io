---
layout: post
title: "Visual Studio-VS2017 E1696 无法打开源文件“afxwin.h”&找不到“mfc140ud.lib”库文件"
date: 2020-07-06 21:47:00
categories: ["Visual Studio"]
tags: ["Visual Studio", "IDE"]
---

#Visua Studio-VS2017  E1696 无法打开源文件“afxwin.h”&找不到“mfc140ud.lib”库文件
缺少编译环境或编译环境默认配置路径不正确导致的。
解决方案：
1.需要安装"用于 x86 和 x64 的 Visual C++ MFC"
2."项目属性->包含目录",添加目录
```language
"C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.16.27023\atlmfc\include"
```
3."项目属性->链接器->附加库目录"添加
```language
	C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.16.27023\atlmfc\lib\x86\mfc140ud.lib
	C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Tools\MSVC\14.16.27023\atlmfc\lib\x64\mfc140ud.lib
```

<!--more-->
4.Other:
  **可以通过Everything,搜索需要的文件，确认文件路径。**