---
layout: post
title: Nvidia-查询显卡信息
date: 2023-10-12 13:00:00
categories:
- Developer Tools
tags:
- Tool
- NVIDIA
---
- `nvidia-smi -L`
- `lspci  |grep -i  nvidia`

本文修订依据：pciutils [`v3.5.0` tagged `lspci.c`](https://github.com/pciutils/pciutils/blob/v3.5.0/lspci.c) 与 [`lspci.man`](https://github.com/pciutils/pciutils/blob/v3.5.0/lspci.man)（版本发布于 2018-05-19）。该版本将程序名定义为 `lspci`；本文仅纠正命令拼写。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 10:42（UTC+08:00）。修订仅将 `lscpi` 更正为 `lspci`。