---
layout: post
title: VMware Workstation-Ubuntu虚拟机-异常关闭后网卡无法工作
date: 2023-04-08 16:42:00
categories:
- Systems
tags:
- VMware Workstation
- Ubuntu
- VMware
- Tool
- OS
---

参考https://blog.csdn.net/lhx526080338/article/details/129360808

<!--more-->
虚拟机镜像ubuntu-22.04.2-desktop-amd64.iso
虚拟机启动之后，右上角电源处的下拉菜单中没有网络设置。
`sudo lshw -c network`
结果如下：
```
  *-network DISABLED        
       description: Ethernet interface
       product: 82545EM Gigabit Ethernet Controller (Copper)
       vendor: Intel Corporation
       physical id: 1
       bus info: pci@0000:02:01.0
       logical name: ens33
       version: 01
       serial: 00:0c:29:91:4c:69
       size: 1Gbit/s
       capacity: 1Gbit/s
       width: 64 bits
       clock: 66MHz
       capabilities: pm pcix bus_master cap_list rom ethernet physical logical tp 10bt 10bt-fd 100bt 100bt-fd 1000bt-fd autonegotiation
       configuration: autonegotiation=on broadcast=yes driver=e1000 driverversion=5.19.0-38-generic duplex=full latency=0 link=no mingnt=255 multicast=yes port=twisted pair speed=1Gbit/s
       resources: irq:19 memory:fd5c0000-fd5dffff memory:fdff0000-fdffffff ioport:2000(size=64) memory:fd500000-fd50ffff

```
`-network DISABLED`，恢复方法：

```bash
sudo service NetworkManager stop
 
sudo rm  /var/lib/NetworkManager/NetworkManager.state
 
sudo gedit /etc/NetworkManager/NetworkManager.conf 
# managed=true
 
sudo service NetworkManager start

```