---
layout: post
title: "Code-C++-fstream-输出到文件"
date: 2023-04-10 23:44:00
categories: ["Code"]
tags: ["C++", "Code", "Linux"]
---

- 利用fstream文件流输出
- 利用stat查看文件大小
- 设定文件最大值宏定义

<!--more-->
```cpp
#include <fstream>
#include <string>
#include <sys/stat.h>

#include <iostream>

#define  LOG_FILE_MAX_SIZE 1024*1024

void exportFile(std::string strFileName, int nVal)
{

    std::string strFilePath = "./" + strFileName;
    
    std::ofstream osFile;
    struct stat64 statbuf;
    stat64(strFilePath.c_str(), &statbuf);
    if(statbuf.st_size > LOG_FILE_MAX_SIZE){
        if(remove(strFilePath.c_str()) != 0)
            return;
    }
        
    osFile.open(strFilePath.c_str(), std::ios::app | std::ios::out);
    if (!osFile.is_open())
        return;
    osFile << "The value is " << nVal << std::endl;
    osFile.close();
}
/*
void open(const char* filename,int mode,int access);
参数：
filename:要打开的文件名
mode:要打开文件的方式
access:打开文件的属性
打开文件的方式在类ios(是所有流式I/O类的基类)中定义，常用的值如下：
ios::app:以追加的方式打开文件
ios::ate:文件打开后定位到文件尾,ios::app就包含有此属性
ios::binary:以二进制方式打开文件，缺省的方式是文本方式。两种方式的区别见前文
ios::in:文件以输入方式打开（文件数据输入到内存）
ios::out:文件以输出方式打开（内存数据输出到文件）
ios::nocreate: 不建立文件，所以文件不存在时打开失败
ios::noreplace:不覆盖文件，所以打开文件时如果文件存在失败
ios::trunc:如果文件存在,把文件长度设为0
可以用“或”把以上属性连接起来,如ios::out|ios::binary
打开文件的属性取值是：
0:普通文件，打开访问
1:只读文件
2:隐含文件
4:系统文件
*/
void parseFileSize(const off_t &st_size);
int main()
{   
    int i=0;
    // while(i < 100){
        exportFile("log", i++);
    // }
    
    struct stat64 statbuf;
    stat64("./log", &statbuf);
    std::cout << "log file size is  " << statbuf.st_size << std::endl;
    parseFileSize(statbuf.st_size);

    return 0;
}

void parseFileSize(const off_t &st_size)
{
    int nTB = 0;    // TB
    int nGB = 0;    // GB
    int nMB = 0;    // MB
    int nKB = 0;    // KB
    int nBytes = 0; // Byte
    int nCount = 0;
    int64_t nSize = st_size;
    while (int nTmp = nSize % 1024)
    {
        nCount++;
        switch (nCount)
        {
        case 1:
            nBytes = nTmp;
            nTmp = 0;
            break;
        case 2:
            nKB = nTmp;
            nTmp = 0;
            break;
        case 3:
            nMB = nTmp;
            nTmp = 0;
            break;
        case 4:
            nGB = nTmp;
            nTmp = 0;
            break;
        case 5:
            nTB = nTmp;
            nTmp = 0;
            break;
        default:
        {
        };
        };
        nSize /= 1024;
    }

    printf("占用空间 %dTB %dGB %dMB %dKB %dByte(s)\n",
           nTB, nGB, nMB, nKB, nBytes);
}

// int64_t parsePreSetSize(){}
```