---
layout: post
title: "C++-shared_ptr"
date: 2023-05-10 06:04:00
categories: ["C++"]
tags: ["C++"]
---

```cpp
#include <iostream>
#include <memory>
#include <vector>

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
输出结果如下：智能指针执行了类A的析构。
```
A cc.
A cc.
A dd.
[1] + Done
```