---
layout: post
title: Linux-C-信号未决/阻塞-BlockSig(sigset_t s)
date: 2021-01-08 18:10:00
categories:
- Systems
tags:
- Linux
- C
---
```
//BlockSig(SIGPIPE)
void BlockSig(int sig)
{
	sigset_t signal_mask; 		 //设置信号集参数
	sigemptyset(&signal_mask);   //sigemptyset是将s的信号集先清空，
	sigaddset(&signal_mask, sig); // 将 sig 加入 signal_mask；此时只修改信号集，尚未修改线程的信号屏蔽掩码。
	//pthread_sigmask(SIG_BLOCK, &signal_mask, NULL);
    // SIG_BLOCK 将 signal_mask 中的信号并入调用线程的信号屏蔽掩码；NULL 表示不保存旧掩码。
    sigprocmask(SIG_BLOCK, &signal_mask, NULL);
    // 此后若该信号被产生且处理方式不是“忽略”，它会保持未决，直到解除屏蔽或被处理。
}
```

本文修订依据：Linux man-pages 6.19（2026-02-08）的 [`sigsetops(3)`](https://man7.org/linux/man-pages/man3/sigsetops.3.html)、[`sigprocmask(2)`](https://man7.org/linux/man-pages/man2/sigprocmask.2.html) 和 [`sigpending(2)`](https://man7.org/linux/man-pages/man2/sigpending.2.html)。`sigaddset()` 只修改信号集，`sigprocmask()` 修改调用线程的屏蔽掩码；`sigprocmask()` 在多线程进程中的使用未由本文展开。

<!--more-->

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 09:39（UTC+08:00）。修订仅纠正信号集操作、`sigprocmask` 拼写及其屏蔽/未决状态说明。
