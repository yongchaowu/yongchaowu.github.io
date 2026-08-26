---
layout: post
title: "Tool-CMake-添加自定义宏定义"
date: 2023-07-24 19:32:00
categories: ["Tool"]
tags: ["CMake", "Tool"]
---

cmake, makefile 中定义的宏变量，其实和C/C++中的#define 是一致的，可以传入到C/C++中。
控制程序的编译
比如：cmake中有宏定义：`add_definitions(-Dhello="hello cmake")`

<!--more-->
