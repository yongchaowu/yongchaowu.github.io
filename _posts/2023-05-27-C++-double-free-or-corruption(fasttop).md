---
layout: post
title: "C++-double free or corruption(fasttop)"
date: 2023-05-27 11:28:00
categories: ["C++"]
tags: ["C++"]
---

出现double free or corruption(fasttop)
检查：
1. delete，是否有重复delete
2. 隐式的复制构造函数导致析构次数增加
3. 全局变量，项目代码合并时，不同的共享库中出现同名的全局变量[本次问题的原因，修改新增的全局变量名称后fixed.]

<!--more-->
