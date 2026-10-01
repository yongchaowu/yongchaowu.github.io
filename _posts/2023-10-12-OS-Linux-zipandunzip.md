---
layout: post
title: Linux-zip&unzip
display_title: 'Linux zip 与 unzip'
date: 2023-10-12 12:58:00
categories:
- Systems
tags:
- Linux
- OS
---
- `zip -rP password filename.zip filename`  加密
- `unzip -O GBK XXX.zip` 或GBK18030      中文乱码

本文修订依据：Info-ZIP `zip` 3.0 手册（2008-06-16 版本）及 Debian Bookworm `zip` `3.0-13` 的 [`-P password` 选项说明](https://manpages.debian.org/bookworm/zip/zip.1.en.html#OPTIONS)。本文仅将示例中的占位词 `passwork` 更正为 `password`；手册同时警告在命令行中传递明文密码存在安全风险，本文未扩展或现代化该安全说明。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 14:18（UTC+08:00）。修订仅纠正 zip 命令示例中的密码占位词。