---
layout: post
title: CMake-添加自定义宏定义
display_title: 'CMake 添加自定义宏定义'
date: 2023-07-24 19:32:00
categories:
- Developer Tools
tags:
- CMake
- Tool
---
CMake 中传给编译器的预处理器定义，作用与 C/C++ 中的 `#define` 相近，可以用于控制 C/C++ 编译。
控制程序的编译
比如：CMake 中有预处理器定义：`add_definitions(-Dhello="hello cmake")`

本文修订依据：CMake 3.31.12 文档中的 [`add_definitions`](https://cmake.org/cmake/help/v3.31/command/add_definitions.html) 和 [`add_compile_definitions`](https://cmake.org/cmake/help/v3.31/command/add_compile_definitions.html)。原文未指定 CMake 版本，因此保留原有命令，不将其改写为其他版本中的替代命令。

<!--more-->

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 08:56（UTC+08:00）。修订仅区分 CMake 变量与传给编译器的预处理器定义。
