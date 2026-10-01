---
layout: post
title: Postgresql
summary: >
  PostgreSQL installation on Ubuntu 18.04, including password reset,
  SQL import, and basic configuration for development environments.
lang: zh-CN
date: 2024-08-09 09:15:00
categories:
- Database
tags:
- DB
- Tool
---
Ubuntu18.04 安装postgresql

## 安装&修改密码&导入sql
```shell
apt install postgresql

<!--more-->

su postgres # postgres账户

psql -h localhost -U postgres  # localhost 用户postgres

alter user postgres with password '123456';#修改密码
\i xx.sql
\q

```

---

> **版本范围：** 本文按 Ubuntu 18.04（Bionic）官方仓库的标准 `postgresql` 包编写；该包在 2018-02-09 发布为 `10+190`，因此配置路径使用 `/etc/postgresql/10/main/`。若另行从其他仓库安装 PostgreSQL 12，应使用对应的 `/12/` 路径。

## 修改访问权限

- `sudo vim /etc/postgresql/10/main/postgresql.conf`:listen_addresses 
- `sudo vim /etc/postgresql/10/main/pg_hba.conf`:0.0.0.0/0
- `sudo service postgresql restart`

## 其他
- `journalctl -r -u postgresql`:服务系统启动日志 
- `netstat -alnt`:服务端口工作

参考：[Ubuntu Bionic `postgresql` 包发布历史](https://launchpad.net/ubuntu/bionic/amd64/postgresql)、[Bionic `pg_ctlcluster(1)`](https://manpages.ubuntu.com/manpages/bionic/man1/pg_ctlcluster.1.html) 和 [`netstat(8)`](https://man7.org/linux/man-pages/man8/netstat.8.html)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 02:58（UTC+08:00）。