---
layout: post
title: C++-shared_ptr
display_title: 'C++ shared_ptr'
date: 2023-05-10 06:04:00
categories:
- C & C++
tags:
- C++
---
```
#include <iostream>
#include <memory>
#include <vector>

<!--more-->

class A
{
public:
    A(){
        std::cout<<"A cc."<<std::endl;
    };
    ~A(){
        std::cout<<"A dd."<<std::endl;
    };
};

static std::vector<std::shared_ptr<A>> p;
static std::vector<A*> pAA;

void testP()
{
    A* pA = new A;
    std::shared_ptr<A> sp(new A);
    p.push_back(sp);
    pAA.push_back(pA);
}

int main()
{
    testP();

    p.pop_back();
    pAA.pop_back();
    return 0;
}
```

`p` 和 `pAA` 实际保存的是两个不同的 `A` 对象。`sp` 被复制到 `p` 后，`testP` 结束时局部 `sp` 被销毁，但 `p` 中仍有一个 `shared_ptr` 持有第二个对象。执行 `p.pop_back()` 时，最后一个 `shared_ptr` 被销毁，共享控制块调用删除器，因而输出一次 `A dd.`。

`pAA.pop_back()` 只是移除原始指针，不会删除 `pA` 指向的第一个对象，所以该对象会泄漏。并不是 `shared_ptr` 对象直接“执行了类 A 的析构”；是最后一个所有者释放对象后，控制块负责销毁被管理的对象。输出中的 `[1] + Done` 是终端提示符，不属于程序输出；实际输出为：

```
A cc.
A cc.
A dd.
```

参考：[Microsoft Learn：shared_ptr class](https://learn.microsoft.com/en-us/cpp/standard-library/shared-ptr-class) 和 [cppreference：std::shared_ptr](https://en.cppreference.com/w/cpp/memory/shared_ptr)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 01:31（UTC+08:00）。