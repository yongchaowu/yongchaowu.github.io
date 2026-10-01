---
layout: post
title: Wireshark
date: 2020-07-08 23:44:00
categories:
- Developer Tools
tags:
- Wireshark
- Tool
- Capture Packet
---
July 8, 2020 11:03 PM
[HomePage](https://www.wireshark.org/)

##Tip
### 如何抓取本地localhost的包
1. 将原有的 WinPcap 换为 Npcap，可以通过 Wireshark 的界面选择本地回环（Loopback Address）接口。
2. 设置路由

<!--more-->

```language
- 管理员身份运行CMD.exe
- 添加路由，输入 route add 本机ip mask 255.255.255.255 网关ip
- 使用后使用route delete 本机ip mask 255.255.255.255 网关ip来删除路由
```

### 长时间抓包分为多个文件
参考 [wireshark长时间抓包分多个文件](https://www.cnblogs.com/wangqiguo/p/5068602.html)
1. 通过Wireshark界面设置
  选择Capture—Interfaces… ->选择需要截取数据帧的网络接口的Options，其中CaptureFiles为设置参数。
  缺点：长时间运行，会出现多个 “Closing file!”的对话框，软件bug。
2. 通过dumpcap.exe命令行形式截数据帧。
  Demo：dumpcap.exe -i \Device\NPF_{845F9D1E-8F0B-4991-9F9A-C55D107A046B} -w d:\000\ddd.pcap -b filesize:50000
  缺点：运行时依赖Wireshark的其他dll。
3. `dumpcap`
   `dumpcap -D` 命令可以列出可用的网络接口。
   Windows 示例：`dumpcap.exe -D`
   抓包示例：`dumpcap.exe -i \Device\NPF_{89515393-AC8F-4D23-9A03-AF35F9950E72} -w E:\000\test.pcap -C 2`

### 文件分割和合并
[Wireshark 文件分割和合并](https://blog.csdn.net/qq_20480611/article/details/50774686)
- Capinfos 查看捕获文件的基本信息。 capinfos <filename>
- editcap  分割文件
- Mergecap 合并文件

### 远程抓包
[Wireshark入门与进阶系列三之远程抓包](https://blog.csdn.net/qq_29277155/article/details/52059974?utm_medium=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-8.edu_weight&depth_1-utm_source=distribute.pc_relevant.none-task-blog-BlogCommendFromMachineLearnPai2-8.edu_weight)
Wireshark也支持remote packet capture protocol（rpcapd）协议远程抓包，只要在远程主机上安装相应的rpcapd服务

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 00:05（UTC+08:00）。