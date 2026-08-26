---
layout: post
title: C++-Code-Time Transfer-Windows FILETIME(1601) To 1970 UTC
date: 2020-11-28 17:00:00
categories:
- C & C++
tags:
- Time
- Code
- C++
---

November 28, 2020 4:56 PM

<!--more-->
最近遇到需要进行时间转换的实现。
以下是从mongoose.c中截取的，与之后在网上找到的思路是一致的。
## Function
```c++
double cs_time(void) {
  double now;
#ifndef _WIN32
  struct timeval tv;
  if (gettimeofday(&tv, NULL /* tz */) != 0) return 0;
  now = (double) tv.tv_sec + (((double) tv.tv_usec) / 1000000.0);
#else
  SYSTEMTIME sysnow;
  FILETIME ftime;
  GetLocalTime(&sysnow);
  SystemTimeToFileTime(&sysnow, &ftime);
  /*
   * 1. VC 6.0 doesn't support conversion uint64 -> double, so, using int64
   * This should not cause a problems in this (21th) century
   * 2. Windows FILETIME is a number of 100-nanosecond intervals since January
   * 1, 1601 while time_t is a number of _seconds_ since January 1, 1970 UTC,
   * thus, we need to convert to seconds and adjust amount (subtract 11644473600
   * seconds)
   */
  now = (double) (((int64_t) ftime.dwLowDateTime +
                   ((int64_t) ftime.dwHighDateTime << 32)) /
                  10000000.0) -
        11644473600;
#endif /* _WIN32 */
  return now;
}
```

## 网上抄的代码
转自[Windows中的时间(SYSTEMTIME和FILETIME)](https://www.cnblogs.com/liquntao/articles/9785601.html)
```c++
#include <iostream>

using namespace std;

#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <windows.h>


int main()
{
    SYSTEMTIME      stLocal, stUTC, stUTC2;
    FILETIME        ftLocal, ftUTC, ft;
    ULARGE_INTEGER  uli;

    GetLocalTime(&stLocal);
    GetSystemTime(&stUTC);
    printf("Local System Time(YYYY-MM-DD HH:MM:SS): %d-%d-%d %d:%d:%d\n", stLocal.wYear, stLocal.wMonth,
        stLocal.wDay, stLocal.wHour, stLocal.wMinute, stLocal.wSecond);
    printf("UTC System Time  (YYYY-MM-DD HH:MM:SS): %d-%d-%d %d:%d:%d\n", stUTC.wYear, stUTC.wMonth,
        stUTC.wDay, stUTC.wHour, stUTC.wMinute, stUTC.wSecond);

    SystemTimeToFileTime(&stLocal, &ftLocal);
    uli.LowPart = ftLocal.dwLowDateTime;
    uli.HighPart = ftLocal.dwHighDateTime;
    printf("Local File Time: %llu\n", uli.QuadPart);

    LocalFileTimeToFileTime(&ftLocal, &ftUTC);
    uli.LowPart = ftUTC.dwLowDateTime;
    uli.HighPart = ftUTC.dwHighDateTime;
    printf("UTC File Time: %llu\n", uli.QuadPart);

    FileTimeToSystemTime(&ftUTC, &stUTC2);
    printf("UTC System Time2 (YYYY-MM-DD HH:MM:SS): %d-%d-%d %d:%d:%d\n", stUTC2.wYear, stUTC2.wMonth,
        stUTC2.wDay, stUTC2.wHour, stUTC2.wMinute, stUTC2.wSecond);

    return EXIT_SUCCESS;
}

```