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

<!--more-->
```cpp
//getUserName.c
#include <iostream>
#include <string>

using namespace std;

#ifdef linux
	#include <unistd.h>
	#include <pwd.h>
#endif
#ifdef _WIN32
	#include <Windows.h>
#endif

std::string getUserName()
{
#ifdef linux
	uid_t userid;
	struct passwd* pwd;
	userid = getuid();
	pwd = getpwuid(userid);
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
