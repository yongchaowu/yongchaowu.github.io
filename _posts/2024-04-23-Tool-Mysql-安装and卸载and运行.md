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

<!--more-->
`Ubuntu 18.04.5`操作系统，安装与卸载`MySQL`数据库。



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

- 默认root密码为空，可通过`error.log`文件查看。终端`sudo vim /var/log/mysql/error.log`

- 登录，终端`mysql -u root -p`

- 启动服务，终端`sudo service mysql start` 或终端`sudo systemctl start mysql.service`

- 修改密码，登录mysql后，终端`ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'new_password';` ，然后刷新权限，终端`FLUSH PRIVILEGES;`

- `show databases;`:显示当前数据库
- `use database-name`:使用database-name数据库
    - `source xx.sql`
- `CREATE DATABASE database-name;`:创建database-name数据库
- `mysql -u root -p database-name < xxx.sql`: 向database-name 数据库导入sql



## Mysql 配置文件
- `/etc/mysql`



## 其他问题

### 登录报错
#### error：1130
原因：没有远程连接权限。

方法：
    - `mysql -u root -p`
    - `show databases;`
    - `use mysql`
    - `select Host, User from user;`
    - `update user set Host='%' where User='root';`
    - `FLUSH PRIVILEGES;`

#### 启动失败，`su: warning: cannot change directory to /nonexistent: No such file or directory`
原因：一般是mysql服务器异常关机导致

方法：
```shell
sudo service mysql stop
sudo usermod -d /var/lib/mysql mysql
sudo service mysql start
```
