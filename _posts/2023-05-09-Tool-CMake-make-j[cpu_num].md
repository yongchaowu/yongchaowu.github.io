---
layout: post
title: CMake-make -j[cpu_num]
date: 2023-05-09 05:39:00
categories:
- Developer Tools
tags:
- CMake
- Tool
---

>https://blog.csdn.net/KingOfMyHeart/article/details/105438151

<!--more-->
执行make指令效率较低。
使用make -j后面跟一个数字,让make最多允许n个编译命令同时执行，可以更有效的利用CPU资源。

假设我们的系统cpu是8核，在不影响其他工作的情况下，我们可以`make -j8` 将cpu资源充分利用起来。

一般来说，最大并行任务数为`cpu_num * 2`

```bash
cpu_num=$(nproc)
echo "make -j${cpu_num}"
make -j${cpu_num}
```
或
`nproc`

```sh
cpu_num=$(nproc | awk '{print $1 -1}')
echo $cpu_num
```