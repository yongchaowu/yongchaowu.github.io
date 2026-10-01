---
layout: post
title: C++-Error:invalid new-expression of abstract class type
date: 2023-04-11 19:58:00
categories:
- C & C++
tags:
- C++
- Debug
---
C++工程，使用new操作符，new一个抽象类对象时编译报错如下：
`Error:invalid new-expression of abstract class type XXX`

## 原因
派生类如果仍含有未被覆盖的纯虚函数，就仍是抽象类。
抽象类不能直接创建对象；只有纯虚函数都被非纯虚函数覆盖、派生类成为具体类后，才能用 new 创建。

<!--more-->

## 实际情况
1. 在子类中实现未实现的纯虚函数。可以考虑用空函数体`{}`。
2. 所谓的“实现”没有真正覆盖基类纯虚函数（例如函数名或参数列表不匹配）；可加 `override` 让编译器检查。
3. 函数写的太乱，纯虚函数夹在其他函数之间，漏掉了。

本文修订依据：C++11 工作草案 [N3337 `class.abstract`](https://timsong-cpp.github.io/cppwp/n3337/class.abstract) 和 [`class.virtual`](https://timsong-cpp.github.io/cppwp/n3337/class.virtual)，并以 C++17 N4659 对应章节交叉核对。标准按“是否仍存在最终覆盖者为纯虚函数”判断类是否抽象；`override` 用于让编译器检查声明是否真正覆盖基类虚函数。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 09:39（UTC+08:00）。修订仅纠正抽象类条件、对象创建条件及 `override` 的作用。
