---
layout: post
title: "OS-Windows-计算机内存型号配置查看"
date: 2023-04-05 08:07:00
categories: ["OS"]
tags: ["Tool", "Windows", "OS"]
---

近来想给计算机配置内存，在网上百度到了如何查看型号和配置的方法,整理如下。
1.直接在计算机底部查看标识。
2.win+R --> cmd -->systeminfo--->结果输出在当前窗口中。
3.win+R --> cmd -->dxdiag--->弹出DirectX诊断工具窗口。
4.cpu-z https://www.cpuid.com/softwares/cpu-z.html#install
5.其他软件，如鲁大师、驱动人生等。**（未验证）**

<!--more-->
## dxdiag信息
dxdiag信息可以保存为txt。以下是其中关于system information。
```txt
------------------
System Information
------------------
      Time of this report: 4/5/2023, 06:59:23
             Machine name: W-PC
               Machine Id: {65B6DF9B-3AC6-4EFC-85C4-4739823BB7E9}
         Operating System: Windows 10 专业版 64-bit (10.0, Build 19045) (19041.vb_release.191206-1406)
                 Language: Chinese (Simplified) (Regional Setting: Chinese (Simplified))
      System Manufacturer: TOSHIBA
             System Model: Satellite C805
                     BIOS: InsydeH2O Version 03.72.016.50 (type: BIOS)
                Processor: Intel(R) Core(TM) i5-3210M CPU @ 2.50GHz (4 CPUs), ~2.5GHz
                   Memory: 6144MB RAM
      Available OS Memory: 6114MB RAM
                Page File: 7211MB used, 5047MB available
              Windows Dir: C:\WINDOWS
          DirectX Version: DirectX 12
      DX Setup Parameters: Not found
         User DPI Setting: 96 DPI (100 percent)
       System DPI Setting: 96 DPI (100 percent)
          DWM DPI Scaling: Disabled
                 Miracast: Not Available
Microsoft Graphics Hybrid: Not Supported
 DirectX Database Version: 1.0.8
           DxDiag Version: 10.00.19041.2075 64bit Unicode
-------------

```

*（图片缺失，未随博客园迁移：`./dxdiag_systeminfo.png`）*
![dxdiag_systeminfo](https://images.cnblogs.com/cnblogs_com/yongchao/2296107/o_230404234557_dxdiag_systeminfo.png)

## cpu-z
*（图片缺失，未随博客园迁移：`./cpu-z_cpuinfo.png`）*
![cpu-z_cpuinfo](https://images.cnblogs.com/cnblogs_com/yongchao/2296107/o_230404235523_cpu-z_cpuinfo.png)

*（图片缺失，未随博客园迁移：`./cpu-z_mainboardinfo.png`）*
![cpu-z_mainboardinfo](https://images.cnblogs.com/cnblogs_com/yongchao/2296107/o_230404235603_cpu-z_mainboardinfo.png)

*（图片缺失，未随博客园迁移：`./cpu-z_memoryinfo.png`）*
![cpu-z_memoryinfo](https://images.cnblogs.com/cnblogs_com/yongchao/2296107/o_230404235625_cpu-z_memoryinfo.png)

*（图片缺失，未随博客园迁移：`./cpu-z_SPD_slot1.png`）*
![cpu-z_SPD_slot1](https://images.cnblogs.com/cnblogs_com/yongchao/2296107/o_230404235641_cpu-z_SPD_slot1.png)

*（图片缺失，未随博客园迁移：`./cpu-z_SPD_slot2.png`）*
![cpu-z_SPD_slot2](https://images.cnblogs.com/cnblogs_com/yongchao/2296107/o_230404235655_cpu-z_SPD_slot2.png)

*（图片缺失，未随博客园迁移：`./cpu-z_graphicscard.png`）*
![cpu-z_graphicscard](https://images.cnblogs.com/cnblogs_com/yongchao/2296107/o_230404235544_cpu-z_graphicscard.png)
