---
layout: post
title: "Code-C++-Linux-获取时间time()/localtime()/gettimeofday()"
date: 2023-04-10 23:50:00
categories: ["Code"]
tags: ["C++", "Code", "Time"]
---

```cpp
#include <iostream>
//#include <time.h>
#include <sys/time.h>  //for gettimeofday()
#include <string>

void getCurrentTime(){
    time_t llTime;
    time(&llTime);
    std::cout << asctime(gmtime(&llTime))<<std::endl;
}

static std::string getCurrentLocalTime(void){
    time_t llSeconds;   //以秒为单位的时间值
    tm *struTime;       //本地时间结构体
    char cBuf[128] = {0};
    llSeconds = time(NULL);//获取目前以秒为单位的时间值
    struTime = localtime(&llSeconds);//转为本地时间，注意：localtime非线程安全--->localtime_r 线程安全
    strftime(cBuf, 64, "%Y-%m-%d %H:%M:%S", struTime);
    return cBuf;
}

static std::string getCurrentLocalTimeWithMs(void){
    std::string strDefaultTime = "19700101000000000";
    struct timeval struCurrentTime;
    gettimeofday(&struCurrentTime, NULL); //#include <sys/time.h>
    int nMillisec = struCurrentTime.tv_usec/1000;
    char cBuf[80] = {0};
    struct tm struNowTime;
    localtime_r(&struCurrentTime.tv_sec, &struNowTime);
    strftime(cBuf, sizeof(cBuf), "%Y-%m-%d %H:%M:%S", &struNowTime);
    char cCurTime[84] = {0};
    snprintf(cCurTime, sizeof(cCurTime), "%s.%03d", cBuf, nMillisec);
    return cCurTime;
}
```