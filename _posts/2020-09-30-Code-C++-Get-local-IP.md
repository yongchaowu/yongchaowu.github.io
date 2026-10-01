---
layout: post
title: C++-Get local IP
date: 2020-09-30 13:23:00
categories:
- Programming
tags:
- Code
- C++
---
September 30, 2020 1:17 PM

##使用Windows Socket API
库：wsock32.lib
头文件：
- winsock.h
- wsipx.h
- wsnwlink.h
- stdio.h

<!--more-->

涉及函数：
- gethostname
- gethostbyname
- inet_ntoa
涉及结构体：hostent

Code：
``` c++
#pragma comment(lib, "wsock32.lib")

#include <winsock.h>
#include <wsipx.h>
#include <wsnwlink.h>
#include <stdio.h>
#include <cstring>

int main()
{
	////////////////
	// Initialize windows sockets API. Ask for version 1.1
	//
	WORD wVersionRequested = MAKEWORD(1, 1);
	WSADATA wsaData;
	if (WSAStartup(wVersionRequested, &wsaData)) {
		printf("WSAStartup failed %d\n", WSAGetLastError());
		return -1;
	}

	//////////////////
	// Get host name.
	//
	char hostname[256];
	int res = gethostname(hostname, sizeof(hostname));
	if (res != 0) {
		printf("Error: %u\n", WSAGetLastError());
		return -1;
	}
	printf("hostname=%s\n", hostname);

	////////////////
	// Get host info for hostname. 
	//
	hostent* pHostent = gethostbyname(hostname);
	if (pHostent == NULL) {
		printf("Error: %u\n", WSAGetLastError());
		return -1;
	}

	//////////////////
	// Parse the hostent information returned
	//
	hostent& he = *pHostent;
	const char *alias = (he.h_aliases && he.h_aliases[0]) ? he.h_aliases[0] : "";
	printf("name=%s\naliases=%s\naddrtype=%d\nlength=%d\n",
		he.h_name, alias, he.h_addrtype, he.h_length);

	printf("name=%s\naliases=%s\naddrtype=%d\nlength=%d\n",
		pHostent->h_name, alias, pHostent->h_addrtype, pHostent->h_length);

	sockaddr_in sa;
	for (int nAdapter = 0; he.h_addr_list[nAdapter]; nAdapter++) {
		std::memcpy(&sa.sin_addr.s_addr, he.h_addr_list[nAdapter], he.h_length);
		// Output the machines IP Address.
		printf("Address: %s\n", inet_ntoa(sa.sin_addr)); // display as string
	}

	//////////////////
	// Terminate windows sockets API
	//
	WSACleanup();

	return 0;
}
```

参考：[Microsoft Learn：`WSAGetLastError`](https://learn.microsoft.com/en-us/windows/win32/api/winsock/nf-winsock-wsagetlasterror) 和 [`HOSTENT`](https://learn.microsoft.com/en-us/windows/win32/api/winsock/ns-winsock-hostent)。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 02:02（UTC+08:00）。