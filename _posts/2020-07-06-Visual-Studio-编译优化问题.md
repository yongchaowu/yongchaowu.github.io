---
layout: post
title: "Visual Studio-编译优化问题"
date: 2020-07-06 22:33:00
categories: ["Visual Studio"]
tags: ["Visual Studio", "IDE"]
---

July 6, 2020 9:58 PM

<!--more-->
## 编译优化问题
[编译优化问题](https://blog.csdn.net/xinqingwuji/article/details/79557712)
如果发生错误，多数是优化时的命名返回值优化产生的问题，这样的优化会导致程序在优化与未优化之间的不同行为
下面是vs的优化选项说明：
/O 选项控制有助于创建具有最高速度或最小大小的代码的各种优化。
/O1 为获得最小大小而优化代码。
/O2 为获得最高速度而优化代码。
/Ob 控制内联函数展开。
/Od 禁用优化，从而加快编译并简化调试。
/Og 启用全局优化。
/Oi 为适当的函数调用生成内部函数。
/Os 通知编译器优选大小优化而非速度优化。
/Ot（默认设置）通知编译器优选速度优化而非大小优化。
/Ox 选择完全优化。
/Oy 取消在调用堆栈上创建框架指针，以更快地进行函数调用。
可以将多个 /O 选项组合到一个选项语句。 例如，/Odi 与 /Od /Oi 是相同的
————————————————
版权声明：本文为CSDN博主「道格拉斯范朋克」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/xinqingwuji/java/article/details/79557712

## 一次/O2 崩溃
[O2导致程序崩溃](https://blog.csdn.net/vonger/article/details/7533242)
函数定义类型说明少了STDAPICALLTYPE,即Windows的CALLTYPE(_stdcall),少了这个导致堆栈错误,程序崩溃.
