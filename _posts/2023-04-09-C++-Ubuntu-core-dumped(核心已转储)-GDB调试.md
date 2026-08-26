---
layout: post
title: C++-Ubuntu core dumped(核心已转储)-GDB调试
date: 2023-04-09 23:07:00
categories:
- C & C++
tags:
- C++
- GDB
- coredump
- Debug
---

Linux的可执行程序异常退出时，提示“核心已转储”。
此时需要系统生成core文件，并通过GDB调试以确定问题。

<!--more-->
>[https://blog.csdn.net/scjdas/article/details/128585787](https://blog.csdn.net/scjdas/article/details/128585787)

## 设置系统生成core文件
用 `ulimit -a` 查看 `core` `file size` 项是否为 `unlimited`。如果不是，修改成`unlimited` （指令：`ulimit -c unlimited`）
当程序异常时，使用`ll` 命令应该就可以在当前路径下看到core文件。

### core文件路径
*ps：按照以下方法，确实在可执行文件当前目录下生成了core。*

检查core产生路径是否正确，`cat /proc/sys/kernel/core_pattern`
如果路径不存在，则设置：`echo "./core-%e-%p-%s" > /proc/sys/kernel/core_pattern`

core设置主要命令解析：
```
# 控制core文件的文件名中是否添加pid作为扩展
echo "1" > /proc/sys/kernel/core_uses_pid  
# 设置core文件的输出路径和输出文件名，这里我的路径是/home/boy/corefile，文件名就是后面的部分
echo "/home/boy/corefile/core-%e-%p-%t"> /proc/sys/kernel/core_pattern 
 
# 参数说明
%p - insert pid into filename 添加pid
%u - insert current uid into filename 添加当前uid
%g - insert current gid into filename 添加当前gid
%s - insert signal that caused the coredump into the filename 添加导致产生core的信号
%t - insert UNIX time that the coredump occurred into filename 添加core文件生成时的unix时间
%h - insert hostname where the coredump happened into filename 添加主机名
%e - insert coredumping executable name into filename 添加程序名
```

----------

因为ubuntu官方为了自动收集错误，设置了服务`apport.service`，用于自动生成崩溃报告，我们还是无法获取core文件，可以暂时将该服务关闭。
```bash
#1.关闭错误报告
sudo systemctl disable apport.service
#或
sudo service apport stop
 
 
#2.启用错误报告
sudo systemctl enable apport.service
#或
sudo service apport start
```
重新运行程序即可。

## gdb调试core
`gdb  可执行文件  core文件`
更多操作需要查看gdb相关文档。
