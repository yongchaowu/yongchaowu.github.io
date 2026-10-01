---
layout: post
title: C++-Struct string初始化&&map初始化
date: 2020-07-10 02:17:00
categories:
- C & C++
tags:
- C++
---
July 10, 2020 2:16 AM

- swap：vector/map
```cpp
std::vector<T>().swap(m_vStruct);
std::map<K, V>().swap(m_map);
```

<!--more-->

- struct memset
结构体成员包含 `std::string` 等非平凡类型时，不应使用 `memset` 初始化对象；对非平凡可复制对象调用 `memset` 属于未定义行为，可能破坏对象内部资源。

- struct 有 map 类型成员
`std::map` 成员可以在结构体构造函数中初始化；不要用 `memset` 或未初始化的聚合初始化方式处理包含 `std::map` 的对象。

参考：[cppreference: std::memset](https://en.cppreference.com/w/cpp/string/byte/memset)

[Online resources](https://blog.csdn.net/taolinke/article/details/5269096)

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 00:05（UTC+08:00）。
