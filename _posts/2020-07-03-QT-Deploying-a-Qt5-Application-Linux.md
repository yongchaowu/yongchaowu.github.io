---
layout: post
title: "QT-Deploying a Qt5 Application Linux"
date: 2020-07-03 23:22:00
categories: ["QT"]
tags: ["cqtdeployer", "linuxdeployqt", "Deploying", "QT", "IDE"]
---

July 3, 2020 11:11 PM
参考：
[Deploying a Qt5 Application Linux](https://wiki.qt.io/Deploying_a_Qt5_Application_Linux)
[AppImage](https://appimage.org/)

<!--more-->
##Original text
Multiple Ways to deploy a Qt 5 application for desktop Linux systems:
- One is to create native distribution packages that have dependencies on the distribution's Qt installation.
- Another is to create a self-contained application bundle that contains the application and everything the application needs to run that cannot be expected to be present on each target system, and still another is to create an installer for it.

## Tool&Code
- linuxdeployqt:A [deployment tool](https://github.com/probonopd/linuxdeployqt) is available that automates the procedures described here and provide an [AppImage](https://appimage.org/).

- cqtdeployer:If you want one utility for cross platform deploy use a [cqtdeployer](https://github.com/QuasarApp/CQtDeployer) tool for deploy qt on linux and windows.