---
layout: post
title: Windows API-SwitchToThread
date: 2020-07-09 08:10:00
categories:
- Systems
tags:
- Windows API
- C++
---
May 6, 2020 8:58 AM

## SwitchToThread
[Windows编程－－线程的切换](https://www.cnblogs.com/fangshenghui/archive/2011/01/05/1926335.html)

<!--more-->

系统提供了一个称为 `SwitchToThread` 的函数，使调用线程自愿让出当前处理器的一个时间片：`BOOL SwitchToThread();`。如果没有其他可运行线程，该函数立即返回 `FALSE`；如果发生了线程切换，则返回非零值。

该函数不会切换到其他处理器，也不会强制其他线程释放资源或执行抢占；让出时间片也不等于保证低优先级线程获得执行机会。

- SwitchToThread 和 Sleep 的异同
  `SwitchToThread` 与 `Sleep(0)` 都会暂时让出当前线程的执行机会，但 `SwitchToThread` 的让出最多持续一个线程时间片，且只针对当前处理器上准备运行的线程；二者都不是资源抢占机制。

参考：[Microsoft Learn：SwitchToThread function](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-switchtothread) 和 [Sleep function](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-sleep)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 01:56（UTC+08:00）。