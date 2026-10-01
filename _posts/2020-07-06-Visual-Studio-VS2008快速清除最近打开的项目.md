---
layout: post
title: Visual Studio-VS2008快速清除最近打开的项目
date: 2020-07-06 22:39:00
categories:
- Developer Tools
tags:
- Visual Studio
- IDE
---
July 6, 2020 10:37 PM
参考[快速清除vs2008最近打开的项目的几个方法](http://www.jquerycn.cn/a_13222)

## 删除最近打开的文件
运行regedit，打开HKEY_CURRENT_USER\Software\Microsoft\VisualStudio\9.0\FileMRUList之后，在右边找到相应的键值删除即可。

<!--more-->

## 删除最近打开的项目
运行regedit，打开：HKEY_CURRENT_USER\Software\Microsoft\VisualStudio\9.0\ProjectMRUList之后，在右边找到相应的键值删除即可。

## Bat脚本
全部清除
```
@echo off
@REG Delete HKCU\Software\Microsoft\VisualStudio\9.0\FileMRUList /va /f
@REG Delete HKCU\Software\Microsoft\VisualStudio\9.0\ProjectMRUList /va /f
```

本文修订依据：CommonMark `0.31.2`（2024-01-28）§4.2 的 ATX heading 语法。规范要求起始 `#`/`##` 后使用空格或 tab；本文仅为一处一级标题和两处二级标题补入必需空格，历史注册表命令与流程未改动。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 16:14（UTC+08:00）。修订仅补齐三处标题的 CommonMark 必需空格。
