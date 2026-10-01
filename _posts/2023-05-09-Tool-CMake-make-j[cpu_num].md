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

执行make指令效率较低。
使用make -j后面跟一个数字,让make最多允许n个编译命令同时执行，可以更有效的利用CPU资源。

<!--more-->

假设我们的系统是cpu是8核，在不影响其他工作的情况下，我们可以`make -j8` 将cpu资源充分利用起来。

并行度没有通用的 `cpu_num * 2` 规则；应根据可用处理单元和系统负载选择显式数值。

```
jobs=$(nproc)
echo "make -j${jobs}"
make -j"${jobs}"
```
或先查看可用处理单元：

```sh
jobs=$(nproc)
echo "$jobs"
```

如果要为其他任务保留处理单元，应显式选择一个小于 `nproc` 的正整数。

本文修订依据：Bash 手册的 [`Shell Parameters`](https://www.gnu.org/software/bash/manual/html_node/Shell-Parameters.html) 和 [`Command Substitution`](https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html)、GNU Make 手册的 [`Parallel Execution`](https://www.gnu.org/software/make/manual/html_node/Parallel.html)，以及 GNU Coreutils 的 [`nproc`](https://www.gnu.org/software/coreutils/manual/html_node/nproc-invocation.html)。原代码的带空格赋值不是 shell 变量赋值，裸 `-j` 也没有 job-slot 上限。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 08:33（UTC+08:00）。修订仅修正并行度示例中的 shell 赋值和 `make -j` 参数。