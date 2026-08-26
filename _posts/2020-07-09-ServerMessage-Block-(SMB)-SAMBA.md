---
layout: post
title: "ServerMessage Block (SMB)--SAMBA"
date: 2020-07-09 12:23:00
categories: ["ServerMessage Block (SMB)"]
tags: ["ServerMessage Block (SMB)", "SAMBA"]
---

[website Samba](https://www.samba.org/samba/)
在Unix Like 上面可以分享档案数据的 file system 是 NFS，
在 Windows 上面使用的『网络邻居』所使用的档案系统则称为Common Internet File System, CIFS

<!--more-->
一般来说，除非 Linux distribution 已经相当的老旧了 (例如 Red Hat6.x 以前的版本)，并且在旧的系统上面正在正常的运作一些服务，而仅想要增加SAMBA 的服务，那就只好使用 Tarball 的方式来安装SAMBA ，否则的话，蛮强烈的建议直接以 RPM 的方法来安装您的SAMBA 服务器软件即可！因为既简单方便，又容易统一设定。Server端的设定由于 SAMBA 几乎一定包含在各个主要的 Linux distribution 当中，并且不同版本之间的功能差异也不是很大.

SAMBA 的设定档档名都是不变的 ( smb.conf )