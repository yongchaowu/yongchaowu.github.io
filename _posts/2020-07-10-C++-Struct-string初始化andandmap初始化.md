---
layout: post
title: "C++-Struct string初始化&&map初始化"
date: 2020-07-10 02:17:00
categories: ["C++"]
tags: ["C++"]
---

July 10, 2020 2:16 AM

<!--more-->
- swap：vector map
std::vector<struct T>().swap(m_vStruct);
std::vector<struct T>().swap(m_mStruct);

- struct memset
结构体成员有string时不可以memset,会导致内存无法释放掉（即使是结构体对象，也无法释放）

- struct 有map类型成员，不能初始化
当结构体中有map成员变量的时候，不能进行初始化，否则在插入操作的时候，会出现异常。
[Online resources](https://blog.csdn.net/taolinke/article/details/5269096)
