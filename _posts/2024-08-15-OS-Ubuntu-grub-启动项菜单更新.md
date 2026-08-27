---
layout: post
title: Ubuntu-grub-启动项菜单更新
display_title: 'Ubuntu GRUB 启动项菜单更新'
date: 2024-08-15 09:57:00
categories:
- Systems
tags:
- OS
- Ubuntu
---

Ubuntu18.04.5 系统启动时，启动项菜单有多个ubuntu系统，其中部分系统的磁盘已经格式化，系统不可用，但仍然在启动菜单中。

<!--more-->
- `/etc/default/grub`:grub配置项
- `sudo update-grub`:更新grub启动项菜单，自动识别当前可用系统。