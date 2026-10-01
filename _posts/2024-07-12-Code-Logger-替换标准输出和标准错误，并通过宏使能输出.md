---
layout: post
title: Logger-替换标准输出和标准错误，并通过宏使能输出
display_title: 'Logger 替换标准输出和标准错误，并通过宏使能输出'
date: 2024-07-12 13:18:00
categories:
- Programming
tags:
- Code
---
需求：替换标准输出和标准错误，并通过宏使能输出
- `class Logger`
```c++

#ifndef ENABLE_LOGS
#define ENABLE_LOGS 1 // 设置为1表示启用日志输出，0则禁用
#endif

#include <iostream>
#include <sstream>

class Logger {
public:
    template<typename T>
    Logger& operator<<(const T& value) {
        if (ENABLE_LOGS) {
            stream_ << value;
        }
        return *this;
    }

    // 当需要输出时，调用此函数
    void printCOUT() {
        if (ENABLE_LOGS) {
            std::cout << stream_.str() << std::endl;
            stream_.str(""); // 清空stringstream
        }
    }

    void printCERR() {
        if (ENABLE_LOGS) {
            std::cerr << stream_.str() << std::endl;
            stream_.str(""); // 清空stringstream
        }
    }

private:
    std::stringstream stream_;
};
```

- Demo
```c++
#include "logger.h" // 假设上面的Logger定义在这个文件中

<!--more-->

void exampleUsage() {
    Logger example;
    example << "这是一个例子: " << 123 << " 和 " << 45.67;
    example.printCOUT();
    // 或者使用print方法
    Logger log;
    log << "另一个例子: " << true << " 在行尾不需要手动换行";
    log.printCOUT();
}
```

参考：[Microsoft Learn：`basic_stringstream` class](https://learn.microsoft.com/en-us/cpp/standard-library/basic-stringstream-class?view=msvc-170)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 02:02（UTC+08:00）。