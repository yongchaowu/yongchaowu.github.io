---
layout: post
title: "Code-pThreads+TCPClient"
date: 2020-07-09 21:02:00
categories: ["Code"]
tags: ["Code", "C++", "Open Source Library"]
---

` rc:return code`

<!--more-->
```cpp
#include <windows.h>
#include "pThreads/pthread.h"
#pragma comment(lib, "./x64/pthreadVC2.lib")
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

	InitSocket();

	SOCKET s_fd;
	if ((s_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
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
			break;
			//WSACleanup();
			//return NULL;
		}

		while (1)
		{
        	//int sendLen = send(s_fd, "Get Lic.", 100, 0);
			int sendLen = sendto(s_fd, "Get Lic.", 100, 0, (SOCKADDR*)&s_fdServer, sizeof(SOCKADDR));
			if (sendLen < 0) {
				cout << "发送失败！" << endl;
				break;
			}
			char szBuf[65535];
			memset(szBuf, 0, sizeof(szBuf));
			int nLen;
            //int recvLen = recv(s_fd, szBuf, 65535, 0);
			int recvLen = recvfrom(s_fd, szBuf, 65535, 0, (SOCKADDR*)&s_fdServer, &nLen);
			if (recvLen < 0) {
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


void InitSocket() 
{
	//初始化套接字库
	WORD w_req = MAKEWORD(2, 2);//版本号
	WSADATA wsadata;
	int err = -1;
	err = WSAStartup(w_req, &wsadata);
	if (err != 0) {
		cout << "初始化套接字库失败！" << endl;
	}
	else {
		cout << "初始化套接字库成功！" << endl;
	}
	//检测版本号
	if (LOBYTE(wsadata.wVersion) != 2 || HIBYTE(wsadata.wHighVersion) != 2) {
		cout << "套接字库版本号不符！" << endl;
		WSACleanup();
	}
	else {
		cout << "套接字库版本正确！" << endl;
	}
	//填充服务端地址信息

}

```

```cpp
int GetResponseByCmd(const char* pszCmd)
{
	if (pszCmd == NULL)
	{
		return -1;
	}

	SOCKET s_fd;
	if ((s_fd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
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
		//closesocket(s_fd);
		return -1;
	}

	int sendLen = sendLen = sendto(s_fd, pszCmd, strlen(pszCmd), 0, (SOCKADDR*)&s_fdServer, sizeof(SOCKADDR));
	if (sendLen < 0)
	{
		closesocket(s_fd);
		return -1;
	}
	char szBuf[65535];
	memset(szBuf, 0, sizeof(szBuf));

	int nLen;
	int recvLen = recvfrom(s_fd, szBuf, 65535, 0, (SOCKADDR*)&s_fdServer, &nLen);
	if (recvLen < 0) {
		closesocket(s_fd);
		return -1;
	}

	printf("%s\n", szBuf);

	return 0;
}
```
