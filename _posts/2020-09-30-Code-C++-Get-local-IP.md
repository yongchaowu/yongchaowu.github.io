---
layout: post
title: "Code-C++-Get local IP"
date: 2020-09-30 13:23:00
categories: ["Code"]
tags: ["Code", "C++"]
---

September 30, 2020 1:17 PM

<!--more-->
## 使用Windows Socket API
库：wsock32.lib
头文件：
- winsock.h
- wsipx.h
- wsnwlink.h
- stdio.h

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

int main()
{
	////////////////
	// Initialize windows sockets API. Ask for version 1.1
	//
	WORD wVersionRequested = MAKEWORD(1, 1);
	WSADATA wsaData;
	if (WSAStartup(wVersionRequested, &wsaData)) {
		printf("WSAStartup failed %u\n", WSAGetLastError());
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
	printf("name=%s\naliases=%s\naddrtype=%d\nlength=%d\n",
		he.h_name, he.h_aliases, he.h_addrtype, he.h_length);

	printf("name=%s\naliases=%s\naddrtype=%d\nlength=%d\n",
		pHostent->h_name, pHostent->h_aliases, pHostent->h_addrtype, pHostent->h_length);

	sockaddr_in sa;
	for (int nAdapter = 0; he.h_addr_list[nAdapter]; nAdapter++) {
		memcpy(&sa.sin_addr.s_addr, he.h_addr_list[nAdapter], he.h_length);
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