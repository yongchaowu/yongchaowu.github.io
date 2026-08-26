---
layout: post
title: "OS-Linux-动态链接文件设置环境变量-/etc/ld.so.conf ldconfig ldd"
date: 2020-10-22 20:37:00
categories: ["OS"]
tags: ["OS", "Linux"]
---

October 22, 2020 8:22 PM
现象：在Linux下，用sh脚本可以启动的程序使用pytest的时候提示xxx.so文件不存在
原因：so不在环境变量中，pytest查询时无法查询到
解决方法：配置Linux的ld.so.conf文件
具体步骤：
```language
1. vi  /etc/ld.so.conf
2. 在文件最后加入so的文件路径，使用绝对路径
3. 保存退出
4. ldconfig
```

<!--more-->
## 原理
参照 [动态装入器（dynamic loader）](https://blog.csdn.net/leonliu06/article/details/78587511)
```plain
动态装入器（dynamic loader）负责将动态可执行程序和所有必需的共享库一起装入，以使它们能正确执行。
/lib64/ld-linux-x86-64.so.2 即是64位linux系统下的动态装入器

动态装入器找到共享库要依靠两个文件 —— /etc/ld.so.conf和 /etc/ld.so.cache。

ld.so.conf 文件包含一个所有目录（/lib 和 /usr/lib 除外，它们会自动包含在其中）的清单，动态装入器将在其中查找共享库。
但是在动态装入器能“看到”这一信息之前，必须将它转换到 ld.so.cache 文件中。可以通过运行 ldconfig 命令做到这一点，当 ldconfig 操作结束时，您会有一个最新的 /etc/ld.so.cache 文件，它反映您对 /etc/ld.so.conf 所做的更改。从这一刻起，动态装入器在寻找共享库时会查看您在 /etc/ld.so.conf 中指定的所有新目录。

$ldconfig
LD_LIBRARY_PATH
　　要指示动态装入器首先检查某个目录，请将 LD_LIBRARY_PATH 变量设置成您希望搜索的目录。多个路径之间用冒号分隔；例如：
　　$ export LD_LIBRARY_PATH="/usr/lib/old:/opt/lib"
　　导出 LD_LIBRARY_PATH 后，如有可能，所有从当前 shell 启动的可执行程序都将使用 /usr/lib/old 或 /opt/lib 中的库，如果仍不能满足一些共享库相关性要求，则转回到 /etc/ld.so.conf 中指定的库。

$ldd命令查看程序依赖的动态库，可以判断是否有动态库缺失
ldd [程序名]
```
