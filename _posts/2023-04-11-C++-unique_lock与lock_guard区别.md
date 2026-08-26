---
layout: post
title: "C++-unique_lock与lock_guard区别"
date: 2023-04-11 21:13:00
categories: ["C++"]
tags: ["C++"]
---

>[https://blog.csdn.net/ccw_922/article/details/124662275](https://blog.csdn.net/ccw_922/article/details/124662275)
>[https://blog.csdn.net/sinat_35945236/article/details/124505414](https://blog.csdn.net/sinat_35945236/article/details/124505414)

<!--more-->
都可以对std::mutex进行封装，实现RAII的效果。绝大多数情况下这两种锁是可以互相替代的，区别是unique_lock比lock_guard能提供更多的功能特性（但需要付出性能的一些代价）

## 使用方式
- lock_guard：
lock_guard 通常用来管理一个 std::mutex 类型的对象，通过定义一个 lock_guard 一个对象来管理 std::mutex 的上锁和解锁。
(1) 创建即加锁，作用域结束自动析构并解锁，无需手工解锁
(2) 不能中途解锁，必须等作用域结束才解锁
(3) 不能复制
注意：
lock_guard 并不管理 std::mutex 对象的生命周期，也就是说在使用 lock_guard 的过程中，如果 std::mutex 的对象被释放了，那么在 lock_guard 析构的时候进行解锁就会出现空指针错误。

- unique_lock：
创建时可以不锁定（通过指定第二个参数为 std::defer_lock），而在需要时再锁定
可以随时加锁解锁
作用域规则同 lock_guard，析构时自动释放锁
不可复制，可移动


## 赋值操作
unique_lock和lock_guard都不能复制
lock_guard不能移动，但是unique_lock可以移动。
```cpp
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
- unique_lock更加灵活，因为它要维持mutex的状态，但也因此对于资源的消耗明显要大一些，同时效率也比lock_guard更低一点。
- lock_guard虽然笨重一些,但是资源消耗相对要小一点。

另外，unique_lock还在条件变量的使用时发挥作用
