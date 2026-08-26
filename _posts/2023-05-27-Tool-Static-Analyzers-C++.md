---
layout: post
title: Static Analyzers-C++
date: 2023-05-27 17:36:00
categories:
- Developer Tools
tags:
- C++
- Tool
- Static Analyzers
---

## C++ Code Style

<!--more-->
### Google styleguide
>https://google.github.io/styleguide/
包含cpplint

#### Google styleguide cppguide
>https://google.github.io/styleguide/cppguide.html


----------

## Tool-Static Analyzers
### cppcheck
>https://cppcheck.sourceforge.io/

Cppcheck is a static analysis tool for C/C++ code. It provides unique code analysis to detect bugs and focuses on detecting undefined behaviour and dangerous coding constructs. The goal is to have very few false positives. Cppcheck is designed to be able to analyze your C/C++ code even if it has non-standard syntax (common in embedded projects).

官网提供
- Windows 64-bit (No XP support)
- Source code (.zip)
- Source code (.tar.gz)

Debian:	`sudo apt install cppcheck`

Running Command: `cppcheck src`

----------

### TscanCode

>https://github.com/Tencent/TscanCode

Repository:
- release ->编译后的二进制文件，分别有Linux、Mac、Windows平台
- samples ->测试的代码样例，分别有C++、C#、Lua语言
- trunk ->TscanCode源代码

Install：
1. linux平台下：
- 第一种：
```bash
$ git clone https://github.com/Tencent/TscanCode.git
$ cd TscanCode/release/linux/
$ unzip TscanCodeV2.14.24.linux.zip
$ cd TscanCodeV2.14.24.linux/TscanCodeV2.14.2395.linux
$ chmod a+x tscancode
$ echo "PATH=$PATH:$(pwd)" >> ~/.bashrc
$ source ~/.bashrc
```

- 第二种，建议使用：
```bash
cd trunk/
make
修改cfg/cfg.xml #cfg.xml 配置不当，可能导致检测结果为空，建议value="0"的再开启。通过设置value=0则禁用，value=1则启用。
```

Running Command:
`./tscancode --xml --enable=all -q /home/yang/test/cpp/ >scan_result.xml 2>&1`

扫描规则与配置：cfg/cfg.xml


----------
### Valgrind
Valgrind是开放源代码（GPL V2）的仿真调试工具的集合，支持Linux操作系统。它的功能同样强大：
1）Memcheck：重量级的内存检查器，能够发现开发中绝大多数内存错误使用情况，比如：使用未初始化的内存，使用已经释放了的内存，内存访问越界等；
2）Callgrind：检查程序中函数调用过程中出现的问题，也可以用于性能调优；
3）Cachegrind：检查程序中缓存使用出现的问题；
4）Helgrind：检查多线程程序中出现的竞争问题；
5）Massif：检查程序中堆栈使用中出现的问题；
6）Extension：编写特定的内存调试工具。


----------
### Online website for static analyzer

1. OnlineGDB:`https://www.onlinegdb.com/`

2. C++ Shell:`http://cpp.sh/`

3. https://paiza.io/en


----------

### cpplint
cpplint是Google提供的工具，用于检查代码是否符合Google C++ Style Guide.

Install:
`pip3 install cpplint`

Running Command:
```
cpplint <文件名>
cpplint --recursive <目录名>
```

项目代码在git的pre-commit或者pre-push之前可以使用cpplint，下面是来自brickgao的一段gist

>https://gist.github.com/brickgao/fb359764d46f9c96dd3af885e94b0bab

