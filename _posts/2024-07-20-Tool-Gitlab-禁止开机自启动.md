---
layout: post
title: Gitlab-禁止开机自启动
date: 2024-07-20 17:22:00
categories:
- Developer Tools
tags:
- GitLab
- Tool
---

Ubuntu18.04 Gitlab设置禁止开机自启动方法

<!--more-->
- `sudo systemctl disable gitlab-runsvdir.service` 禁止开机自启动
- `sudo systemctl enable gitlab-runsvdir.service` 允许开机自启动