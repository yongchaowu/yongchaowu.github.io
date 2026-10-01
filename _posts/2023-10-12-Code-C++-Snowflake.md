---
layout: post
title: C++-Snowflake
display_title: 'C++ Snowflake'
date: 2023-10-12 12:49:00
categories:
- Programming
tags:
- C++
- Code
- Snowflake
---
```
#include <iostream>
#include <chrono>
#include <cstdint>
#include <stdexcept>

<!--more-->

using std::int64_t;

class Snowflake {
private:
    // 雪花算法的各个参数
    static constexpr int64_t workerIdBits = 5;
    static constexpr int64_t datacenterIdBits = 5;
    static constexpr int64_t sequenceBits = 12;

    static constexpr int64_t maxWorkerId = -1 ^ (-1 << workerIdBits);
    static constexpr int64_t maxDatacenterId = -1 ^ (-1 << datacenterIdBits);
    static constexpr int64_t sequenceMask = -1 ^ (-1 << sequenceBits);
 // sequenceMask =0b111111111111
    int64_t workerId;
    int64_t datacenterId;
    int64_t sequence = 0;
    int64_t lastTimestamp = -1;

public:
    Snowflake(int64_t workerId, int64_t datacenterId)
            : workerId(workerId), datacenterId(datacenterId) {}

    int64_t generateId() {
        // 获取当前时间戳（毫秒级）
        auto timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count();

        if (timestamp < lastTimestamp) {
            throw std::runtime_error("Invalid system clock!");
        }

        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) & sequenceMask;
            if (sequence == 0) {
                timestamp = waitNextMillis(lastTimestamp);
            }
        } else {
            sequence = 0;
        }

        lastTimestamp = timestamp;

        // 生成最终的唯一ID
        int64_t uniqueId = (timestamp << (workerIdBits + datacenterIdBits + sequenceBits)) |
                           (datacenterId << (workerIdBits + sequenceBits)) |
                           (workerId << sequenceBits) |
                           sequence;
        return uniqueId;
    }

private:
    int64_t waitNextMillis(int64_t lastTimestamp) {
        auto timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count();
        while (timestamp <= lastTimestamp) {
            timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
                    std::chrono::system_clock::now().time_since_epoch()).count();
        }
        return timestamp;
    }
};

int main() {
    Snowflake snowflake(1, 1);
    for (int i = 0; i < 10; i++) {
        int64_t uniqueId = snowflake.generateId();
        std::cout << uniqueId << std::endl;
    }

    return 0;
}
```

本文修订依据：C++11 工作草案 [N3337 §18.4.1 `cstdint.syn`](https://timsong-cpp.github.io/cppwp/n3337/cstdint.syn)。该头文件在 `std` 命名空间中提供 `int64_t`；本文补充 `<cstdint>` 和 `using std::int64_t;`，不改变 Snowflake 位布局、时间戳或唯一性假设。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 10:42（UTC+08:00）。修订仅补充 C++11 `int64_t` 所需的 `<cstdint>` 和命名空间引入。