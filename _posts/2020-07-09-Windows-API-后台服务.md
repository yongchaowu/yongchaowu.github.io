---
layout: post
title: "Windows API-后台服务"
date: 2020-07-09 08:12:00
categories: ["Windows API"]
tags: ["Backstage Service", "Windows API", "C++"]
---

## C++创建Windows后台服务程序
[C++创建Windows后台服务程序](https://blog.csdn.net/blade1080/article/details/82015323)

<!--more-->
服务程序通常编写成控制台类型的应用程序，一个遵守服务控制管理程序接口要求的程序包含下面三个函数：

- 服务程序主函数（main）：调用系统函数 StartServiceCtrlDispatcher 连接程序主线程到服务控制管理程序。
- 服务入口点函数（ServiceMain）：执行服务初始化任务，同时执行多个服务的服务进程有多个服务入口函数。
- 控制服务处理程序函数（Handler）：在服务程序收到控制请求时由控制分发线程引用。

```cpp
- 服务程序主函数
#include <iostream>
#include "Windows.h"

#define SERVICE_NAME "srv_demo"
SERVICE_STATUS ServiceStatus;
SERVICE_STATUS_HANDLE hServiceStatusHandle;

int main (int argc, const char *argv[])
{
    SERVICE_TABLE_ENTRY ServiceTable[2];

    ServiceTable[0].lpServiceName = SERVICE_NAME;
    ServiceTable[0].lpServiceProc = (LPSERVICE_MAIN_FUNCTION)service_main;

    ServiceTable[1].lpServiceName = NULL;
    ServiceTable[1].lpServiceProc = NULL;
    // 启动服务的控制分派机线程
    StartServiceCtrlDispatcher(ServiceTable); 
    return 0;
}

首先声明几个全局变量，以便在程序的多个函数之间共享它们值。之后在主函数中创建一个分派表。分派表是SERVICE_TABLE_ENTRY 类型结构，它有两个域：

- lpServiceName: 指向表示服务名称字符串的指针；当定义了多个服务时，那么这个域必须指定
- lpServiceProc: 指向服务主函数的指针（服务入口点）

一个程序可能包含若干个服务。每一个服务都必须列于分派表中，分派表的最后一项的两个域都必须为 NULL 指针。并且在只有一个服务的情况下，服务名是可选的。

StartServiceCtrlDispatcher函数启动服务的控制分派机线程，当分派表中所有的服务执行完之后（服务为停止状态），或发生运行时错误，该函数调用返回，进程终止。

```

```
-服务入口点函数

void WINAPI service_main(int argc, char** argv)
{
    ServiceStatus.dwServiceType        = SERVICE_WIN32;
    ServiceStatus.dwCurrentState       = SERVICE_START_PENDING;
    ServiceStatus.dwControlsAccepted   = SERVICE_ACCEPT_STOP | SERVICE_ACCEPT_SHUTDOWN | SERVICE_ACCEPT_PAUSE_CONTINUE;
    ServiceStatus.dwWin32ExitCode      = 0;
    ServiceStatus.dwServiceSpecificExitCode = 0;
    ServiceStatus.dwCheckPoint         = 0;
    ServiceStatus.dwWaitHint           = 0;
    hServiceStatusHandle = RegisterServiceCtrlHandler(SERVICE_NAME, ServiceHandler);
    if (hServiceStatusHandle==0)
    {
        DWORD nError = GetLastError();
    }
    //add your init code here

    //add your service thread here


    // Initialization complete - report running status
    ServiceStatus.dwCurrentState       = SERVICE_RUNNING;
    ServiceStatus.dwCheckPoint         = 0;
    ServiceStatus.dwWaitHint           = 9000;
    if(!SetServiceStatus(hServiceStatusHandle, &ServiceStatus))
    {
        DWORD nError = GetLastError();
    }

}

上面给出的是是服务的入口点函数示例代码。它运行在一个单独的线程当中，这个线程由控制分派器创建。该函数应尽快调用 RegisterServiceCtrlHadler 函数为服务注册控制处理器，注册完控制处理器之后，获得状态句柄（hServiceStatusHandle）。

ServiceStatus 结构的每个域的用途如下：
- dwServiceType ：指示服务类型，创建 Win32 服务。赋值 SERVICE_WIN32
- dwCurrentState ：指定服务的当前状态。因为服务的初始化在这里没有完成，所以这里的状态为SERVICE_START_PENDING
- dwControlsAccepted ：这个域通知 SCM 服务接受哪个域。本文例子是允许 STOP 和 SHUTDOWN 请求。处理控制请求将在第三步讨论
- dwWin32ExitCode 和 dwServiceSpecificExitCode ：这两个域在你终止服务并报告退出细节时很有用。初始化服务时并不退出，因此，它们的值为 0
- dwCheckPoint 和 dwWaitHint ：这两个域表示初始化某个服务进程时要30 秒以上。本文例子服务的初始化过程很短，所以这两个域的值都为 0

- SetServiceStatus 函数用于向 SCM 报告服务的状态。需要提供 hStatus 句柄和 ServiceStatus 结构。


```

```language
- 控制服务处理程序函数
void WINAPI ServiceHandler(DWORD fdwControl)
{
    switch(fdwControl)
    {
        case SERVICE_CONTROL_STOP:
        case SERVICE_CONTROL_SHUTDOWN:
        ServiceStatus.dwWin32ExitCode = 0;
        ServiceStatus.dwCurrentState  = SERVICE_STOPPED;
        ServiceStatus.dwCheckPoint    = 0;
        ServiceStatus.dwWaitHint      = 0;

        //add you quit code here

        break;
        default:
            return;
    };
    if (!SetServiceStatus(hServiceStatusHandle,  &ServiceStatus))
    {
        DWORD nError = GetLastError();
    }
}
在第二步中，我们用 RegisterServiceCtrlHadler函数注册了控制处理器函数。控制处理器与处理各种 Windows 消息的窗口回调函数非常类似。它检查 SCM 发送了什么请求并采取相应行动。

STOP 请求是 SCM 终止服务的时候发送的。例如，如果用户在“ 服务” 控制面板中手动终止服务。SHUTDOWN 请求是关闭机器时，由 SCM 发送给所有运行中服务的请求。两种情况的处理方式相同。

控制处理器函数必须报告服务状态，即便 SCM 每次发送控制请求的时候状态保持相同。因此，不管响应什么请求，都要调用 SetServiceStatus 。

```

- 创建一个服务
`sc cteate ServiceName binPath= "D:\server.exe"`
注意：该指令运行时需要管理员权限，且“=”后面必须空一格。
- 启动服务
`sc start ServiceName` 或 通过windows提供的控制界面来启动服务
若服务启动时出现如下错误信息：“服务没有及时响应启动或控制请求”，这是因为运行作为服务的应用程序不是按服务的流程写的。
- 停止服务
`sc stop ServiceName`
- 删除服务
`sc delete ServiceName`


main函数及service_main函数中均有argc、argv参数，可以向这两个函数中传递参数.
- 向main函数中传递参数需要在创建服务时指定:
`sc create atest binPath= "D:\Project Files\ImosServer\x64\Release  -port=1024"`
- 向service_main函数中传递参数需要在启动服务时指定
`sc start atest -port=1024`
- 测试代码段
```language
FILE* log = fopen("D:\\log.txt", "a");
for (int i = 0; i < argc; ++i)
{
    fprintf(log, "main: %s\n", argv[i]);
}
fclose(log);
```
————————————————
版权声明：本文为CSDN博主「blade1080」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/blade1080/java/article/details/82015323