---
layout: post
title: ServerMessage Block (SMB)--SAMBA
date: 2020-07-09 12:23:00
categories:
- Security & Networking
tags:
- SMB
- SAMBA
---
[website Samba](https://www.samba.org/samba/)
在Unix Like 上面可以分享档案数据的 file system 是 NFS，
Windows 的网络文件共享协议称为 SMB（Server Message Block）；CIFS 是 SMB 的一个方言。

一般来说，除非 Linux distribution 已经相当的老旧了 (例如 Red Hat6.x 以前的版本)，并且在旧的系统上面正在正常的运作一些服务，而仅想要增加SAMBA 的服务，那就只好使用 Tarball 的方式来安装SAMBA ，否则的话，蛮强烈的建议直接以 RPM 的方法来安装您的SAMBA 服务器软件即可！因为既简单方便，又容易统一设定。Server端的设定由于 SAMBA 几乎一定包含在各个主要的 Linux distribution 当中，并且不同版本之间的功能差异也不是很大.

<!--more-->

SAMBA 的设定档档名都是不变的 ( smb.conf )

本文修订依据：Microsoft Learn [`Microsoft SMB Protocol and CIFS Protocol Overview`](https://learn.microsoft.com/en-us/windows/win32/fileio/microsoft-smb-protocol-and-cifs-protocol-overview)，发布日期 2025-07-08、更新 2025-07-10，源提交 `804c358a9c4bce679f7de9c1ef714669cb168959`。该文档将 SMB 定义为网络文件共享协议，并将 CIFS 定义为 SMB 的一个方言。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 09:39（UTC+08:00）。修订仅纠正 SMB 与 CIFS 的协议术语关系。