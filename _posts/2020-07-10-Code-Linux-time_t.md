---
layout: post
title: Linux-time_t
display_title: 'Linux time_t'
date: 2020-07-10 22:58:00
categories:
- Programming
tags:
- Code
- C
---

https://www.runoob.com/w3cnote/cpp-time_t.html
## 概念
Unix时间戳(Unix timestamp)，或称Unix时间(Unix time)、POSIX时间(POSIX time)，是一种时间表示方式，定义为从格林威治时间1970年01月01日00时00分00秒起至现在的总秒数。Unix时间戳不仅被使用在Unix 系统、类Unix系统中，也在许多其他操作系统中被广泛采用。

<!--more-->
目前相当一部分操作系统使用32位二进制数字表示时间。此类系统的Unix时间戳最多可以使用到格林威治时间2038年01月19日03时14分07秒（二进制：01111111 11111111 11111111 11111111）。其后一秒，二进制数字会变为10000000 00000000 00000000 00000000，发生溢出错误，造成系统将时间误解为1901年12月13日20时45分52秒。这很可能会引起软件故障，甚至是系统瘫痪。使用64位二进制数字表示时间的系统（最多可以使用到格林威治时间292,277,026,596年12月04日15时30分08秒）则基本不会遇到这类溢出问题。

*   本地时间(locale time)
*   格林威治时间（Greenwich Mean Time GMT）
*   时间协调时间 （Universal Time Coordinated UTC）

**（1）世界时**

世界时是最早的时间标准。在1884年，国际上将1s确定为全年内每日平均长度的1/8.64×104。以此标准形成的时间系统，称为世界时，即UT1。1972年国际上开始使用国际原子时标，从那以后，经过格林威治老天文台本初子午线的时间便被称为世界时，即UT2，或称格林威治时间（GMT），是对地球转速周期性差异进行校正后的世界时。

**（2）原子时**

1967年，人们利用铯原子振荡周期极为规律的特性，研制出了高精度的原子时钟，将铯原子能级跃迁辐射9192631770周所经历的时间定为1s。现在用的时间就是1971年10月定义的国际原子时，是通过世界上大约200多台原子钟进行对比后，再由国际度量衡局时间所进行数据处理，得出的统一的原子时，简称TAI。

**（3）世界协调时**

世界协调时是以地球自转为基础的时间标准。由于地球自转速度并不均匀，并非每天都是精确的86400原子s，因而导致了自转时间与世界时之间存在每18个月有1s的误差。为纠正这种误差，国际地球自转研究所根据地球自转的实际情况对格林威治时间进行增减闰s的调整，与国际度量衡局时间所联合向全世界发布标准时间，这就是所谓的世界协调时（UTC:CoordinatedUniversalTime）。UTC的表示方式为：年（y）、月（m）、日（d）、时（h）、分（min）、秒（s），均用数字表示。

GPS 系统中有两种时间区分，一为UTC，另一为LT（地方时）。两者的区别为时区不同，UTC就是0时区的时间，地方时为本地时间，如北京为早上八点（东八区），UTC时间就为零点，时间比北京时晚八小时，以此计算即可。通过上面的了解，我们可以认为格林威治时间就是时间协调时间（GMT=UTC），格林威治时间和UTC时间均用秒数来计算的。

注：计算机日志里面写的时间大多数是用UTC时间来计算的

## linux命令及time结构体
使用linux/unix命令date来进行本地时间和local时间的转化

linux下存储时间常见的有两种存储方式，一个是从1970年到现在经过了多少秒，一个是用一个结构来分别存储年月日时分秒的。

time_t 这种类型就是用来存储从1970年到现在经过了多少秒，要想更精确一点，可以用结构struct timeval，它精确到微秒。

    struct timeval
    {
        long tv_sec; /*秒*/
        long tv_usec; /*微秒*/
    };

而直接存储年月日的是一个结构：

    struct tm
    {
        int tm_sec;  /*秒，正常范围0-59， 但允许至61*/
        int tm_min;  /*分钟，0-59*/
        int tm_hour; /*小时， 0-23*/
        int tm_mday; /*日，即一个月中的第几天，1-31*/
        int tm_mon;  /*月， 从一月算起，0-11*/  1+p->tm_mon;
        int tm_year;  /*年， 从1900至今已经多少年*/  1900＋ p->tm_year;
        int tm_wday; /*星期，一周中的第几天， 从星期日算起，0-6*/
        int tm_yday; /*从今年1月1日到目前的天数，范围0-365*/
        int tm_isdst; /*日光节约时间的旗标*/
    };

