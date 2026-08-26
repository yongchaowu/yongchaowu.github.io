---
layout: post
title: "Tool-GitLab"
date: 2023-04-14 22:50:00
categories: ["Tool"]
tags: ["Tool", "GitLab"]
---

>[https://about.gitlab.com/](https://about.gitlab.com/ "gitlab")

<!--more-->
GitLab 是一个用于仓库管理系统的开源项目，使用Git作为代码管理工具，并在此基础上搭建起来的Web服务。
安装方法是参考GitLab在GitHub上的Wiki页面。
Gitlab是被广泛使用的基于git的开源代码管理平台, 基于Ruby on Rails构建, 主要针对软件开发过程中产生的代码和文档进行管理, Gitlab主要针对group和project两个维度进行代码和文档管理, 其中group是群组, project是工程项目, 一个group可以管理多个project, 可以理解为一个群组中有多项软件开发任务, 而一个project中可能包含多个branch, 意为每个项目中有多个分支, 分支间相互独立, 不同分支可以进行归并。

## GitLab 离线包下载
https://packages.gitlab.com/gitlab/gitlab-ce

## GitLab 安装指令
`sudo dpkg -i gitlab-ce_15.10.2-ce.0_arm64.deb`

## GitLab 配置
安装完成后，会有相关提示。可以根据相关提示操作

`sudo gedit /etc/gitlab/gitlab.rb` 修改`external_url`
`sudo gitlab-ctl reconfigure`启动Gitlab实例。
提示默认账户管理员账户配置细节如下：
账户名称：root
账户密码：不显示，但提示在 /etc/gitlab/initial_root_password(24h后删除)[可以备份一下]

重置密码：https://docs.gitlab.com/ee/security/reset_user_password.html#reset-the-root-password.

## 防火墙与端口
```bash
sudo ufw status		#查看ufw的状态 
sudo ufw enable		#开启ufw
sudo ufw reload		#重启防火墙ufw
sudo ufw allow 9999	#对外开放9999端口
sudo ufw status		#
```

## 其他命令
1. `gitlab-ctl start` # 启动所有 gitlab 组件；
2. `gitlab-ctl stop` # 停止所有 gitlab 组件；
3. `gitlab-ctl restart` # 重启所有 gitlab 组件；
4. `gitlab-ctl status` # 查看服务状态；
5. `gitlab-ctl reconfigure` # 启动服务；
6. `vim /etc/gitlab/gitlab.rb` # 修改默认的配置文件；
7. `gitlab-rake gitlab:check SANITIZE=true --trace` # 检查gitlab；
8. `sudo gitlab-ctl tail` # 查看日志；
日志位置：`/var/log/gitlab` 可以进去查看访问日志以及报错日志等，供访问查看以及异常排查。
	- `gitlab-ctl tail` #查看所有日志
	- `gitlab-ctl tail nginx/gitlab_access.log` #查看nginx访问日志


## 添加SSH Key
生成密钥文件：使用`ssh-keygen`生成密钥文件`.ssh/id_rsa.pub`
用于`git clone`


## 提交一份代码步骤
```bash
git init\git clone
git status
git diff
git add .
git pull\git fetch
git commit -m "备注"
git push -uf origin master
```

gitlab创建项目自动生成的Readme中提到的方法：
```bash
git remote add origin projectaddress. 
git branch -M main
git push -uf origin main
```

## 默认branch
- project的默认branch名字是main。
- 如果项目创建时是私有，默认branch是保护分支，不允许push，需要在设置中修改--取消保护分支
- 如果希望更改默认branch，在设置中选择其他branch作为默认分支。(ps:我操作时，已保存，但是刷新后未更新过来，一直以为没该改成功，后来去看branchlist时才看到默认branch已改变，我差点要重启gitlab服务了。)

## 重命名branch
```bash
#重命名本地分支
git branch -m branch_old_name branch_new_name
#删除远程自己的原分支 
git push --delete origin branch_old_name
#ps:我删除的默认分支的名字，push被拒绝
#我就直接用当前工程remote add了一个新分支，然后删除原来的默认分支，我确认了commit记录都在。
-----------------------------------------
#推送新命名的分支
git push origin branch_new_name
#修改后的本地分支与远程分支关联
git branch --set-upstream-to origin/branch_new_name

```

## 删除branch
1.gitlab的项目的branch管理可以直接删除，会提示确认删除操作
2.指令删除
`git push origin --delete`
`git push origin --delete branch_name`

## 回退版本
回退到指定commit-number的版本
`git reset --hard [commit-number]`