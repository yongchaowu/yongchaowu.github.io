---
layout: post
title: Linux-Ubuntu
display_title: 'Linux Ubuntu'
date: 2023-04-05 12:38:00
categories:
- Systems
tags:
- OS
- Ubuntu
---

- 开源 Ubuntu一直是免费下载，使用和分享
- 安全 Ubuntu是最为安全的操作系统之一，其内建了防火墙和病毒保护软件。并且，长期支持的版本将提供5年的安全补丁和更新。
- 可访问 计算用于所有人，不论国籍，性别或障碍。Ubuntu被完整地翻译成50多种语言，且包含了必要的辅助技术。

<!--more-->
## cn.ubuntu.com

https://cn.ubuntu.com/
https://cn.ubuntu.com/desktop
https://cn.ubuntu.com/download


## ubuntu.com

[Ubuntu+Server+CLI+pro+tips+06.01.20.pdf](https://assets.ubuntu.com/v1/bb21c0e8-Ubuntu+Server+CLI+pro+tips+06.01.20.pdf?_ga=2.73769234.1060759144.1680618607-730245605.1680618607 "Ubuntu Server CLI pro tips")


### Download Address 
[https://ubuntu.com/download/desktop](https://ubuntu.com/download/desktop "Download Ubuntu Desktop")

### Install Ubuntu Desktop
[https://ubuntu.com/download/desktop](https://ubuntu.com/download/desktop "How to install Ubuntu Desktop")

### Install Multipass
Mini-clouds on desktops with Multipass
With Multipass you can download, configure, and control Ubuntu Server virtual machines with the latest updates preinstalled. Set up a mini-cloud on your Linux, Windows, or macOS system.

[https://multipass.run/install](https://multipass.run/install "Install Multipass")
[https://multipass.run/docs](https://multipass.run/docs "multipass docs")
[https://multipass.run/docs/set-up-a-graphical-interface](https://multipass.run/docs/set-up-a-graphical-interface "multipass set-up-a-graphical-interface")

Get an instant Ubuntu VM with a single command. Multipass can launch and run virtual machines and configure them with cloud-init like a public cloud. Prototype your cloud launches locally for free.

#### How to launch LTS instances
```bash
Launch an instance (by default you get the current Ubuntu LTS)
$ multipass launch --name foo

Run commands in that instance, try running bash (logout or ctrl-d to quit)
$ multipass exec foo -- lsb_release -a

See your instances
$ multipass list

Stop and start instances
$ multipass stop foo bar
$ multipass start foo

Clean up what you don’t need
$ multipass delete bar
$ multipass purge

Find alternate images to launch
$ multipass find

Pass a cloud-init metadata file to an instance on launch. See using cloud-init with multipass for more details
$ multipass launch -n bar --cloud-init cloud-config.yaml

See your instances
$ multipass list

Get help
$ multipass help
$ multipass help <command>
```

### Ubuntu WSL 
Access the Linux Terminal on Windows with Ubuntu WSL

For a more integrated environment, activate Windows Subsystem for Linux (WSL) to run Linux applications and workflows while developing cross-platform on your Windows machine.
You can download Ubuntu directly from the Microsoft Store.

#### 规格
2023/4/5 9:56:33 已验证，规格如下
发布者  	Canonical Group Limited
规格		2204.1.8.0
应用		566MB
数据		1.29GB
总使用量	1.84GB

更新缓存和升级
```bash
sudo apt-get update
sudo apt-get upgrade
```
更新后，规格如下：
```
发布者  	Canonical Group Limited
规格		2204.1.8.0
应用		566MB
数据		1.61GB
总使用量	2.17GB
```
### 更改镜像源
源 `/etc/apt/sources.list`

1.备份源 `cp -ra /etc/apt/sources.list /etc/apt/sources.list.bak`

2.查询ubuntu代号 `lsb_release -a`
```
yongchao@W-PC:~$ lsb_release -a
No LSB modules are available.
Distributor ID: Ubuntu
Description:    Ubuntu 22.04.2 LTS
Release:        22.04
Codename:       jammy
```
3.更换成国内源`sudo vi /etc/apt/sources.list`
参考https://blog.csdn.net/sandonz/article/details/120854876
```
#网易源
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb http://mirrors.163.com/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.163.com/ubuntu/ focal-security main restricted universe multiverse
deb http://mirrors.163.com/ubuntu/ focal-updates main restricted universe multiverse
deb http://mirrors.163.com/ubuntu/ focal-backports main restricted universe multiverse
# deb-src http://mirrors.163.com/ubuntu/ focal main restricted universe multiverse
# deb-src http://mirrors.163.com/ubuntu/ focal-security main restricted universe multiverse
# deb-src http://mirrors.163.com/ubuntu/ focal-updates main restricted universe multiverse
# deb-src http://mirrors.163.com/ubuntu/ focal-backports main restricted universe multiverse
# 预发布软件源，不建议启用
# deb http://mirrors.163.com/ubuntu/ focal-proposed main restricted universe multiverse
# deb-src http://mirrors.163.com/ubuntu/ focal-proposed main restricted universe multiverse

#阿里源
deb http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ focal-backports main restricted universe multiverse

#清华源https

# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-updates main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-backports main restricted universe multiverse
deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-security main restricted universe multiverse

# 预发布软件源，不建议启用
# deb https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-proposed main restricted universe multiverse
# deb-src https://mirrors.tuna.tsinghua.edu.cn/ubuntu/ focal-proposed main restricted universe multiverse

```
4.更新缓存和升级
```bash
sudo apt-get update
sudo apt-get upgrade
```
更新后，规格如下：
```
发布者  	Canonical Group Limited
规格		2204.1.8.0
应用		566MB
数据		2.19GB
总使用量	2.74GB
```
### 图形界面安装
参考 https://blog.csdn.net/sandonz/article/details/120854876

1.安装桌面环境xubuntu `sudo apt-get install xubuntu-desktop` 已包含xfce4和xorg

2.安装远程桌面服务xrdp `sudo apt-get install xrdp`

3.配置xrdp端口 `sudo sed -i 's/port=3389/port=3390/g' /etc/xrdp/xrdp.ini`
默认配置3389改为3390，避免和windows的端口冲突。

4.配置xsession
`sudo echo xfce4-session > ~/.xsession`
告诉系统，开启桌面环境的时候用xfce4-session。

5.配置sesman.ini
`sudo vim /etc/xrdp/sesman.ini`
将KillDisconnected的值修改为true,保存退出

6.重启电脑主机，然后启动xrdp
`sudo service xrdp restart`

7.远程连接
打开远程桌面连接[Win+R--->mstsc]，在计算机（Computer）栏输入localhost:3390，用户名使用当前配置的用户名密码。

8.设置为中文
`sudo dpkg-reconfigure locales`，选择zh_CN UTF-8, 然后按空格勾选，再tab切换到ok上回车，接下来的界面选zh再回车。
如果键盘不可用，注销重新登录。

9.每次通过远程桌面连接时需要重新启动服务`sudo service xrdp restart`（这里或许可以设置，未验证）

### 映射Ubuntu的根目录
win+R -> `\\wsl$` --->鼠标右键Ubuntu文件夹-->映射网络驱动器

### 注销WSL子系统 (未验证)
参考 http://blog.itpub.net/70003733/viewspace-2894493/
首先打开windows powershell（管理员），查询你安装的linux发行版
`wslconfig /l`

然后注销子系统
`wslconfig /u [子系统名称]`

### Run system containers with LXD
When running Linux on Linux, consider LXD system containers instead of VMs for optimizing resources. LXD runs a full OS inside containers, providing all the benefits of a VM without the usual overhead.