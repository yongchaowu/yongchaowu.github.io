---
layout: post
title: Log4cxx Building
display_title: 'Log4cxx Building'
date: 2020-07-09 00:05:00
categories:
- C & C++
tags:
- Log4cxx
- Open Source
---

## Building Apache log4cxx with Microsoft Visual Studio

<!--more-->
### Preparation
```bash
unzip apr-1.2.11-win32-src.zip
rename apr-1.2.11 apr
unzip apr-util-1.2.10-win32-src.zip
rename apr-util-1.2.10 apr-util
cd apache-log4cxx-0.10.0
configure
configure-aprutil
```
configure.bat copies the prefabricated log4cxx.hw and private/log4cxx_private.hw over to log4cxx.h and private/log4cxx_private.h.

configure-aprutil.bat uses "sed" to modify apu.hw and apr_ldap.hw to disable APR-Iconv and LDAP which are not necessary for log4cxx and problematic to build. If "sed" is not available, the modifications would be trivial to do in any text editor.

Use the Win32 source zips for APR and APR-Util to preserve the required line endings for the project files. Directories need to be renamed to "apr" and "apr-util" respectively.


---

Supplement:
[apache-log4cxx-0.10.0](https://logging.apache.org/log4cxx/latest_stable/download.html)
[apr-1.7.0-win32-src、apr-util-1.6.1-win32-src](https://apr.apache.org/)
[Windows:sed](https://jaist.dl.sourceforge.net/project/gnuwin32/sed/4.2.1/),并设置环境变量

### Building log4cxx.dll
Open projects/log4cxx.dsw with Microsoft Visual Studio 6 or later at which time you may be prompted to upgrade the projects to the format used by your version of Microsoft Visual Studio.

Select log4cxx as active project and build.

### Running unit tests
To pass the unit tests, gzip, zip and sed must be on the path. Also three environment variables need to be defined: TOTO=wonderful, key1=value1 and key2=value2. These must be done outside of Microsoft Visual Studio, either in the Control Panel or in a Command Prompt used to launch Microsoft Visual Studio.

Open projects/testsuite.dsw or projects/testsuite-standalone.dsw (test suite and implementation in one project) in Microsoft Visual Studio, select active project and build.

On the Debug Tab of the Project/Settings dialog, set the Working Directory to "../src/test/resources". Individual tests can be specified in Program Arguments and "-v" can be specified to output verbose test results.

### Known Issues

- APR 1.2.12 has a known issue that will prevent compilation with Visual Studio 6 unless a later Platform SDK is installed. See APR bug 44327. APR 1.2.11 and the corresponding APR-Util 1.2.10 will compile with Visual Studio 6.
- APR-Util requires later LDAP headers than provided with Visual Studio 6 and will fail to compile. log4cxx does not use LDAP, it can be disabled in apr_ldap.hw.
- APR-Iconv is problematic and not used by log4cxx, it can be disabled in apu.hw.


### 编译log4cxx的坑
- 若出现：error C2252: 只能在命名空间范围内显式实例化模板
    ```cpp
    请双击 "输出" 窗口中的错误行, 此时会在 "代码窗口" 中出现错误的位置.
    选择 LOG4CXX_LIST_DEF, 按键盘 F12, 此时会跳转到该宏的定义将
    #define LOG4CXX_LIST_DEF(N, T) \
    template class LOG4CXX_EXPORT std::allocator<T>; \
    template class LOG4CXX_EXPORT std::vector<T>; \
    typedef std::vector<T> N
    替换为:
    #define LOG4CXX_LIST_DEF(N, T) \
    typedef std::vector<T> N
	```

- 若出现：error C2079: “mip”使用未定义的struct “group_source_req”错误
	```
    请双击第一行出错输出, 将 #if MCAST_JOIN_SOURCE_GROUP 注释, 替换为 #if defined (group_source_req)
    ```

- 若出现：error C2039: “insert_iterator”: 不是“std”的成员等错误.
	```
    在该 .cpp 中加入头文件 #include<iterator>, 使用vs2019时，可以通过编译器的修补功能自动添加
	```
- 出现 '无法解析的外部符号 xxx' 等错误.
	```
    将 apr, aprutil, xml 添加至 log4cxx 的引用中
	```
- APR编译
	[Building APR with the included Visual Studio project files](https://apr.apache.org/compiling_win32.html#workspace)
- APR编译报错
	[apr_arch_misc.h error](https://www.apachelounge.com/viewtopic.php?p=38033)
     set in apr/include/apr.hw : #define _WIN32_WINNT 0x0600 (was 502).
- expat.h 不存在
	apr_xml.c中需要expat.h，这个是一个c的xml解析库。 需要自己下载编译。 用的绝对路径编译的。
    [expat-win32bin-2.2.9](https://sourceforge.net/projects/expat/)
    [Github:expat](https://github.com/libexpat/libexpat/tree/master/expat)
- warning MSB8012：TargetPath与Linker的OutputFile属性值不匹配
	其实就是和warning中提示的一样，在"项目->属性->配置属性->常规"选项卡下的“目标文件名”选项，和“项目->属性->配置属性->链接器->常规”选项卡下的“输出文件”选项(Vs2019:文档管理程序)，不一致，所以造成了输出文件命名上的矛盾，从而产生该warning。
- LNK2019	无法解析的外部符号 \__imp__UuidCreate@4，该符号在函数 _apr_os_uuid_get@4 中被引用	log4cxx	D:\Workspace\Log4-Compile\apache-log4cxx-0.10.0\projects\apr.LIB(rand.obj)	1
	测试发现在apr中搜索**_apr_os_uuid_get**，屏蔽内部的UuidCreate则通过
    ```
    if (FAILED(UuidCreate((UUID *)uuid_data))) {
      return APR_EGENERAL;
    }
	```
    最后，	链接器->输入->附加依赖项：增加Rpcrt4.lib，最后通过。

### Demo
[Demo](https://www.cnblogs.com/lovelp/articles/3719735.html)
```code
    #include <iostream>
    #include <log4cxx/logger.h>
    #include <log4cxx/basicconfigurator.h>
    #include <log4cxx/helpers/exception.h>
    #include <log4cxx/propertyconfigurator.h>

    #pragma comment(lib,"log4cxx.lib")

    using namespace std;
    using namespace log4cxx;
    using namespace log4cxx::helpers;


    LoggerPtr logger(Logger::getLogger("R"));
    LoggerPtr logger_lib_a(Logger::getLogger("Lib_a"));
    LoggerPtr logger_lib_b(Logger::getLogger("Lib_b"));

    int main(int argc, char **argv)
    {

        try
        {
            // Set up a simple configuration that logs on the console.
            PropertyConfigurator::configure("log4cxx.properties");
            for (int i=0 ; i<100;i++)
            {
                LOG4CXX_INFO(logger, "测试下 R");
                LOG4CXX_DEBUG(logger_lib_a, "测试下  R.a");
                LOG4CXX_DEBUG(logger_lib_b, "测试下 t R.b");
            }

        }
        catch(...)
        {
        }

        cin.get();
        return 0;
    }
```

```log4cxx.properties
log4cxx.properties:
    log4j.additivity.gather = false
    log4j.rootLogger= debug, R, stdout

    #设置子logger
    log4j.logger.Lib_a =debug, ap1, stdout
    log4j.logger.Lib_b =debug, ap2, stdout


    #设置不继承父Logger
    log4j.additivity.Lib_a=false
    log4j.additivity.Lib_b=false

    log4j.appender.logfile.encoding=UTF-8

    #标准输出，向控制台打印
    log4j.appender.stdout=org.apache.log4j.ConsoleAppender
    log4j.appender.stdout.layout=org.apache.log4j.PatternLayout
    log4j.appender.stdout.layout.ConversionPattern=%5p [%t] (%F:%L) - %m%n

    #Root
    log4j.appender.R=org.apache.log4j.RollingFileAppender
    log4j.appender.R.File=./info.log
    log4j.appender.R.MaxFileSize=100KB
    log4j.appender.R.MaxBackupIndex=10
    log4j.appender.R.layout=org.apache.log4j.PatternLayout
    log4j.appender.R.layout.ConversionPattern=%d [%c]-[%p] %m%n

    log4j.appender.ap1=org.apache.log4j.RollingFileAppender
    log4j.appender.ap1.File=./hello_a.log
    log4j.appender.ap1.MaxFileSize=100KB
    log4j.appender.ap1.MaxBackupIndex=10
    log4j.appender.ap1.layout=org.apache.log4j.PatternLayout
    log4j.appender.ap1.layout.ConversionPattern=%d{yyyy-MM-dd} [%c]-[%p] %m%n

    log4j.appender.ap2=org.apache.log4j.RollingFileAppender
    log4j.appender.ap2.File=./hello_b.log
    log4j.appender.ap2.MaxFileSize=100KB
    log4j.appender.ap2.MaxBackupIndex=10
    log4j.appender.ap2.layout=org.apache.log4j.PatternLayout
    log4j.appender.ap2.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} [%c]-[%p] %m%n
```