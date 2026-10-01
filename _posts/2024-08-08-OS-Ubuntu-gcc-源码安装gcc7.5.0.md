---
layout: post
title: Ubuntu-gcc-源码安装gcc7.5.0
display_title: 'Ubuntu 源码安装 GCC 7.5.0'
summary: >
  Build GCC 7.5.0 from source on Ubuntu for legacy project compatibility,
  covering prerequisite packages, mirror selection, and multi-stage build.
lang: zh-CN
date: 2024-08-08 17:59:00
categories:
- Systems
tags:
- C++
- OS
- Ubuntu
---
> **TL;DR**：老项目如果硬性要求 GCC 7，优先确认发行版仓库是否提供 `gcc-7`；Ubuntu 22.04（Jammy）和 24.04（Noble）的官方二进制仓库通常没有可直接安装的 GCC 7，这时可以从 GNU 官方源码构建。真正麻烦的不是下载，而是 GMP / MPFR / MPC 依赖，以及用较新的 glibc 编译旧版 `libsanitizer` 时可能出现的 `assertion_failed__xxx is negative` 编译期断言。

本文整理自 `intall_gcc7` 操作记录，目标是 **GCC 7.5.0**。原始记录中的系统信息是 Ubuntu 22.04.4 LTS（Jammy），而依赖下载输出中又出现了 Ubuntu 24.04（Noble）的包地址；下面会明确区分这两种环境，不把它们误写成同一次测试。

<!--more-->

---

## 0. 先判断是否真的需要源码编译

Ubuntu 的软件包可用性会随发行版、仓库组件和版本变化。对 `gcc-7` 来说，可以先查询当前系统实际能看到什么：

```bash
apt-cache policy gcc-7 g++-7
```

在本次核查时，官方仓库的情况大致如下：

| Ubuntu 发行版 | 官方仓库中的 `gcc-7` | 建议 |
|---|---|---|
| 20.04 Focal | `universe` 中曾发布 `7.5.0-6ubuntu2` | 优先尝试 apt 安装 |
| 22.04 Jammy | 官方二进制包页面未发布 `gcc-7` | 查询当前仓库；必要时源码构建或使用兼容环境 |
| 24.04 Noble | 官方二进制包页面未发布 `gcc-7` | 源码构建，或使用容器 / 虚拟机中的旧工具链 |

因此，“24.04 没有 `gcc-7`”只表示官方仓库当前没有发布这个二进制包，不表示 GCC 7.5.0 一定不能从源码构建，也不表示 Focal 一定没有。软件仓库状态会变化，实际操作前以上述 `apt-cache` 输出和官方包页面为准：

