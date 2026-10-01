---
layout: post
title: CMake-Own Finder(-I -L -l)-compiling
date: 2023-04-29 13:52:00
categories:
- Developer Tools
tags:
- CMake
- Tool
---
What is a finder

- When compiling a piece of software which 
links to third­party libraries, we need to know:
	- Where to find the .h files (-I in gcc)
	- Where to find the libraries (.so/.dll/.lib/.dylib/...) (-L
in gcc)
	- The filenames of the libraries we want to link to (-l
in gcc)
- That's the basic information a finder needs to 
return

<!--more-->

本文修订依据：GCC 4.8.5 官方手册的 [`Options for Directory Search`](https://gcc.gnu.org/onlinedocs/gcc-4.8.5/gcc/Directory-Options.html) 与 [`Options for Linking`](https://gcc.gnu.org/onlinedocs/gcc-4.8.5/gcc/Link-Options.html)，分别定义了 `-I`、`-L` 和 `-l` 选项。本文仅移除这三个选项前误插入的 U+00AD 软连字符，保留 `third-party` 原有的 U+00AD 软连字符。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 13:30（UTC+08:00）。修订仅纠正 `-I`、`-L` 和 `-l` 三个 GCC 选项标记。
