---
layout: post
title: "OS-Ubuntu-显卡驱动异常导致花屏-nomodeset"
date: 2024-08-15 10:17:00
categories: ["OS"]
tags: ["OS", "Ubuntu"]
---

Ubuntu系统，显卡驱动异常，导致启动后花屏或无法正常显示输出。

<!--more-->
解决方法：设置`nomodeset`
- 系统启动项页面(grub菜单页面),按`e`键编辑，在`splash`后面增加`nomodeset`参数
- `/etc/modprobe.d/blacklist.conf`
    ```shell
    blacklist nouveau
    options nouveau modeset=0
    ```
    - `sudo update-initramfs -u`
    - `reboot`
    - `lsmod | grep nouveau`
