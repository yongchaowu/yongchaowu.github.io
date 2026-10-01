---
layout: post
title: C语言-C语言程序设计-Function-fopen
date: 2020-11-14 10:48:00
categories:
- C & C++
tags:
- C
---
直接抄的书上的，编译没过，应该和系统有关，用的windows系统去编译unix上的函数。
就功能理解上还是可以的，所以没有在去linux上重新编译。

```C
#include <stdio.h>
#include <stdlib.h>

<!--more-->

#include <fcntl.h>
#include "sys/fcntl.h"

int main()
{
    printf("Hello world!\n");
    return 0;
}

#define PERMS 0666 /*  所有者、所有者组和其他成员都可以读写*/

/*fopen 函数： 打开文件，并返回文件指针 */
FILE* fopen(char *name, char *mode)
{
    int fd;
    FILE* fp;

    if(*mode != 'r' && *mode != 'w' && *mode != 'a')
        return NULL;
    for(fp = _iob; fp < _iob + OPEN_MAX; fp++)
        if((fp->flag &(_READ | _WRITE)) == 0)
            break;  /*寻找一个空闲位*/

    if(fp >= _iob + OPEN_MAX)  /*没有空闲位置*/
        return NULL;

    if(*mode == 'w')
        fd = creat(name, PERMS);
    else if(*mode == 'a'){
        if((fd = open(name, O_WRONLY, 0)) == -1)
            fd = creat(name, PERMS);
        lseek(fd, 0L, 2);
    }
    else
        fd = open(name, O_RDONLY, 0);

    if(fd == -1)
        return NULL;

    fp->fd = fd;
    fp->cnt = 0;
    fp->base = NULL;
    fp->flag = (*mode == 'r') ? _READ : _WRITE;
    return fp;
}
/*
    以上未涉及标准C的所有访问模式。
    不能识别标识二进制访问方式的b标志
    不能识别允许同时进行读和些的+标志
*/

```

本文修订依据：The Open Group Base Specifications Issue 8 / IEEE Std 1003.1-2024 [`creat()`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/creat.html)。POSIX 接口名称是 `creat()`；本文仅修正该名称，没有重写原有的非可移植 `fopen` 示例。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 09:39（UTC+08:00）。修订仅将 POSIX `creat()` 的拼写错误 `create()` 更正为 `creat()`。