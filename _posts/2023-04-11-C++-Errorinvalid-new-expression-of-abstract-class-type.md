---
layout: post
title: "C++-Error:invalid new-expression of abstract class type"
date: 2023-04-11 19:58:00
categories: ["C++"]
tags: ["C++", "Debug"]
---

C++工程，使用new操作符，new一个抽象类对象时编译报错如下：
`Error:invalid new-expression of abstract class type XXX`

<!--more-->
## 原因
派生的子类没有完全实现基类父类（接口）中的纯虚函数。
即父类中有函数未在子类中实现，纯虚函数全部需要实现，才能new子类。

## 实际情况
1. 在子类中实现未实现的纯虚函数。可以考虑用空函数体`{}`。
2. 在实现纯虚函数时，漏掉了override。
3. 函数写的太乱，纯虚函数夹在其他函数之间，漏掉了。
