---
layout: post
title: "协议-Magnet协议 磁力链接（Magnet URI scheme）"
date: 2023-02-27 02:03:00
categories: ["协议"]
tags: ["协议"]
---

# MagNet协议  磁力链接（Magnet URI scheme）

<!--more-->
一个常见的磁力链接形式为“magnet:?xt=urn:btih:”

磁力链接（Magnet URI scheme）实际就是以“magnet:?”开头的一种链接协议，与传统BT不同的是，它不再需要tracker服务器储存和解析BT种子文件。

通过不同文件内容的Hash结果生成一个纯文本的“数字指纹”，并用它来识别文件，有点类似于ISBN。任何拥有此文件的人可以生成基于文件内容的指纹。

Magnet URI表征了下载文件的特征，其值是基于对文件内容的运算而来，而非具体的文件名和文件位置。

磁力链接不需要任何“中心机构”的支持，且识别准确度极高。因此任何人都可以生成一个Magnet链接并确保通过该链接下载的文件准确无误。




特点：
- 共享优势  MagNet每次连接的源头都是不固定的，也就没法查找源头。
- 开放性和跨平台性  以普通文本存在，简单的复制粘贴即分享。
- 性能优势  整个下载网络的可靠性和稳定性提高了，每一个节点都是可以被替代的（动态变化），中间节点可以随时离线，不存在"被拔线"风险。

- 速度优势  Magnet URI下载一方面可以从Tracker服务器中获取对等用户，这点和BT获取对等用户的方式是一样的,另一方面还可以从DHT网络中获取对等用户。可以看出,磁力下载的用户连接数可以大于BT，从而获取更多的下载速度。
- 共享优势  若网络中两台计算机同时下载同一个文件，则它们的ID应该是相似的，这两台计算机就可以通过与之相似的ID找到可以与之交换数据的其它节点。所以共享方便是它的一大优势。

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
urn:(Uniform Resource Name, URN)表示资源名
btih：BitTorrent info hash，种子散列函数

应用程序定义的实验参数，必须以“x.”开头
标准还建议同类的多个参数可以在参数名称后面加上".1", ".2"等来使用，例如：
magnet:?xt.1=urn:sha1:YNCKHTQCWBTRNJIV4WNAE52SJUQCZO5C&xt.2=urn:sha1:TXGCZQTH26NL6OUQAJJPFALHG2LTGBC7
```
