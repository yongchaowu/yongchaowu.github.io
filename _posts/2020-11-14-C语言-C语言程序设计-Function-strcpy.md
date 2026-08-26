---
layout: post
title: "C语言-C语言程序设计-Function-strcpy"
date: 2020-11-14 10:56:00
categories: ["C语言"]
tags: ["C语言", "C"]
---

书上关于strcpy介绍了数组、指针、指针简化的例子，对于代码简化是个可见的例子，记录下来。

<!--more-->
```C
#include <stdio.h>
#include <stdlib.h>

int main()
{
    //initial value
    char cTmp[] = "It will be better, tomorrow.";
    printf("cTmp:%s\n", cTmp);

    char* pTmp =  "It will be better, tomorrow.";
    printf("pTmp:%s\n", pTmp);

    char* pCon = malloc(100);
    memset(pCon, 0, sizeof(char));
    printf("pCon:%s\n", pCon);

    //
    strcpy1(pCon, pTmp);
    printf("pCon1:%s\n", pCon);
    memset(pCon, 0, sizeof(char));
    printf("pCon:%s\n", pCon);

    strcpy2(pCon, pTmp);
    printf("pCon2:%s\n", pCon);
    memset(pCon, 0, sizeof(char));
    printf("pCon:%s\n", pCon);

    strcpy3(pCon, pTmp);
    printf("pCon3:%s\n", pCon);
    memset(pCon, 0, sizeof(char));
    printf("pCon:%s\n", pCon);

    strcpy4(pCon, pTmp);
    printf("pCon4:%s\n", pCon);
    memset(pCon, 0, sizeof(char));
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