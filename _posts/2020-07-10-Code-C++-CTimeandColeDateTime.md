---
layout: post
title: C++-CTime&ColeDateTime
display_title: 'C++ CTime 与 COleDateTime'
date: 2020-07-10 02:24:00
categories:
- Programming
tags:
- Code
- C++
---
July 10, 2020 2:23 AM
[COleDateTime类型的应用](https://www.cnblogs.com/carekee/articles/1948298.html)

```language

<!--more-->

#include <ATLComTime.h>

使用COleDateTime类
1) 获取当前时间。
    CTime time;
    time = CTime::GetCurrentTime();
2) 获取时间元素。
    int year = time.GetYear() ;
    int month = time.GetMonth();
    int day = time.GetDay();
    int hour = time.GetHour();
    int minute = time.GetMinute();
    int second = time.GetSecond();
    int DayOfWeek = time.GetDayOfWeek() ;
3) 获取时间间隔。
    CTimeSpan timespan(0,0,1,0); // days,hours,minutes,seconds
    timespan = CTime::GetCurrentTime() - time;
4) 把时间转换为字符串。
    CString sDate,sTime,sElapsed Time ;
    sDate = time.Format("%m/%d/%y"); //ex: 12/10/98
    sTime = time.Format("%H:%M:%S"); //ex: 9:12:02
    sElapsed Time = timespan.Format("%D:%H:%M:%S"); // %D is total elapsed days

    CString strTemp;
    COleDateTime aCOleDateTime((time_t)time);
    strTemp = aCOleDateTime.Format(_T("%Y-%m-%d %H:%M:%S"));

5) 把字符串转换为时间。
     CString sDateTime;
     int nYear, nMonth, nDate, nHour, nMin, nSec;
     sscanf(sDateTime, "%d-%d-%d %d:%d:%d", &nYear, &nMonth, &nDate, &nHour, &nMin, &nSec);
     CTime sTime(nYear, nMonth, nDate, nHour, nMin, nSec);
要想知道更多的时间格式，参见MFC文档中的strftime

使用COleDateTime类
1) 获得一年中的某一天。
      COleDateTime datetime;
      datetime = COleDateTime::GetCurrentTime();
      int DayOfYear = datetime.GetDayOfYear();
2) 从文本串中读取时间。
      COleDateTime datetime;
      datetime.ParseDateTime("12:12:23 27 January 93");
3) 获取时间间隔。
         //比方计算日期差
         COleDateTime begin_date(1970, 1, 1, 0, 0, 0);
         COleDateTime end_date(1990, 1, 1, 0, 0, 0);
         COleDateTimeSpan timeSpan;    //计算时间差
         timeSpan = end_date - begin_date;
         long expi_date = timeSpan.GetDays();

说明
■ CTime和COleDateTime具有几乎同样的功能。然而，COleDateTime允许用户获得一年中的某一天，以及分析一个时间文本串。
■ `COleDateTime` 封装 OLE Automation 的 `DATE`：`DATE` 是 8 字节浮点值，以 1899-12-30 为零点按天计数，小时可表示为天的小数部分；`COleDateTime` 处理 100-01-01 至 9999-12-31 的日期。
■ 按 Microsoft `msvc-140` 文档线，`CTime` 对象也是 8 字节，类级日期范围为 1970-01-01 至 3000-12-31，`GetTime()` 返回 `__time64_t`。2038 年限制是旧的 32 位 `time_t` 配置（例如定义 `_USE_32BIT_TIME_T`）的限制，不应直接归因于现代 `CTime` 类。
```

本文修订依据：Microsoft Learn `msvc-140` 文档线中的 [`CTime`](https://learn.microsoft.com/en-us/cpp/atl-mfc-shared/reference/ctime-class?view=msvc-140)、[`COleDateTime`](https://learn.microsoft.com/en-us/cpp/atl-mfc-shared/reference/coledatetime-class?view=msvc-140)、[`DATE`](https://learn.microsoft.com/en-us/cpp/atl-mfc-shared/date-type?view=msvc-140) 和 [`time`](https://learn.microsoft.com/en-us/cpp/c-runtime-library/reference/time-time32-time64?view=msvc-140)。该文档线将 `CTime` 描述为 8 字节、类级上限为 3000-12-31，并将 2038 年限制归因于旧的 32 位 `time_t` 配置；`DATE` 为 8 字节浮点值。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 08:33（UTC+08:00）。修订仅纠正 `CTime`、`COleDateTime` 和 `DATE` 的范围、存储及 2038 年限制说明。
