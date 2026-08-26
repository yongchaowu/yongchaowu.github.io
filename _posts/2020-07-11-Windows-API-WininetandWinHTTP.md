---
layout: post
title: Windows API-Wininet&WinHTTP
date: 2020-07-11 22:36:00
categories:
- Systems
tags:
- WinHTTP
- Wininet
- Windows API
---

July 11, 2020 10:33 PM

<!--more-->
# WinInet

WinInet（“Windows Internet”）API帮助程序员使用三个常见的Internet协议，这三个协议是用于World Wide Web万维网的[超文本](https://baike.baidu.com/item/%E8%B6%85%E6%96%87%E6%9C%AC)[传输协议](https://baike.baidu.com/item/%E4%BC%A0%E8%BE%93%E5%8D%8F%E8%AE%AE)（HTTP：Hypertext Transfer Protocol）、[文件传输协议](https://baike.baidu.com/item/%E6%96%87%E4%BB%B6%E4%BC%A0%E8%BE%93%E5%8D%8F%E8%AE%AE/1874113)（FTP：File Transfer Protocol）和另一个称为Gopher的文件传输协议。WinInet函数的语法与常用的Win32 API函数的语法类似，这使得使用这些协议就像使用本地硬盘上的文件一样容易。

## WinInet 概述

⊙ Hinternet 句柄的层次关系

⊙ HTTP 函数层次关系

⊙ 典型的 HTTP 客户端程序的处理流程

1、普通 WinInet 处理函数

⊙ [InternetOpen](https://baike.baidu.com/item/InternetOpen) 初始化 WinInet.dll

⊙ [InternetOpenUrl](https://baike.baidu.com/item/InternetOpenUrl) 打开 Url，读取数据

⊙ InternetAttemptConnect 尝试建立到 Internet 的连接

⊙ InternetConnect 建立 Internet 的连接

⊙ InternetCheckConnection 检查 Internet 的连接是否能够建立

⊙ InternetSetOption 设置一个 Internet 选项

⊙ InternetSetStatusCallback 安装一个[回调函数](https://baike.baidu.com/item/%E5%9B%9E%E8%B0%83%E5%87%BD%E6%95%B0)，供 API [函数调用](https://baike.baidu.com/item/%E5%87%BD%E6%95%B0%E8%B0%83%E7%94%A8)

⊙ InternetQueryOption 查询在一个指定句柄上的 Internet 选项

⊙ InternetQueryDataAvailable 查询可用数据的数量

⊙ InternetReadFile(Ex) 从一个打开的句柄读取数据

⊙ InternetFindNextFile 继续文件搜寻

⊙ InternetSetFilePointer 为 InternetReadFile 设置一个文件位置

⊙ InternetWriteFile 将数据写到一个打开的 Internet 文件

⊙ InternetLockRequestFile 允许用户为正在使用的文件加锁

⊙ InternetUnlockRequestFile 解锁被锁定的文件

⊙ InternetTimeFromSystemTime 根据指定的 RFC 格式格式化日期和时间

⊙ InternetTimeToSystemTime 将一个 HTTP 时间/日期字串格式化为 SystemTime 结构对象

⊙ InternetConfirmZoneCrossing 检查在安全 URL 和非安全 URL 间的变化

⊙ InternetCloseHandle 关闭一个单一的 Internet 句柄

⊙ InternetErrorDlg 显示错误信息对话框

⊙ InternetGetLastResponseInfo 获取最近发送的 API函数的错误

2、HTTP 处理函数

⊙ HttpOpenRequest 打开一个 HTTP 请求的句柄

⊙ HttpSendRequest(Ex) 向 HTTP 服务器发送指定的请求

⊙ HttpQueryInfo 查询有关一次 HTTP 请求的信息

⊙ HttpEndRequest 结束一个 HTTP 请求

⊙ HttpAddRequestHeaders 添加一个或多个 HTTP 请求报头到 HTTP请求句柄

3、FTP 处理函数

⊙ FtpCreateDirectory 在 Ftp 服务器新建一个目录

⊙ FtpDeleteFile 删除存储在 Ftp 服务器上的文件

⊙ FtpFindFirstFile 查找给定 Ftp 会话中的指定目录

⊙ FtpGetCurrentDirectory 为指定 Ftp 会话获取当前目录

⊙ FtpGetFile 从 Ftp 服务器下载文件

⊙ FtpOpenFile 访问一个远程文件以对其进行读写

⊙ FtpPutFile 向 Ftp 服务器上传文件

⊙ FtpRemoveDirectory 在 Ftp 服务器删除指定的目录

⊙ FtpRenameFile 为 Ftp 服务器上的指定文件改名

⊙ FtpSetCurrentDirectory 更改在 Ftp 服务器上正在使用的目录

## WinInet 层关系

1、WinInet 是一个[网络编程](https://baike.baidu.com/item/%E7%BD%91%E7%BB%9C%E7%BC%96%E7%A8%8B)接口，包含了 Internet 底层协议 HTTP，FTP。

2、借助 WinInet 接口，可不必去了解 Winsock、TCP/IP 和特定 Internet 协议的细节就可以编写出高水平的 Internet 客户端程序。

3、WinInet 为 HTTP、FTP 提供了统一的函数集，也就是 Win32 API 接口。

4、WinInet 简化了 HTTP、FTP 协议的编程，可轻松地将 Internet 集成到应用程序中。

### Hinternet 句柄的层次关系

1、首先通过 [InternetOpen](https://baike.baidu.com/item/InternetOpen) 函数创建位于根部的 Hinternet 句柄，然后才能通过其进一步建立 HTTP、FTP 的连接。

2、使用 InternetConnect 函数创建一个指定的连接，它将通过传递给它的参数为指定的站点初始化 HTTP、FTP 连接并创建一个从根句柄分支出去的 Hinternet 句柄。

3、[HttpOpenRequest](https://baike.baidu.com/item/HttpOpenRequest) 和 FtpOpenFile、FtpFindFirstFile等函数将使用 InternetConnect 所创建的句柄以建立到指定站点的连接。

### HTTP 函数层次关系

1、对于 WWW 服务器提供的资源可以直接通过 [InternetOpenUrl](https://baike.baidu.com/item/InternetOpenUrl) 或是 HTTP 函数对潜在的协议进行处理来访问。

2、由于 HTTP 协议是在不断发展的，当这些底层协议被更新后也将影响这些 HTTP 函数行为

3、[InternetOpen](https://baike.baidu.com/item/InternetOpen)、InternetConnect、[HttpOpenRequest](https://baike.baidu.com/item/HttpOpenRequest) 将返回 Hinternet 句柄，而HttpAddRequestHeaders、HttpQueryInfo、HttpSendRequest、HttpSendRequestEx、InternetErrorDlg 将使用它们所依靠的这些函数创建的 Hinternet句柄。

### FTP 函数层次关系

1、FTP 函数需要请求得到特定类型的 Hinternet句柄才能正常工作，这些句柄的创建必须按一定次序来进行：

1、首先使用 [InternetOpen](https://baike.baidu.com/item/InternetOpen) 创建根句柄，然后才能通过 InternetConnect 创建一个FTP连接句柄

2、该图展示了依赖于 InternetConnect 所返回FTP 连接句柄的 FTP函数之间的层次关系。

### 典型的 HTTP 客户端程序的处理流程
1、目的：开始 HTTP会话，建立 HTTP 连接
方法：InternetOpen、InternetAttemptConnect、InternetConnect
结果：初始化 WinInet.dll 并联接服务器，返回相应的句柄

2、目的：创建一个 HTTP请求
方法：[HttpOpenRequest](https://baike.baidu.com/item/HttpOpenRequest)
结果：

3、目的：发送一个 HTTP请求
方法：HttpAddRequestHeaders
HttpSendRequest(Ex)
结果：

4、目的：读文件
方法：InternetReadFile(Ex)
结果：使用你提供的缓冲读指定的字节

5、目的：获取 HTTP请求信息
方法：HttpQueryInfo
结果：从服务器获取 HTTP 请求头信息

6、目的：[异常处理](https://baike.baidu.com/item/%E5%BC%82%E5%B8%B8%E5%A4%84%E7%90%86)
方法：InternetGetLastResponseInfo、InternetErrorDlg
结果：处理所有普通的异常类型

7、目的：结束 HTTP 会话
方法：HttpEndRequest、InternetCloseHandle
结果：自动清除打开的句柄的连接


### InternetOpen 初始化

#### InternetOpen(lpszAgent: PChar;
dwAccessType: DWORD;
lpszProxy,
lpszProxyBypass:PChar;
dwFlags: DWORD): HINTERNET; stdcall;

参数：
1、lpszAgent 应用程序名，可以自定义
2、dwAccessType 存取类型，可以是：
①INTERNET_OPEN_TYPE_PRECONFIG =0 使用 IE 中的连接设置
②INTERNET_OPEN_TYPE_DIRECT =1 直接连接到服务器
③INTERNET_OPEN_TYPE_PROXY =3 通过代理服务器进行连接
为 3 时需指定代理服务器地址

3、lpszProxy CERN 代理服务器地址，一般设置为 null;
4、lpszProxyBypass 代理服务器地址；
5、dwFlags 标记，一般设置为 0，可以是：
①INTERNET_FLAG_DONT_CACHE 不在缓存中保存取得的内容
②INTERNET_FLAG_OFFLINE 脱机方式


#### InternetOpenUrl   打开 Url，读取数据
InternetOpenUrl(hInet: HINTERNET;
lpszUrl: PChar;
lpszHeaders: PChar;
dwHeadersLength: DWORD;
dwFlags: DWORD;
dwContext: DWORD): HINTERNET; stdcall;

2、参数：

1、hInet 由 InternetOpen返回的句柄
2、lpszUrl 文件 Url 地址，以 http:，ftp: 打头的 Url 地址；
3、lpszHeaders 发送到服务器的数据头；
4、dwHeadersLength 发送到服务器的数据头长度
5、dwFlags 标记，可以是：
①INTERNET_FLAG_RELOAD 强制重读数据
②INTERNET_FLAG_DONT_CACHE 不保存到缓存
③INTERNET_FLAG_TRANSFER_ASCII 使用文本数据
④INTERNET_FLAG_TRANSFER_BINARY 使用二进制数据
6、dwContext 上下文标记，如果使用回调功能时这个值将传送给回调函数

### Internet 的连接

#### InternetConnect 
InternetConnect(hInet: HINTERNET;
lpszServerName: PChar;
nServerPort: INTERNET_PORT;
lpszUsername: PChar;
lpszPassword: PChar;
dwService: DWORD;
dwFlags: DWORD;
dwContext: DWORD): HINTERNET; stdcall;

参数：
1、hInet 由 InternetOpen 返回的句柄
2、lpszServerName 服务器的地址
HTTP 地址必须为服务器名作InternetOpenUrl语法分析
3、nServerPort HTTP协议端口号（缺省80）
4、lpszUsername 用户名
5、lpszPassword 用户密码
6、dwService 决定服务类型 HTTP，FTP，可以是：
①INTERNET_SERVICE_FTP = 1; 连接到一个 FTP 服务器上
②INTERNET_SERVICE_HTTP = 3; 连接到一个 HTTP 服务器上
7、dwFlags
8、dwContext

#### HttpOpenRequest
HttpOpenRequest(hConnect: HINTERNET;
lpszVerb: PChar;
lpszObjectName: PChar;
lpszVersion: PChar;
lpszReferrer: PChar;
lplpszAcceptTypes: PLPSTR;
dwFlags: DWORD;
dwContext: DWORD): HINTERNET; stdcall;

参数：
1、hConnect InternetConnect句柄
2、lpszVerb 命令字，如果为 NULL，使用缺省值“GET”
3、lpszObjectName 命令对象，通常是一个文件名、可执行文件或是一个搜索列表
4、lpszVersion HTTP版本，如果为空，将使用“HTTP/1.0”
5、lpszReferrer 一个网址，可以为空
6、lplpszAcceptTypes中程序接收的文件类型列表。把空值传给该函数即通知了服务器只有文本文件可以被接收'application/octet-stream'
7、dwFlags 标志 使用 or 连接标志
①INTERNET_FLAG_NO_CACHE_WRITE 标志不缓冲写
②INTERNET_FLAG_KEEP_CONNECTION 保持连接
③INTERNET_FLAG_SECURE { use PCT/SSL if applicable (HTTP) }
{ Security Ignore Flags, Allow HttpOpenRequest to overide
Secure Channel (SSL/PCT) failures of the following types. }
④INTERNET_FLAG_IGNORE_CERT_CN_INVALID { bad common name in X509 Cert. }
⑤INTERNET_FLAG_IGNORE_CERT_DATE_INVALID { expired X509 Cert. }
8、dwContext Integer(Self)？

### 向 HTTP 服务器发送指定的请求
#### HttpSendRequest
HttpSendRequest(hRequest: HINTERNET;
lpszHeaders: PChar;
dwHeadersLength: DWORD;
lpOptional: Pointer;
dwOptionalLength: DWORD): BOOL; stdcall;

参数：
1、hRequest HttpOpenRequest句柄
2、lpszHeaders 服务请求的数据头
3、dwHeadersLength 服务请求的数据头的长度
4、lpOptional 紧跟在标题后任意数据的地址，此参数一般用于 POST 和 PUT 操作
5、dwOptionalLength 数据的长度

#### InternetSetOption 
InternetSetOption 设置一个 Internet 选项

InternetSetOption(hInet: HINTERNET;
dwOption: DWORD;
lpBuffer: Pointer;
dwBufferLength: DWORD): BOOL; stdcall;

参数：
1、hInet 句柄
2、dwOption Internet 选项，可以是：
①INTERNET_OPTION_SEND_TIMEOUT 设置，发送请求和连接时的超时时间
②INTERNET_OPTION_RECEIVE_TIMEOUT 设置，接收请求和连接时的超时时间
3、lpBuffer 值
4、dwBufferLength 值大小






# WinHTTP
https://docs.microsoft.com/en-us/windows/desktop/winhttp/porting-wininet-applications-to-winhttp
## Code demo
| **Header** | winhttp.h |
| **Library** | Winhttp.lib |
| **DLL** | Winhttp.dll |
```cpp
    DWORD dwSize = 0;
    LPVOID lpOutBuffer = NULL;
    BOOL  bResults = FALSE;
    HINTERNET hSession = NULL,
              hConnect = NULL,
              hRequest = NULL;

    // Use WinHttpOpen to obtain a session handle.
    hSession = WinHttpOpen(  L"A WinHTTP Example Program/1.0",
                             WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                             WINHTTP_NO_PROXY_NAME,
                             WINHTTP_NO_PROXY_BYPASS, 0);

    // Specify an HTTP server.
    if (hSession)
        hConnect = WinHttpConnect( hSession, L"www.microsoft.com",
                                   INTERNET_DEFAULT_HTTP_PORT, 0);

    // Create an HTTP request handle.
    if (hConnect)
        hRequest = WinHttpOpenRequest( hConnect, L"GET", NULL,
                                       NULL, WINHTTP_NO_REFERER,
                                       WINHTTP_DEFAULT_ACCEPT_TYPES,
                                       0);

    // Send a request.
    if (hRequest)
        bResults = WinHttpSendRequest( hRequest,
                                       WINHTTP_NO_ADDITIONAL_HEADERS,
                                       0, WINHTTP_NO_REQUEST_DATA, 0,
                                       0, 0);

    // End the request.
    if (bResults)
        bResults = WinHttpReceiveResponse( hRequest, NULL);

    // First, use WinHttpQueryHeaders to obtain the size of the buffer.
    if (bResults)
    {
        WinHttpQueryHeaders( hRequest, WINHTTP_QUERY_RAW_HEADERS_CRLF,
                             WINHTTP_HEADER_NAME_BY_INDEX, NULL,
                             &dwSize, WINHTTP_NO_HEADER_INDEX);

        // Allocate memory for the buffer.
        if( GetLastError( ) == ERROR_INSUFFICIENT_BUFFER )
        {
            lpOutBuffer = new WCHAR[dwSize/sizeof(WCHAR)];

            // Now, use WinHttpQueryHeaders to retrieve the header.
            bResults = WinHttpQueryHeaders( hRequest,
                                       WINHTTP_QUERY_RAW_HEADERS_CRLF,
                                       WINHTTP_HEADER_NAME_BY_INDEX,
                                       lpOutBuffer, &dwSize,
                                       WINHTTP_NO_HEADER_INDEX);
        }
    }

    // Print the header contents.
    if (bResults)
        printf("Header contents: \n%S",lpOutBuffer);

    // Free the allocated memory.
    delete [] lpOutBuffer;

    // Report any errors.
    if (!bResults)
        printf("Error %d has occurred.\n",GetLastError());

    // Close any open handles.
    if (hRequest) WinHttpCloseHandle(hRequest);
    if (hConnect) WinHttpCloseHandle(hConnect);
    if (hSession) WinHttpCloseHandle(hSession);
```

WinHttpQueryDataAvailable\WinHttpReadData
```cpp
    DWORD dwSize = 0;
    DWORD dwDownloaded = 0;
    LPSTR pszOutBuffer;
    BOOL  bResults = FALSE;
    HINTERNET  hSession = NULL, 
               hConnect = NULL,
               hRequest = NULL;

    // Use WinHttpOpen to obtain a session handle.
    hSession = WinHttpOpen( L"WinHTTP Example/1.0",  
                            WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                            WINHTTP_NO_PROXY_NAME, 
                            WINHTTP_NO_PROXY_BYPASS, 0);

    // Specify an HTTP server.
    if (hSession)
        hConnect = WinHttpConnect( hSession, L"www.microsoft.com",
                                   INTERNET_DEFAULT_HTTPS_PORT, 0);

    // Create an HTTP request handle.
    if (hConnect)
        hRequest = WinHttpOpenRequest( hConnect, L"GET", NULL,
                                       NULL, WINHTTP_NO_REFERER, 
                                       WINHTTP_DEFAULT_ACCEPT_TYPES, 
                                       WINHTTP_FLAG_SECURE);

    // Send a request.
    if (hRequest)
        bResults = WinHttpSendRequest( hRequest,
                                       WINHTTP_NO_ADDITIONAL_HEADERS,
                                       0, WINHTTP_NO_REQUEST_DATA, 0, 
                                       0, 0);

    // End the request.
    if (bResults)
        bResults = WinHttpReceiveResponse( hRequest, NULL);

    // Continue to verify data until there is nothing left.
    if (bResults)
        do 
        {

            // Verify available data.
            dwSize = 0;
            if (!WinHttpQueryDataAvailable( hRequest, &dwSize))
                printf( "Error %u in WinHttpQueryDataAvailable.\n",
                        GetLastError());

            // Allocate space for the buffer.
            pszOutBuffer = new char[dwSize+1];
            if (!pszOutBuffer)
            {
                printf("Out of memory\n");
                dwSize=0;
            }
            else
            {
                // Read the Data.
                ZeroMemory(pszOutBuffer, dwSize+1);

                if (!WinHttpReadData( hRequest, (LPVOID)pszOutBuffer, 
                                      dwSize, &dwDownloaded))
                    printf( "Error %u in WinHttpReadData.\n", GetLastError());
                else
                    printf( "%s\n", pszOutBuffer);

                // Free the memory allocated to the buffer.
                delete [] pszOutBuffer;
            }

        } while (dwSize > 0);

    // Report any errors.
    if (!bResults)
        printf( "Error %d has occurred.\n", GetLastError());

    // Close open handles.
    if (hRequest) WinHttpCloseHandle(hRequest);
    if (hConnect) WinHttpCloseHandle(hConnect);
    if (hSession) WinHttpCloseHandle(hSession);
```
