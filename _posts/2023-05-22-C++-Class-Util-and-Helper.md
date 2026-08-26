---
layout: post
title: C++-Class-Util & Helper
date: 2023-05-22 21:11:00
categories:
- C & C++
tags:
- C++
---

>https://zhuanlan.zhihu.com/p/352749160
>https://www.cnblogs.com/ligiggy/p/15320192.html

<!--more-->
```
A Utility class is understood to only have static methods and be stateless. You would not create an instance of such a class.
A Helper can be a utility class or it can be stateful or require an instance be created.
```

翻译一下。

Util类，一般是无状态的，只包含静态方法。使用时无需创建类的实例。
Helper类，可以有状态（类的成员变量），一般需要创建实例才能使用。
