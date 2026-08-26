---
layout: post
title: Libevent-windows 编译&引用
date: 2020-07-09 00:06:00
categories:
- Personal / Misc
tags:
- Libevent
- Open Source Library
---

# Libevent

<!--more-->
## windows 编译


### 编译libevent遇到编译错误
下载地址：http://libevent.org/ ，下载版本：libevent-2.1.11-stable.tar.gz
解压， 目录为...\libevent-2.1.11-stable(自己的目录)
修改以下三个文件，添加宏定义：
在以下3个文件开头添加"#define _WIN32_WINNT 0x0500"
libevent-2.1.11-stable\event_iocp.c
libevent-2.1.11-stable\evthread_win32.c
libevent-2.1.11-stable\listener.c

打开VS2015命令工具，切换到解压后的libevent目录，然后执行nmake /f Makefile.nmake命令进行编译:
    先输入cd/d D:\aa_zhj\a_work\projects\libevent\libevent-2.0.22-stable切换目录
    然后输入nmake /f Makefile.nmake进行编译。

生成三个lib文件：
libevent.lib、libevent_core.lib、libevent_extras.lib

```cpp
Q：e:\github\libevent-2.1.11-stable\minheap-internal.h(76) : error C2065: “UINT32_MAX”: 未声明的标识符
A:在该文件中添加#include "stdint.h"
```
#### x64
编译64位 lib,用VS2015 x64命令行工具 进行nmake /f Makefile.nmake即可。
需要修改Makefile.nmake
`LIBFLAGS=/nologo` 改为 `LIBFLAGS=/nologo /MACHINE:X64`


## 引用
- 新建一个控制台“空”项目
- 拷贝文件
项目目录下建一个libevent文件夹
在libevent中新建一个lib文件夹，将上面三个lib文件copy到该目录下。
在libevent中再新建一个include文件夹，
将libevent-2.0.22-stable\include下的文件和文件夹copy到该目录下，
将libevent-2.0.22-stable\WIN32-Code下的文件和文件夹copy到该目录下，
2个event2目录下的文件合并一起，主要是event-config.h。

- 项目配置
VC++目录：
    包含目录，添加刚刚新建的include目录
    库目录，添加刚刚的lib目录;
C/C++：
    代码生成-->运行库：
    Debug模式下选：多线程调试 (/MTd)，
    Release模式下选：多线程 (/MT)
连接器：
输入->附加依赖项：
    ws2_32.lib
    wsock32.lib
    libevent.lib
    libevent_core.lib
    libevent_extras.lib
    另外两个库ws2_32.lib和wsock32.lib是用来编译Windows网络相关的程序库。

- 工程中头文件
** 注意：把头文件的引用写到windows.h引用前，不然编译会提示各种struct undefined 或者 struct redefine**