```
#!/bin/sh
#
# Modified from http://qiita.com/janus_wel/items/cfc6914d6b7b8bf185b6
#
# An example hook script to verify what is about to be committed.
# Called by "git commit" with no arguments. The hook should
# exit with non-zero status after issuing an appropriate message if
# it wants to stop the commit.
#
# To enable this hook, rename this file to "pre-commit".

if git rev-parse --verify HEAD >/dev/null 2>&1
then
against=HEAD
else
# Initial commit: diff against an empty tree object
against=4b825dc642cb6eb9a060e54bf8d69288fbee4904
fi

# Redirect output to stderr.
exec 1>&2

cpplint=cpplint
sum=0
filters='-build/include_order,-build/namespaces,-legal/copyright,-runtime/references'

# for cpp
for file in $(git diff-index --name-status $against -- | grep -E '\.[ch](pp)?$' | awk '{print $2}'); do
$cpplint --filter=$filters $file
sum=$(expr ${sum} + $?)
done

if [ ${sum} -eq 0 ]; then
exit 0
else
exit 1
fi
```

----------


### Clang

>https://www.oschina.net/p/clang?hmsr=aladdin1e1
>https://github.com/llvm/llvm-project

Clang: a C language family frontend for LLVM
>https://clang.llvm.org/
>https://llvm.org/docs/GettingStarted.html#checkout


#### clang-format

严格来说，它不是静态检查工具，而是代码格式化的工具，类似的工具还有astyle，但是相对来说，clang-format会好用一些，支持的配置参数也多一些。它的使用请参考Clang-Format Style Options。

#### codechecker
https://github.com/Ericsson/codechecker


#### clang-check、clang static analyzer、clang-tidy

是编译器级别的检查，它们需要编译文件从而检查代码

所以理论上它们的可靠性会比cpplint和cppcheck要强一些，同时它的耗时也会比它们长一些。

>https://clang-analyzer.llvm.org/
>http://clang.llvm.org/extra/clang-tidy/

Install:
`sudo apt install clang-tidy`


`cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON ...`
`DCMAKE_EXPORT_COMPILE_COMMANDS`这个选项会生成一个叫`compile_commands.json`的文件，有了这个文件，我们可以直接在编译目录下执行`run-clang-tidy`命令，对整个项目做静态的检查。

```
clang-tidy -list-checks来查看所有已经enable的检查
clang-tidy -list-checks -checks=*查看所有支持的检查
```

----------

### PC-lint

>https://baike.baidu.com/item/PC-lint/8340681?fr=aladdin

>https://pclintplus.com/?nordt=1

----------

### VS Code Extensions

#### C/C++ Advanced Lint for VS Code

>http://web.archive.org/web/20260411051622/https://marketplace.visualstudio.com/items?itemName=jbenden.c-cpp-flylint

----------

>http://web.archive.org/web/20260610180411/https://marketplace.visualstudio.com/items?itemName=QiuMingGe.cpp-check-lint
```bash
http://cppcheck.net/
sudo apt-get install cppcheck
https://github.com/cpplint/cpplint
pip install cpplint
```

----------

### flawfinder
flawfinder, a simple program that examines C/C++ source code and reports possible security weaknesses (“flaws”) sorted by risk level
>https://dwheeler.com/flawfinder/


### Lizard 
Lizard is an extensible Cyclomatic Complexity Analyzer for many programming languages including C/C++ (doesn't require all the header files or Java imports). It also does copy-paste detection (code clone detection/code duplicate detection) and many other forms of static code analysis.
>https://github.com/terryyin/lizard

### Sonar
>https://www.sonarsource.com/products/sonarqube/

#### sonarlint (free)
>https://www.sonarsource.com/open-source-editions/

For coding [IN YOUR IDE]
Analyze your code in real time as you type in your IDE and get live feedback & guidance. Always free and available in your IDE marketplace.

----------
### Visual Studio 中的C++代码分析

>https://learn.microsoft.com/zh-cn/cpp/code-quality/

Visual Studio 提供了多种用于分析和提升 C++ 代码质量的工具。


----------
### conclusion

*（图片缺失，未随博客园迁移：`.Static Analyzers.jpeg`）*
![](https://images.cnblogs.com/cnblogs_com/yongchao/2296107/o_230527125337_Static%20Analyzers.jpeg)
