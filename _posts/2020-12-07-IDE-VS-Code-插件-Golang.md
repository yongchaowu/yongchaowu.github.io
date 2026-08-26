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

<!--more-->
使用go mod 代理来安装

https://goproxy.io是一个国内的代理

执行

```plain
go env -w GO111MODULE=on
go env -w GOPROXY=https://goproxy.io,direct
```

关闭vscode重新打开，再次点击install all.

参考：

golang GOPROXY 设置 - 梁二狗的个人空间 - OSCHINA - 中文开源技术交流社区

我们知道从 Go 1.11 版本开始，官方支持了 go module 包依赖管理工具。 其实还新增了 GOPROXY 环境变量。如果设置了该变量，下载源代码时将会通过这个环境变量设置的代理地址，而不再是以前的直接从代码库下载。这...

![img](https://static.oschina.net/new-osc/img/favicon.ico)https://my.oschina.net/u/3305368/blog/3044169

## 使用VsCode调试时：

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