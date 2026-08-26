---
layout: post
title: Windbg-Debugging Tools for Windows网上搜集资料整理
date: 2020-07-08 02:04:00
categories:
- Security & Networking
tags:
- Windbg
- Windows
- Tool
---

官方下载地址：
x64
http://download.microsoft.com/download/A/6/A/A6AC035D-DA3F-4F0C-ADA4-37C8E5D34E3D/setup/WinSDKDebuggingTools_amd64/dbg_amd64.msi
x86
http://download.microsoft.com/download/A/6/A/A6AC035D-DA3F-4F0C-ADA4-37C8E5D34E3D/setup/WinSDKDebuggingTools/dbg_x86.msi

<!--more-->
http://www.windbg.org/ 非windbg的官网。
[Windows 调试工具(WinDbg、KD、CDB、NTSD)](https://docs.microsoft.com/zh-cn/windows-hardware/drivers/debugger/)

## symbol file path
程序运行需要将相关二进制文件（包括.exe和.dll文件）加载到内存地址空间，即内存映射文件。内存映射文件包含的是二进制信息，一批跟这些二进制文件配套的符号文件（后缀名为“*.pdb”）供调试时使用，它包含函数名、变量名等各种符号和调试信息，实际程序运行并不需要它。

symbol file一般包括两类，一类是我们自己的程序的.exe和.dll文件的对应.pdb文件，另一类是系统dll的符号文件，如kernel32.dll等。我们把系统dll的符号文件称为“Microsoft公共符号文件”。

1）Symbol Server

    对于Microsoft公共符号文件，我们一般使用“ cache* + srv* ”，即设置为在线服务器，并缓存部分文件到本地主机。这样就不用每次都从在线服务器去下载符号文件了，而只是更新部分符号文件。

    为此，我们需要先新建一个本地缓存文件夹，我的是：F:\SymbolCache

    然后，将该路径设置为系统环境变量，这样可以省去每次都重新设置的麻烦。

a. 将windbg的安装路径添加到系统path中

    该路径下需要包含“symsrv.dll”和“symstore.exe”两个文件，分别用于symbol server和cache。

b. 新增系统环境变量项：_NT_SYMBOL_PATH 值为: SRV*F:\SymbolCache*http://msdl.microsoft.com/download/symbols

    具体可以在help文档中搜“symbol”，查看“symbol file and symbol path”。

2）目标程序符号文件

    直接通过命令“.sympath+ ”设置目标程序符号文件路径即可。

通常符号文件中包含以下内容:
        全局变量的名字和地址
        函数名，地址及其原型
        帧指针优化数据
        局部变量的名字和地址
        源文件路径以及每个符号的行号
        变量，结构等的类型信息

## 源码路径

    直接通过命令“.srcpath ”设置目标程序源码文件路径即可。

## 可执行映像文件（Image File）

    主要用于调试dump文件，可以直接通过命令“.exepath ”，将待调试的.exe、.dll或.sys的路径设置进去即可。

## “.reload”
注：当各个路径设置好后，需要运行“.reload”命令来加载各个符号和源码。

## 启动
以最简单的用户模式应用程序为例，参考help文档的“Getting Started with WinDbg (User-Mode)”这一篇。

1，选择可执行文件

    启动windbg -> 点开File菜单 -> 选择“Open Executable...”，选中待调试的exe文件即可。

2，输入下列三个命令

    .sympath srv*

    .sympath+ C:\MyAPP\x64\Debug

    .srcpath C:\MyApp\MyApp


    .reload

注：windbg中以“点号，.”开头的命令，都是配置环境的命令。

3，用“x MyApp!*”检查相关符号的加载情况

    “*”，星号在windbg中属于通配符。

    “!”，叹号在windbg中，一般位于模块名后，起分隔模块名和模块内符号名的作用。

      叹号在最前面，表示这是一个扩展命令，如：“!analyze -v”。

4，清屏“.cls”


5.设断点并运行

    bu TestDebug!main

    bl

    g

6.单步调试

    按F10或F11进行单步调试，同VS的调试器。

    在单步过程中，可以通过view菜单打开“Locals”窗口查看局部变量，“Watch”窗口监视某变量，“Memory”窗口看内存，“Call Stack”窗口看调用堆栈，等等。这些功能都类似VS的调试器。

7.通过命令方式

    k      —— 查看堆栈

    dv    —— 查看变量    d -display

注：所有的这些命令，都可以在help文档中进行搜索。

8.bug分析

    该示例程序，设计了一个被0除的bug，运行到该处时，调试器会中断，这时，可以输入扩展命令“!analyze -v”

查看调试器对该bug的详细分析信息，包括：

1）bug类型

2）bug发生的位置

3）当前堆栈

--------------------- 
作者：Sagittarius_Warrior 
来源：CSDN 
原文：https://blog.csdn.net/sagittarius_warrior/article/details/52512843 
版权声明：本文为博主原创文章，转载请附上博文链接！


##  .lastevent
**.lastevent** 命令显示最近一次发生的异常或事件。
```
0:000> .lastevent Last event: 1534.f4c: Break instruction exception - code 80000003 (first chance) debugger time: Tue May 22 10:47:26.962 2012 (GMT+8)
 0:000> ~
 . 0 Id: 1534.e8c Suspend: 1 Teb: 7ffdf000 Unfrozen 1 Id: 1534.1338 Suspend: 
 1 Teb: 7ffde000 Unfrozen 
 # 2 Id: 1534.f4c Suspend: 1 Teb: 7ffdd000 Unfrozen
```
当前为2号线程发生异常，线程0前面的点号(.)表示它是当前线程。线程2前面的数字号(#)表示它是产生异常或调试器附加到进程时活动的线程。如果使用CTRL+C、 CTRL+BREAK或Debug | Break中断到调试器，总是会产生一个 0x80000003异常代码。

```
0:000> .lastevent Last event: 1664.4184: Access violation - code c0000005 (first/second chance not available)
  debugger time: Thu Aug 13 11:20:44.037 2015 (GMT+8)
```

异常错误码查询

EXCEPTION_ACCESS_VIOLATION
0xC0000005
程序企图读写一个不可访问的地址时引发的异常。例如企图读取0地址处的内存。

EXCEPTION_ARRAY_BOUNDS_EXCEEDED
0xC000008C
数组访问越界时引发的异常。

EXCEPTION_BREAKPOINT
0x80000003
触发断点时引发的异常。

EXCEPTION_DATATYPE_MISALIGNMENT
0x80000002
程序读取一个未经对齐的数据时引发的异常。

EXCEPTION_FLT_DENORMAL_OPERAND
0xC000008D
如果浮点数操作的操作数是非正常的，则引发该异常。所谓非正常，即它的值太小以至于不能用标准格式表示出来。

EXCEPTION_FLT_DIVIDE_BY_ZERO
0xC000008E
浮点数除法的除数是0时引发该异常。

EXCEPTION_FLT_INEXACT_RESULT
0xC000008F
浮点数操作的结果不能精确表示成小数时引发该异常。

EXCEPTION_FLT_INVALID_OPERATION
0xC0000090
该异常表示不包括在这个表内的其它浮点数异常。

EXCEPTION_FLT_OVERFLOW
0xC0000091
浮点数的指数超过所能表示的最大值时引发该异常。

EXCEPTION_FLT_STACK_CHECK
0xC0000092
进行浮点数运算时栈发生溢出或下溢时引发该异常。

EXCEPTION_FLT_UNDERFLOW
0xC0000093
浮点数的指数小于所能表示的最小值时引发该异常。

EXCEPTION_ILLEGAL_INSTRUCTION
0xC000001D
程序企图执行一个无效的指令时引发该异常。

EXCEPTION_IN_PAGE_ERROR
0xC0000006
程序要访问的内存页不在物理内存中时引发的异常。

EXCEPTION_INT_DIVIDE_BY_ZERO
0xC0000094
整数除法的除数是0时引发该异常。

EXCEPTION_INT_OVERFLOW
0xC0000095
整数操作的结果溢出时引发该异常。

EXCEPTION_INVALID_DISPOSITION
0xC0000026
异常处理器返回一个无效的处理时引发该异常。

EXCEPTION_NONCONTINUABLE_EXCEPTION
0xC0000025
发生一个不可继续执行的异常时，如果程序继续执行，则会引发该异常。

EXCEPTION_PRIV_INSTRUCTION
0xC0000096
程序企图执行一条当前CPU模式不允许的指令时引发该异常。

EXCEPTION_SINGLE_STEP
0x80000004
标志寄存器的TF位为1时，每执行一条指令就会引发该异常。主要用于单步调试。

EXCEPTION_STACK_OVERFLOW
0xC00000FD
栈溢出时引发该异常。

--------------------- 
作者：花熊 
来源：CSDN 
原文：https://blog.csdn.net/hgy413/article/details/7590052 
版权声明：本文为博主原创文章，转载请附上博文链接！

## 常用命令
bug分析：!analyze -v
查看栈的命令：k,kb,kn,kd,kl
查看内存的命令：db,dw,dd,da,du

## Windbg工作空间

Windbg的工作空间主要表示调试会话的状态、调试器的设置以及窗口布局的设置等。工作空间的使用主要分为以下几点：

    未加载任何调试文件的时候，选择File -> Save Workspace保存默认工作空间，则当每次打开Windbg的时候，将采用这个默认的工作空间
    当调试器已经加载了调试文件的时候，选择File -> Save Workspace将当前工作空间保存为默认工作空间 （这个默认空间仅针对这个调试文件），则当下次还是调试这个文件的时候，则采用之前保存的默认工作空间。
    可以选择File -> Save Workspace As...保存为命名的工作空间，在以后调试应用程序的时候可以选择File -> Open Workspace去打开指定的工作空间
    以上的工作空间都保存在注册表项HKEY_CURRENT_USER\Software\Microsoft\Windbg\Workspaces里面，你也可以通过File -> Save Worksapce to File...将工作空间保存到文件

## Windbg的命令分类

Windbg主要分为3大类的调试命令:

    标准命令 (Standard Command): 这类命令对于所有的调试目标都适用，比如常见的k命令;
    元命令 (Meta-Command)： 这类目标主要针对特定的目标所做的扩展命令，比如常见的.sympath命令。因为这类命令前面都有一个.,所以也叫作Dot-Command；
    扩展命令 (Extension Command)：标准命令和元命令都是Windbg内建的命令，而扩展命令是实现在动态加载的DLL中。这类命令前面都有一个!, 比如常用!analyze -v.

顺便在这里提一个很实用的命令.hh，用来在Windbg中打开帮助文档，比如使用.hh k则帮助文档会打开到索引k命令处。
--------------------- 
作者：河边一支柳 
来源：CSDN 
原文：https://blog.csdn.net/cjf_iceking/article/details/51955540 
版权声明：本文为博主原创文章，转载请附上博文链接！


## Other
https://www.cnblogs.com/kekec/archive/2012/11/14/2755924.html

### **#使用windbg**

#### **0. Attach方式**

启动windbg，使用菜单【Attach to a Process】，可以选择注入到现在正在运行的某个进程中。

注入到进程中后，进程被暂停执行，windbg处于可输入命令状态，但此时当前线程为windbg产生的线程。

按g继续运行进程时，windbg会随即销毁该线程。

![](https://images2017.cnblogs.com/blog/78946/201711/78946-20171101002305107-1661537787.png)

如果要观察主线程堆栈，需要切换到主线程（0号线程）（在windbg命令窗口输入这个命令，然后回车）：

> ~0s

当程序出现CPU占用100%的情况时，通常可以使用这种方式进行注入，然后切换到占用CPU的线程，

同时根据需要使用单步跟踪、设置断点等手段，来判断是何处的代码导致CPU100%问题。

#### **1. Open Executable方式**

使用【Open Executable】方式，可以通过windbg启动被调试程序。在这种方式下，被调试程序从启动时刻起就在调试器的监控之下。

对于一些在程序启动过程中产生的异常，可以使用这种方式进行调试。

#### **2. Just in time Debugger 方式 （JIT）**

当进程产生结构化异常时，如果进程不作处理，也没有调试器在监控这个进程，那么windows就会调用默认的调试器来调试发生异常的进程。

通过把windbg设置为Just in time Debugger，可以在任意进程发生异常时自动调用windbg来进行调试。

在注册表编辑器中修改下面的注册表项：

HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\AeDebug

HKEY_LOCAL_MACHINE\Software\Wow6432Node\Microsoft\Windows NT\CurrentVersion\AeDebug  // 注：64位系统上的32位程序使用该注册表项

Debugger键值修改为下面的取值 "D:\Tools\windbg.exe " -p %ld -e %ld

注1：将例中windbg.exe的路径替换为本机windbg绝对路径即可

注2：一般该值为："C:\Windows\system32\vsjitdebugger.exe" -p %ld -e %ld

#### **3\. Dump文件**

为了分析程序发生异常的原因，还可以借助Dump文件。

当异常发生时，把进程当前的信息保存到一个Dump文件中，再把该Dump文件发送给分析者，由分析者通过windbg进行分析。

![Dump分类](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200708015749367-824281289.png)


##### 内核dump：（**蓝屏**后，由系统生成）

1\. 完全内存转储。这个文件比较大，和物理内存相当，包含了程序崩溃前系统及用户模式下的所有信息。
2\. 核心内存转储。这个文件大小约物理内存的三分之一，主要包含崩溃前系统内核的所有信息。一般为了分析内核错误，就选用这种文件。
3\. 小内存转储（MiniDump）。保存内存前64KB的基本空间数据，主要包含crash进程及crash线程内核上下文信息，crash线程内核模式堆栈，加载的驱动和模块等信息。

![Dump1](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200708015815769-290452424.png)

```
问题签名:
  问题事件名称:	BlueScreen
  OS 版本:	6.1.7601.2.1.0.256.48
  区域设置 ID:	2052

有关该问题的其他信息:
  BCCode:	1000007e
  BCP1:	FFFFFFFFC0000005
  BCP2:	FFFFF80004CCC0E4
  BCP3:	FFFFF88004993668
  BCP4:	FFFFF88004992EC0
  OS Version:	6_1_7601
  Service Pack:	1_0
  Product:	256_1

有助于描述该问题的文件:
  C:\Windows\Minidump\060717-10280-01.dmp
  C:\Users\nicochen\AppData\Local\Temp\WER-41964-0.sysdata.xml

联机阅读隐私声明:
  http://go.microsoft.com/fwlink/?linkid=104288&clcid=0x0804

如果无法获取联机隐私声明，请脱机阅读我们的隐私声明:
  C:\Windows\system32\zh-CN\erofflps.txt
```
[Dump2](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200708015835191-275032785.png)


##### 不同信息量的minidump：

    (1)标准的minidump。包含了相对比较少的信息，适合在做在线分析：系统信息、加载的模块（DLL）信息、进程信息和线程信息。
        .dump /m c:\stardardMini.dmp（注：不指定/m和/f，/m为缺省选项）

    (2) full dump。在内核模式下，生成完全内存转储；用户模式下，最好不使用（/ma和/mf是更好的选择，生成出的dump信息也更丰富一些）
        .dump /f c:\fullMini.dmp

    (3)带有尽量多选项的minidump。包括完整的内存内容、句柄、未加载的模块，等等。文件很大（本机和局域网环境适用）~
        .dump /ma c:\bigMini.dmp（注：/ma等价于/mfFhut；/m的子参数包括：a,A,f,F,h,u,t,i,p,w,d,c,r,R ）.[dump命令详细用法](https://msdn.microsoft.com/en-us/library/windows/hardware/ff562428(v=vs.85).aspx)


##### 下面列出六种生成Dump文件的方法：

(1)在产品代码中加入自动生成Dump文件功能

使用下面的函数，可以生成一个Dump文件：
```
BOOL MiniDumpWriteDump (
HANDLE hProcess,
DWORD ProcessId,
HANDLE hFile,
MINIDUMP_TYPE DumpType,
PMINIDUMP_EXCEPTION_INFORMATION ExceptionParam,
PMINIDUMP_USER_STREAM_INFORMATION UserStreamParam,
PMINIDUMP_CALLBACK_INFORMATION CallbackParam
);
```
这个函数定义在**dbghelp.dll**中，windbg安装目录中带有这个dll，同时在sdk子目录中提供了.h和.lib文件。
在进程捕捉结构化异常的地方，使用这个API生成一个Dump文件。

(2) 使用AdPlus生成Dump文件
windbg附带了一个AdPlus的脚本，可以用于监控进程运行情况，并且可以在发生异常时把进程信息写入到Dump文件中。
如果产品没有自动生成Dump文件的功能，可以通过使用这个工具来弥补缺陷。

通过如下命令来使用AdPlus：

    cscript D:\tools\windbg\adplus.vbs -crash -pn DebugTest.exe -o D:\CrashDumps

上述命令的意思是：监控当前运行的DebugTest.exe，如果发生了结构化异常，则生成一个Dump文件到D:\CrashDumps目录中。
关于AdPlus更详细的介绍请参阅：[http://support.microsoft.com/kb/286350/zh-cn](http://support.microsoft.com/kb/286350/zh-cn)


(3) 使用windbg生成Dump文件
windbg可以通过命令生成mini-Dump文件：

    .dump /mfh D:\CrashDumps\mydumpfile.dmp

(4) win7任务管理器 - 进程标签页 - 创建转储文件

(5) 使用vs2010以上版本生成  在调试状态下【菜单】：调试 - 将转储另存为

(6) 第三方系统工具  如：最新版本的Process Explorer、proccump.exe命令行工具等


##### **分析Dump文件**

使用菜单【Open Crash Dump】打开Dump文件，然后打开堆栈观察窗口，此时看到的堆栈可能不是异常发生时的堆栈。

通过如下命令切换到异常发生时的堆栈：

    .ecxr

为了分析异常，可以通过下面的语句来获取分析信息，帮助定位问题：

    !analyze -v

# Windbg实用手册
https://blog.csdn.net/aoebug/article/details/51997221

#  windbg dump demo 
http://www.debuginfo.com/examples/effmdmpexamples.html
Demo可以下载到

## MiniDumpWriteDump API DEMO
http://www.debuginfo.com/examples/src/effminidumps/MiniDump.cpp
```cpp
///////////////////////////////////////////////////////////////////////////////
//
// MiniDump.cpp 
//
// Sample approach to collecting data with MiniDumpWriteDump and MiniDumpCallback 
// 
// Author: Oleg Starodumov (www.debuginfo.com)
//
//


///////////////////////////////////////////////////////////////////////////////
// Include files 
//

#include <windows.h>
#include <tchar.h>
#include <dbghelp.h>
#include <stdio.h>
#include <crtdbg.h>


///////////////////////////////////////////////////////////////////////////////
// Directives 
//

#pragma comment ( lib, "dbghelp.lib" )


///////////////////////////////////////////////////////////////////////////////
// Function declarations 
//

void CreateMiniDump( EXCEPTION_POINTERS* pep ); 

BOOL CALLBACK MyMiniDumpCallback(
	PVOID                            pParam, 
	const PMINIDUMP_CALLBACK_INPUT   pInput, 
	PMINIDUMP_CALLBACK_OUTPUT        pOutput 
); 


///////////////////////////////////////////////////////////////////////////////
// Test data and code 
//

struct A 
{
	int a; 

	A() 
		: a( 0 ) {}

	void Print() 
	{
		_tprintf( _T("a: %d\n"), a ); 
	}
};

struct B 
{
	A* pA; 

	B() 
		: pA( 0 ) {}

	void Print() 
	{
		_tprintf( _T("pA: %x\n"), pA ); 
		pA->Print(); 
	}

};

void DoWork() 
{
	B* pB = new B(); // but forget to initialize B::pA 

	pB->Print(); // here it should crash 
}


///////////////////////////////////////////////////////////////////////////////
// main() function 
//

int main( int argc, char* argv[] ) 
{
	__try 
	{
		DoWork(); 
	}
	__except( CreateMiniDump( GetExceptionInformation() ), EXCEPTION_EXECUTE_HANDLER ) 
	{
	}

	return 0; 
}


///////////////////////////////////////////////////////////////////////////////
// Minidump creation function 
//

void CreateMiniDump( EXCEPTION_POINTERS* pep ) 
{
	// Open the file 

	HANDLE hFile = CreateFile( _T("MiniDump.dmp"), GENERIC_READ | GENERIC_WRITE, 
		0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL ); 

	if( ( hFile != NULL ) && ( hFile != INVALID_HANDLE_VALUE ) ) 
	{
		// Create the minidump 

		MINIDUMP_EXCEPTION_INFORMATION mdei; 

		mdei.ThreadId           = GetCurrentThreadId(); 
		mdei.ExceptionPointers  = pep; 
		mdei.ClientPointers     = FALSE; 

		MINIDUMP_CALLBACK_INFORMATION mci; 

		mci.CallbackRoutine     = (MINIDUMP_CALLBACK_ROUTINE)MyMiniDumpCallback; 
		mci.CallbackParam       = 0; 

		MINIDUMP_TYPE mdt       = (MINIDUMP_TYPE)(MiniDumpWithIndirectlyReferencedMemory | MiniDumpScanMemory); 

		BOOL rv = MiniDumpWriteDump( GetCurrentProcess(), GetCurrentProcessId(), 
			hFile, mdt, (pep != 0) ? &mdei : 0, 0, &mci ); 

		if( !rv ) 
			_tprintf( _T("MiniDumpWriteDump failed. Error: %u \n"), GetLastError() ); 
		else 
			_tprintf( _T("Minidump created.\n") ); 

		// Close the file 

		CloseHandle( hFile ); 

	}
	else 
	{
		_tprintf( _T("CreateFile failed. Error: %u \n"), GetLastError() ); 
	}

}


///////////////////////////////////////////////////////////////////////////////
// Custom minidump callback 
//

BOOL CALLBACK MyMiniDumpCallback(
	PVOID                            pParam, 
	const PMINIDUMP_CALLBACK_INPUT   pInput, 
	PMINIDUMP_CALLBACK_OUTPUT        pOutput 
) 
{
	BOOL bRet = FALSE; 


	// Check parameters 

	if( pInput == 0 ) 
		return FALSE; 

	if( pOutput == 0 ) 
		return FALSE; 


	// Process the callbacks 

	switch( pInput->CallbackType ) 
	{
		case IncludeModuleCallback: 
		{
			// Include the module into the dump 
			bRet = TRUE; 
		}
		break; 

		case IncludeThreadCallback: 
		{
			// Include the thread into the dump 
			bRet = TRUE; 
		}
		break; 

		case ModuleCallback: 
		{
			// Does the module have ModuleReferencedByMemory flag set ? 

			if( !(pOutput->ModuleWriteFlags & ModuleReferencedByMemory) ) 
			{
				// No, it does not - exclude it 

				wprintf( L"Excluding module: %s \n", pInput->Module.FullPath ); 

				pOutput->ModuleWriteFlags &= (~ModuleWriteModule); 
			}

			bRet = TRUE; 
		}
		break; 

		case ThreadCallback: 
		{
			// Include all thread information into the minidump 
			bRet = TRUE;  
		}
		break; 

		case ThreadExCallback: 
		{
			// Include this information 
			bRet = TRUE;  
		}
		break; 

		case MemoryCallback: 
		{
			// We do not include any information here -> return FALSE 
			bRet = FALSE; 
		}
		break; 

		case CancelCallback: 
			break; 
	}

	return bRet; 

}

```
