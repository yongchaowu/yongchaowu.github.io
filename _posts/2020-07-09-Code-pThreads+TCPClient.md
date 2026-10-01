---
layout: post
title: pThreads+TCPClient
display_title: 'pThreads + TCP Client'
date: 2020-07-09 21:02:00
categories:
- Programming
tags:
- Code
- C++
- Open Source
---
` rc:return code`

> **API 范围：** 以下按 Winsock 2.2 的 API 合约校对；`SOCKET` 失败值使用 `INVALID_SOCKET`，数据收发函数失败值使用 `SOCKET_ERROR`。`GetResponseByCmd` 片段假定调用方已经完成 `InitSocket()`；若独立使用，需要自行配对 `WSAStartup`/`WSACleanup`。

<!--more-->

```language
#include <windows.h>
#include "pThreads/pthread.h"
#pragma comment(lib, "./x64/pthreadVC2.lib")

void* thFunction(LPVOID lpParam);
bool InitSocket();

int main()
{
	pthread_t m_pThtid;
	pthread_create(&m_pThtid, NULL, thFunction, this);
    while(1)
    {
    	Sleep(1000);
    }
    return 0;
}

void* thFunction(LPVOID lpParam)
{
	pthread_t myid = pthread_self();

	if (lpParam == NULL)
		return NULL;

	if (!InitSocket()) {
		return NULL;
	}

	SOCKET s_fd = INVALID_SOCKET;
	if ((s_fd = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET)
	{
		WSACleanup();
		return NULL;
	}

	SOCKADDR_IN s_fdServer;
	//memset(&s_fdServer, 0, sizeof(s_fdServer));
	s_fdServer.sin_family = AF_INET;
	s_fdServer.sin_port = htons(6800);
	s_fdServer.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");

		if (connect(s_fd, (SOCKADDR*)&s_fdServer, sizeof(SOCKADDR)) == SOCKET_ERROR)
		{
			Sleep(10000);
			closesocket(s_fd);
			WSACleanup();
			return NULL;
		}

		while (1)
		{
        	//int sendLen = send(s_fd, "Get Lic.", 100, 0);
			int sendLen = sendto(s_fd, "Get Lic.", sizeof("Get Lic.") - 1, 0, (SOCKADDR*)&s_fdServer, sizeof(SOCKADDR));
			if (sendLen == SOCKET_ERROR) {
				cout << "发送失败！" << endl;
				break;
			}
			char szBuf[65535];
			memset(szBuf, 0, sizeof(szBuf));
			int nLen = sizeof(s_fdServer);
            //int recvLen = recv(s_fd, szBuf, 65535, 0);
			int recvLen = recvfrom(s_fd, szBuf, 65535, 0, (SOCKADDR*)&s_fdServer, &nLen);
			if (recvLen == SOCKET_ERROR) {
				cout << "接受失败！" << endl;
				break;
			}

			printf("%s\n", szBuf);
		}

	//关闭套接字
	closesocket(s_fd);
	//释放DLL资源
	WSACleanup();
	return NULL;
}

bool InitSocket()
{
	//初始化套接字库
	WORD w_req = MAKEWORD(2, 2);//版本号
	WSADATA wsadata = {};
	int err = WSAStartup(w_req, &wsadata);
	if (err != 0) {
		cout << "初始化套接字库失败！" << endl;
		return false;
	}
	cout << "初始化套接字库成功！" << endl;
	//检测协商后应使用的版本号
	if (LOBYTE(wsadata.wVersion) != 2 || HIBYTE(wsadata.wVersion) != 2) {
		cout << "套接字库版本号不符！" << endl;
		WSACleanup();
		return false;
	}
	cout << "套接字库版本正确！" << endl;
	//填充服务端地址信息
	return true;
}

```

```language
int GetResponseByCmd(const char* pszCmd)
{
	if (pszCmd == NULL)
	{
		return -1;
	}

	SOCKET s_fd = INVALID_SOCKET;
	if ((s_fd = socket(AF_INET, SOCK_STREAM, 0)) == INVALID_SOCKET)
	{
		return -1;
	}

	SOCKADDR_IN s_fdServer;
	//memset(&s_fdServer, 0, sizeof(s_fdServer));
	s_fdServer.sin_family = AF_INET;
	s_fdServer.sin_port = htons(6800);
	s_fdServer.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");

	int nNetTimeout = 5000;
	setsockopt(s_fd, SOL_SOCKET, SO_RCVTIMEO, (char *)&nNetTimeout, sizeof(int));

	if (connect(s_fd, (SOCKADDR*)&s_fdServer, sizeof(SOCKADDR)) == SOCKET_ERROR)
	{
		closesocket(s_fd);
		return -1;
	}

	int sendLen = sendto(s_fd, pszCmd, strlen(pszCmd), 0, (SOCKADDR*)&s_fdServer, sizeof(SOCKADDR));
	if (sendLen == SOCKET_ERROR)
	{
		closesocket(s_fd);
		return -1;
	}
	char szBuf[65535];
	memset(szBuf, 0, sizeof(szBuf));

	int nLen = sizeof(s_fdServer);
	int recvLen = recvfrom(s_fd, szBuf, 65535, 0, (SOCKADDR*)&s_fdServer, &nLen);
	if (recvLen == SOCKET_ERROR) {
		closesocket(s_fd);
		return -1;
	}

	printf("%s\n", szBuf);

	return 0;
}
```

---

本文修订依据：Microsoft Learn [`socket`](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-socket)、[`sendto`](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-sendto)、[`recvfrom`](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-recvfrom) 和 [`WSAStartup`](https://learn.microsoft.com/en-us/windows/win32/api/winsock2/nf-winsock2-wsastartup)（页面元数据更新于 2024-02-22）。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 07:59（UTC+08:00）。修订仅纠正 Winsock 错误哨兵、版本协商、缓冲区长度和连接失败控制流。
