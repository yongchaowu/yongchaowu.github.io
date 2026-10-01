---
layout: post
title: C语言-C语言程序设计-Practice code
date: 2020-11-14 11:02:00
categories:
- C & C++
tags:
- C
---
书上第一章的几个练习。 关于直方图有点头疼，之后再仔细研究一下。

```C
    /*1-8 统计空格、制表符、换行符个数*/
    int c;
    int nl = 0;
    int nt = 0;
    int nb = 0;
    while((c = getchar()) != EOF){
        if(c == '\n'){
            ++nl;
            printf("nl:%d\n", nl);
        }
         if(c == '\t'){
            ++nt;
            printf("nt:%d\n", nt);
        }
         if(c == ' '){
            ++nb;
            printf("nb:%d\n", nb);
        }
    }
    printf("nl:%d\n", nl);

<!--more-->

```

```C
 	/*1-9 连续多个空格替换为一个*/
    int c;
    int nSpaceNum = 0;
    while((c = getchar()) != EOF){
        if(c == ' '){
            ++nSpaceNum;
            if(nSpaceNum > 1){
                continue;
            }
        }else{
            nSpaceNum = 0;
        }

        putchar(c);
    }

```

```C
	/*1-10 输出\t \b \\*/
    int c;
    while((c = getchar()) != EOF){
        if(c == '\t'){
            printf("\\t");
            continue;
        }

        if(c == '\b'){
            printf("\\b");
            continue;
        }

        if(c == '\\'){
            printf("\\\\");
            continue;
        }

        putchar(c);
    }

```

```C
#include <ctype.h>
 	/*1-12 每行一个单词*/
    int c;
    int nb = 0;
    while((c = getchar()) != EOF){
        if (isalnum(c)) {
                if(nb > 0){
                    printf("\n");
                    nb = 0;
                }

            printf("%c", c);
            continue;
        }else{
            ++nb;
        }
    }

```

```C
	/*1-13 直方图*/
    待更新
```

本文修订依据：The Open Group Base Specifications Issue 7（IEEE Std 1003.1-2017）的 [`isalnum()`](https://pubs.opengroup.org/onlinepubs/9699919799/functions/isalnum.html) 与 [`getchar()`](https://pubs.opengroup.org/onlinepubs/9699919799/functions/getchar.html) 文档，并交叉核对 WG14 C17 草案 [N2176](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n2176.pdf)。`isalnum()` 需包含 `<ctype.h>`，其参数可接收 `getchar()` 返回的 `unsigned char` 转换后的 `int` 或 `EOF`；本文仅修正 1-12 示例的字母数字判断。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 10:22（UTC+08:00）。修订仅将不可靠的字符范围判断改为 `isalnum()` 并补充所需头文件。