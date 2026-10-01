---
layout: post
title: Windows CMD生成文件夹目录结构
date: 2020-07-06 23:35:00
categories:
- Systems
tags:
- Windows批处理 (cmd/bat)
- Windows
- OS
---
July 6, 2020 11:18 PM

参考 [CMD生成文件夹目录结构](https://blog.csdn.net/Draling/article/details/8855520?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2)

<!--more-->

##单层生成
命令：
	`dir [drive:][path] /b > [drive:][path]filename`
如何把多个目录下的所有文件名都导入同一文件：
	`dir [drive:][path] /b >> [drive:][path]filename`

##多层生成
###Tree
   Tree是Windows操作系统专门用来以图形方式显示驱动器或路径的文件夹结构的命令，它是DOS命令，它显示的文件目录按照树型显示，非常的直观，就像一个分支表。
命令格式为：`Tree [drive:][path] [/f] [/a]`
各参数的分别为：
　　drive表示要显示目录结构的磁盘的驱动器。
　　path 表示要显示目录结构的目录。
　　/f 表示显示每个目录中的文件名。
　　/a 表示命令使用文本字符而不是图形字符显示链接子目录的行。

###Dir
Dir命令是显示文件和目录的命令.
其中两个参数“/s”和“/a”，前者表示显示指定目录和子目录下的所有文件，后者表示显示目录下所有文件的名称，包括隐藏文件和系统文件。
使用 /b 保存时只输出驱动器、目录、文件名和扩展名；普通 dir 输出还包含最后修改时间、文件大小等信息（创建时间需 /t:c）。

本文修订依据：Microsoft Learn [`dir` command](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/dir)，源文档提交 `b775a304e25c750193233a6e3562ab309b52aa55`（页面更新 2026-09-08），并交叉核对 [Windows Server 2012/2012 R2 `dir` reference](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/cc755121(v=ws.11))。`/b` 是无附加信息的裸列表，`/t:c` 明确选择创建时间；本文仅修正 `/b` 输出说明。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 10:42（UTC+08:00）。修订仅纠正 `dir /b` 与普通 `dir` 输出的说明。