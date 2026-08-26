---
layout: post
title: C++-std::this_thread::get_id()-获取线程id
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

<!--more-->
## `std::thread`对象的成员函数`get_id()`
头文件：`<thread>`
函数：`std::thread::id get_id()`
用例:通过调用std::thread对象的成员函数get_id()来直接获取
```cpp
#include <thread>

std::thread t;
t.get_id();
```