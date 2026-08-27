---
layout: post
title: Other-个人博客系统-Build
display_title: '个人博客系统 Build'
date: 2020-10-22 18:50:00
categories:
- Developer Tools
tags:
- Other
- WordPress
- Blog
- Website
---

October 20, 2020 5:31 PM

<!--more-->
- WordPress
- z-blog
- Blogger
- Medium
- Ghost Pro
- jekyll
- b2evolution
- viddler
- Joomla
- Drupal

2019个人博客系统汇总

## WordPress
https://wordpress.org/download/


## Z-Blog
https://www.zblogcn.com/zblogphp/


## 个人PC搭建博客
参考 https://jingyan.baidu.com/article/5552ef47f920b1518ffbc91a.html

- XAMPP
- WordPress

### XAMPP Download
https://www.apachefriends.org/index.html

### 安装方法
1.先安装XAMPP，比如C:\xampp，然后双击C:\xampp目录里的xampp-control.exe 启动XAMPP控制面板
2.再启用“Apache 服务器”和“MySQL数据库”，开启后就可以用浏览器访问 http://localhost 以登陆XAMPP的设置页面
3.进入http://localhost/phpmyadmin数据库管理页面，点击顶部菜单中的【数据库】，创建一个新数据库，比如：personalblog，数据库服务器地址是 localhost ，数据库超级用户root ，本地测试用密码可以先留空
4.将WordPress解压，并放到XAMPP默认网站目录C:\xampp\htdocs（你可以将“wordpress文件夹”随意改个你要的名字，比如：PersonalBlog，必须是英文，最好简单好记）
5.浏览器访问 http://localhost/PersonalBlog，点“创建配置文件”按钮，在“数据库名”里输入刚才你创建的数据库，在用户名里输入默认的root，密码因为刚才我们在XAMPP留空了，所以可以不填就好，最后点提交进行安装
备注：局域网其它机器访问要先在WordPress里通过"设置项"把“WordPress地址”和“站点地址”改成你的IP地址（内网就内网，外网就外网）
6.另外绑定域名后，可以取消默认进入dashboard页面，修改方法：在C:\xampp\htdocs目录中，修改index.php内容，把dashboard改为其他你想默认指定的目录

### 坑
1.WordPress设置错误的url导致网站不能访问
参考 [WordPress设置错误的url导致网站不能访问:](https://www.cnblogs.com/guanzelin/p/8868294.html)  https://www.cnblogs.com/guanzelin/p/8868294.html
```latex
修改数据库
    1.登录到你的管理页面，找到wp_options表
    2.将表中的siteurl和home字段修改为当前的新域名
```
2.wordpress在本地局域网跨网段无法访问
web服务器只能在相同网段访问，如果想跨网段访问应该是下级网络可以访问上级网络。要装在一台公司网络顶端的机器才能让所有下属网络及同网段机器访问到

3.公司内部局域网结构，以及笔记本不能做web服务器原因
公司的网络环境：
	公网--路由---核心 （1个，在核心上划分vlan，分网段）--二层（二层交换机不需要配置）--pc
	二层的作用就是接入计算机
	端口映射是在路由上设置
笔记本的问题是因为：笔记本接入的交换机有向上路由协议，但是没有向下的协议。能访问其他网段机器，但是不能被其他网段机器访问。
