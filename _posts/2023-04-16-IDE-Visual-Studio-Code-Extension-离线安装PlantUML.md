---
layout: post
title: "IDE-Visual Studio Code-Extension-离线安装PlantUML"
date: 2023-04-16 22:47:00
categories: ["IDE"]
tags: ["Visual Studio Code", "IDE"]
---

>[https://www.hd2y.net/archives/plantuml-installation-and-use](http://web.archive.org/web/20260416181302/https://www.hd2y.net/archives/plantuml-installation-and-use)

<!--more-->
PlantUML + Graphviz + Java

## PlantUML Extension
1. [vscode marketplace](https://marketplace.visualstudio.com/vscode "Visual Studio Code Marketplace" ) *注意路径，我第一次下载的vs的插件。*
https://marketplace.visualstudio.com/vscode

2. http://web.archive.org/web/20260619130217/https://marketplace.visualstudio.com/items?itemName=jebbs.plantuml
3. 安装插件
- 搜索vscode的位置：`whereis code`

```
yongchao@yongchao-virtual-machine:~/Desktop$ whereis code
code: /usr/bin/code /usr/share/code

```
两个目录`code: /usr/bin/code  /usr/share/code`
左边为链接code可执行文件，右边的才是目录。
- 然后
`cp jebbs.plantuml-2.17.5.vsix /usr/share/code/bin`
`cd /usr/share/code/bin`
`code --install-extension jebbs.plantuml-2.17.5.vsix`
或者vscode的插件管理右上角...有从VSIX安装

```
yongchao@yongchao-virtual-machine:/usr/share/code/bin$ code --install-extension jebbs.plantuml-2.17.5.vsix 
Installing extensions...
(node:32844) [DEP0005] DeprecationWarning: Buffer() is deprecated due to security and usability issues. Please use the Buffer.alloc(), Buffer.allocUnsafe(), or Buffer.from() methods instead.
(Use `code --trace-deprecation ...` to show where the warning was created)
Extension 'jebbs.plantuml-2.17.5.vsix' was successfully installed.

```
### Features
- Preview Diagram, Press Alt + D to start PlantUML preview (option + D on MacOS).
	- Auto update.
	- Zoom & scroll support.
	- Multi-Page Diagram support.
	- Instant preview, if diagram's been exported.
	- From local or server.
	- Snap to Border
- Export Diagrams
	- At cursor, in current file, in whole workspace, in workspace selected.
	- Concurrent export.
	- Generate URLs.
	- Multi-Page Diagram support.
	- From local or server.
	- Image map (cmapx) support.
- Editing Supports
	- Format PlantUML code. (Deprecated)
	- All type syntax highlight.
	- All type snippets.
	- Basic auto completion & macro signature support
	- Symbol List support.
- Others
	- Multi-root Workspace Support.
	- MarkDown integrating support. View Demo
	- Extracting source from images support.

### Supported Formats
*.wsd, *.pu, *.puml, *.plantuml, *.iuml

### Requirements for Local render
It's necessary to have following installed:

Java : Platform for PlantUML running.
Graphviz : PlantUML requires it to calculate positions in diagram.

## Graphviz Extension
### Graphviz (dot) language 
support for Visual Studio Code
[http://web.archive.org/web/20230927192452/https://marketplace.visualstudio.com/items?itemName=joaompinto.vscode-graphviz](http://web.archive.org/web/20230927192452/https://marketplace.visualstudio.com/items?itemName=joaompinto.vscode-graphviz)
joaompinto.vscode-graphviz-0.0.6.vsix

### Graphviz Interactive Preview
[https://marketplace.visualstudio.com/items?itemName=tintinweb.graphviz-interactive-preview](http://web.archive.org/web/20260417053736/https://marketplace.visualstudio.com/items?itemName=tintinweb.graphviz-interactive-preview)
tintinweb.graphviz-interactive-preview-0.3.5.vsix

Language Features 
- Graphviz/Dot Language Support / Syntax Highlighting and Snippets (thanks @joaompinto)
- AutoCompletion
- Rename Symbols
- Find References of node IDs
- Color selection via Color decoration
- Hover information for settings
- Shows syntax errors (only available when the preview of the document is active)
 
#### How to preview
Open a Graphviz/Dot file in the active editor and use either of the following methods to render the preview:

(a) open the command prompt (cmd+shift+p) and type > graphviz preview
(b) click the image button in the editor title
(c) from the editor window's context menu, select Preview Graphviz / Dot (beside)
## 导出
`ctrl+shift+p`打开首选项，输入：`PlantUML:导出当前图表`；选择导出格式png；导出即可。

## java
jdk/jre:[https://www.oracle.com/java/technologies/downloads/#java8](https://www.oracle.com/java/technologies/downloads/#java8)
```bash
sudo mkdir /usr/local/java
sudo cp jdk-8u361-linux-x64.tar.gz /usr/local/java
cd /usr/local/java
sudo tar -zxvf jdk-8u361-linux-x64.tar.gz
sudo gedit ~/.bashrc

##java 8 jdk-8u361-linux-x64.tar.gz /usr/local/java
export JAVA_HOME=/usr/local/java/jdk1.8.0_361 
export JAVA_BIN=$JAVA_HOME/bin 
export JAVA_LIB=$JAVA_HOME/lib 
export CLASSPATH=.:$JAVA_LIB/tools.jar:$JAVA_LIB/dt.jar 
export PATH=$JAVA_BIN:$PATH

source ~/.bashrc

java -version
java version "1.8.0_361"
Java(TM) SE Runtime Environment (build 1.8.0_361-b09)
Java HotSpot(TM) 64-Bit Server VM (build 25.361-b09, mixed mode)

```

## Others
### Q1
```
Dot Executable: /usr/bin/dot
File does not exist
Cannot find Graphviz. You should try

@startuml
testdot
@enduml

or

java -jar plantuml.jar -testdot
```

### Q2
```
Error: File does not exist
Error: only sequence diagrams will be generated
```

### Resolved Q1&Q2

安装包&源码

- [https://graphviz.gitlab.io/download/](https://graphviz.gitlab.io/download/)
`sudo apt install graphviz`

- [https://graphviz.gitlab.io/download/source/](https://graphviz.gitlab.io/download/source/)

```bash
./configure
make
sudo make install

./configure --help

```