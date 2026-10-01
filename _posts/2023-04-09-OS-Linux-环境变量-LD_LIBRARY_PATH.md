---
layout: post
title: Linux-环境变量-LD_LIBRARY_PATH
display_title: 'Linux 环境变量 LD_LIBRARY_PATH'
date: 2023-04-09 21:55:00
categories:
- Systems
tags:
- Linux
- OS
---
----------
> [Linux中PATH、 LIBRARY_PATH、 LD_LIBRARY_PATH的区别](https://blog.csdn.net/weixin_48859611/article/details/113986310 "Linux中PATH、 LIBRARY_PATH、 LD_LIBRARY_PATH的区别")
----------

运行时（动态链接器）为没有斜杠的依赖库搜索时，通常按以下顺序处理（具体还取决于 ELF 的 `DT_RPATH`/`DT_RUNPATH` 和安全执行模式）：

<!--more-->

1. `DT_RPATH`（仅在没有 `DT_RUNPATH` 时）；
2. 环境变量 `LD_LIBRARY_PATH` 指定的目录（安全执行模式下会忽略该变量）；
3. `DT_RUNPATH` 指定的目录；
4. `/etc/ld.so.cache` 中由 `ldconfig` 生成的缓存；
5. 默认目录，例如 `/lib` 和 `/usr/lib`（多架构系统还可能包含对应的 multiarch 目录）。

> 参考：[ld.so(8) 动态链接器手册](https://man7.org/linux/man-pages/man8/ld.so.8.html)

Linux 指定运行时动态库搜索路径的方法：
1. 将目录加入 `/etc/ld.so.conf` 或其中的配置文件，然后执行 `sudo ldconfig` 更新缓存。
2. 临时使用 `LD_LIBRARY_PATH`，例如 `export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH`；该设置只对当前 shell 及其子进程生效，重新登录后需要重新设置。
3. 在编译/链接阶段使用编译器的库搜索选项；这与运行时的 `LD_LIBRARY_PATH` 是不同机制。

## LD_LIBRARY_PATH
`LD_LIBRARY_PATH`是Linux环境变量名，该环境变量主要用于在程序运行期间指定查找共享库（动态链接库）时除了默认路径之外的其他路径。
- 临时修改：用`export`命令来设置值。
`export LD_LIBRARY_PATH=/path/to/libtest1:/path/to/libtest2:$LD_LIBRARY_PATH`

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
在 Linux 下可以用 `export` 命令临时设置这个值，例如：

```bash
export LD_LIBRARY_PATH=/opt/au1200_rm/build_tools/bin:$LD_LIBRARY_PATH
```

然后用 `printf '%s\n' "$LD_LIBRARY_PATH"` 检查变量是否生效。

**export方式在重启后失效**，所以也可以用 `vim /etc/bashrc` ，修改其中的`LD_LIBRARY_PATH`变量。
例如：`LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/au1200_rm/build_tools/bin`

### 区别于LIBRARY_PATH
StackOverflow 上关于 `LIBRARY_PATH` 和 `LD_LIBRARY_PATH` 的解释如下：
- `LIBRARY_PATH` is used by gcc before compilation to search for directories containing libraries that need to be linked to your program.

- `LD_LIBRARY_PATH` is used by your program to search for directories containing the libraries after it has been successfully compiled and linked.

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 00:05（UTC+08:00）。
