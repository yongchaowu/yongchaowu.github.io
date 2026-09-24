---

layout: post
title: '银河麒麟 V10 SP1 内网离线 C/C++ 开发环境构建指南'
summary: 'Guide to building an offline C/C++ development environment on air-gapped Kylin V10 SP1 servers, covering dependency analysis, local APT repositories, deployment, and automation.'
lang: zh-CN
date: 2026-09-08 21:43:00
categories:
- C & C++
tags:
- Kylin
- C++
- OS
---
> Version: v2.0 Single File Final  
> 文档类型：技术 Blog / 企业内部交付文档

---

<!--more-->

## 目录

- [1. 背景](#1-背景)
- [2. 目标环境](#2-目标环境)
- [3. 软件来源策略](#3-软件来源策略)
- [4. Docker 下载环境](#4-docker-下载环境)
- [5. 软件源配置](#5-软件源配置)
- [6. 版本验证](#6-版本验证)
- [7. 依赖分析](#7-依赖分析)
- [8. 下载离线软件包](#8-下载离线软件包)
- [9. 生成本地 APT 仓库](#9-生成本地-apt-仓库)
- [10. 导出和归档](#10-导出和归档)
- [11. 内网部署](#11-内网部署)
- [12. 自动化脚本](#12-自动化脚本)
- [13. 附录](#13-附录)

---

## 1. 背景

银河麒麟 V10 SP1 服务器通常部署在内网环境，无法直接访问互联网。

为了支持：

- C/C++ 后端编译
- CMake 工程构建
- Redis 源码编译
- Ninja 构建
- GDB 调试
- AddressSanitizer 分析

需要在联网环境提前准备完整 deb 软件仓库。

整体流程：

```text
联网机器
    |
    v
Kylin Docker环境
    |
    v
APT依赖解析
    |
    v
下载deb包
    |
    v
生成本地APT仓库
    |
    v
内网部署
```

---

## 2. 目标环境

| 项目 | 值 |
|---|---|
|系统|银河麒麟 V10 SP1|
|架构|amd64|
|glibc|libc6 = 2.31-0kylin9.2k0.3|
|Kernel|5.15.0-52-generic|

说明：

Kernel 主要影响内核和驱动，不决定用户态 gcc/cmake 版本。

---

## 3. 软件来源策略

## 3.1 ISO pool

银河麒麟 ISO 中：

```text
pool/
```

可以提供部分 deb：

- 基础系统库
- runtime
- 部分工具

但是 ISO 通常不是完整开发仓库。

---

## 3.2 KYLIN-ALL 仓库

完整开发环境需要：

- gcc
- g++
- cmake
- ninja-build
- gdb
- git
- pkg-config
- libasan
- libssl-dev
- zlib1g-dev

推荐：

```text
ISO pool
+
KYLIN-ALL

=
完整离线开发环境
```

---

## 4. Docker 下载环境

镜像：

```text
liyaosong/kylin:v10.1-sp1-amd64
```

启动：

```bash
docker run -it \
--name kylin-download \
liyaosong/kylin:v10.1-sp1-amd64 \
bash
```

---

## 5. 软件源配置

Docker 内：

```bash
cat >/etc/apt/sources.list <<EOF
deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1 main restricted universe multiverse
deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2203-updates main restricted universe multiverse
deb http://archive.kylinos.cn/kylin/KYLIN-ALL 10.1-2203-hwe-updates main restricted universe multiverse
EOF

apt update
```

验证：

```bash
apt-cache policy | grep kylin
```

---

## 6. 版本验证

通过：

```bash
apt-cache policy <package>
```

确认版本。

|软件|版本|
|-|-|
|gcc|9.3.0|
|g++|9.3.0|
|gcc-10|10.3.0|
|g++-10|10.3.0|
|make|4.2.1|
|cmake|3.16.3|
|pkg-config|0.29.1|
|libc6-dev|2.31-0kylin9.2|
|libasan5|GCC9|
|libasan6|GCC10|

保存：

```text
apt-cache-policy.txt
```

---

## 7. 依赖分析

安装：

```bash
apt install -y apt-rdepends dpkg-dev
```

说明：

- apt-rdepends：依赖审计
- apt-get --download-only：真正下载依赖

执行：

```bash
apt-rdepends \
build-essential \
cmake \
pkg-config \
libasan6 \
ninja-build \
git \
gdb \
tcl \
libssl-dev \
zlib1g-dev \
python3 \
> apt-rdepends.txt
```

---

## 8. 下载离线软件包

准备：

```bash
mkdir -p /download

apt-get clean

rm -f /download/*.deb

cd /download
```

下载：

```bash
apt-get install --download-only \
-o Dir::Cache::archives="/download" \
build-essential \
gcc-10 \
g++-10 \
cmake \
pkg-config \
libasan5 \
libasan6 \
ninja-build \
git \
gdb \
tcl \
libssl-dev \
zlib1g-dev \
python3 \
file \
autoconf \
automake \
libtool \
patch
```

验证：

```bash
ls /download/*.deb | wc -l
```

结果：

```text
159
```

生成：

```bash
ls -1 *.deb > package-list.txt
```

---

## 9. 生成本地 APT 仓库

生成索引：

```bash
cd /download

dpkg-scanpackages . /dev/null > Packages
```

检查：

```bash
grep Package Packages | wc -l
```

---

## 10. 导出和归档

Docker外：

```bash
docker cp \
kylin-download:/download \
./kylin-v10-cpp-dev-env
```

修改权限：

```bash
sudo chown -R \
$(whoami):$(whoami) \
./kylin-v10-cpp-dev-env
```

生成校验：

```bash
cd kylin-v10-cpp-dev-env

sha256sum *.deb Packages > SHA256SUM
```

归档：

```bash
tar czvf \
kylin-v10-cpp-dev-env-v2.0.tar.gz \
kylin-v10-cpp-dev-env
```

---

## 11. 内网部署

解压：

```bash
mkdir -p /opt/kylin-local-repo

tar xf kylin-v10-cpp-dev-env-v2.0.tar.gz \
-C /opt/kylin-local-repo \
--strip-components=1
```

添加源：

```bash
cat >/etc/apt/sources.list.d/kylin-local.list <<EOF
deb [trusted=yes] file:/opt/kylin-local-repo ./
EOF
```

更新：

```bash
apt update
```

确认：

```bash
apt-cache policy gcc
```

应该出现：

```text
file:/opt/kylin-local-repo
```

离线验证：

```bash
apt install --no-download \
build-essential \
gcc-10 \
g++-10 \
cmake \
pkg-config
```

---

## 12. 自动化脚本

## 12.1 构建离线仓库脚本

保存：

```text
build-offline-repo.sh
```

内容：

```bash
#!/bin/bash

set -e

mkdir -p /download

apt-get clean

rm -f /download/*.deb

cd /download

apt-get install --download-only \
-o Dir::Cache::archives="/download" \
build-essential \
gcc-10 \
g++-10 \
cmake \
pkg-config \
libasan5 \
libasan6 \
ninja-build \
git \
gdb \
tcl \
libssl-dev \
zlib1g-dev \
python3 \
file \
autoconf \
automake \
libtool \
patch

dpkg-scanpackages . /dev/null > Packages

sha256sum *.deb Packages > SHA256SUM

echo "offline repository ready"
```

执行：

```bash
chmod +x build-offline-repo.sh

./build-offline-repo.sh
```

---

## 12.2 内网部署脚本

保存：

```text
install-offline-dev-env.sh
```

内容：

```bash
#!/bin/bash

set -e

REPO=/opt/kylin-local-repo

cat >/etc/apt/sources.list.d/kylin-local.list <<EOF
deb [trusted=yes] file:${REPO} ./
EOF

apt update

apt install --no-download \
build-essential \
gcc-10 \
g++-10 \
cmake \
pkg-config

echo "install complete"
```

执行：

```bash
chmod +x install-offline-dev-env.sh

./install-offline-dev-env.sh
```

---

## 13. 附录

## 附录 A：版本证据

文件：

```text
apt-cache-policy.txt
```

记录：

- 软件源
- gcc版本
- cmake版本
- libc版本
- sanitizer版本


---

## 附录 B：依赖证据

文件：

```text
apt-rdepends.txt
```

记录完整依赖闭包。


---

## 附录 C：软件包清单

文件：

```text
package-list.txt
```

记录：

```text
159 deb packages
```

---

## 附录 D：完整性

文件：

```text
SHA256SUM
```

用于：

- 传输校验
- 内网审计
- 版本固定

---

## 附录 E：最终目录

```text
kylin-v10-cpp-dev-env/

├── Packages
├── *.deb
├── SHA256SUM
├── package-list.txt
├── apt-cache-policy.txt
├── apt-rdepends.txt
├── build-offline-repo.sh
└── install-offline-dev-env.sh
```

---

## 总结

最终实现：

```text
KYLIN官方仓库
        |
        v
Kylin Docker
        |
        v
APT依赖解析
        |
        v
159个deb
        |
        v
离线APT仓库
        |
        v
内网C++开发环境
```

适用于：

- 银河麒麟 V10 SP1
- amd64
- 内网隔离环境
- C++后端开发
- Redis源码编译
- CMake工程
