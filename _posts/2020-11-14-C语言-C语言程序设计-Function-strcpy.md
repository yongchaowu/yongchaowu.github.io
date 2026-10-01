---
layout: post
title: C语言-C语言程序设计-Function-strcpy
date: 2020-11-14 10:56:00
categories:
- C & C++
tags:
- C
---
书上关于strcpy介绍了数组、指针、指针简化的例子，对于代码简化是个可见的例子，记录下来。

```C
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

<!--more-->

int main()
{
    //initial value
    char cTmp[] = "It will be better, tomorrow.";
    printf("cTmp:%s\n", cTmp);

    char* pTmp =  "It will be better, tomorrow.";
    printf("pTmp:%s\n", pTmp);

    char* pCon = calloc(100, sizeof *pCon);
    if (pCon == NULL) {
        return 1;
    }
    memset(pCon, 0, 100 * sizeof *pCon);
    printf("pCon:%s\n", pCon);

    //
    strcpy1(pCon, pTmp);
    printf("pCon1:%s\n", pCon);
    memset(pCon, 0, 100 * sizeof *pCon);
    printf("pCon:%s\n", pCon);

    strcpy2(pCon, pTmp);
    printf("pCon2:%s\n", pCon);
    memset(pCon, 0, 100 * sizeof *pCon);
    printf("pCon:%s\n", pCon);

    strcpy3(pCon, pTmp);
    printf("pCon3:%s\n", pCon);
    memset(pCon, 0, 100 * sizeof *pCon);
    printf("pCon:%s\n", pCon);

    strcpy4(pCon, pTmp);
    printf("pCon4:%s\n", pCon);
    memset(pCon, 0, 100 * sizeof *pCon);
    printf("pCon:%s\n", pCon);

    return 0;
}

void strcpy1(char *s, char *t)
{
    int i = 0;
    while((s[i]=t[i]) != '\0')
        i++;
}

void strcpy2(char *s, char *t)
{
    while((*s = *t) != '\0')
    {
        s++;
        t++;
    }
}

void strcpy3(char *s, char *t)
{
    while((*s++ = *t++) != '\0');
}

void strcpy4(char *s, char *t)
{
    while(*s++ = *t++);
}

```

参考：[cppreference：`calloc`](https://en.cppreference.com/w/c/memory/calloc) 和 [`memset`](https://en.cppreference.com/w/c/string/byte/memset)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 02:02（UTC+08:00）。