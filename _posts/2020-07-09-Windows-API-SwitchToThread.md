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

<!--more-->
## SwitchToThread
[Windows编程－－线程的切换](https://www.cnblogs.com/fangshenghui/archive/2011/01/05/1926335.html)

系统提供了一个称为SwitchToThread的函数，使得另一个可调度线程（如果存在能够运行）：BOOL SwitchToThread();
当调用这个函数的时候，系统要查看是否存在一个迫切需要CPU时间的线程。如果没有线程迫切需要CPU时间，SwitchToThread就会立即返回。如果存在一个迫切需要CPU时间的线程，SwitchToThread就对该线程进行调度（该线程的优先级可能低于调用SwitchToThread的线程）。这个迫切需要CPU时间的线程可以运行一个时间段，然后系统调度程序照常运行。
该函数允许一个需要资源的线程强制另一个优先级较低、而目前却拥有该资源的线程放弃该资源（抢占资源）。如果调用SwitchToThread函数时没有其他线程能够运行，那么该函数返回FALSE，否则返回一个非0值。
- SwitchToThread和Sleep的异同
  调用SwitchToThread函数与调用Sleep是相似的，并且传递给它一个0ms的超时。差别：是SwitchToThread允许优先级较低的线程运行。即使低优先级线程迫切需要CPU时间，Sleep也能够立即对调用线程重新进行调度。
（FangSH注：网上有人这样说：区别在于，SwitchToThread允许执行低优先级线程，Sleep会立即重新调度主调线程，即使低优先级线程会处于饥饿状态。）