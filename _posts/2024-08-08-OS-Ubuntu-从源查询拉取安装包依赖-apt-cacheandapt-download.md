---
layout: post
title: Ubuntu-从源查询拉取安装包依赖-apt-cache&apt download
date: 2024-08-08 17:38:00
categories:
- Systems
tags:
- OS
- Ubuntu
---

引用：

<!--more-->
- [Ubuntu apt-get apt-cache 命令使用](https://blog.csdn.net/u010472607/article/details/77483675)
- [apt-get下载包及所有依赖](https://blog.csdn.net/qq_51470638/article/details/127136484)

## 指令

- `apt-cache `
  - `depends`
  - `--no-*`
    - `--no-pre-depends`
    - `--no-suggests`
    - `--no-recommends`
    - `--no-conflicts`
    - `--no-breaks`
    - `--no-enhances`
  - `--recurse`
- `apt-get download`



---

## 安装包缓存

1. `apt-get`指令会缓存安装包。
2. 缓存安装包路径为:`/var/cache/apt/archives`
3. `apt clean all`:清空缓存



---

## 安装文件位置

一般的deb包(包括新立得或者apt-get下载的)都在`/usr/share`。 



自己下载的压缩包或者编译的包，有些可以选择安装目录，一般放在`/usr/local/`，也有在`/opt`的。

---

## apt-get

- [Ubuntu apt-get apt-cache 命令使用](https://blog.csdn.net/u010472607/article/details/77483675)

| 命令                             | 说明                                                         |
| -------------------------------- | ------------------------------------------------------------ |
| apt-get update                   | 更新源                                                       |
| apt-get upgrade                  | 更新所有已安装的包                                           |
| **apt-get install <pkg>**        | 安装软件包<pkg>，**多个**软件包用空格隔开                    |
| apt-get install --reinstall <pkg> | 重新安装软件包<pkg>                                          |
| apt-get install -f <pkg>         | 修复安装（破损的依赖关系）软件<pkg>                          |
| **apt-get remove <pkg>**         | 删除软件包<pkg>（不包括配置文件）                            |
| **apt-get purge <pkg>**          | 删除软件包<pkg>（包括配置文件）                              |
| apt-get clean                    | 清除缓存(/var/cache/apt/archives/{,partial}下) 中所有已下载的包 |
| apt-cache stats                  | 显示系统软件包的统计信息                                     |
| **apt-cache search <pkg>**       | 使用关键字pkg搜索软件包                                      |
| **apt-cache show**               | 显示软件包pkg_name的详细信息                                 |
| **apt-cache depends <pkg>**      | 查看pkg所依赖的软件包                                        |
| apt-cache rdepends <pkg>         | 查看pkg被哪些软件包所依赖                                    |
| **apt-get build-dep <pkg>**      | 构建pkg源码包的编译依赖 (这条命令很神奇，一步搞定所有编译依赖) |



**apt-get命令的一般语法格式为：**`apt-get subcommands [ -d | -f | -m | -q| --purge | --reinstall | -b | -s | -y | -u | -h | -v ] [pkg] `



---

比如：

1. 更新或升级操作：

```bash
apt-get update                  # 更新源  
apt-get upgrade                 # 更新所有已安装的包  
apt-get dist-upgrade            # 发行版升级（如，从10.10到11.04）
```

2. 安装或重装类操作：

```bash
apt-get install <pkg>             # 安装软件包<pkg>，多个软件包用空格隔开  
apt-get install --reinstall <pkg> # 重新安装软件包<pkg>  
apt-get install -f <pkg>          # 修复安装（破损的依赖关系）软件包<pkg>  
```

3. 卸载类操作：

```bash
apt-get remove <pkg>          # 删除软件包<pkg>（不包括配置文件）  
apt-get purge <pkg>           # 删除软件包<pkg>（包括配置文件）  
```

4. 下载清除类操作：

```bash
apt-get source <pkg>              # 下载pkg包的源代码到当前目录  
apt-get download <pkg>            # 下载pkg包的二进制包到当前目录  
apt-get source --download-only <pkg>  # 仅下载源码包，不编译  
apt-get build-dep   <pkg>         # 构建pkg源码包的依赖环境（编译环境？）  
apt-get clean                     # 清除缓存(/var/cache/apt/archives/{,partial}下)中所有已下载的包  
apt-get autoclean                 # 类似于clean，但清除的是缓存中过期的包（即已不能下载或者是无用的包）  
apt-get autoremove                # 删除因安装软件自动安装的依赖，而现在不需要的依赖包  
```

5. 查询类操作：

```bash
apt-cache stats             # 显示系统软件包的统计信息  
apt-cache search <pkg>            # 使用关键字pkg搜索软件包  
apt-cache show   <pkg_name>   # 显示软件包pkg_name的详细信息  
apt-cache depends <pkg>       # 查看pkg所依赖的软件包  
apt-cache rdepends <pkg>      # 查看pkg被哪些软件包所依赖  
```



---



## 下载指定安装包依赖

- [apt-get下载包及所有依赖](https://blog.csdn.net/qq_51470638/article/details/127136484)

```shell
#!/bin/bash

#$1     pkg
get_all_depends()
{
        apt-cache depends --no-pre-depends --no-suggests --no-recommends \
                --no-conflicts --no-breaks --no-enhances\
                --no-replaces --recurse $1 | awk '{print $2}'| tr -d '<>' | sort --unique
}


## 遍历命令行参数，参数应为包名。
for pkg in $*
do
        all_depends=$(get_all_depends $pkg)
        echo -e "所有依赖共计"$(echo $all_depends | wc -w)"个"
        echo $all_depends
        i=0
        for depend in $all_depends
        do
                i=$((i+1))
                echo -e "\033[1;32m正在下载第$i个依赖："$depend "\033[0m"
                apt-get download $depend
        done
        apt-get download $pkg
done

```
