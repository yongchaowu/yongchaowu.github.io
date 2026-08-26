---
layout: post
title: Postgresql
date: 2024-08-09 09:15:00
categories:
- Developer Tools
tags:
- DB
- Tool
---

Ubuntu18.04 安装postgresql

<!--more-->
## 安装&修改密码&导入sql
```shell
apt install postgresql

su postgres //postgres账户

psql -h localhost -U postgres  //localhost 用户postgres

alter user postgres with password '123456';//修改密码
\i xx.sql
\q

```

---
## 修改访问权限

- `sudo vim /etc/postgresql/12/main/postgresql.conf`:listen_addresses 
- `sudo vim /etc/postgresql/12/main/pg_hba.conf`:0.0.0.0/0
- `sudo service postgresql restart`

## 其他
- `journalctl -r -u postgresql`:服务系统启动日志 
- `netstat -alnt`:服务端口工作
