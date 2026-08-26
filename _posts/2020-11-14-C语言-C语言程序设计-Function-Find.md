---
layout: post
title: C语言-C语言程序设计-Function-Find
date: 2020-11-14 10:41:00
categories:
- C & C++
tags:
- C
---

照着书敲了一遍然后又重新读了一次才发现程序通过while循环识别的 -xn这种输入。

<!--more-->
```C
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXLINE 1000

int getline(char *line, int max);

/* find函数: 打印所有与第一个参数指定的模式相匹配的行*/
/* find -x -n */
int main(int argc, char *argv[])
{
    char line[MAXLINE];
    long lineno = 0;
    int c, except = 0, number = 0,found = 0;

    while(--argc > 0 && (*++argv)[0] == '-')
        while( c = *++argv[0]) //这里循环直接识别了 -xn
            switch(c){
            case 'x':
                except = 1;
                break;
            case 'n':
                number = 1;
                break;
            default:
                printf("find: illegal option %c\n", c);
                argc = 0;
                found = -1;
                break;
            }
    if(argc != 1)
        printf("Usage:find -x -n pattern\n");
    else
        while(getline(line, MAXLINE) > 0){
            lineno++;
            if((strstr(line, *argv) != NULL) != except){
                if(number)
                    printf("%ld", lineno);
                printf("%s", line);
                found++;
            }
        }
    return found;
}

int getline(char *line, int max)
{
    if(fgets(line, max, stdin) == NULL)
        return 0;
    else
        return strlen(line);
}

```