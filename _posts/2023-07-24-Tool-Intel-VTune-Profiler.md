---
layout: post
title: "Tool-Intel VTune Profiler"
date: 2023-07-24 18:51:00
categories: ["Tool"]
tags: ["Tool"]
---

转自 [使用Intel VTune Profiler进行性能分析及优化](https://blog.csdn.net/yaojingqingcheng/article/details/120335335)
##  初识Intel® VTune™ Profiler
Intel VTune Profiler是一个全平台的性能分析工具，可以帮助你快速发现和分析应用程序及整个系统的性能瓶颈。工具支持分析本地或远程的Windows，Linux及Android应用，这些应用可以部署在CPU，GPU，FPGA等硬件平台上。支持分析的语言包括：DPC++， C，C++，C#，Fortran，OpenCL，Python，Go，Java，汇编等。

<!--more-->
## VTune集成了多种性能分析方法
- 性能快照（Performance Snapshot）生成程序性能问题的分析总结。在总结报告里，会推荐你采用哪些具体的分析手段进行下一步的分析和优化。

- 算法（ALGORITHM）可以帮助你分析程序中所采用的算法的效率，理解程序最花时的地方在哪里。算法分析组包含了热点，异常探测，内存消耗三种分析方法。

- 热点（Hotspots）专注在一个具体的可执行文件，识别消耗cpu时钟最多的函数，可以直观的展示程序的线程信息及每个函数的调用栈信息。

- 异常探测（Anomaly Detection）可以帮助你在循环迭代中识别性能异常。

- 内存消耗（Memory Consumption）探索随时间而变化的内存消耗，并分析运行期间分配和释放的内存对象。

- 微架构（Microarchitecture）分析组包含了可以评估代码运行效率的一系列分析类型。

- 微架构探索（Microarchitecture Exploration） 有助于识别影响应用程序性能的最重要的硬件问题。在进行硬件级分析时，可以将此分析类型作为起点。

- 内存访问（Memory Access）用于识别内存访问中的一些问题，特别适用于NUMA架构中。

- 并行（Parallelism）分析组介绍了基于计算敏感的应用程序的分析类型。在进行更有针对性的分析之前，可以先用此类方法分析整体的应用程序性能。

- 线程（Threading）展示应用程序在当前cpu分布下的线程化情况，识别占用CPU时间较长的函数和可能导致cpu等待的一些非必要同步问题。

- HPC性能表征（HPC Performance Characterization）可以评估计算敏感型或含有大量浮点运算的应用程序的运算及内存使用效率，可以作为理解整个应用程序性能的起点。

- 输入和输出（I/O）基于一些硬件事件来分析设备的PCIe和I/O带宽消耗，DDIO的使用效率，程序的数据面（DPDK和SPDK）利用率。

- 硬件加速器（Accelerators）组包含了用于应用程序及系统的CPU、GPU和FPGA使用情况的分析方法。

- GPU卸载（GPU Offload）适用于使用GPU进行渲染，视频处理和计算的应用程序。它可以分析应用程序的瓶颈是受限于CPU还是GPU。

- GPU热点（GPU Compute/Media Hotspots）针对GPU绑定的应用程序，分析GPU内核执行的每一行代码，并能识别出由内存延迟或低效的内核算法造成的性能问题。

- CPU/FPGA交互（CPU/FPGA Interaction）分析每个FPGA加速器的利用率，并确定最耗时的FPGA计算任务。

- 平台分析（Platform Analysis）用于监控应用程序的系统行为和电力使用情况。

- 系统概述（System Overview）是一种基于硬件事件的采样分析，监控目标系统的通用行为，并识别限制性能的平台级因素。

- 平台采样（Platform Profiler）分析收集系统在一段时间内满负荷运行的数据，并深入了解整个系统配置、性能和行为。集合在VTune Profiler外部的命令提示符上运行，并可以在web浏览器中查看结果。

## Download

- https://www.intel.com/content/www/us/en/developer/tools/oneapi/toolkits.html#base-kit

- https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html
