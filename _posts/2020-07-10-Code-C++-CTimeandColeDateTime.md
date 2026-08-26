---
layout: post
title: C++-CTime&ColeDateTime
date: 2020-07-10 02:24:00
categories:
- Programming
tags:
- Code
- C++
---

July 10, 2020 2:23 AM
[COleDateTime类型的应用](https://www.cnblogs.com/carekee/articles/1948298.html)

<!--more-->
```cpp

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
    CString sDate,sTime,sElapsedTime ;
    sDate = time.Format("%m/%d/%y"); //ex: 12/10/98
    sTime = time.Format("%H:%M:%S"); //ex: 9:12:02
    sElapsedTime = timespan.Format("%D:%H:%M:%S"); // %D is total elapsed days

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
■ CTime和COleDateTime具有几乎同样的功能。然而，COleDateTime允许用户获得一年中的某一天(创建Julian日期的一种好方法)，以及分析一个时间文本串。
■ 与CTime相比， COleDateTime的优点在于它支持DWORD变量。COleDateTime使用的位数是双浮点的两倍，既然CTime只是简单地计算从1970年1月1日之后经过的秒数，所以到了2037年它将达到4294967295，从而不能再使用。相反,COleDateTime是一个
浮点数，它表示是从1899年12月30号之后的天数(小时是天的小数部分)，几千年之内不会溢出。

```
