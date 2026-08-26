---
layout: post
title: Linux-ARM-Actual use of physical memory
date: 2020-07-10 01:10:00
categories:
- Systems
tags:
- Physical Memory
- ARM
- Linux
- OS
---

[在ARM板上的linux系统中查看进程实际使用物理内存](https://blog.csdn.net/yangjie1987636/article/details/45871103?utm_source=blogxgwz0)

<!--more-->
在/proc/pid/status可以查看，pid为你要查看进程的进程号，比如我要查看的进程"./MQTTServer"就得进入/proc/31540/status进行查看，输入，返回如下：
![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710010838452-10121562.png)

下面对相关参数进行解释：

Name       ： 应用程序或命令的名字
State        ：  任务的状态，运行/睡眠/僵死/ 
Tgid         ： 线程组号
Pid           ：任务ID
Ppid         ：父进程ID
TracerPid ：接收跟踪该进程信息的进程的ID号


Uid:    0       0       0       0
Gid:    0       0       0       0

解释:
第一列数字(RUID):实际用户ID,指的是进程执行者是谁.
第二列数字(EUID):有效用户ID,指进程执行时对文件的访问权限.
第三列数字(SUID):保存设置用户ID,作为effective user ID的副本,在执行exec调用时后能重新恢复原来的effective user ID.
第四列数字(FSUID):目前进程的文件系统的用户识别码.一般情况下,文件系统的用户识别码(fsuid)与有效的用户识别码(euid)是相同的.

FDSize： 文件描述符的最大个数，file->fds
Groups
VmPeak（KB）：进程地址空间的大小，当前进程运行过程中占用内存的峰值（虚拟内存）
VmSize(KB)     ：任务虚拟地址空间的大小 (total_vm-reserved_vm)，其中total_vm为进程的地址空间的大小，reserved_vm：进程在预留或特殊的内存间的物理页
VmLck(KB)      ：任务已经锁住的物理内存的大小。锁住的物理内存不能交换到硬盘 (locked_vm)
VmHWM(KB)   :  程序得到分配到物理内存的峰值
VmRSS(KB)     ：应用程序正在使用的物理内存的大小，就是用ps命令的参数rss的值 (rss)
VmData(KB)    ：程序数据段的大小（所占虚拟内存的大小），存放初始化了的数据； (total_vm-shared_vm-stack_vm)
VmStk(KB)      ：任务在用户态的栈的大小 (stack_vm)
VmExe(KB)     ：程序所拥有的可执行虚拟内存的大小，代码段，不包括任务使用的库 (end_code-start_code)
VmLib(KB)      ：被映像到任务的虚拟内存空间的库的大小 (exec_lib)
VmPTE           :该进程的所有页表的大小，单位：kb
Threads          :共享使用该信号描述符的任务的个数，在POSIX多线程应用程序中，线程组中的所有线程使用同一个信号描述符。
SigQ               :待处理信号的个数
SigPnd            :屏蔽位，存储了该线程的待处理信号
ShdPnd           :屏蔽位，存储了该线程组的待处理信号
SigBlk             :存放被阻塞的信号
SigIgn             :存放被忽略的信号
SigCgt             :存放被俘获到的信号
CapInh     :能被当前进程执行的程序的继承的能力
CapPrm     :进程能够使用的能力，可以包含CapEff中没有的能力，这些能力是被进程自己临时放弃的
CapEff     ：是CapPrm的一个子集，进程放弃没有必要的能力有利于提高安全性

voluntary_ctxt_switches    :进程主动切换的次数
nonvoluntary_ctxt_switches :进程被动切换的次数
————————————————
版权声明：本文为CSDN博主「IT之路」的原创文章，遵循 CC 4.0 BY-SA 版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/yangjie1987636/java/article/details/45871103