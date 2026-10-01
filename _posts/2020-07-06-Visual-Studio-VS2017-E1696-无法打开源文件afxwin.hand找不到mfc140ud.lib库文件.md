---
layout: post
title: Visual Studio-VS2017 E1696 无法打开源文件“afxwin.h”&找不到“mfc140ud.lib”库文件
date: 2020-07-06 21:47:00
categories:
- Developer Tools
tags:
- Visual Studio
- IDE
---
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

4.Other:
  **可以通过Everything,搜索需要的文件，确认文件路径。**

<!--more-->

本文修订依据：Microsoft Learn 归档的 [Visual Studio 2017 IDE 文档](https://learn.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-2017)，`vs-2017` 文档 moniker，文档源 commit `d68e43133363683ebcded460efd8a903f329f558`。本文仅将标题中的 `Visua Studio` 更正为产品名 `Visual Studio`，未改动错误代码、路径或解决步骤。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 13:46（UTC+08:00）。修订仅纠正标题中的 Visual Studio 产品名拼写。