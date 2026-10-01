---
layout: post
title: Visual Studio-基本使用
date: 2020-07-08 01:39:00
categories:
- Developer Tools
tags:
- Visual Studio
- IDE
---
转载[Visual Studio基本使用](https://blog.csdn.net/dadan1314/article/details/89519300)
##卸载
从 https://github.com/Microsoft/VisualStudioUninstaller/releases
下载Setup.ForcedUninstall.exe，并以管理员运行，输入Y，等待完成...

##调试
库调试两种方式
1. 启动调试
  库工程属性 > 配置属性 > 调试 > 命令
     指定运行程序（包含目录和运行程序）
2. 附加调试
  菜单 > 调试 > 附加到进程
     从列表中指定运行程序，然后附加

<!--more-->

release下调试四步设置
	C/C++ --> 常规 --> 调试信息格式 --> 程序数据库 (/Zi) ；
	C/C++ --> 常规 --> 优化 --> 优化 --> 已禁用 (/Od)；
	链接器 --> 常规--> 启动增量链接 --> 是 (/INCREMENTAL)；
	链接器 --> 调试 --> 生成调试信息 --> 生成调试信息 (/DEBUG)。

##工具
###集成工具
在VS的安装目录下有个Common7/Tools目录下
- errlook.exe   通过 [Visua Studio ->工具->错误查找]   启动 ---  查看GetLastError()错误码描述 
- guidgen.exe 通过 [Visua Studio ->工具->创建GUID] 启动 --- 创建GUID

##快捷键
Ctrl+K Ctrl+D   代码格式化
Ctrl+U          小写
Shift+Ctrl+U    大写
Tab             前进一个tab键
Shift+Tab       后退一个tab键

##版本
WIN_VER	系统版本
0x500	Windows 2000
0x501	Windows xp
0x600	Windows vista
0x601	Windows 7
0x0602	Windows 8
0x0A00	Windows 10

名称	内部版本（MSVC++）	  _MSC_VER
Visual Studio 2008	9.0	    1500
Visual Studio 2010	10.0	1600
Visual Studio 2013	12.0	1800
Visual Studio 2015	14.0	1900
Visual Studio 2017	15.0	1910
Visual Studio 2019	16.0	1920

————————————————
版权声明：本文为CSDN博主「师从小白」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/dadan1314/java/article/details/89519300

本文修订依据：Microsoft C++ 文档 [`compiler-versions.md` commit `e1708c80585b0c1aaa70e57190cd04b4779602ab`](https://raw.githubusercontent.com/MicrosoftDocs/cpp-docs/e1708c80585b0c1aaa70e57190cd04b4779602ab/docs/overview/compiler-versions.md) 和 [`predefined-macros.md` commit `914fb42b812623a3822545d0fdad2a7d95d9536d`](https://raw.githubusercontent.com/MicrosoftDocs/cpp-docs/914fb42b812623a3822545d0fdad2a7d95d9536d/docs/preprocessor/predefined-macros.md)。表中填写的是 Visual Studio 2015、2017 RTW 和 2019 RTW 的基础 `_MSC_VER` 值；后续 servicing release 可能需要用 `_MSC_FULL_VER` 区分。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 09:39（UTC+08:00）。修订仅补全 Visual Studio 2015、2017 RTW 和 2019 RTW 的 `_MSC_VER` 基础值。