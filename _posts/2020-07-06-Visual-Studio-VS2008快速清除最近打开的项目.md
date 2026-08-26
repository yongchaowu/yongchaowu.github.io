---
layout: post
title: "Visual Studio-VS2008快速清除最近打开的项目"
date: 2020-07-06 22:39:00
categories: ["Visual Studio"]
tags: ["Visual Studio", "IDE"]
---

July 6, 2020 10:37 PM
参考[快速清除vs2008最近打开的项目的几个方法](http://www.jquerycn.cn/a_13222)

<!--more-->
##删除最近打开的文件
运行regedit，打开HKEY_CURRENT_USER\Software\Microsoft\VisualStudio\9.0\FileMRUList之后，在右边找到相应的键值删除即可。

##删除最近打开的项目
运行regedit，打开：HKEY_CURRENT_USER\Software\Microsoft\VisualStudio\9.0\ProjectMRUList之后，在右边找到相应的键值删除即可。

## Bat脚本
全部清除
```
@echo off
@REG Delete HKCU\Software\Microsoft\VisualStudio\9.0\FileMRUList /va /f
@REG Delete HKCU\Software\Microsoft\VisualStudio\9.0\ProjectMRUList /va /f
```
