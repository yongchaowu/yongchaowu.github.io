---
layout: post
title: "OS-Linux-Tool-可视化比较与合并工具Meld"
date: 2023-04-06 21:37:00
categories: ["OS"]
tags: ["Linux", "OS", "Tool"]
---

在Linux系统上有时会需要进行文件比较与合并，Meld能提供相关功能。

<!--more-->
[http://meldmerge.org/](http://meldmerge.org/ "Meld Visual diff and merge tool")
[http://meldmerge.org/help/](http://meldmerge.org/help/ "Meld Help")

## Meld  Visual diff and merge tool
Meld helps you compare files, directories, and version controlled projects. It provides two- and three-way comparison of both files and directories, and has support for many popular version control systems.

Meld helps you review code changes and understand patches. It might even help you to figure out what's going on in that merge you keep avoiding.

### Version control
- Supports Git, Mercurial, Bazaar and Subversion
- Check your changes, commit and push easily
- View and manage version control states
- Tool integration with e.g., git mergetool

*（图片缺失，未随博客园迁移：`./vcview.png`）*
![](http://meldmerge.org/images/vcview.png)

### File comparison
- Compare, edit and merge files using live comparison updates
- Navigate between changes and operate on change blocks
- Simple text filtering for ignoring irrelevant differences
- Three-way merge assistance with conflict handling and base version display

*（图片缺失，未随博客园迁移：`./filediff.png`）*
![](http://meldmerge.org/images/filediff.png)

### Folder comparison
- Identify and manage missing or modified files across folders
- Drill down into a file comparison for a detailed view of differences
- Ignore certain files or folders for more useful comparisons

*（图片缺失，未随博客园迁移：`./dirdiff.png`）*
![](http://meldmerge.org/images/dirdiff.png)

### Others
1. Resources
Project page
https://gitlab.gnome.org/GNOME/meld
Source view
https://gitlab.gnome.org/GNOME/meld/tree/main
Issue tracker
https://gitlab.gnome.org/GNOME/meld/issues
Discussion
https://discourse.gnome.org/tag/meld
Translations
https://l10n.gnome.org/module/meld/

2. Project details
License:	GPLv2 or later, except as noted
Primary authors:	Kai Willadsen, Stephen Kennedy, Vincent Legoll

## Developing
You can run Meld directly from your git clone, without installing:
```bash
$ git clone https://gitlab.gnome.org/GNOME/meld.git
$ bin/meld
```
在Ubuntu22.04x64映像的虚拟机中没有自带meld
```bash
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get install meld
$ meld
```
