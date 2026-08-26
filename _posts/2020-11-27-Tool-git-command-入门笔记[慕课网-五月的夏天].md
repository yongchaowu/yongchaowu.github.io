---
layout: post
title: "Tool-git-command-入门笔记[慕课网-五月的夏天]"
date: 2020-11-27 01:25:00
categories: ["Tool"]
tags: ["git", "Tool"]
---

November 26, 2020 11:45 PM

<!--more-->
## 1.github新建一个仓库，名称"TestGit"
```plain
create a new repository on the command line
echo "# TestGit" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/xxx/TestGit.git
git push -u origin main
```
xxx是用户名

```plain
push an existing repository from the command line
git remote add origin https://github.com/xxx/TestGit.git
git branch -M main
git push -u origin main
```

```plain
import code from another repository
You can initialize this repository with code from a Subversion, Mercurial, or TFS project.
```


## 2.指令记录
###查看版本
`git --version`

### .gitignore
`.gitignore`
该文件记录上传时忽略的文件

###初始化仓库
`git init`

###添加
`git add .`

###提交
`git commit -m xxxx`
xxxx是提交的说明内容

###log
查看所有人的改动：
`git log`

查看指定作者的改动：
`git log --author='<usetName>'`

###配置用户名和邮箱
```plain
git config --global user.name 'xxxx'
git config --global user.email 'xxxx'
```
查看配置信息：
`git config --global --list`

###查看文件状态
`git status`

###删除文件
- 手动删除
- 命令：`git rm <filename>`

###重命名文件
- 手动重命名
- 命令：`git mv <source> <dest>`

###移动文件
- 手动移动
- 命令：`git mv <source> <dest>`

###查看文件前后变化
```plain
git log --pretty=oneline <filename>
git show <id>
或：
git log -p <filename>
```

###一键还原未提交文件的改动
```plain
误操作未提交。
- git diff  然后手动修改
- git checkout -- <filename>
```

###撤销追踪[针对已提交的文件]
`git reset HEAD <filename>`

###回到上一版本或指定版本
```plain
- git reset --hard HEAD^ //回到上一个版本
- git reset --hard HEAD^^ //回到上两个版本
- git reset --hard <ID>   //回到指定ID版本
```

###回退某一个文件到上一版本
`git checkout <id> -- <file>`

### 提交远程仓库
`git push origin master`
提交到master分支

### 创建标签
```plain
- git tag xxx         //默认加在最新一次commit
- git tag             //查看
- git tag xxx <commitId>//添加到指定commit上
- git tag -d xxx      //删除标签
- git push origin xxx //推送标签
```

### 分支
```plain
git branch xxx    //创建分支
git branch        //查看分支，按字母排序
git checkout xxx  //切换分支
git branch -d xxx //删除分支，不能删除当前分支
git checkout -b xxx//创建并跳到分支
git branch -D xxx //强制删除
git merge xxx     //合并分支
合并分支冲突：
- 手动修改
- git merge -abort //保留原分支内容，忽略其他分支内容
```
### 创建并检出一个分支
`git checkout -b xxx remotes/origin/xxx`

###查看版本路线
`git log --pretty=oneline --graph`

### 拉取远程仓库
`git fetch`
### 查看仓库的分支
`git branch -av`
### 删除不想要的分支
`git push origin --delete <remoteBranch>`
其中remoteBranch是要删除的远程分支

## 3.github拓展
谷歌访问助手
插件：
- Octotree          -->左侧树形结构显示
- enhanced github   -->显示单个文件大小并可以下载
- gitzip for github -->直接下载某一个文件夹：双击需要下载的文件夹