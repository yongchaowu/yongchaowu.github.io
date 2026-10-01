---
layout: post
title: C++-unique_lock与lock_guard区别
display_title: 'C++ unique_lock 与 lock_guard 区别'
date: 2023-04-11 21:13:00
categories:
- C & C++
tags:
- C++
---
>[https://blog.csdn.net/ccw_922/article/details/124662275](https://blog.csdn.net/ccw_922/article/details/124662275)
>[https://blog.csdn.net/sinat_35945236/article/details/124505414](https://blog.csdn.net/sinat_35945236/article/details/124505414)

`lock_guard` 和 `unique_lock` 都可以对 `std::mutex` 进行 RAII 管理。前者是严格的作用域锁，后者是可移动、可延迟加锁且支持手动解锁的锁所有权包装器；应根据所需语义选择，而不能仅按“能否互相替代”判断。

<!--more-->

## 使用方式
- lock_guard：
`lock_guard` 通常用来管理一个 `std::mutex` 类型的对象，通过定义一个 `lock_guard` 对象来管理 `std::mutex` 的上锁和解锁。
(1) 创建即加锁，作用域结束自动析构并解锁，无需手工解锁
(2) 不能中途解锁，必须等作用域结束才解锁
(3) 不能复制
注意：
`lock_guard` 并不延长 `std::mutex` 对象的生命周期。如果在 `lock_guard` 仍持有锁时让该 `mutex` 结束生命周期，之后析构 `lock_guard` 试图解锁的行为是未定义行为，不是“空指针错误”。

- unique_lock：
创建时可以不锁定（通过指定第二个参数为 `std::defer_lock`），而在需要时再锁定
可以随时加锁、解锁或尝试加锁
作用域规则同 `lock_guard`，析构时自动释放它仍然拥有的锁
不可复制，可移动

## 赋值操作
`unique_lock` 和 `lock_guard` 都不能复制；`lock_guard` 不能移动，但是 `unique_lock` 可以移动。
```
// unique_lock 可以移动，不能复制
std::unique_lock<std::mutex> guard1(_mu);
std::unique_lock<std::mutex> guard2 = guard1;  // error
std::unique_lock<std::mutex> guard2 = std::move(guard1); // ok

// lock_guard 不能移动，不能复制
std::lock_guard<std::mutex> guard1(_mu);
std::lock_guard<std::mutex> guard2 = guard1;  // error
std::lock_guard<std::mutex> guard2 = std::move(guard1); // error
```

## 资源消耗
`unique_lock` 需要额外维护锁状态，通常比 `lock_guard` 占用的状态空间更大，但 C++ 标准不规定两者的具体性能差异。只需在整个作用域持锁时，优先使用语义更简单的 `lock_guard`；需要延迟加锁、手动解锁、所有权转移或与 `std::condition_variable` 配合时，再使用 `unique_lock`。

`std::condition_variable` 的 `wait` 系列函数使用 `std::unique_lock<std::mutex>`；`std::condition_variable_any` 则支持其他满足 BasicLockable 要求的锁类型。

参考：[cppreference：std::lock_guard](https://en.cppreference.com/w/cpp/thread/lock_guard)、[std::unique_lock](https://en.cppreference.com/w/cpp/thread/unique_lock) 和 [std::condition_variable](https://en.cppreference.com/w/cpp/thread/condition_variable)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 01:31（UTC+08:00）。