需要特别注意的是，年份是从1900年起至今多少年，而不是直接存储如2011年，月份从0开始的，0表示一月，星期也是从0开始的， 0表示星期日，1表示星期一。

## 函数

    #include <time.h>
    char *asctime(const struct tm* timeptr);//将结构中的信息转换为真实世界的时间，以字符串的形式显示
    char *ctime(const time_t *timep);//将timep转换为真实世界的时间，以字符串显示，它和asctime不同就在于传入的参数形式不一样
    double difftime(time_t time1, time_t time2);//返回两个时间相差的秒数
    int gettimeofday(struct timeval *tv, struct timezone *tz);//返回当前距离1970年的秒数和微秒数，后面的tz是时区，一般不用
    struct tm* gmtime(const time_t *timep);//将time_t表示的时间转换为没有经过时区转换的UTC时间，是一个struct tm结构指针
    struct tm* localtime(const time_t *timep);//和gmtime类似，但是它是经过时区转换的时间。
    time_t mktime(struct tm* timeptr);//将struct tm 结构的时间转换为从1970年至今的秒数
    time_t time(time_t *t);//取得从1970年1月1日至今的秒数。

```
//strftime() 函数将时间格式化
size_t strftime(
     char *strDest,
     size_t maxsize,
     const char *format,
     const struct tm *timeptr
);
据format指向字符串中格式命令把timeptr中保存的时间信息放在strDest指向的字符串中，最多向strDest中存放maxsize个字符。该函数返回向strDest指向的字符串中放置的字符数。

函数strftime()的操作有些类似于sprintf()：识别以百分号(%)开始的格式命令集合，格式化输出结果放在一个字符串中。格式化命令说明串 strDest中各种日期和时间信息的确切表示方法。格式串中的其他字符原样放进串中。格式命令列在下面，它们是区分大小写的。

  %a 星期几的简写
  %A 星期几的全称
  %b 月份的简写
  %B 月份的全称
  %c 标准的日期的时间串
  %C 年份的后两位数字
  %d 十进制表示的每月的第几天
  %D 月/天/年
  %e 在两字符域中，十进制表示的每月的第几天
  %F 年-月-日
  %g 年份的后两位数字，使用基于周的年
  %G 年份，使用基于周的年
  %h 简写的月份名
  %H 24小时制的小时
  %I 12小时制的小时
  %j 十进制表示的每年的第几天
  %m 十进制表示的月份
  %M 十时制表示的分钟数
  %n 新行符
  %p 本地的AM或PM的等价显示
  %r 12小时的时间
  %R 显示小时和分钟：hh:mm
  %S 十进制的秒数
  %t 水平制表符
  %T 显示时分秒：hh:mm:ss
  %u 每周的第几天，星期一为第一天 （值从0到6，星期一为0）
  %U 第年的第几周，把星期日做为第一天（值从0到53）
  %V 每年的第几周，使用基于周的年
  %w 十进制表示的星期几（值从0到6，星期天为0）
  %W 每年的第几周，把星期一做为第一天（值从0到53）
  %x 标准的日期串
  %X 标准的时间串
  %y 不带世纪的十进制年份（值从0到99）
  %Y 带世纪部分的十进制年份
  %z，%Z 时区名称，如果不能得到时区名称则返回空字符。
  %% 百分号
```

## 测试实例

```cpp
/*gettime1.c*/
#include <time.h>

int main()
{
    time_t timep;

    time(&timep); /*获取time_t类型的当前时间*/
    /*用gmtime将time_t类型的时间转换为struct tm类型的时间，／／没有经过时区转换的UTC时间
      然后再用asctime转换为我们常见的格式 Fri Jan 11 17:25:24 2008
    */
    printf("%s", asctime(gmtime(&timep)));
    return 0;
}

编译并运行：

  $gcc -o gettime1 gettime1.c
  $./gettime1
  Fri Jan 11 17:04:08 2008
```

time, gmtime, asctime 所表示的时间都是UTC时间，只是数据类型不一样，

而localtime, ctime 所表示的时间都是经过时区转换后的时间，它和你用系统命令date所表示的CST时间应该保持一致。


```
# gmtime_s， _gmtime32_s， _gmtime64_s
```
