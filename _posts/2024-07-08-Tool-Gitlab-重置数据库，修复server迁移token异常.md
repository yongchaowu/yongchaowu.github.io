---
layout: post
title: Gitlab-重置数据库，修复server迁移token异常
display_title: 'GitLab 重置数据库，修复 server 迁移 token 异常'
date: 2024-07-08 13:41:00
categories:
- DevOps & Infrastructure
tags:
- GitLab
- Tool
---

迁移gitlab的server数据之后，导致token异常
影响：修改工程配置信息，提交时页面报错502

<!--more-->
```shell
sudo gitlab-rails dbconsole --database main
DELETE FROM ci_group_variables;
DELETE FROM ci_variables;
UPDATE projects SET runners_token = null,runners_token_encrypted = null;
UPDATE namespaces SET runners_token = null,runners_token_encrypted = null;
UPDATE application_settings SET runners_registration_token_encrypted = null;
UPDATE application_settings SET encrypted_ci_jwt_signing_key = null;
UPDATE ci_runners SET token = null,token_encrypted = null;


sudo gitlab-rails console -e production
ApplicationSetting.first.delete
ApplicationSetting.first
```