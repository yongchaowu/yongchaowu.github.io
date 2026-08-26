---
layout: post
title: "Tool-Navicat"
date: 2024-04-23 08:30:00
categories: ["Tool"]
tags: ["DB", "Tool"]
---

## Ubuntu

<!--more-->
### 背景

Navicat Premium16

* [Navicat 中国 | 支持 MySQL、Redis、MariaDB、MongoDB、SQL Server、SQLite、Oracle 和 PostgreSQL 的数据库管理](https://www.navicat.com.cn/)
  
* [Download - Navicat | 下载 Navicat Premium 14 天免费 Windows、macOS 和 Linux 的试用版](https://www.navicat.com.cn/download/navicat-premium)
  

软件包`navicat16-premium-cs.AppImage`

**运行命令：**

    chmod +x navicat16-premium-cs.AppImage
    ./navicat16-premium-cs.AppImage

**注意：从 Ubuntu 22.04 开始，可能需要安装额外的软件包。请运行以下命令：**`sudo apt install libfuse2`

### 初始化&重置

* 关闭应用程序
  
* 终端`sudo rm -rf ~/.config/navicat` 以及`sudo rm -rf ~/.config/dconf/user`**注意** 该重置方式会丢失已有的连接配置
  

### 导入sql文件

* 建立数据库连接
  
* 打开数据库
  
* 新建数据库
  
* 执行sql语句，插入数据**注意** 操作不当会修改原有数据库表，导致部分库表丢失，影响数据库服务运行