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

<!--more-->
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
 	/*1-12 每行一个单词*/
    int c;
    int nb = 0;
    while((c = getchar()) != EOF){
        if((c>='A')&& (c<='z')){
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