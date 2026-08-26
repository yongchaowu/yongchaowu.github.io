---
layout: post
title: "Tool-Cross-compilation-Toolchain-ARM-Linaro"
date: 2024-07-15 10:50:00
categories: ["Tool"]
tags: ["Tool", "Cross-compilation"]
---

Ubuntu上基于Arm的交叉编译工具链。

<!--more-->
---

引用：[arm生态发展与交叉编译链选择-知乎](https://zhuanlan.zhihu.com/p/50230894)

- `arm-none-linux-gnueabi-gcc`：是 Codesourcery 公司（目前已经被Mentor收购）基于GCC推出的的ARM交叉编译工具。可用于交叉编译ARM（32位）系统中所有环节的代码，包括裸机程序、u-boot、Linux kernel、filesystem和App应用程序。

- `arm-linux-gnueabihf-gcc`：是由 Linaro 公司基于GCC推出的的ARM交叉编译工具。可用于交叉编译ARM（32位）系统中所有环节的代码，包括裸机程序、u-boot、Linux kernel、filesystem和App应用程序。

- `aarch64-linux-gnu-gcc`：是由 Linaro 公司基于GCC推出的的ARM交叉编译工具。可用于交叉编译ARMv8 64位目标中的裸机程序、u-boot、Linux kernel、filesystem和App应用程序。

- `arm-none-elf-gcc`：是 Codesourcery 公司（目前已经被Mentor收购）基于GCC推出的的ARM交叉编译工具。可用于交叉编译ARM MCU（32位）芯片，如ARM7、ARM9、Cortex-M/R芯片程序。

- `arm-none-eabi-gcc`：是 GNU 推出的的ARM交叉编译工具。可用于交叉编译ARM MCU（32位）芯片，如ARM7、ARM9、Cortex-M/R芯片程序。

命名规则: 交叉编译工具链的命名规则为：`arch [-vendor] [-os] [-(gnu)eabi]`
- `arch` – 体系架构，如ARM，MIPS（通过交叉编译工具生成的可执行文件或系统镜像的运行平台或环境）
- `vendor` – 工具链提供商
- `os` – 目标操作系统（host主要操作平台，也就是编译时的系统）
- `eabi` – 嵌入式应用二进制接口（Embedded Application Binary Interface）


根据对操作系统的支持与否，ARM GCC可分为支持和不支持操作系统，如

`arm-none-eabi`：这个是没有操作系统的，自然不可能支持那些跟操作系统关系密切的函数，比如fork(2)。他使用的是newlib这个专用于嵌入式系统的C库。

`arm-none-linux-eabi`：用于Linux的，使用Glibc

---
---

- [Linaro Home](https://www.linaro.org/)
- [Linaro Downloads](https://www.linaro.org/downloads/)
- [Linaro releases storage server](http://releases.linaro.org/)

- [arm developer](https://developer.arm.com/downloads/-/gnu-a)
---
- [Linaro ToolChain aarch64 7.5.0](http://releases.linaro.org/components/toolchain/binaries/7.5-2019.12/)

- `gcc-linaro-7.5.0-2019.12-x86_64_aarch64-linux-gnu.tar`
- `runtime-gcc-linaro-7.5.0-2019.12-aarch64-linux-gnu.tar`
- `sysroot-glibc-linaro-2.25-2019.12-aarch64-linux-gnu.tar`

---
安装步骤：
1. 解压
2. 配置环境变量
3. 测试gcc版本

---
查看编译文件适用平台：
- `file xx`
- `readelf -d xx`
- `objdump -a xx`或`-f`
- `ldd xx`

---
CMakeList.txt
```shell
# 设置编译器和链接器的路径
set(CMAKE_C_COMPILER "/path/to/gcc")
set(CMAKE_CXX_COMPILER "/path/to/g++")
#set(CMAKE_LINKER "/path/to/ld")
```

---
编译参数
- `--sysroot`