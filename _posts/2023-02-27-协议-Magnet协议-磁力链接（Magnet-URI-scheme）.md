---
layout: post
title: 协议-Magnet协议 磁力链接（Magnet URI scheme）
date: 2023-02-27 02:03:00
categories:
- Personal
tags:
- 协议
---
一个常见的磁力链接形式为“magnet:?xt=urn:btih:”

> **版本范围：** 下面对 `btih` 的说明针对 BitTorrent v1 info-hash；BEP 9 的 `btmh` v2 形式是另一种 metadata 标识格式，不能与本文的 `btih` 说明混用。

<!--more-->

对 BEP 9，磁力链接允许客户端从对等端取得 metadata，因此无需先下载 .torrent 文件；tracker（tr）是可选的 peer 来源，没有 tracker 时客户端应使用 DHT 获取 peers。tracker 不负责储存或解析 .torrent 文件。

对本文的 btih（v1）而言，info-hash 是 .torrent 中 bencoded info 字典的 SHA-1 摘要，不是对文件字节直接计算出的 Hash。

Magnet URI 通过 info-hash 标识 torrent metadata，而不是文件名和文件位置；客户端仍需取得并校验 metadata。

仅凭 Magnet URI 不能保证下载结果准确无误；客户端必须取得并验证 metadata 和数据，且实际下载依赖可用的 peers。

特点：
- 共享优势  MagNet每次连接的源头都是不固定的，也就没法查找源头。
- 开放性和跨平台性  以普通文本存在，简单的复制粘贴即分享。
- 性能优势  整个下载网络的可靠性和稳定性提高了，每一个节点都是可以被替代的（动态变化），中间节点可以随时离线，不存在"被拔线"风险。

- 速度优势  Magnet URI下载一方面可以从Tracker服务器中获取对等用户，这点和BT获取对等用户的方式是一样的,另一方面还可以从DHT网络中获取对等用户。可以看出,磁力下载的用户连接数可以大于BT，从而获取更多的下载速度。
- 共享优势  同一 swarm 的下载者共享 info-hash；每个下载者在开始新下载时生成自己的随机 peer ID。

```txt
//例子
magnet:?xt=urn:btih:4D9FA761D69964B00DF0B3B0C9C1F968EA6C47D0&xt=urn:ed2k:7655dbacff9395e579c4c9cb49cbec0e&dn=bbb_sunflower_2160p_30fps_stereo_abl.mp4&tr=udp%3a%2f%2ftracker.openbittorrent.com%3a80%2fannounce&tr=udp%3a%2f%2ftracker.publicbt.com%3a80%2fannounce&ws=http%3a%2f%2fdistribution.bbb3d.renderfarming.net%2fvideo%2fmp4%2fbbb_sunflower_2160p_30fps_stereo_abl.mp4
虽然这个链接指向一个特定文件，但是客户端应用程序仍然必须进行搜索来确定哪里。
在标准的草稿中其他参数的定义如下：
magnet：协议名。
xt：exact topic的缩写，包含文件哈希值的统一资源名称。BTIH（BitTorrent Info Hash）表示哈希方法名，这里还可以使用ED2K，AICH，SHA1和MD5等。这个值是文件的标识符，是不可缺少的。
dn：display name的缩写，表示向用户显示的文件名。这一项是选填的。
tr：tracker的缩写，表示tracker服务器的地址。这一项也是选填的。
ws:webseed的缩写，表示网络种子。
urn:(Uniform Resource Name, URN 表示资源名
btih：BitTorrent info hash，种子散列函数

应用程序定义的实验参数，必须以“x.”开头
标准还建议同类的多个参数可以在参数名称后面加上".1", ".2"等来使用，例如：
magnet:?xt.1=urn:sha1:YNCKHTQCWBTRNJIV4WNAE52SJUQCZO5C&xt.2=urn:sha1:TXGCZQTH26NL6OUQAJJPFALHG2LTGBC7
```

本文的协议说明依据 BEP 9（版本 `cfd7cd53addbea7e87363ae1a52e2e4b397df3a9`，Last-Modified 2017-03-26）和 BEP 3（版本 `0e08ddf84d8d3bf101cdf897fc312f2774588c9e`，Last-Modified 2017-02-04）。参考：[BEP 9](https://www.bittorrent.org/beps/bep_0009.html) 和 [BEP 3](https://www.bittorrent.org/beps/bep_0003.html)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 03:56（UTC+08:00）。
