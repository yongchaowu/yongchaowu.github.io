---
layout: post
title: "Tool-SVN（Apache Subversion）"
date: 2023-02-27 10:08:00
categories: ["Tool"]
tags: ["Tool"]
---

# Tool-SVN
2023/2/27 10:07:15 
转自[https://www.runoob.com/svn/svn-tutorial.html](https://www.runoob.com/svn/svn-tutorial.html "菜鸟教程-SVN教程")

<!--more-->
Apache Subversion 通常被缩写成 SVN，是一个开放源代码的版本控制系统，Subversion 在 2000 年由 CollabNet Inc 开发，现在发展成为 Apache 软件基金会的一个项目，同样是一个丰富的开发者和用户社区的一部分。

SVN相对于的RCS、CVS，采用了分支管理系统，它的设计目标就是取代CVS。互联网上免费的版本控制服务多基于Subversion。

相关链接
SVN 官网：https://subversion.apache.org/
Github SVN 源码：https://github.com/apache/subversion

----------

## SVN的相关概念

- repository（源代码库）:源代码统一存放的地方
- Checkout（提取）:当你手上没有源代码的时候，你需要从repository checkout一份
- Commit（提交）:当你已经修改了代码，你就需要Commit到repository
- Update (更新):当你已经 checkout 了一份源代码， update 一下你就可以和Repository上的源代码同步，你手上的代码就会有最新的变更

----------

## SVN的主要功能

（1）目录版本控制
CVS 只能跟踪单个文件的历史, 不过 Subversion 实作了一个 "虚拟" 的版本控管文件系统, 能够依时间跟踪整个目录的变动。 目录和文件都能进行版本控制。

（2）真实的版本历史
自从 CVS 限制了文件的版本记录，CVS 并不支持那些可能发生在文件上，但会影响所在目录内容的操作，如同复制和重命名。除此之外，在 CVS 里你不能用拥有同样名字但是没有继承老版本历史或者根本没有关系的文件替换一个已经纳入系统的文件。在 Subversion 中，你可以增加（add）、删除（delete）、复制（copy）和重命名（rename），无论是文件还是目录。所有的新加的文件都从一个新的、干净的版本开始。

（3）自动提交
一个提交动作，不是全部更新到了档案库中，就是不完全更新。这允许开发人员以逻辑区间建立并提交变动，以防止当部分提交成功时出现的问题。

（4）纳入版本控管的元数据
每一个文件与目录都附有一組属性关键字并和属性值相关联。你可以创建, 并儲存任何你想要的Key/Value对。 属性是随着时间来作版本控管的,就像文件內容一样。

（5）选择不同的网络层
Subversion 有抽象的档案库存取概念, 可以让人很容易地实作新的网络机制。 Subversion 可以作为一个扩展模块嵌入到 Apache HTTP 服务器中。这个为 Subversion 提供了非常先进的稳定性和协同工作能力，除此之外还提供了许多重要功能: 举例来说, 有身份认证, 授权, 在线压缩, 以及文件库浏览等等。还有一个轻量级的独立 Subversion 服务器， 使用的是自定义的通信协议, 可以很容易地通过 ssh 以 tunnel 方式使用。

（6）一致的数据处理方式
Subversion 使用二进制差异算法来异表示文件的差异, 它对文字(人类可理解的)与二进制文件(人类无法理解的) 两类的文件都一视同仁。 这两类的文件都同样地以压缩形式储存在档案库中, 而且文件差异是以两个方向在网络上传输的。

（7）有效的分支(branch)与标签(tag)
在分支与标签上的消耗并不必一定要与项目大小成正比。 Subversion 建立分支与标签的方法, 就只是复制该项目, 使用的方法就类似于硬连接（hard-link）。 所以这些操作只会花费很小, 而且是固定的时间。

（8）Hackability
Subversion没有任何的历史包袱; 它主要是一群共用的 C 程序库, 具有定义完善的API。这使得 Subversion 便于维护, 并且可被其它应用程序与程序语言使用。


----------

## SVN优于 CVS 之处
1、原子提交：一次提交不管是单个还是多个文件，都是作为一个整体提交的，所以要么全部提交成功，要么就是全部不成功，这样就不会引起数据库的不完整和数据损坏。

2、重命名、复制、删除文件等动作都保存在版本历史记录当中。

3、对于二进制文件，使用了节省空间的保存方法。（简单的理解，就是只保存和上一版本不同之处）

4、目录也有版本历史。整个目录树可以被移动或者复制，操作很简单，而且能够保留全部版本记录。

5、分支的开销非常小。

6、优化过的数据库访问，使得一些操作不必访问数据库就可以做到。这样减少了很多不必要的和数据库主机之间的网络流量。


----------

## SVN 生命周期

1. 创建版本库
版本库相当于一个集中的空间，用于存放开发者所有的工作成果。版本库不仅能存放文件，还包括了每次修改的历史，即每个文件的变动历史。
Create 操作是用来创建一个新的版本库。大多数情况下这个操作只会执行一次。当你创建一个新的版本库的时候，你的版本控制系统会让你提供一些信息来标识版本库，例如创建的位置和版本库的名字。

2. 检出
Checkout 操作是用来从版本库创建一个工作副本。工作副本是开发者私人的工作空间，可以进行内容的修改，然后提交到版本库中。

3. 更新
顾名思义，update 操作是用来更新版本库的。这个操作将工作副本与版本库进行同步。由于版本库是由整个团队共用的，当其他人提交了他们的改动之后，你的工作副本就会过期。
让我们假设 Tom 和 Jerry 是一个项目的两个开发者。他们同时从版本库中检出了最新的版本并开始工作。此时，工作副本是与版本库完全同步的。然后，Jerry 很高效的完成了他的工作并提交了更改到版本库中。
此时 Tom 的工作副本就过期了。更新操作将会从版本库中拉取 Jerry 的最新改动并将 Tom 的工作副本进行更新。

4. 执行变更
当检出之后，你就可以做很多操作来执行变更。编辑是最常用的操作。你可以编辑已存在的文件，例如进行文件的添加/删除操作。
你可以添加文件/目录。但是这些添加的文件目录不会立刻成为版本库的一部分，而是被添加进待变更列表中，直到执行了 commit 操作后才会成为版本库的一部分。
同样地你可以删除文件/目录。删除操作立刻将文件从工作副本中删除掉，但该文件的实际删除只是被添加到了待变更列表中，直到执行了 commit 操作后才会真正删除。
Rename 操作可以更改文件/目录的名字。"移动"操作用来将文件/目录从一处移动到版本库中的另一处。

5. 复查变化
当你检出工作副本或者更新工作副本后，你的工作副本就跟版本库完全同步了。但是当你对工作副本进行一些修改之后，你的工作副本会比版本库要新。在 commit 操作之前复查下你的修改是一个很好的习惯。
Status 操作列出了工作副本中所进行的变动。正如我们之前提到的，你对工作副本的任何改动都会成为待变更列表的一部分。Status 操作就是用来查看这个待变更列表。
Status 操作只是提供了一个变动列表，但并不提供变动的详细信息。你可以用 diff 操作来查看这些变动的详细信息。

6. 修复错误
我们来假设你对工作副本做了许多修改，但是现在你不想要这些修改了，这时候 revert 操作将会帮助你。
Revert 操作重置了对工作副本的修改。它可以重置一个或多个文件/目录。当然它也可以重置整个工作副本。在这种情况下，revert 操作将会销毁待变更列表并将工作副本恢复到原始状态。

7. 解决冲突
合并的时候可能会发生冲突。Merge 操作会自动处理可以安全合并的东西。其它的会被当做冲突。例如，"hello.c" 文件在一个分支上被修改，在另一个分支上被删除了。这种情况就需要人为处理。Resolve 操作就是用来帮助用户找出冲突并告诉版本库如何处理这些冲突。

8. 提交更改
Commit 操作是用来将更改从工作副本到版本库。这个操作会修改版本库的内容，其它开发者可以通过更新他们的工作副本来查看这些修改。
在提交之前，你必须将文件/目录添加到待变更列表中。列表中记录了将会被提交的改动。当提交的时候，我们通常会提供一个注释来说明为什么会进行这些改动。这个注释也会成为版本库历史记录的一部分。Commit 是一个原子操作，也就是说要么完全提交成功，要么失败回滚。用户不会看到成功提交一半的情况。

----------

## SVN 启动模式

首先,在服务端进行SVN版本库的相关配置

手动新建版本库目录     `mkdir /opt/svn`
利用svn命令创建版本库  `svnadmin create /opt/svn/runoob`
使用命令svnserve启动服务 `svnserve -d -r 目录 --listen-port 端口号`
-r: 配置方式决定了版本库访问方式。
--listen-port: 指定SVN监听端口，不加此参数，SVN默认监听3690

由于-r 配置方式的不一样，SVN启动就可以有两种不同的访问方式

方式一：-r直接指定到版本库(称之为单库svnserve方式)
`svnserve -d -r /opt/svn/runoob`
在这种情况下，一个svnserve只能为一个版本库工作。

authz配置文件中对版本库权限的配置应这样写：
```
[groups]
admin=user1
dev=user2
[/]
@admin=rw
user2=r
使用类似这样的URL：svn://192.168.0.1/　即可访问runoob版本库
```

方式二：指定到版本库的上级目录(称之为多库svnserve方式)
`svnserve -d -r /opt/svn`
这种情况，一个svnserve可以为多个版本库工作

authz配置文件中对版本库权限的配置应这样写：
```
[groups]
admin=user1
dev=user2
[runoob:/]
@admin=rw
user2=r

[runoob01:/]
@admin=rw
user2=r
```
如果此时你还用[/]，则表示所有库的根目录，同理，[/src]表示所有库的根目录下的src目录。

使用类似这样的URL：svn://192.168.0.1/runoob　即可访问runoob版本库。


----------

## SVN 创建版本库

使用 svn 命令创建资源库：`svnadmin create /opt/svn/runoob01`

进入` /opt/svn/runoob01/conf` 目录，修改默认配置文件配置，包括 svnserve.conf、passwd、authz 配置相关用户和权限。

1、svn 服务配置文件 svnserve.conf

svn 服务配置文件为版本库目录中的文件 `conf/svnserve.conf`。该文件仅由一个 [general] 配置段组成。
```
[general]
anon-access = none
auth-access = write
password-db = /home/svn/passwd
authz-db = /home/svn/authz
realm = tiku 
```
- anon-access: 控制非鉴权用户访问版本库的权限，取值范围为 "write"、"read" 和 "none"。 即 "write" 为可读可写，"read" 为只读，"none" 表示无访问权限，默认值：read。

- auth-access: 控制鉴权用户访问版本库的权限。取值范围为 "write"、"read" 和 "none"。 即"write"为可读可写，"read"为只读，"none"表示无访问权限，默认值：write。

- authz-db: 指定权限配置文件名，通过该文件可以实现以路径为基础的访问控制。 除非指定绝对路径，否则文件位置为相对conf目录的相对路径，默认值：authz。

- realm: 指定版本库的认证域，即在登录时提示的认证域名称。若两个版本库的认证域相同，建议使用相同的用户名口令数据文件。默认值：一个UUID(Universal Unique IDentifier，全局唯一标示)。



2、用户名口令文件 passwd

用户名口令文件由 svnserve.conf 的配置项 password-db 指定，默认为 conf 目录中的 passwd。该文件仅由一个 [users] 配置段组成。

[users] 配置段的配置行格式如下：
`<用户名> = <口令>`

```
[users]
admin = admin
thinker = 123456
```

3、权限配置文件

权限配置文件由 svnserve.conf 的配置项 authz-db 指定，默认为 conf 目录中的 authz。该配置文件由一个 [groups] 配置段和若干个版本库路径权限段组成。

[groups]配置段中配置行格式如下：`<用户组> = <用户列表>`
版本库路径权限段的段名格式如下：`[<版本库名>:<路径>] `
```
[groups]
g_admin = admin,thinker

[admintools:/]
@g_admin = rw
* =

[test:/home/thinker]
thinker = rw
* = r
```


----------

## SVN 检出操作

通过URL在客户端对版本库进行检出操作
`svn checkout http://svn.server.com/svn/project_repo --username=user01` 以上命令将产生如下结果：

```
root@runoob:~/svn# svn checkout svn://192.168.0.1/runoob01 --username=user01
A    runoob01/trunk
A    runoob01/branches
A    runoob01/tags
Checked out revision 1.
```
检出成功后在当前目录下生成runoob01副本目录。查看检出的内容
```
root@runoob:~/svn# ll runoob01/
total 24
drwxr-xr-x 6 root root 4096 Jul 21 19:19 ./
drwxr-xr-x 3 root root 4096 Jul 21 19:10 ../
drwxr-xr-x 2 root root 4096 Jul 21 19:19 branches/
drwxr-xr-x 4 root root 4096 Jul 21 19:19 .svn/
drwxr-xr-x 2 root root 4096 Jul 21 19:19 tags/
drwxr-xr-x 2 root root 4096 Jul 21 19:19 trunk/
```
查看更多关于版本库的信息，执行 info 命令。


----------

## SVN 解决冲突

查看更改： `svn diff`
```
root@runoob:~/svn/runoob01/trunk# svn diff 
Index: HelloWorld.html
===================================================================
--- HelloWorld.html     (revision 5)
+++ HelloWorld.html     (working copy)
@@ -1,2 +1 @@
-HelloWorld! http://www.runoob.com/
+HelloWorld! http://www.runoob.com/!
```

为了避免两人的代码被互相覆盖，在提交更改之前必须先更新工作副本。所以使用 update 命令。

```
root@runoob:~/svn/runoob01/trunk# svn update
Updating '.':
C    HelloWorld.html
Updated to revision 6.
Conflict discovered in file 'HelloWorld.html'.
Select: (p) postpone, (df) show diff, (e) edit file, (m) merge,
        (mc) my side of conflict, (tc) their side of conflict,
        (s) show all options: mc
Resolved conflicted state of 'HelloWorld.html'
Summary of conflicts:
  Text conflicts: 0 remaining (and 1 already resolved)
```
输入"mc",以本地的文件为主。
默认是更新到最新的版本，也可以指定更新版本 `svn update -r6`

工作副本是和仓库同步后，可以安全地提交更改
```
root@runoob:~/svn/runoob01/trunk# svn commit -m "change HelloWorld.html second"
Sending        HelloWorld.html
Transmitting file data .
Committed revision 7.
```


----------

## SVN 提交操作

在库本版中需要增加一个readme的说明文件。
```
root@runoob:~/svn/runoob01/trunk# cat readme 
this is SVN tutorial.
```

查看工作副本中的状态。
```
root@runoob:~/svn/runoob01/trunk# svn status
?       readme
```
此时 readme的状态为？，说明它还未加到版本控制中。
将文件readme加到版本控制，等待提交到版本库。
```
root@runoob:~/svn/runoob01/trunk# svn add readme 
A         readme
```

查看工作副本中的状态
```
root@runoob:~/svn/runoob01/trunk# svn status     
A       readme
```
此时 readme的状态为A,它意味着这个文件已经被成功地添加到了版本控制中。

为了把 readme 存储到版本库中，使用 commit -m 加上注释信息来提交。
如果忽略 -m 选项， SVN会打开一个可以输入多行的文本编辑器来让输入提交信息。
```
root@runoob:~/svn/runoob01/trunk# svn commit -m "SVN readme."
Adding         readme
Transmitting file data .
Committed revision 8.
svn commit -m "SVN readme."
```
现在 readme 被成功地添加到了版本库中，并且修订版本号自动增加了1。


----------

## SVN 版本回退

放弃对文件的修改，可以使用 SVN revert 命令。
svn revert 操作将撤销任何文件或目录里的局部更改。

对文件 readme 进行修改,查看文件状态。
```
root@runoob:~/svn/runoob01/trunk# svn status
M       readme
```
这时我们发现修改错误，要撤销修改，通过 svn revert 文件 readme 回归到未修改状态。
```
root@runoob:~/svn/runoob01/trunk# svn revert readme 
Reverted 'readme'
```
再查看状态。
```
root@runoob:~/svn/runoob01/trunk# svn status 
root@runoob:~/svn/runoob01/trunk# 
```

进行 revert 操作之后，readme 文件恢复了原始的状态。 

revert 操作不单单可以使单个文件恢复原状， 而且可以使整个目录恢复原状。恢复目录用 -R 命令，如下。`svn revert -R trunk`


想恢复一个已经提交的版本:
为了消除一个旧版本，必须撤销旧版本里的所有更改，然后提交一个新版本。这种操作叫做 reverse merge。
找到仓库的当前版本，现在是版本 22，要撤销回之前的版本，比如版本 21。  `svn merge -r 22:21 readme `


----------

## SVN 查看历史信息

通过svn命令可以根据时间或修订号去除过去的版本，或者某一版本所做的具体的修改。以下四个命令可以用来查看svn 的历史：
- svn log: 用来展示svn 的版本作者、日期、路径等等。
- svn diff: 用来显示特定修改的行级详细信息。
- svn cat: 取得在特定版本的某文件显示在当前屏幕。
- svn list: 显示一个目录或某一版本存在的文件。

1. `svn log`
`svn log`  可以显示所有的信息

查看特定的某两个版本之间的信息`svn log -r version1:version2`：

```
root@runoob:~/svn/runoob01/trunk# svn log -r 6:8
-----------------------------------------------------
r6 | user02 | 2016-11-07 02:01:26 +0800 (Mon, 07 Nov 2016) | 1 line

change HelloWorld.html first.
-----------------------------------------------------
r7 | user01 | 2016-11-07 02:23:26 +0800 (Mon, 07 Nov 2016) | 1 line

change HelloWorld.html second
-----------------------------------------------------
r8 | user01 | 2016-11-07 02:53:13 +0800 (Mon, 07 Nov 2016) | 1 line

SVN readme.
-----------------------------------------------------

```

查看某一个文件的版本修改信息 `svn log 文件路径`。
```
root@runoob:~/svn/runoob01# svn log trunk/HelloWorld.html 
-----------------------------------------------------
r7 | user01 | 2016-11-07 02:23:26 +0800 (Mon, 07 Nov 2016) | 1 line

change HelloWorld.html second
-----------------------------------------------------
r6 | user02 | 2016-11-07 02:01:26 +0800 (Mon, 07 Nov 2016) | 1 line

change HelloWorld.html first.
-----------------------------------------------------
r5 | user01 | 2016-11-07 01:50:03 +0800 (Mon, 07 Nov 2016) | 1 line


-----------------------------------------------------
r4 | user01 | 2016-11-07 01:45:43 +0800 (Mon, 07 Nov 2016) | 1 line

Add function to accept input and to display array contents
-----------------------------------------------------
r3 | user01 | 2016-11-07 01:42:35 +0800 (Mon, 07 Nov 2016) | 1 line


-----------------------------------------------------
r2 | user01 | 2016-08-23 17:29:02 +0800 (Tue, 23 Aug 2016) | 1 line

first file
-----------------------------------------------------

```

带有目录的信息要加 -v。

示限定N条记录的目录信息`svn log -l N -v`。
```
root@runoob:~/svn/runoob01/trunk# svn log -l 5 -v 
-----------------------------------------------------
r6 | user02 | 2016-11-07 02:01:26 +0800 (Mon, 07 Nov 2016) | 1 line
Changed paths:
   M /trunk/HelloWorld.html

change HelloWorld.html first.
-----------------------------------------------------
r5 | user01 | 2016-11-07 01:50:03 +0800 (Mon, 07 Nov 2016) | 1 line
Changed paths:
   M /trunk/HelloWorld.html


-----------------------------------------------------
r4 | user01 | 2016-11-07 01:45:43 +0800 (Mon, 07 Nov 2016) | 1 line
Changed paths:
   M /trunk/HelloWorld.html

Add function to accept input and to display array contents
-----------------------------------------------------
r3 | user01 | 2016-11-07 01:42:35 +0800 (Mon, 07 Nov 2016) | 1 line
Changed paths:
   A /trunk/HelloWorld.html (from /trunk/helloworld.html:2)
   D /trunk/helloworld.html


-----------------------------------------------------
r2 | user01 | 2016-08-23 17:29:02 +0800 (Tue, 23 Aug 2016) | 1 line
Changed paths:
   A /trunk/helloworld.html

first file
-----------------------------------------------------

```


----------


2. svn diff
`svn diff`用来检查历史修改的详情。

- 检查本地修改
- 比较工作拷贝与版本库
- 比较版本库与版本库


不带任何参数，将会比较工作文件与缓存在 .svn 的"原始"拷贝
```
root@runoob:~/svn/runoob01/trunk# svn diff
Index: rules.txt
===================================================================
--- rules.txt (revision 3)
+++ rules.txt (working copy)
@@ -1,4 +1,5 @@
Be kind to others
Freedom = Responsibility
Everything in moderation
-Chew with your mouth open
```

比较工作拷贝和版本库
	比较你的工作拷贝和版本库中版本号为 3 的文件 rule.txt。
	`svn diff -r 3 rule.txt`

比较版本库与版本库
	通过 -r(revision) 传递两个通过冒号分开的版本号，这两个版本会进行比较。
	比较 svn 工作版本中版本号2和3的这个文件的变化。`svn diff -r 2:3 rule.txt`


----------

3. svn cat

检查一个过去版本，不查看他们的区别，可使用`svn cat`

`svn cat -r 版本号 rule.txt`
这个命令会显示在该版本号下的该文件内容


----------

4. svn list
`svn list` 可以在不下载文件到本地目录的情况下来察看目录中的文件：
```bash
$ svn list http://192.168.0.1/runoob01
README
branches/
clients/
tags/
```

----------

## SVN分支

Branch 选项会给开发者创建出另外一条线路。当有人希望开发进程分开成两条不同的线路时，这个选项会非常有用。

分支其实就是 trunk 版（主干线）的一个copy版，不过分支也是具有版本控制功能的，而且是和主干线相互独立的。当然，到最后可以通过（合并）功能，将分支合并到 trunk 上来，从而最后合并为一个项目。


----------


## SVN 标签（tag）

版本管理系统支持 tag 选项，通过使用 tag 的概念，我们可以给某一个具体版本的代码一个更加有意义的名字。

Tags 即标签主要用于项目开发中的里程碑，比如开发到一定阶段可以单独一个版本作为发布等，它往往代表一个可以固定的完整的版本，这跟 VSS 中的 Tag 大致相同。


----------

## TortoiseSVN 使用教程
TortoiseSVN 是 Subversion 版本控制系统的一个免费开源客户端，可以超越时间的管理文件和目录。

### TortoiseSVN 安装
下载地址：https://tortoisesvn.net/downloads.html, 页面里有语言包补丁的下载链接。

目前最新版为 1.14.5 下载地址： https://osdn.net/projects/tortoisesvn/storage/1.14.5/
