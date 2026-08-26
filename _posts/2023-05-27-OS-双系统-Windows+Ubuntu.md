---
layout: post
title: 双系统-Windows+Ubuntu
date: 2023-05-27 11:20:00
categories:
- Systems
tags:
- OS
- Ubuntu
---

在已有的Windows10上安装Ubuntu。

<!--more-->
## Ubuntu Image
>https://ubuntu.com/download

Ubuntu 22.04.2 LTS
ubuntu-22.04.2-desktop-amd64.iso

## Ubuntu Install
>https://ubuntu.com/tutorials/install-ubuntu-desktop#1-overview

- A laptop or PC with at least 25GB of storage space.
- A flash drive (12GB or above recommended).

### Create a Bootable USB stick
>https://etcher.balena.io/
>https://etcher.balena.io/#download-etcher

Flash OS images to SD cards & USB drives, safely and easily.

### Boot from USB flash drive
`F12` is the most common key for bringing up your system’s boot menu, but Escape, `F2` and `F10` are common alternatives. If you’re unsure, look for a brief message when your system starts – this will often inform you of which key to press to bring up the boot menu.

### Update
update Ubuntu using the terminal.

Press `CTRL+ALT+T` to bring up a Terminal window (or click the terminal icon in the sidebar).

Type in:`sudo apt update`
You will be prompted to enter your login password.
This will check for updates and tell you if there are any that need applying. 

To apply any updates, type:`sudo apt upgrade`
Type `Y`, then press `ENTER` to confirm to finish the update process.

## 修复启动引导
> https://neosmart.net/EasyBCD/
> https://neosmart.net/Download/Register

EasyBCD supercharges your Windows PC, allowing you to dual-boot to your heart's content.

### 添加新条目
注意选择的驱动器，需要选择Ubuntu系统安装后默认的第二个分区，大小在500MB+[EFI系统分区]

```
Linux/BSD
GRUB2
Ubuntu22.04
驱动器：选默认分区2，大小500MB
```