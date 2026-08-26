---
layout: post
title: Ubuntu-gcc-源码安装gcc7.5.0
date: 2024-08-08 17:59:00
categories:
- Systems
tags:
- C++
- OS
- Ubuntu
---

- [GNU Mirror List](https://www.gnu.org/prep/ftp.html)
- [FTP server of the GNU project--gcc](https://ftp.gnu.org/gnu/gcc/)
- [Gcc-依赖](https://gcc.gnu.org/pub/gcc/infrastructure/)

<!--more-->
## 下载GCC源代码
`wget https://ftp.gnu.org/gnu/gcc/gcc-X.Y.Z/gcc-X.Y.Z.tar.gz`

## 解压、配置、编译gcc7.5.0
操作指令序列：
```shell
#解压源代码
tar -xzf gcc-7.5.0.tar.gz
cd gcc-7.5.0

#安装依赖（以Ubuntu为例）
sudo apt-get build-dep gcc
sudo apt-get install build-essential

#配置安装选项
./configure --prefix=/opt/gcc --enable-languages=c,c++ --disable-multilib

#编译GCC
make -j$(nproc)

#安装GCC
sudo make install

#清理编译产生的临时文件
make distclean
```

### 编译报错
```c++
编译报错：
error: size of array ‘assertion_failed__1150’ is negative
typedef char IMPL_PASTE(assertion_failed_##_, line)[2*(int)(pred)-1]
以及后面跟着一堆报错信息

解决方法：注释<gcc源码目录>/libsanitizer/sanitizer_common/sanitizer_platform_limits_posix.cc里面的CHECK_SIZE_AND_OFFSET(ipc_perm, mode); 
```

---
## 依赖
1. Ubuntu20.04 可以从源安装gcc7.5.0:`apt install gcc-7`
2. Ubuntu24.04 源不支持gcc7.5.0
**Ubuntu24.04**编译GCC（GNU编译器集合）需要满足一定的依赖关系，具体需要
GMP（GNU Multiple Precision Arithmetic Library）版本4.2或更高
MPFR（Multiple-Precision Floating-Point Computations With Correct Rounding）版本2.4.0或更高
MPC（Multiple-Precision Complex Floating-Point Library）版本0.8.0或更高
	```shell
	apt install libgmp-dev   # 6.3.0
    apt install libmpfr-dev  # 4.2.1
    apt install libmpc-dev   # 1.3.1
	```
3. gcc依赖:https://gcc.gnu.org/pub/gcc/infrastructure/

---
## 查看gcc版本

- `ls /usr/bin/gcc*`:查看已安装gcc版本
- `gcc --version`

## 修改gcc默认版本
使用`update-alternatives`修改gcc默认版本，其是系统自带指令，不需安装

```shell
update-alternatives --help    # 
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 60 --slave /usr/bin/g++ g++ /usr/bin/g++-7
gcc --version

update-alternatives --config gcc

update-alternatives --query gcc
```