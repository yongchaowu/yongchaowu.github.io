---
layout: post
title: Ubuntu2204 install input method-Sougoupinyin
date: 2026-05-31 11:57:00
categories:
- Systems
tags:
- OS
- Ubuntu
---

- 背景：基于Ubuntu22.04 安装 拼音输入法
- 方案：首选 搜狗拼音输入法； 次选 Google拼音输入法
- 关键：首先要完整安装 Fcitx 4 输入法框架（而非系统默认的 IBus），其次要补充缺失的 Qt 依赖，最后必须配置好系统的环境变量。

<!--more-->
## 步骤
1. 第一步：清理旧环境 (可选但推荐)

为了避免与系统自带的输入法框架（IBus）发生冲突，建议先将其移除。打开终端，执行以下命令：
```bash
# 移除系统自带的ibus输入法框架
sudo apt purge ibus
# 清理并更新软件包列表
sudo apt autoremove
sudo apt update
```


2. 第二步：安装 Fcitx 4 及核心依赖

搜狗输入法基于 Fcitx 4 开发，需要安装它以及必要的 Qt 依赖库。

```bash
# 1. 安装 Fcitx 4 框架
sudo apt install fcitx fcitx-config-gtk fcitx-frontend-qt5

# 2. 安装搜狗拼音所必需的 Qt 库 (这是解决“打不出字”的关键)
sudo apt install libqt5qml5 libqt5quick5 libqt5quickwidgets5 qml-module-qtquick2
sudo apt install libgsettings-qt1
```

3. 第三步：配置环境变量

设置vscode启动别名，附带输入法环境变量

`alias code='GTK_IM_MODULE=fcitx QT_IM_MODULE=fcitx XMODIFIERS=@im=fcitx code --ozone-platform=x11'`

4. 第四步：安装搜狗输入法

从搜狗输入法Linux官网下载最新版的 .deb 安装包。

在终端中，通过 cd 命令进入下载文件夹，然后执行安装：

```bash
# 将文件名替换为已下载的版本
sudo dpkg -i sogoupinyin_4.2.1.145_amd64.deb

# 备用方案 Google PinYin
#sudo apt install fcitx-googlepinyin
```

5. 第五步：设置系统默认输入法并重启

- 打开 系统设置 (Settings) -> 区域与语言 (Region & Language) -> 管理已安装的语言 (Manage Installed Languages)。

- 在弹窗中，将 “键盘输入法系统” (Keyboard input method system) 从 IBus 改为 fcitx。

- 点击“应用到整个系统”(Apply System-Wide)，然后 重启电脑。

6. 第六步：添加搜狗输入法

- 重启后，点击桌面右上角的 键盘图标，选择 “配置当前输入法” (Configure Current Input Method)。

- 在打开的 Fcitx Configuration 窗口中，点击左下角的 + 号。

- 在弹出的对话框中，取消勾选“只显示当前语言” (Only Show Current Language)，然后在搜索框输入 sogou 找到 “搜狗拼音”，点击“确定”即可。