---
layout: post
title: "OS-Windows CMD生成文件夹目录结构"
date: 2020-07-06 23:35:00
categories: ["OS"]
tags: ["Windows批处理 (cmd/bat)", "Windows", "OS"]
---

July 6, 2020 11:18 PM

<!--more-->
参考 [CMD生成文件夹目录结构](https://blog.csdn.net/Draling/article/details/8855520?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-2)

## 单层生成
命令：
	`dir [drive:][path] /b > [drive:][path]filename`
如何把多个目录下的所有文件名都导入同一文件：
	`dir [drive:][path] /b >> [drive:][path]filename`

## 多层生成
### Tree
   Tree是Windows操作系统专门用来以图形方式显示驱动器或路径的文件夹结构的命令，它是DOS命令，它显示的文件目录按照树型显示，非常的直观，就像一个分支表。
命令格式为：`Tree [drive:][path] [/f] [/a]`
各参数分别为：
　　drive表示要显示目录结构的磁盘的驱动器。
　　path 表示要显示目录结构的目录。
　　/f 表示显示每个目录中的文件名。
　　/a 表示命令使用文本字符而不是图形字符显示链接子目录的行。

### Dir
Dir命令是显示文件和目录的命令.
其中两个参数“/s”和“/a”，前者表示显示指定目录和子目录下的所有文件，后者表示显示目录下所有文件的名称，包括隐藏文件和系统文件。
Dir 在保存文件目录时，还会保存文件的日期、创建时间、文件大小等信息。