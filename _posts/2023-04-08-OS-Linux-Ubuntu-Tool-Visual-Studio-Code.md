---
layout: post
title: "OS-Linux-Ubuntu-Tool-Visual Studio Code"
date: 2023-04-08 02:02:00
categories: ["OS"]
tags: ["OS", "C++", "Tool", "Visual Studio Code", "Debug"]
---

在Ubuntu上，可以使用Visual Studio Code进行代码调试。
Visual Studio Code官网如下：[https://code.visualstudio.com/](https://code.visualstudio.com/ "vscode download address")
对于Ubuntu，提供deb包。
下载deb包，在同级路径中打开终端，使用以下指令安装：`sudo dpkg -i code_1.77.1-1680651665_amd64.deb`

<!--more-->
Ubuntu的图形界面中Show Applications翻页可以看到安装好的vscode图标。
添加收藏->鼠标右键vscode图标，提示可以添加到收藏，能快速启动VS Code。

## Visual Studio Code Extension
1. C/C++ v1.14.5
2. C/C++ Extension Pack
3. C/C++ Themes
4. Python v2023.6.0
5. ...

## Visual Studio Code 调试C++
[https://code.visualstudio.com/docs](https://code.visualstudio.com/docs "vscode docs")

1. `sudo apt-get install g++ gcc cmake`
2. `g++ -v` `gcc -v` `cmake -version`
3. 打开vscode，创建main.cpp，写一个Demo(main.cpp)。
4. F5(Start Debugging)即可。
- 因为是第一次Debug，先选择调试器，生成相对应的配置文件夹`.vscode`，以及json格式配置文件，如tasks.json。
同时生成输出文件如main。
- 可以先添加配置文件，再Debug。
	- 菜单栏->Run->Add Configurations
	- 左侧->RUN AND DEBUG

### Visual Studio Code .vscode 配置文件
1. launch.json	可执行文件生成位置等
2. tasks.json	编译链接相关参数等
3. c_cpp_properties.json  其中：includePath包含第三方头文件
4. ...


## Visual Studio Code Docs
- [https://code.visualstudio.com/docs/editor/debugging](https://code.visualstudio.com/docs/editor/debugging "vscode debug")
- [https://code.visualstudio.com/docs/languages/cpp](https://code.visualstudio.com/docs/languages/cpp "vscode language cpp")
- [https://code.visualstudio.com/docs/cpp/introvideos-cpp](https://code.visualstudio.com/docs/cpp/introvideos-cpp)


----------

**2023/4/8 12:33:55 在后期查阅Visual Studio Code的官网文档时，发现本文的内容在[https://code.visualstudio.com/docs/cpp/config-linux](https://code.visualstudio.com/docs/cpp/config-linux "Using C++ on Linux in VS Code")有较为完整的总结。**

<iframe 
  name="visualstudio cpp config-linux"
  src="https://code.visualstudio.com/docs/cpp/config-linux/" 
  width="630"
  height="355" 
  frameborder="0"
  scrolling="no">
</iframe>