---
layout: post
title: "Python-Pyspider-Installation"
date: 2020-07-09 21:32:00
categories: ["Python"]
tags: ["pyspider", "Python"]
---

July 9, 2020 9:30 PM

<!--more-->
http://docs.pyspider.org/en/latest/#pyspider
## Installation

*   `pip install pyspider`
*   run command `pyspider`, visit [http://localhost:5000/](http://localhost:5000/)

Quickstart: [http://docs.pyspider.org/en/latest/Quickstart/](http://docs.pyspider.org/en/latest/Quickstart/)

### 安装pyspider出现的问题（pycurl安装失败）和解决方案
https://blog.csdn.net/sinat_33487968/article/details/69421147
安装pyspider之前需要安装lxml 和 pycurl ，但是在安装pycurl的过程中遇到了同样的错误

解决方案是安装wheel 和到 http://www.lfd.uci.edu/~gohlke/pythonlibs/#pycurl 这个网址下载相应版本的pycurl ，如果是64位的就用

pip install wheel 
pip install pycurl‑7.43.0‑cp36‑cp36m‑win_amd64.whl

- 3.7.1（x32） 舍弃，使用3.6（x64）可以---2018-11-24 
