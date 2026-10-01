---
layout: post
title: C++-改变终端（cout/printf）输出不同颜色的字体-Linux
display_title: 'C++ 改变终端输出不同颜色的字体 (Linux)'
date: 2023-04-29 18:18:00
categories:
- C & C++
tags:
- C++
---
>https://blog.csdn.net/qq_41972382/article/details/90311102

不同颜色的输出主要使用 SGR 序列 `ESC [ Pm m`；在 C/C++ 字符串中 ESC 可写作八进制转义 `\033`，多个参数用分号 `;` 分隔。

<!--more-->

> **版本范围：** 下表按 Linux man-pages 6.19（2026-07-29）和 XTerm Control Sequences（XTerm Patch #411，2026-08-23）核对；不同终端的扩展序列可能不同。

## printf
```
#include <cstdio>
using namespace std;
int main()
{
    printf("\033[31m红色\033[0m");
    return 0;
}
```
其中:	31m：字体为红色； 0m：关闭所有属性。

## cout
```
#include <iostream>
using namespace std;
int main()
{   
    cout  << "\033[32m修改\033[0m"<< endl ;
    return 0;
}
```

## 常用的ANSI控制码

```
\033[0m 关闭所有属性
\033[1m 高亮
\033[2m 亮度减半
\033[3m 斜体
\033[4m 下划线
\033[5m 闪烁
\033[6m 快闪
\033[7m 反显
\033[8m 消隐
\033[9m 中间一道横线
10-19 关于字体的
21-29 基本与1-9正好相反
30-37 设置前景色
40-47 设置背景色
30:黑
31:红
32:绿
33:黄
34:蓝色
35:紫色
36:深绿
37:白色
38 扩展前景色；后续参数指定 256 色或 24 位颜色 / extended foreground color; 256-color or 24-bit parameters follow
39 设置默认前景色 / set default foreground color
40 黑色背景
41 红色背景
42 绿色背景
43 棕色背景
44 蓝色背景
45 品红背景
46 孔雀蓝背景
47 白色背景
48 扩展背景色；后续参数指定 256 色或 24 位颜色 / extended background color; 256-color or 24-bit parameters follow
49 设置默认背景色
50-89 未在本文所依据的 Linux console / xterm SGR 表中定义；终端扩展需查各自文档 / Not defined in the documented Linux console/xterm SGR tables
90-97 设置亮前景色；100-107 设置亮背景色 / 90–97 bright foreground; 100–107 bright background
\033[nA 光标上移n行
\033[nB 光标下移n行
\033[nC 光标右移n行
\033[nD 光标左移n行
\033[y;xH设置光标位置
\033[2J 清屏
\033[K 清除从光标到行尾的内容
\033[s 保存光标位置
\033[u 恢复光标位置
\033[?25l 隐藏光标
\033[?25h 显示光标
```

参考：[Linux `console_codes(4)`](https://man7.org/linux/man-pages/man4/console_codes.4.html)、[XTerm Control Sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html) 和 [Microsoft `<cstdio>`](https://learn.microsoft.com/en-us/cpp/standard-library/cstdio?view=msvc-170)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 03:56（UTC+08:00）。