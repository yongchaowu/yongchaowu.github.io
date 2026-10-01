---
layout: post
title: Windows-bat-不等待当前命令返回继续执行后续指令
date: 2020-07-11 17:29:00
categories:
- Systems
tags:
- Windows
- OS
- Windows批处理 (cmd/bat)
---
`start` 用于启动程序；是否立即返回取决于程序类型和调用场景。从命令脚本启动 32 位 GUI 程序时，`cmd.exe` 会等待该程序结束，因此不能把“批处理一定不会等待”作为规则。

本文修订依据：Microsoft Learn [`start` command](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/start#remarks)，源文档提交 `e2e67b0962e0757cdac4d226ee7386120abf0664`（页面日期 2026-04-16）。Remarks 明确说明，从命令脚本启动 32 位 GUI 程序时不会产生通常的非等待行为；本文仅将绝对表述改为有条件表述。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 11:30（UTC+08:00）。修订仅纠正 `start` 等待行为说明。