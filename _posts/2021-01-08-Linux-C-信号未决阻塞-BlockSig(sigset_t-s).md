---
layout: post
title: "Linux-C-信号未决/阻塞-BlockSig(sigset_t s)"
date: 2021-01-08 18:10:00
categories: ["Linux"]
tags: ["Linux", "C"]
---

```
//BlockSig(SIGPIPE)
void BlockSig(int sig)
{
	sigset_t signal_mask; 		 //设置信号集参数
	sigemptyset(&signal_mask);   //sigemptyset是将s的信号集先清空，
	sigaddset(&signal_mask, sig);//sigaddset就是把sig加入到s的信号集中，即该位设为1，堵塞。
	//pthread_sigmask(SIG_BLOCK, &signal_mask, NULL);
    //函数中的参数SIG_BLOCK 的作用是将s集合set集合相或操作，于是set的信号集中的第二位被设置为阻塞，NULL 表明不关心信号set集中原有的内容
    sigpromask(SIG_BLOCK, &signal_mask, NULL);
    //当按下ctrl+c时，由于阻塞信号集的第二位设为1，信号未被处理，呈现出未决态
}
```

<!--more-->
