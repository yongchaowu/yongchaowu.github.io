---
layout: post
title: Linux-C-GetUserName
display_title: 'Linux C GetUserName'
date: 2021-01-08 19:52:00
categories:
- Systems
tags:
- Linux
- C
---
1. code

```
//getUserName.c
#include <iostream>
#include <string>

<!--more-->

using namespace std;

#ifdef __linux__
	#include <unistd.h>
	#include <pwd.h>
#endif
#ifdef _WIN32
	#include <Windows.h>
#endif

std::string getUserName()
{
#ifdef __linux__
	uid_t userid;
	struct passwd* pwd;
	userid = getuid();
	pwd = getpwuid(userid);
	if (!pwd)
		return "";
	return pwd->pw_name;
#elif _WIN32
	const int MAX_LEN = 100;
	char szBuffer[MAX_LEN];
	DWORD len = MAX_LEN;
	if(GetUserName(szBuffer,len))
	return szBuffer;
#endif
	return "";
}

int main()
{
	string name = getUserName();
	cout << "Hello World!" << name << endl;
	return 0;
}
```

2. 编译运行

```
g++ getUserName.c
./a.out
```

本文修订依据：POSIX Issue 8 [`getpwuid()`](https://pubs.opengroup.org/onlinepubs/9799919799/functions/getpwuid.html) 和 GCC 文档 [`System-specific Predefined Macros`](https://gcc.gnu.org/onlinedocs/cpp/System-specific-Predefined-Macros.html)。POSIX 规定找不到条目或发生错误时 `getpwuid()` 可能返回空指针；GCC 文档要求新代码优先使用保留名称的系统宏，因此示例改用 `__linux__`。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 08:33（UTC+08:00）。修订仅将 Linux 判断改为保留系统宏，并处理 `getpwuid()` 返回空指针的情况。
