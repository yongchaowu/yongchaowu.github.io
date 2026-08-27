---
layout: post
title: Gitlab-备份恢复-迁移
display_title: 'GitLab 备份恢复与迁移'
date: 2023-07-24 19:26:00
categories:
- DevOps & Infrastructure
tags:
- GitLab
- Tool
---

## 备份
sudo gitlab-rake gitlab:backup:create
使用命令会在/var/opt/gitlab/backups目录下创建一个压缩包，这个压缩包就是Gitlab整个的完整部分。
需要在gitlab 运行时操作。
gitlab.rb 和 gitlab-secrets.json 两个文件包含敏感信息。未被备份到备份文件中。需要手动备份。这两个文件在/etc/gitlab/ 目录下。

<!--more-->
## 恢复
1、停止相关数据连接服务
gitlab-ctl stop unicorn
gitlab-ctl stop sidekiq
2、恢复gitlab仓库
进入/var/opt/gitlab/backups
现在我们要从1537261122_2018_09_18_9.2.5这个备份编号中，恢复数据，命令如下：
gitlab-rake gitlab:backup:restore BACKUP=1546916920_2019_01_08_10.5.1
按照提示输入两次yes并回车
如果出现多个done的信息，说明整个gitlab数据就已经正常恢复完毕。

4、恢复两个配置文件
我们进入备份目录使用cp命令复制到配置目录
cp gitlab.rb gitlab-secrets.json /etc/gitlab/
5、恢复完毕以后，我们现在来启动gitlab，使用以下命令：
gitlab-ctl start
