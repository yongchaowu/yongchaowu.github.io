---
layout: post
title: VS Code-插件-Golang
date: 2020-12-07 21:17:00
categories:
- Developer Tools
tags:
- Golang
- Visual Studio Code
- IDE
---
## 安装Golang插件

使用go mod 代理来安装

<!--more-->

https://goproxy.io是一个国内的代理

执行

```plain
go env -w GO111MODULE=on
go env -w GOPROXY=https://goproxy.io,direct
```

关闭 VS Code重新打开，再次点击install all.

参考：

golang GOPROXY 设置 - 梁二狗的个人空间 - OSCHINA - 中文开源技术交流社区

我们知道从 Go 1.11 版本开始，官方支持了 go module 包依赖管理工具。 其实还新增了 GOPROXY 环境变量。如果设置了该变量，下载源代码时将会通过这个环境变量设置的代理地址，而不再是以前的直接从代码库下载。这...

![img](https://static.oschina.net/new-osc/img/favicon.ico)https://my.oschina.net/u/3305368/blog/3044169

## 使用 VS Code 调试时：

按下<kbd>F5</kbd>

launch.json:

```json
{
    // 使用 IntelliSense 了解相关属性。 
    // 悬停以查看现有属性的描述。
    // 欲了解更多信息，请访问: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Launch",
            "type": "go",
            "request": "launch",
            "mode": "auto",
            "program": "${workspaceFolder}//src",//"{file}",
            "env": {},
            "args": []
        }
    ]
}
```
设置`GOPATH` 为当前工作空间
然后 `go mod init v0`

本文修订依据：Microsoft `microsoft/vscode` 官方仓库 [`README.md`](https://raw.githubusercontent.com/microsoft/vscode/d681a7635a0f6d26e9a353ef0cebfdb842c257f1/README.md)，commit `d681a7635a0f6d26e9a353ef0cebfdb842c257f1`（2026-09-25），以及官方 [VS Code FAQ](https://code.visualstudio.com/docs/supporting/faq)（核验日期 2026-09-25）。官方资料使用全名 `Visual Studio Code` 及简称 `VS Code`；本文仅将两处 `vscode`/`VsCode` 更正为 `VS Code`，未推断或更改 VS Code 版本、插件行为、命令、路径或调试配置。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 16:00（UTC+08:00）。修订仅纠正两处 VS Code 官方简称的大小写与空格。