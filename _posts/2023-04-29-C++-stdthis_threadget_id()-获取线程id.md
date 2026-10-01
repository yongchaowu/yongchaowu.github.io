---
layout: post
title: C++-std::this_thread::get_id()-获取线程id
display_title: 'C++ std::this_thread::get_id() 获取线程 ID'
date: 2023-04-29 18:42:00
categories:
- C & C++
tags:
- C++
---
## `std::this_thread::get_id()`
头文件：`<thread>`
函数：`std::this_thread::get_id()`
用例：`std::thread::id thread_id = std::this_thread::get_id();`

## `std::thread`对象的成员函数`get_id()`
头文件：`<thread>`
函数：`std::thread::id get_id()`
用例：通过调用 `std::thread` 对象的 `get_id()` 获取该对象所关联线程的 `std::thread::id`；默认构造的对象未关联线程，返回 `std::thread::id()`。获取当前线程应使用 `std::this_thread::get_id()`。
```
#include <thread>

<!--more-->

std::thread t;
t.get_id();
```

本文修订依据：Microsoft Learn [`thread` class](https://learn.microsoft.com/en-us/cpp/standard-library/thread-class?view=msvc-170) 与 C++11 N3337-derived [`threads.tex`](https://github.com/timsong-cpp/draft/blob/5a74d0ac0486f8400e7340eb1331ac2d6927dea4/source/threads.tex)。`thread::get_id()` 返回对象所关联线程的 ID；默认构造对象未关联线程并返回默认 `thread::id()`，当前线程 ID 应使用 `this_thread::get_id()`。本文仅澄清文字说明。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 11:30（UTC+08:00）。修订仅澄清 `std::thread::get_id()` 与 `std::this_thread::get_id()` 的区别。