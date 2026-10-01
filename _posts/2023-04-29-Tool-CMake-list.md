---
layout: post
title: CMake-list
date: 2023-04-29 14:18:00
categories:
- Developer Tools
tags:
- CMake
- Tool
---
>https://www.visgraf.impa.br/seminar/slides/rodlima_cmake_presentation.pdf

- Useful to manage long list of elements
- Elements can be manipulated depending on running platform
  - Useful for source file lists
- Example:
```
set(sources viewer.cpp config.cpp)
if(WIN32)
list(APPEND sources viewer_mfc.cpp)
elseif(UNIX)
list(APPEND sources viewer_gtk.cpp)
else
message(FATAL_ERROR "Platform not supported")
endif()
add_executable(viewer ${sources})
list(LENGTH sources srclen)
message("${srclen} source files")
foreach(src ${sources})
message("Source: ${src}")
endforeach()
```

<!--more-->

参考：[CMake `message` command](https://cmake.org/cmake/help/latest/command/message.html)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 02:00（UTC+08:00）。