- [Ubuntu Focal 的 `gcc-7` 包页面](https://launchpad.net/ubuntu/focal/+package/gcc-7)
- [Ubuntu Jammy 的 `gcc-7` 包页面](https://launchpad.net/ubuntu/jammy/+package/gcc-7)
- [Ubuntu Noble 的 `gcc-7` 包页面](https://launchpad.net/ubuntu/noble/+package/gcc-7)

`universe` 是 Ubuntu 官方软件源体系中的组件，但由社区维护，支持级别不同于 `main`；精简系统或定制安装也可能没有启用该组件。因此 Focal 上仍应先确认软件源组件已经启用。

如果项目只需要一个能工作的 GCC 7，而不是必须使用当前 Ubuntu 的系统库，Ubuntu 18.04 / 20.04 容器或虚拟机往往比在新宿主机上反复修补旧 GCC 更省事。

---

## 1. 确认 Ubuntu 版本和 Codename

先记录系统版本：

```bash
$ lsb_release -a
Distributor ID:	Ubuntu
Description:	Ubuntu 22.04.4 LTS
Release:	22.04
Codename:	jammy
```

常见的版本与 Codename 对照如下：

| 版本 | Codename | 类型 |
|---|---|---|
| 15.04 | vivid | 非 LTS |
| 16.04 | xenial | LTS |
| 17.04 | zesty | 非 LTS |
| 18.04 | bionic | LTS |
| 19.04 | disco | 非 LTS |
| 20.04 | focal | LTS |
| 22.04 | jammy | LTS |
| 23.04 | lunar | 非 LTS |
| 24.04 | noble | LTS |

原始记录中的 `vivd` 是拼写错误，正确写法是 **`vivid`**。Codename 会出现在 APT 源地址、PPA 地址和软件包索引中，拼错后常见表现就是 404、找不到源或找不到包。

### APT 源文件的位置

Ubuntu 24.04 默认使用 deb822 格式的软件源文件；24.04 之前的 Ubuntu 默认通常使用传统的 `/etc/apt/sources.list`。这是默认布局，不是说其他版本绝对不能使用另一种格式。APT 仍会读取 `/etc/apt/sources.list` 以及 `/etc/apt/sources.list.d/` 下的源文件；真正决定解析方式的是文件格式（`.list` 的单行格式或 `.sources` 的 deb822 格式），不要只凭文件名判断：

```bash
# Ubuntu 22.04 的常见布局
sudoedit /etc/apt/sources.list

# Ubuntu 24.04 的默认布局
sudoedit /etc/apt/sources.list.d/ubuntu.sources
```

修改前建议先查看当前系统到底配置了什么：

```bash
grep -R "^deb\|^Types:\|^URIs:\|^Suites:\|^Components:" \
    /etc/apt/sources.list /etc/apt/sources.list.d 2>/dev/null
```

24.04 的 `ubuntu.sources` 是结构化的 deb822 文件，常见字段包括 `Types`、`URIs`、`Suites` 和 `Components`。如果需要通过 `apt build-dep` 安装源码构建依赖，还要确认启用了 `deb-src` 类型，而不只是二进制 `deb` 类型。

参考：[Ubuntu Server 软件包管理文档](https://documentation.ubuntu.com/server/how-to/software/package-management/)。原始笔记中还保留了一篇第三方换源文章：[Ubuntu 24.04 换源参考](https://blog.csdn.net/ix_fly/article/details/138271843)。

---

## 2. 下载 GCC 7.5.0 源码

官方发布目录和镜像列表：

- [GNU 官方镜像列表](https://www.gnu.org/prep/ftp.html)
- [GCC 官方源码目录](https://ftp.gnu.org/gnu/gcc/)
- [GCC 7.5.0 官方发布目录](https://gcc.gnu.org/pub/gcc/releases/gcc-7.5.0/)

下载并解压：

```bash
wget https://ftp.gnu.org/gnu/gcc/gcc-7.5.0/gcc-7.5.0.tar.gz

tar -xzf gcc-7.5.0.tar.gz
cd gcc-7.5.0
```

官方目录也提供 `.tar.xz` 格式；如果选择它，需要同时把下载文件名、解压命令以及下方的 SHA-512 校验目标从 `.tar.gz` 改为 `.tar.xz`。

下载后可以用官方 SHA-512 清单校验压缩包：

```bash
wget https://gcc.gnu.org/pub/gcc/releases/gcc-7.5.0/sha512.sum
grep -E '[[:space:]]\*?gcc-7\.5\.0\.tar\.gz$' sha512.sum | sha512sum -c -
```

这里用行尾精确匹配压缩包名，避免把同一清单中的 `.sig` 文件也传给 `sha512sum -c`。该步骤只核对压缩包与官方校验清单的一致性；发布者签名验证是另一项独立操作。

> 下文所有 `configure`、源码路径和版本号都针对 GCC 7.5.0。不要把 `gcc-X.Y.Z.tar.gz` 这样的占位符直接复制执行。

---

## 3. 安装构建依赖

### 3.1 GCC 7.5.0 的依赖版本：硬下限与推荐值

GCC 7.5.0 的安装文档和生成的 `configure` 脚本对这三个库给出了两层版本约束，不能把它们混为一谈：

| 库 | 用途 | `configure` 的硬下限 | 安装文档列出的已知可用版本 |
|---|---|---:|---:|
| GMP | Multiple-Precision Arithmetic Library | 4.2.3 | 4.3.2 |
| MPFR | Multiple-Precision Floating-Point Library | 2.4.0 | 2.4.2 |
| MPC | Multiple-Precision Complex Floating-Point Library | 0.8.0 | 0.8.1 |

换句话说，原始笔记中的 `GMP 4.2+` 少写了补丁版本，精确的硬下限是 **4.2.3**；生成的 `configure` 错误提示为了简写会写成 `GMP 4.2+`，但实际版本比较使用的是 4.2.3。GCC 7.5.0 的安装文档（`gcc/doc/install.texi`）列出了 **4.3.2 / 2.4.2 / 0.8.1** 这组已知可用版本；更新版本可能可用，但不能把表中的硬下限直接等同于官方已明确验证的版本。如果使用的是发行版开发包，版本达到这组已知可用版本即可。

启用 Graphite 循环优化时还需要 ISL 0.15 或更高版本：

| 库 | 用途 | 要求 |
|---|---|---|
| ISL | 启用 Graphite 循环优化时需要 | 0.15 或更高 |

原始记录的 Noble 下载输出中出现了以下版本，它们同时满足硬下限和推荐值：

```text
libgmp-dev    6.3.0
libmpfr-dev   4.2.1
libmpc-dev    1.3.1
```

安装系统开发包：

```bash
sudo apt-get update
sudo apt-get install \
    build-essential \
    bison \
    flex \
    texinfo \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    libisl-dev
```

`apt-get build-dep gcc` 可以补充当前发行版 `gcc` 源码包声明的构建依赖，但它依赖 `deb-src` 已经启用，而且得到的是**当前发行版的 gcc 源码包依赖**，不等于 GCC 7.5.0 的完整历史依赖清单：

```bash
# 仅在已经启用 deb-src 且当前仓库提供 gcc 源码包时执行
sudo apt-get build-dep gcc
```

另一种官方方式是在 GCC 源码目录运行：

```bash
./contrib/download_prerequisites
```

GCC 7.5.0 的脚本默认启用 `graphite=1`，会下载并解压 GMP 6.1.0、MPFR 3.1.4、MPC 1.0.3 和 ISL 0.16.1，然后在源码树中建立 `gmp`、`mpfr`、`mpc`、`isl` 链接；这些版本比上表的硬下限更新，也高于文档列出的已知可用版本。需要省略 ISL 时可运行 `./contrib/download_prerequisites --no-isl`。该版本脚本内部使用 `ftp://` 下载基址；如果环境禁用了 FTP，应改用 HTTPS 软件包或手工准备依赖，不能把脚本失败误判为 GCC 源码损坏。

### 3.2 查询包的依赖关系

`apt-cache depends` 只查询，不会安装软件包。下面是原始记录中的递归查询命令，修正了续行位置：

```bash
apt-cache depends --no-pre-depends --no-suggests --no-recommends \
    --no-conflicts --no-breaks --no-enhances \
    --no-replaces --recurse libgmp-dev
```

排查“安装了 A 为什么还缺 B”时，可以先用它查看依赖图，再决定是否需要 `apt-get download` 下载离线包。

---

## 4. 配置 GCC：`configure` 选项怎么理解

记录中的主要配置命令是：

```bash
./configure \
    --prefix=/opt/gcc \
    --enable-languages=c,c++ \
    --disable-multilib
```

各选项的作用：

| 选项 | 作用 |
|---|---|
| `--prefix=/opt/gcc` | 将安装内容放到独立目录，避免直接覆盖 `/usr` 下的系统文件 |
| `--enable-languages=c,c++` | 只构建 C 和 C++ 前端及其运行时，减少不必要的构建量 |
| `--disable-multilib` | 不构建用于不同目标变体的多套库；在 x86_64 上可以避免因缺少 32 位 libc 开发文件而失败，但会牺牲 `-m32` 等 32 位开发能力；它不能修复后文的 `ipc_perm` 断言 |

如果需要同时保留多个版本，建议把前缀改得更明确，例如 `/opt/gcc-7.5.0`。本文后续命令统一使用 `/opt/gcc`；如果改用其他前缀，必须把构建后的验证、`PATH` 和 `update-alternatives` 示例中的 `/opt/gcc` 路径全部同步替换。`--prefix` 只决定安装位置，不会自动让 `gcc` 命令指向新版本，后文的 alternatives 部分会处理这个问题。

原始记录还尝试过：

```bash
./configure --enable-checking=release \
    --enable-languages=c,c++ \
    --disable-multilib \
    CFLAGS="-g -O0"
```

这里要区分两件事：

1. GCC 7.5.0 是正式发布版，`--enable-checking=release` 本来就是该版本的默认检查级别；它不是“关闭所有检查”的万能加速开关。
2. `CFLAGS="-g -O0"` 控制的是**编译 GCC 这套程序时**传给 C 编译器的选项，不是 GCC 7 编译用户代码时使用的优化级别。GCC 7.5.0 的发布树还会在子配置中过滤常规的 `-O*` 选项（bootstrap 情形除外），因此不要假定 `-O0` 会原样作用于所有组件。排查 bootstrap 或调试 GCC 自身时可以临时使用，常规发布构建不应把它当成性能优化参数。

如果更换过 configure 选项，先清理上一轮生成文件：

```bash
make distclean
```

`make distclean` 会删除 configure 生成的 Makefile 和中间文件；执行后需要重新运行 `./configure`。

---

## 5. 编译、安装和验证

GCC 官方安装文档建议使用独立的构建目录。为保留原始操作记录，下面仍以 GCC 源码根目录中的 in-tree build 为例；如果改用 out-of-tree build，应从单独的 build 目录运行 `../configure`，并按实际源码路径调整后续命令。

在 GCC 源码根目录执行：

```bash
# 按 CPU 核数并行构建
make -j"$(nproc)"

# 安装到 --prefix 指定的目录
sudo make install

# 安装完成后可选：清理源码目录中的中间文件
make distclean
```

如果机器内存有限，`-j` 过大可能在 C++ 编译阶段被 OOM killer 终止，可以降低并行度，例如：

```bash
make -j2
```

安装后直接验证绝对路径，避免当前 shell 仍然命中旧的 `gcc`：

```bash
/opt/gcc/bin/gcc --version
/opt/gcc/bin/g++ --version
/opt/gcc/bin/gcc -dumpmachine
```

一个最小的 C 冒烟测试可以是：

```bash
rm -f /tmp/gcc7-smoke
printf 'int main(void) { return 0; }\n' \
  | /opt/gcc/bin/gcc -x c - -o /tmp/gcc7-smoke && /tmp/gcc7-smoke
```

先删除旧产物，再用 `&&` 连接编译和执行，可以避免编译失败后误运行上一次留下的可执行文件。

---

## 6. 踩坑记录：`assertion_failed__xxx is negative`

### 6.1 报错长什么样

原始记录中的关键错误是：

```text
error: size of array ‘assertion_failed__943’ is negative
typedef char IMPL_PASTE(assertion_failed_##_, line)[2*(int)(pred)-1]
```

后面还跟着一串看起来毫不相关的编译错误。`943`、`1150` 等数字只是宏展开时的 `__LINE__` 行号，不是稳定的错误编号；不同 GCC 源码版本或文件版本出现不同数字是正常的。

GCC 7.5.0 的 sanitizer 代码使用编译期断言检查系统结构体的字段大小和偏移。相关宏最终大致是：

```cpp
#define COMPILER_CHECK(pred) IMPL_COMPILER_ASSERT(pred, __LINE__)
#define IMPL_COMPILER_ASSERT(pred, line) \
    typedef char IMPL_PASTE(assertion_failed_##_, line)[2*(int)(pred)-1]
```

当 `pred` 为假时，数组长度变成 `-1`，编译器就会报“数组长度为负”。因此这条错误不是在说 GMP 或 MPC 安装失败，而是在说某个结构体布局假设不成立。

### 6.2 为什么 `ipc_perm, mode` 会触发它

GCC 7.5.0 的文件中确实有这一行：

```cpp
CHECK_SIZE_AND_OFFSET(ipc_perm, mode);
```

位置是：

```text
libsanitizer/sanitizer_common/sanitizer_platform_limits_posix.cc
```

在 GCC 7.5.0 的 x86_64 代码中，sanitizer 私有的 `__sanitizer_ipc_perm` 镜像把 `mode` 建模为 `unsigned short`，并带有相应的填充字段。glibc 的提交 `2f959dfe849e0646e27403f2e4091536496ac0f0` 从 glibc 2.31 起把 `ipc_perm.mode` 改为 POSIX 的 `mode_t`；在 Ubuntu 22.04 / 24.04 的常见 x86_64 环境中，该字段是 32 位。GCC 7 的检查会分别比较：

- 字段大小是否一致；
- 字段偏移是否一致。

因此，在“旧 GCC + 新 glibc”的组合下，`CHECK_SIZE_AND_OFFSET(ipc_perm, mode)` 可能因为成员大小变化而失败。这个解释针对 GCC 7.5.0 和常见 x86_64/glibc 组合；其他架构应直接查看对应源码和系统头文件，不能机械套用。

### 6.3 优先参考 GCC 上游修正

GCC 上游提交 [`4abc46b51af5751d657764d0c44b8a4aeed06302`](https://gcc.gnu.org/git/?p=gcc.git;a=commit;h=4abc46b51af5751d657764d0c44b8a4aeed06302)（2019-11-26）专门处理了新 glibc 导致的 `libsanitizer` 构建问题。补丁的实际条件是：

- 对 Linux + glibc 2.31 及更高版本保留并执行 `ipc_perm.mode` 布局检查；对 Linux + 更早的 glibc 跳过该检查；非 Linux 构建仍按补丁条件检查；
- 将 sanitizer 私有结构体中的 `mode` 从 16 位改为 32 位，并把相关布局对齐到新的系统 ABI。

因此，这个补丁不是“在 glibc 2.31+ 跳过检查”，而是修正私有结构体，使新 glibc 的检查能够通过。这个提交晚于 GCC 7.5.0 的 2019-11-14 发布，因此不会自动包含在 `gcc-7.5.0.tar.gz` 中。它来自较新的 GCC 源码树，相关文件使用 `.cpp` 后缀，而 GCC 7.5.0 发布源码使用 `.cc`；回移时必须人工适配上下文并重新验证，不能机械 cherry-pick。若需要长期维护这套源码，优先在确认补丁上下文与本地源码版本匹配后回移该修正，比永久注释任意断言更容易审计和复现。

### 6.4 原始记录中的临时处理

原始记录采用的处理方式是注释这一行：

```diff
- CHECK_SIZE_AND_OFFSET(ipc_perm, mode);
+ // CHECK_SIZE_AND_OFFSET(ipc_perm, mode);
```

修改后重新构建：

```bash
make -j"$(nproc)"
```

这不是 GCC 官方给出的通用修复，而是**跳过一项布局校验的本地 workaround**。它可能让编译继续，但也意味着 sanitizer 对相关系统结构的假设没有被检查。即使构建成功，也不能据此保证旧版 ASan、UBSan 或 TSan 在新 glibc 上完全兼容。

如果项目根本不需要 sanitizer，可以在重新配置时关闭其运行时库：

```bash
make distclean

./configure \
    --prefix=/opt/gcc \
    --enable-languages=c,c++ \
    --disable-multilib \
    --disable-libsanitizer
```

代价是生成的 GCC 不提供 sanitizer 运行时支持。需要 `-fsanitize=address`、`-fsanitize=undefined` 等功能时，不应采用这个方案；更稳妥的选择通常是使用与 GCC 7 时代兼容的旧发行版容器，或者在充分测试的前提下维护一个最小、明确记录的补丁。

不要看到任意 `assertion_failed__xxx` 就批量注释所有 `CHECK_SIZE_AND_OFFSET` 或 `CHECK_TYPE_SIZE`。不同断言保护的是不同 ABI 假设；应先确认失败的结构体、字段和目标平台，再决定是修复布局、调整构建环境，还是有意禁用整个可选组件。

---

## 7. 多个 GCC 版本共存：`update-alternatives`

### 7.1 查看当前安装情况

```bash
ls -l /usr/bin/gcc*
command -v gcc
gcc --version
```

`update-alternatives` 是 Debian / Ubuntu 的系统自带工具，不需要额外安装。它维护的是一组候选程序和通用命令链接，不是简单地替换 `/usr/bin/gcc` 文件。

### 7.2 使用发行版安装的 `gcc-7`

如果 `/usr/bin/gcc-7` 和 `/usr/bin/g++-7` 确实存在，可以把 GCC 7 注册为一个候选：

```bash
sudo update-alternatives --install \
    /usr/bin/gcc gcc /usr/bin/gcc-7 60 \
    --slave /usr/bin/g++ g++ /usr/bin/g++-7
```

这里四个位置参数的含义是：

```text
--install <通用链接> <候选组名> <真实程序路径> <优先级>
```

`--slave` 让 `g++` 跟随主链接 `gcc` 一起切换，避免出现 `gcc` 是 7、`g++` 却仍是系统默认版本的情况。

### 7.3 使用源码安装的 `/opt/gcc`

源码安装通常使用独立前缀，不应直接假设存在 `/usr/bin/gcc-7`。如果希望把源码版本加入同一个 `gcc` alternatives 组，应使用与发行版包相同的通用链接路径，并确认自己确实要改变系统默认链接：

```bash
# 仅在确认要修改系统 gcc 链接、且没有 alternatives 冲突时执行
sudo update-alternatives --install \
    /usr/bin/gcc gcc /opt/gcc/bin/gcc 70 \
    --slave /usr/bin/g++ g++ /opt/gcc/bin/g++
```

如果不希望触碰 `/usr/bin`，更简单的方式是直接使用绝对路径，或只为当前 shell 设置 `PATH`：

```bash
export PATH=/opt/gcc/bin:$PATH
hash -r
gcc --version
```

如果 `/usr/bin/gcc`、`/usr/bin/g++` 已经是发行版或其他工具链管理的真实文件，不要强行用 alternatives 覆盖它们；先查看现有链接组，再决定采用独立命令名还是统一管理。

### 7.4 查看和切换

```bash
# 交互式选择
update-alternatives --config gcc

# 查看候选项、优先级和当前状态
update-alternatives --query gcc
update-alternatives --display gcc

# 非交互式设置
sudo update-alternatives --set gcc /opt/gcc/bin/gcc

# 恢复为按优先级自动选择
sudo update-alternatives --auto gcc
```

在自动模式下，优先级较高的候选项通常会被选中；`--config` 手动选择后，链接组可能进入手动模式，此时优先级不再是唯一决定因素。

切换后清掉 shell 的命令缓存并确认实际路径：

```bash
hash -r
command -v gcc
readlink -f "$(command -v gcc)"
gcc --version
g++ --version
```

---

## 8. 总结 Checklist

```text
[ ] 用 lsb_release -a 确认 Ubuntu 版本和 Codename
[ ] 用 apt-cache policy gcc-7 g++-7 确认当前仓库实际提供什么
[ ] 24.04 检查 /etc/apt/sources.list.d/ubuntu.sources 和 deb822 格式
[ ] 从 GNU 官方下载 GCC 7.5.0，并校验 SHA-512
[ ] 安装 build-essential、libgmp-dev、libmpfr-dev、libmpc-dev
[ ] 需要 Graphite/LTO 时确认 ISL 依赖
[ ] configure 使用独立 --prefix、--enable-languages=c,c++、--disable-multilib
[ ] make -j"$(nproc)"，内存不足时降低并行度
[ ] 遇到 assertion_failed__xxx is negative 时定位具体 CHECK，而不是批量注释
[ ] 重新 configure 前先 make distclean
[ ] 用 update-alternatives 管理 gcc/g++，切换后执行 hash -r
[ ] 用 /opt/gcc/bin/gcc --version 和最小程序做最终验证
```

---

## 参考资料

- [GNU 官方镜像列表](https://www.gnu.org/prep/ftp.html)
- [GCC 官方源码目录](https://ftp.gnu.org/gnu/gcc/)
- [GCC 7.5.0 官方发布目录](https://gcc.gnu.org/pub/gcc/releases/gcc-7.5.0/)
- [GCC 7.5.0 官方 SHA-512 清单](https://gcc.gnu.org/pub/gcc/releases/gcc-7.5.0/sha512.sum)
- [GCC 7.5.0 安装文档源码（`gcc/doc/install.texi`）](https://gcc.gnu.org/git/?p=gcc.git;a=blob;f=gcc/doc/install.texi;hb=refs/tags/releases/gcc-7.5.0)
- [GCC 7.5.0 生成的 `configure`（依赖版本检查）](https://gcc.gnu.org/git/?p=gcc.git;a=blob;f=configure;hb=refs/tags/releases/gcc-7.5.0)
- [GCC 7.5.0 `configure.ac`（依赖版本检查源文件）](https://gcc.gnu.org/git/?p=gcc.git;a=blob;f=configure.ac;hb=refs/tags/releases/gcc-7.5.0)
- [GCC 7.5.0 `config/multi.m4`（multilib 选项）](https://gcc.gnu.org/git/?p=gcc.git;a=blob;f=config/multi.m4;hb=refs/tags/releases/gcc-7.5.0)
- [GCC 基础设施目录（GMP / MPFR / MPC 等）](https://gcc.gnu.org/pub/gcc/infrastructure/)
- [GCC 7.5.0 `contrib/download_prerequisites`](https://gcc.gnu.org/git/?p=gcc.git;a=blob;f=contrib/download_prerequisites;hb=refs/tags/releases/gcc-7.5.0)
- [GCC 7.5.0 `sanitizer_platform_limits_posix.cc`](https://gcc.gnu.org/git/?p=gcc.git;a=blob;f=libsanitizer/sanitizer_common/sanitizer_platform_limits_posix.cc;hb=refs/tags/releases/gcc-7.5.0)
- [GCC 7.5.0 `sanitizer_platform_limits_posix.h`](https://gcc.gnu.org/git/?p=gcc.git;a=blob;f=libsanitizer/sanitizer_common/sanitizer_platform_limits_posix.h;hb=refs/tags/releases/gcc-7.5.0)
- [GCC 上游修正提交 `4abc46b5`](https://gcc.gnu.org/git/?p=gcc.git;a=commit;h=4abc46b51af5751d657764d0c44b8a4aeed06302)
- [glibc 2.35 的 `bits/ipc-perm.h`](https://sourceware.org/git/?p=glibc.git;a=blob;f=sysdeps/unix/sysv/linux/bits/ipc-perm.h;hb=glibc-2.35)
- [glibc 2.31 的 `ipc_perm.mode` 修正提交](https://sourceware.org/git/?p=glibc.git;a=commit;h=2f959dfe849e0646e27403f2e4091536496ac0f0)
- [glibc Bug 18231：POSIX `mode_t` 与 `ipc_perm` 布局问题](https://sourceware.org/bugzilla/show_bug.cgi?id=18231)
- [Ubuntu Server 软件包管理文档](https://documentation.ubuntu.com/server/how-to/software/package-management/)
- [Ubuntu `sources.list(5)` 与 deb822 格式](https://manpages.ubuntu.com/manpages/noble/man5/sources.list.5.html)
- [Ubuntu Jammy 中搜索 `gcc-7`](https://packages.ubuntu.com/search?keywords=gcc-7&searchon=names&suite=jammy&section=all)
- [Ubuntu Noble 中搜索 `gcc-7`](https://packages.ubuntu.com/search?keywords=gcc-7&searchon=names&suite=noble&section=all)
- [Ubuntu Focal `gcc-7` 包页面](https://launchpad.net/ubuntu/focal/+package/gcc-7)
- [Ubuntu Jammy `gcc-7` 包页面](https://launchpad.net/ubuntu/jammy/+package/gcc-7)
- [Ubuntu Noble `gcc-7` 包页面](https://launchpad.net/ubuntu/noble/+package/gcc-7)
- [Ubuntu `update-alternatives(1)` 手册](https://manpages.ubuntu.com/manpages/noble/en/man1/update-alternatives.1.html)
- [原始笔记中的 Ubuntu 24.04 换源参考](https://blog.csdn.net/ix_fly/article/details/138271843)

---

> **AI 修改声明：** 本文由 LLM 协助整理、补充说明并校对，最近修改时间：2026-09-25 17:52（UTC+08:00）。文中明确区分了原始操作记录与官方资料核查结果；GCC 7.5.0 的源码构建不是重新执行后的统一测试报告，具体结果仍取决于发行版、架构、glibc 和构建选项。本次备份同步还修正了 SHA-512 校验命令、GCC 上游 sanitizer 补丁的适用条件，并补充了安装前缀、冒烟测试和 `download_prerequisites` 的边界说明。