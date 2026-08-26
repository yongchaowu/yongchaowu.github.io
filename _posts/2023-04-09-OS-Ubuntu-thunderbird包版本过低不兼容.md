---
layout: post
title: "OS-Ubuntu-thunderbird包版本过低不兼容"
date: 2023-04-09 23:51:00
categories: ["OS"]
tags: ["OS", "Tool", "Ubuntu"]
---

在安装搜狗输入法时，遇到过thunderbird包版本过低不兼容的问题，
问题的格式如下：
```
thunderbird-local-zh-hans:

    depends: thunderbird(<1:31

build  12.04....

but ..... 14.04  is to be installed
```

<!--more-->
## thunderbird
>[https://www.thunderbird.net/zh-CN/](https://www.thunderbird.net/zh-CN/ "thunderbird")

Thunderbird 是一款免费的电子邮件应用程序。
Thunderbird 是一个开源项目。

## 解决方法
网上一般有两种方法：
1.安装对应版本的包，可以去搜索thunderbird
[https://www.ubuntuupdates.org/package/core/bionic/main/updates/thunderbird-locale-zh-hans](https://www.ubuntuupdates.org/package/core/bionic/main/updates/thunderbird-locale-zh-hans)

2.卸载thunderbird[亲测可行]
```bash
dpkg --get-selections | grep thunderbird #查找软件
sudo apt-get purge thunderbird thunderbird-gnome-support thunderbird-locale-en thunderbird-locale-en-us thunderbird-locale-zh-cn thunderbird-locale-zh-hans #卸载软件  
```