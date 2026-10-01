---
layout: post
title: Mysql-安装&卸载&运行
display_title: 'MySQL 安装、卸载与运行'
date: 2024-04-23 08:12:00
categories:
- Database
tags:
- DB
- Ubuntu
- MySQL
- Tool
---
## 背景

`Ubuntu 18.04.5`操作系统，安装与卸载`MySQL`数据库。

<!--more-->

## 安装MySQL

终端`sudo apt install mysql-server`

注意：默认安装源上的版本

## 卸载MySQL

终端`sudo apt autoremove --purge mysql-server`

终端`sudo apt remove mysql-server`

终端`sudo apt autoremove mysql-server`

终端`sudo apt remove mysql-common`

终端`sudo apt autoremove`

终端`sudo apt autoclean`

## MySQL-Server 5.7.31

> **版本范围：** 本节账户和权限说明针对 MySQL 5.7.31（2020-07-13），不是 MySQL 8/9 的通用语法。

- 默认root密码为空，可通过`error.log`文件查看。终端`sudo vim /var/log/mysql/error.log`

- 登录，终端`mysql -u root -p`

- 启动服务，终端`sudo service mysql start` 或终端`sudo systemctl mysql.service start`

- 修改密码，登录 mysql 后执行 `ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'new_password';`。MySQL 5.7 的账户管理语句立即生效，不需要额外执行 `FLUSH PRIVILEGES;`。

- `show databases;`：列出当前账号可见的数据库（不是当前数据库）
- `use database-name`:使用database-name数据库
    - `source xx.sql`
- `CREATE DATABASE database-name;`:创建database-name数据库
- `mysql -u root -p database-name < xxx.sql`: 向database-name 数据库导入sql

## Mysql 配置文件
- `/etc/mysql`

## 其他问题

### 登录报错
#### error：1130
原因：客户端主机名没有匹配到允许登录的账户（Host/User）。

方法：
    - `mysql -u root -p`
    - `show databases;`
    - `use mysql`
    - `select Host, User from user;`
    - 使用 `CREATE USER`（新账号）或 `ALTER USER`（已有账号）明确远程账户的 `User`/`Host`，再用 `GRANT` 授予实际需要的最小权限；不要直接更新 `mysql.user`。
    - MySQL 5.7 中 `CREATE USER`、`ALTER USER` 和 `GRANT` 等账户管理语句立即生效，不需要额外执行 `FLUSH PRIVILEGES`；具体用户名、主机和权限必须按实际部署填写。

#### 启动失败，`su:warning:cannot change director to /nonexistent:No such file or directory`
原因：一般是mysql服务器异常关机导致

方法：
```shell
sudo service mysql stop
sudo usermod -d /var/lib/mysql mysql
sudo service mysql start
```

参考：[MySQL 5.7 `SHOW DATABASES`](https://docs.oracle.com/cd/E17952_01/mysql-5.7-en/show-databases.html)、[连接验证](https://docs.oracle.com/cd/E17952_01/mysql-5.7-en/connection-access.html)、[`CREATE USER`](https://docs.oracle.com/cd/E17952_01/mysql-5.7-en/create-user.html)、[`ALTER USER`](https://docs.oracle.com/cd/E17952_01/mysql-5.7-en/alter-user.html)、[`GRANT`](https://docs.oracle.com/cd/E17952_01/mysql-5.7-en/grant.html)、[`FLUSH`](https://docs.oracle.com/cd/E17952_01/mysql-5.7-en/flush.html)、[错误 1130 参考](https://docs.oracle.com/cd/E17952_01/mysql-errors-5.7-en/server-error-reference.html) 和 [MySQL 5.7.31 发布说明](https://dev.mysql.com/doc/relnotes/mysql/5.7/en/news-5-7-31.html)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 03:29（UTC+08:00）。
