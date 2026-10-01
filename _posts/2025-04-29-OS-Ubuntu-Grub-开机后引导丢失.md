---
layout: post
title: Ubuntu Grub 开机后引导丢失
date: 2025-04-29 20:35:00
categories:
- Systems
tags:
- OS
- Ubuntu
- Grub
---
##现象
Ubuntu系统启动后提示：
```text
GNU GRUB version 2.02
Minimal BASH-like line editing is supported. 
For the first word. 
TAB lists possible command completions. 
Anywhere else TAB lists possible device or file completions.

grub>
```

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
8. 以上命令在 `grub>` rescue shell 中执行；`update-grub` 和 `grub-install` 是操作系统命令，不应在这个提示符中直接执行。
9. 启动系统或 Live 环境后，在系统 shell（或已挂载系统的 chroot）中执行：
   ```bash
   sudo update-grub
   sudo grub-install /dev/sda
   ```
   `/dev/sda` 仅为示例，应根据实际启动磁盘和 BIOS/UEFI 模式调整。

<!--more-->

参考：[GNU GRUB rescue shell](https://www.gnu.org/software/grub/manual/grub/html_node/GRUB-only-offers-a-rescue-shell.html) 和 [Ubuntu Grub2/Installing](https://help.ubuntu.com/community/Grub2/Installing)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 02:22（UTC+08:00）。
