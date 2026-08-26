---
layout: post
title: Gitlab-重置root账户密码
date: 2024-04-23 08:37:00
categories:
- Developer Tools
tags:
- GitLab
- Tool
---

## 背景

<!--more-->
遗忘或丢失Gitlab的root账户密码时，直接重置其密码

## 方法

终端 `sudo gitlab-rails console`

在Gitlab Rails Console中执行

    user = User.find_by_username('root')
    user.password = 'new_password'
    user.password_confirmation = 'new_password'
    user.save!
    
    
    
    exit