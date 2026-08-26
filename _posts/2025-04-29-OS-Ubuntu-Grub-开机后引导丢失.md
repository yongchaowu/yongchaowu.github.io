---
layout: post
title: "OS-Ubuntu-Grub-开机后引导丢失"
date: 2025-04-29 20:35:00
categories: ["OS"]
tags: ["OS", "Ubuntu", "Grub"]
---

## 现象
Ubuntu系统启动后提示：
```text
GNU GRUB version 2.02
Minimal BASH-like line editing is supported. 
For the first word. 
TAB lists possible command completions. 
Anywhere else TAB lists possible device or file completions.

grub>
```

<!--more-->
## 解决方案
1. `ls`:显示分区
2. `set`:显示当前grub设置
  - `prefix=(hd0,gpt1)/boot/grub/grub.cfg`
  - `root=hd0,gpt1`
3. `search -f /boot/grub`:搜索grub位置
4. `set prefix=xx;set root=xx`:重置grub
5. `set`:查看配置
6. `insmod normal`:载入normal模组
7. `normal`:激活normal模组
8. `update-grub`
9. `grub-install /dev/sda`:更新grub，写入指定硬盘
