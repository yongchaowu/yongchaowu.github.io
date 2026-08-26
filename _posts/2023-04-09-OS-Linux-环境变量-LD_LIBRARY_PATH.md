---
layout: post
title: "OS-Linux-环境变量-LD_LIBRARY_PATH"
date: 2023-04-09 21:55:00
categories: ["OS"]
tags: ["Linux", "OS"]
---

----------
> [Linux中PATH、 LIBRARY_PATH、 LD_LIBRARY_PATH的区别](https://blog.csdn.net/weixin_48859611/article/details/113986310 "Linux中PATH、 LIBRARY_PATH、 LD_LIBRARY_PATH的区别")
----------

<!--more-->
运行时动态库的搜索路径的先后顺序是：
1. 编译目标代码时指定的动态库搜索路径；
2. 环境变量`LD_LIBRARY_PATH`指定的动态库搜索路径；
3. 配置文件`/etc/ld.so.conf`中指定的动态库搜索路径；
4. 默认的动态库搜索路径`/lib`和`/usr/lib`；

----------

Linux指定动态库搜索路径方法：
1. 配置文件`/etc/ld.so.conf`中指定的动态库搜索路径，需要执行`/sbin/ldconfig`使之生效。
2. 环境变量LD_LIBRARY_PATH指定的动态库搜索路径`export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib`该设置只能临时生效，重新启动窗口需要重新设置。
3. 编译代码指定动态库路径

## LD_LIBRARY_PATH
`LD_LIBRARY_PATH`是Linux环境变量名，该环境变量主要用于在程序运行期间指定查找共享库（动态链接库）时除了默认路径之外的其他路径。
- 临时修改：用`export`命令来设置值。
`export LD_LIBRARY_PATH=libtest1:libtest2:$LD_LIBRARY_PATH`

- 永久修改：修改 `~/.bashrc` 或者 `~/.bash_profile`文件，保存、退出，然后执行`source`指令使之生效
```
`~/.bashrc` 或者 `~/.bash_profile`
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/xxx/xxx

source .bashrc或者 source .bash_profile文件
```


### 示例
当执行函数动态链接`.so`时，如果此文件不在缺省目录下`/lib`和`/usr/lib`.那么就需要指定环境变量`LD_LIBRARY_PATH`

假如需要在已有的环境变量上添加新的路径名，则采用如下方式：
`LD_LIBRARY_PATH=NEWDIRS:$LD_LIBRARY_PATH`.（newdirs是新的路径串）
（注：GNU系统可以自动添加在 `/etc/ld.so.conf`文件中来实现环境变量的设置）

### 设置方法
在linux下可以用`export`命令来设置这个值，比如
在linux终端下输入:`export LD_LIBRARY_PATH=/opt/au1200_rm/build_tools/bin: $LD_LIBRARY_PATH:`
然后再输入:`export`即会显示是否设置正确

**export方式在重启后失效**，所以也可以用 `vim /etc/bashrc` ，修改其中的`LD_LIBRARY_PATH`变量。
例如：`LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/au1200_rm/build_tools/bin`

### 区别于LIBRARY_PATH
StackOverflow 上关于 `LIBRARY_PATH` 和 `LD_LIBRARY_PATH` 的解释如下：
- `LIBRARY_PATH` is used by gcc before compilation to search for directories containing libraries that need to be linked to your program.

- `LD_LIBRARY_PATH` is used by your program to search for directories containing the libraries after it has been successfully compiled and linked.
