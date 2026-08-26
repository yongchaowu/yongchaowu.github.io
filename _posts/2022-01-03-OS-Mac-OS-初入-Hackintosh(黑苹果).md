---
layout: post
title: "OS-Mac OS 初入-Hackintosh(黑苹果)"
date: 2022-01-03 01:18:00
categories: ["OS"]
tags: ["OS", "macOS"]
---

## 安装方式

<!--more-->
苹果系统有几种安装方式：

1、macOS Monterey.app直接双击安装；

2、InstallESD.Dmg安装，一般用于U盘制作启动引导盘；

3、InstallAssistant.pkg双击安装。

这3种都是官方的原版安装

macOS Monterey系统下载地址



4.虚拟机镜像



## 版本概况

参考 https://www.apple114.com/pages/macos/

| macOS代号             | macOS版本 | 版号   | MAS/零售原版                                      | 可引导版本                                        | 苹果M芯片版                                                  | 组合更新                                                     | VMware/ESXi镜像                                      | 发布时间   | 备注          |
| --------------------- | --------- | ------ | ------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------------------------------------------- | ---------- | ------------- |
| macOS Monterey        | 12.1      | 21C52  | [原版镜像](https://www.apple114.com/threads/342/) | [引导镜像](https://www.apple114.com/threads/343/) | [IPSW镜像](https://updates.cdn-apple.com/2021FCSWinter/fullrestores/002-42433/F3F6D5CD-67FE-449C-9212-F7409808B6C4/UniversalMac_12.1_21C52_Restore.ipsw) | [-](https://www.apple114.com/pages/macos/#)                  | [CDR/ISO格式](https://www.apple114.com/threads/344/) | 2021-12-13 | 最新正式版    |
| macOS Big Sur         | 11.6.0    | 20G165 | [原版镜像](https://www.apple114.com/threads/240/) | [引导镜像](https://www.apple114.com/threads/241/) | [IPSW镜像](https://updates.cdn-apple.com/2021FallFCS/fullrestores/071-97388/C361BF5E-0E01-47E5-8D30-5990BC3C9E29/UniversalMac_11.6_20G165_Restore.ipsw) | [-](https://www.apple114.com/pages/macos/#)                  | [CDR/ISO格式](https://www.apple114.com/threads/242/) | 2021-09-14 |               |
| macOS Catalina        | 10.15.7   | 19H2   | [原版镜像](https://www.apple114.com/threads/28/)  | [引导镜像](https://www.apple114.com/threads/35/)  | N/A                                                          | [Combo Update](https://support.apple.com/kb/DL2052?locale=zh_CN) | [CDR/ISO格式](https://www.apple114.com/threads/36/)  | 2020-09-24 |               |
| macOS Mojave          | 10.14.6   | 18G103 | [原版镜像](https://www.apple114.com/threads/27/)  | [引导镜像](https://www.apple114.com/threads/34/)  | N/A                                                          | [Combo Update](https://updates.cdn-apple.com/2019/macos/041-88926-20190719-e6bdfc65-d22b-46a9-b8c8-3cd39c0bc675/macOSUpdCombo10.14.6.dmg) | [CDR/ISO格式](https://www.apple114.com/threads/36/)  | 2019-07-22 |               |
| macOS High Sierra     | 10.13.6   | 17G66  | [原版镜像](https://www.apple114.com/threads/26/)  | [引导镜像](https://www.apple114.com/threads/33/)  | N/A                                                          | [Combo Update](https://updates.cdn-apple.com/2019/cert/041-91759-20191011-01650bca-c2ef-42de-b8a8-63c3fd7d55bc/macOSUpdCombo10.13.6.dmg) | [CDR/ISO格式](https://www.apple114.com/threads/36/)  | 2018-07-13 | 17G66         |
| macOS Sierra          | 10.12.6   | 16G29  | [原版镜像](https://www.apple114.com/threads/25/)  | [引导镜像](https://www.apple114.com/threads/32/)  | N/A                                                          | [Combo Update](http://support.apple.com/downloads/DL1931/en_US/macosupdcombo10.12.6.dmg) | [CDR/ISO格式](https://www.apple114.com/threads/36/)  | 2017-07-19 | -             |
| OS X El Capitan       | 10.11.6   | 15G31  | [原版镜像](https://www.apple114.com/threads/24/)  | [引导镜像](https://www.apple114.com/threads/31/)  | N/A                                                          | [Combo Update](http://support.apple.com/downloads/DL1885/zh_CN/osxupdcombo10.11.6.dmg) | [CDR/ISO格式](https://www.apple114.com/threads/36/)  | 2016-07-18 | -             |
| OS X Yosemite         | 10.10.5   | 14F27  | [原版镜像](https://www.apple114.com/threads/23/)  | [引导镜像](https://www.apple114.com/threads/30/)  | N/A                                                          | [Combo Update](http://support.apple.com/downloads/DL1832/zh_CN/osxupdcombo10.10.5.dmg) | [CDR/ISO格式](https://www.apple114.com/threads/36/)  | 2015-08-13 | -             |
| OS X Mavericks        | 10.9.5    | 13F34  | [原版镜像](https://www.apple114.com/threads/22/)  | [引导镜像](https://www.apple114.com/threads/29/)  | N/A                                                          | [Combo Update](http://support.apple.com/downloads/DL1760/zh_CN/OSXUpdCombo10.9.5.dmg) | [CDR/ISO格式](https://www.apple114.com/threads/36/)  | 2014-09-17 | -             |
| OS X Mountain Lion    | 10.8.5    | 12F37  | [原版镜像](https://www.apple114.com/threads/21/)  | 不区分                                            | N/A                                                          | [Combo Update](http://support.apple.com/downloads/DL1676/zh_CN/OSXUpdCombo10.8.5.dmg) | -                                                    | 2013-09-12 | 12F45/12F2029 |
| OS X Lion             | 10.7.5    | 11G56  | [原版镜像](https://www.apple114.com/threads/20/)  | 不区分                                            | N/A                                                          | [Combo Update](http://support.apple.com/downloads/DL1582/zh_CN/MacOSXUpdCombo10.7.5.dmg) | -                                                    | 2012-09-19 | 11G63         |
| Mac OS X Snow Leopard | 10.6.8    | 10K540 | [原版镜像](https://www.apple114.com/threads/19/)  | 不区分                                            | N/A                                                          | [Combo Update](http://support.apple.com/downloads/DL1399/zh_CN/MacOSXUpdCombo10.6.8.dmg) | -                                                    | 2011-07-15 | 10K549        |
| Mac OS X Leopard      | 10.5.8    | 9L30   | [原版镜像](https://www.apple114.com/threads/18/)  | 不区分                                            | N/A                                                          | [Combo Update](http://support.apple.com/downloads/DL866/zh_CN/MacOSXUpdCombo10.5.8.dmg) | -                                                    | 2009-08-12 | 9L34          |
| Mac OS X Tiger        | 10.4.11   | 8S165  | [原版镜像](https://www.apple114.com/threads/5/)   | 不区分                                            | N/A                                                          | [Combo Update](https://download.info.apple.com/Mac_OS_X/061-3461.20071114.8Uy45/MacOSXUpdCombo10.4.11PPC.dmg) | -                                                    | 2007-11-14 | 仅支持PPC     |



## 参考资料&说明(适用于全新引导安装)

参考 https://www.apple114.com/pages/macos/

原版镜像和可引导区别

- 原版镜像:Mac App Store 官方原版镜像，可以用于升级安装，也可以在macOS上制作为U盘引导格式后全新安装系统。

- 引导镜像:采用MAS原版镜像, 再用Apple官方的方法制作为U盘引导格式后打包，可以方便到导入到U盘里面后全新安装系统, 并且支持在win或者macOS里面导入.

总结:跨版本升级请下载原版镜像，如需要全新格式化硬盘安装系统，下载可引导镜像更方便，因为可引导镜像支持在windows或macOS系统下导入到U盘。



10.5.8-10.8.5 可以直接用原版镜像文件(其实也是可引导镜像)导入到U盘后全新引导安装，导入方法请看:http://www.apple114.com/threads/40/

10.9.5或以上如果下载原版系统，需要用Apple官方指南导入到U盘后全新引导安装，制作方法请看:https://www.apple114.com/threads/41/

可引导版本支持在Windows或macOS系统导入到U盘，导入方法请看[在Windows系统导入 ](http://www.apple114.com/threads/37/)----[在macOS系统导入](http://www.apple114.com/threads/40/)

macOS系统重装恢复请看这里:http://www.apple114.com/threads/38/





## U盘启动盘制作

### Windows

#### 软件

macOS镜像

| **macOS 12 正式版下载**                                      | **Ver** | **Build** | **App** | **有效** | **日期** |
| ------------------------------------------------------------ | ------- | --------- | ------- | -------- | -------- |
| InstallAssistant.pkg | 12.1.0  | 21C52     | 17.1.04 | 是       | 12/13/21 |
| InstallAssistant.pkg | 12.0.1  | 21A559    | 17.0.07 | 是       | 10/25/21 |

虚拟机及相关unlocker：

 	1. VMware® Workstation 16 Pro 16.2.1 build-18811642
 	2. [unlocker-3.0.8](https://github.com/DrDonk/unlocker)  给虚拟机打上解锁补丁，执行完成后会自动关闭，然后启动虚拟机创建镜像，就会出现苹果系统的选择

创建U盘镜像，转换dmg格式文件到U盘：

1. [Etcher](https://www.balena.io/etcher/)   https://www.balena.io/etcher/
2. [TransMac(Mac系统启动盘制作工具)v14.3](http://www.xitongcheng.com/soft/qdrj_xiazai_3409.html)

#### VMWare虚拟机使用U盘安装系统 （失败，与使用的镜像有关）

1. 虚拟机设置-->>硬件-->>添加硬盘-->>磁盘类型同推荐-->>使用物理磁盘-->>设备选择U盘，使用情况为单个分区(第二个分区是指定的安装盘)-->>保存我们的硬盘到本地即可完成创建

2. 遇到的错误

   作者：笑笑爸比
   链接：https://www.jianshu.com/p/dea92fbf00a4
   来源：简书
   著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

   - 出现vcpu-0:VERIFY错误时，记事本编辑vmx文件，在smc.present = "TRUE"后面添加smc.version = 0保存，重新开启虚拟机即可。
   - 出现"vmci.sys版本不正确"错误提示时，记事本编辑vmx文件，把vmci0.present = "TRUE"改为vmci0.present = "FALSE"。

3. UEFI安装LINUX出现停在skip startup.nsh的问题(**卡住了，我放弃了，选用cdr格式**)

   启动界面停在

   ```
   > Press ESC in 5 seconds to skip startup.nsh, any other key to continue.
   > Shell>_
   ```

   解决办法：

   - 进入BIOS将硬盘设为第一启动设备。
   - 或者按照以下方式手动写入启动设备：

   可以使用 ls 命令列出文件目录，输入 fs0: 进入目录fs0

   ```
   Shell> fs0:
   ```

   编辑文件 startup.nsh

   ```
   FS0> edit startup.nsh
   ```

   向文件中写入以下内容（例如： \EFI\ubuntu\grubx64.efi ）

   ```
   \EFI\<小写系统名，如：ubuntu>\grubx64.efi
   ```

   按下Ctrl+S再按下Enter键保存文件，然后按下Ctrl+Q再按下Enter退出编辑

   ```
   <ctrl+s 保存>
   <ctrl+q 退出编辑>
   ```

   输入 `reset` 命令

   ```
   FS0> reset
   ```

   即可正常进入系统。

4. 

##### 参考

- https://www.cnblogs.com/yong001/p/15691342.html

- https://www.jianshu.com/p/dea92fbf00a4



---



## VMWare虚拟机使用.cdr格式安装（验证成功，macOS Mojave 10.14 18A391）

macOS Mojave 10.14 18A391 Lazy Installer.cdr

- magnet:?xt=urn:btih:2BD644783657D3D4DB3E25C15BB0FBE0A5C9189F

实用工具->磁盘工具->VMware Virtual SATA Hard Drive Media -> 抹除 ->磁盘名称自定义，如workspace

安装macOS的VMWare Tools

​		安装darwin `macOS 10.14`即`Mojave`匹配，链接: https://pan.baidu.com/s/104Nr_an8_xzG6JQ_AXFfcQ?pwd=jrww 提取码: jrww 

​		按照提示设置系统偏好设置，安装后重新启动，设置安全性与隐私->辅助功能->解锁 vmware-tools-daemon