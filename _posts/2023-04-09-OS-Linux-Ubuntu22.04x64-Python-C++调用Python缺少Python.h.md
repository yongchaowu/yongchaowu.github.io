---
layout: post
title: "OS-Linux-Ubuntu22.04x64-Python-C++调用Python缺少Python.h"
date: 2023-04-09 10:07:00
categories: ["OS"]
tags: ["C++", "Python", "Ubuntu", "Visual Studio Code", "IDE", "OS"]
---

- [使用 C 或 C++ 扩展 Python](https://docs.python.org/zh-cn/3.10/extending/extending.html#extracting-parameters-in-extension-functions "使用 C 或 C++ 扩展 Python")
- [扩展和嵌入 Python 解释器](https://docs.python.org/zh-cn/3.10/extending/index.html "扩展和嵌入 Python 解释器")
- [Python 3.10.11 Python/C API 参考手册](https://docs.python.org/zh-cn/3.10/c-api/index.html#c-api-index "Python 3.10.11 Python/C API 参考手册")
- [Python 3.11.3 Python/C API 参考手册](https://docs.python.org/zh-cn/3/c-api/index.html#c-api-index "Python 3.10.11 Python/C API 参考手册")

<!--more-->
参考
1. https://www.cnblogs.com/lidabo/p/17043302.html
2. https://blog.csdn.net/zong596568821xp/article/details/115690713

在环境中缺少Python.h文件
- `python` `python2` `python3` 查看python是否安装以及安装版本
- `whereis python`	查找python的安装位置
- `locate Python.h` 查找Python.h文件位置


## python-dev
安装python-dev。
python-dev包含构建Python扩展所需的头文件。（在Linux上，通常，python等包的二进制库和头文件是分开的。因此，可以安装Python并且一切正常，但是构建扩展时，需要安装相应的开发包。）


Python-dev 2.0.0.dev0   上次发布日期: 2023-04-08 14:11:02
`pip install Python-dev`：[https://www.cnpython.com/pypi/python-dev](https://www.cnpython.com/pypi/python-dev "pip install Python-dev")


1.`sudo apt-get install python-dev`
结果为：
```
正在读取软件包列表... 完成
正在分析软件包的依赖关系树... 完成
正在读取状态信息... 完成                 
注意，选中 'python-dev-is-python2' 而非 'python-dev'
将会同时安装下列软件：
  libexpat1-dev libpython2-dev libpython2-stdlib libpython2.7 libpython2.7-dev
  libpython2.7-minimal libpython2.7-stdlib python-is-python2 python2
  python2-dev python2-minimal python2.7 python2.7-dev python2.7-minimal
建议安装：
  python2-doc python-tk python2.7-doc binfmt-support
下列【新】软件包将被安装：
  libexpat1-dev libpython2-dev libpython2-stdlib libpython2.7 libpython2.7-dev
  libpython2.7-minimal libpython2.7-stdlib python-dev-is-python2
  python-is-python2 python2 python2-dev python2-minimal python2.7
  python2.7-dev python2.7-minimal
升级了 0 个软件包，新安装了 15 个软件包，要卸载 0 个软件包，有 4 个软件包未被升级。
需要下载 8,126 kB 的归档。
解压缩后会消耗 33.7 MB 的额外空间。
您希望继续执行吗？ [Y/n] n

```

2.`sudo apt-get install python3-dev`
结果为：
```
正在读取软件包列表... 完成
正在分析软件包的依赖关系树... 完成
正在读取状态信息... 完成                 
将会同时安装下列软件：
  javascript-common libexpat1-dev libjs-jquery libjs-sphinxdoc
  libjs-underscore libpython3-dev libpython3.10-dev python3-distutils
  python3.10-dev zlib1g-dev
建议安装：
  apache2 | lighttpd | httpd
下列【新】软件包将被安装：
  javascript-common libexpat1-dev libjs-jquery libjs-sphinxdoc
  libjs-underscore libpython3-dev libpython3.10-dev python3-dev
  python3-distutils python3.10-dev zlib1g-dev
升级了 0 个软件包，新安装了 11 个软件包，要卸载 0 个软件包，有 4 个软件包未被升级。
需要下载 6,329 kB 的归档。
解压缩后会消耗 25.2 MB 的额外空间。
您希望继续执行吗？ [Y/n] Y


python3-dev 已经是最新版 (3.10.6-1~22.04)
```

3.`pip install Python-dev`
```
Defaulting to user installation because normal site-packages is not writeable
ERROR: Could not find a version that satisfies the requirement Python-dev (from versions: none)
ERROR: No matching distribution found for Python-dev

```

4.*Python.h 所在位置*
`locate Python.h`时因为未`updatedb`,所以显示没找到文件，这导致我不确定是此时就已经存在Python.h还是再步骤5、步骤6之后才存在的。
ps：关于`locate`的问题，在后面章节中`python 3.11.3-->Build Instructions`中又出现过一次，才了解到需要使用更新命令`sudo updatedb`。（所以修改此处描述）

```
yongchao@yongchao-virtual-machine:~$ locate Python.h
/usr/include/python3.10/Python.h
/usr/local/include/python3.11/Python.h

```

```
c_cpp_properties.json 
"/usr/local/include/python3.11/**"

tasks.json
"-I/usr/local/include/python3.11",
"-L/usr/local/lib/python3.11",
"-lpython3.11",
```


5.install python
Python-3.11.3.tar.xz from  [https://www.python.org/downloads/](https://www.python.org/downloads/ "Python3.11.3 Download")

6.`pip install python-dev-tools`

## python 3.11.3
安装完整python。
Python-3.11.3.tar.xz
[https://www.python.org/downloads/](https://www.python.org/downloads/ "Python3.11.3 Download")

### General Information
- Website: https://www.python.org
- Source code: https://github.com/python/cpython
- Issue tracker: https://github.com/python/cpython/issues
- Documentation: https://docs.python.org
- Developer's Guide: https://devguide.python.org/

### Build Instructions
On Unix, Linux, BSD, macOS, and Cygwin::
```bash
    ./configure  --enable-optimizations  
	//--prefix=/usr/local
    make
    //make test
    sudo make install
```
This will install Python as `python3`.
To get an optimized build of Python, `configure --enable-optimizations` before you run `make`.  This sets the default make targets up to enable Profile Guided Optimization (PGO) and may be used to auto-enable Link Time Optimization (LTO) on some platforms.


----------

如果在linux下遇到“undefined reference”错误可能是编译的时候没有生成libpython3.11.so

`./configure --enable-shared`
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv

后来发现在`/usr/local/lib`中有libpython3.11.so，但是locate找不到~然而原有的libpython3.10.so却可以locate出来

```locate libpython3.11.so
yongchao@yongchao-virtual-machine:/usr/local/lib$ ll
总计 70372
drwxr-xr-x  5 root root     4096  4月  9 01:23 ./
drwxr-xr-x 10 root root     4096  2月 23 11:57 ../
-rwxr-xr-x  1 root root 48708890  4月  8 22:10 libpython3.11.a*
lrwxrwxrwx  1 root root       20  4月  9 01:23 libpython3.11.so -> libpython3.11.so.1.0*
-rwxr-xr-x  1 root root 23313416  4月  9 01:23 libpython3.11.so.1.0*
-rwxr-xr-x  1 root root    15120  4月  9 01:23 libpython3.so*
drwxr-xr-x  2 root root     4096  4月  9 01:25 pkgconfig/
drwxr-xr-x  3 root root     4096  2月 23 11:57 python3.10/
drwxr-xr-x 39 root root     4096  4月  9 01:23 python3.11/
yongchao@yongchao-virtual-machine:/usr/local/lib$ locate libpython3.so
yongchao@yongchao-virtual-machine:/usr/local/lib$ locate libpython3.11.so
yongchao@yongchao-virtual-machine:/usr/local/lib$ 

```

```locate libpython3.10.so
yongchao@yongchao-virtual-machine:/usr/local/lib$ locate libpython3.10.so
/usr/lib/python3.10/config-3.10-x86_64-linux-gnu/libpython3.10.so
/usr/lib/x86_64-linux-gnu/libpython3.10.so
/usr/lib/x86_64-linux-gnu/libpython3.10.so.1
/usr/lib/x86_64-linux-gnu/libpython3.10.so.1.0
yongchao@yongchao-virtual-machine:/usr/local/lib$ 
```

原因：
- `locate`不是从磁盘中实时查找文件，而是到由`updatedb`命令产生的信息库中查找相应的文件和目录。
- 好处是定位速度快，缺点就是有时候找不到文件。
- 若找不到文件，终端执行：`updatedb`，重新建立整个系统所有文件和目录的资料库，方便以后再查找文件。

find命令进行文件查找执行速度要比locate慢的多，find是使用时再从硬盘查找，比较耗磁盘空间，所以一般优先使用locate查找。
- `locate file_name` 
- `find -name file_name`

## remove python
卸载python。
*[执行之后，我的虚拟机崩了，重启之后默认进入命令行模式，不再直接进入用户图形界面，使用`startx`进入之后感觉系统运行很慢，放弃挣扎，重新建虚拟机了(ps:虚拟机创建之后，忘记快照了，泪目~~)]*

1. 卸载python3.10
`sudo apt-get remove python3.10`

2. 卸载python3.10及其依赖
`sudo apt-get remove --auto-remove python3.10`

3. 清除python3.10
`sudo apt-get purge python3.10` 
or 
`sudo apt-get purge --auto-remove python3.10`



----------

## undefined reference to `Py_Initialize'
在Python.h能够找到后，还出现`undefined reference to Py_Initialize`错误，在百度之后，把-I -L -l放到编译参数最后，通过编译。
ld寻找函数的顺序是从左往右，所以要放在${file}后面。
tasks.json中args值如下：
```tasks.json
"args": [
                "-fdiagnostics-color=always",
                "-g",
                "${file}",
                "-o",
                "${fileDirname}/${fileBasenameNoExtension}",
                "-I/usr/local/include/python3.11",
                "-L/usr/local/lib/python3.11",
                "-lpython3.11"
            ]
```
```tasks.json
"args": [
                "-fdiagnostics-color=always",
                "-g",
                "${file}",
                "-o",
                "${fileDirname}/${fileBasenameNoExtension}",
                "-I/usr/local/include/python3.11",
                "-L/usr/local/lib/python3.11",
                "-lpython3.11"
            ]
```


## loading shared libraries: libpython3.11.so.1.0: cannot open shared object file: No such file or directory
因为动态链接库找不到，所以要在你的配置文件里加入库的路径。
解决方法是在·`etc/ld.so.conf.d`中添加`python3.conf`文件，并添加lib路径，最后`ldconfig`。
```bash
cd  /etc/ld.so.conf.d
sudo gedit python3.conf
/usr/local/lib
/usr/local/lib/python3.11

sudo ldconfig
```

### 在添加库的路径前，我用`nm`看过`libpython3.11.so.1.0`
`nm -D libpython3.11.so.1.0  | grep Py_Initialize`

```
yongchao@yongchao-virtual-machine:/usr/local/lib$ nm -D libpython3.11.so.1.0  | grep Py_Initialize
00000000002a0df0 T Py_Initialize
00000000002a0d40 T Py_InitializeEx
000000000029fda0 T Py_InitializeFromConfig
000000000029ffd0 T _Py_InitializeMain
```
