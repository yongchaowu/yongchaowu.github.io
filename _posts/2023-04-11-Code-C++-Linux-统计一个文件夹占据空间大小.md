---
layout: post
title: C++-Linux-统计一个文件夹占据空间大小
date: 2023-04-11 21:58:00
categories:
- Programming
tags:
- C++
- Code
- Linux
---

>[https://my.oschina.net/Tsybius2014/blog/330628](https://my.oschina.net/Tsybius2014/blog/330628)

<!--more-->
从以上链接中拷贝的代码
```cpp
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <dirent.h>
#include <string.h>

#define BYTES_OF_CURRENT_FOLDER 4096

class CheckSpace
{
public:
    // 构造函数
    CheckSpace(char *filepath)
    {
        this->m_TB = 0;
        this->m_GB = 0;
        this->m_MB = 0;
        this->m_KB = 0;
        this->m_Bytes = 0;
        strcpy(this->m_FilePath, filepath);

        CheckSpaceWithoutDir(filepath); // 统计目录中的文件占据的空间大小
        AddBytes(4096);  // 加上该目录本身占据的4096
    }

    // 获取各项属性
    int GetTB() { return this->m_TB; }
    int GetGB() { return this->m_GB; }
    int GetMB() { return this->m_MB; }
    int GetKB() { return this->m_KB; }
    int GetBytes() { return this->m_Bytes; }

    // 展示内容
    void Display()
    {
        printf("查询目录路径 %s\n", m_FilePath);
        printf("占用空间 %dTB %dGB %dMB %dKB %dByte(s)\n",
               m_TB, m_GB, m_MB, m_KB, m_Bytes);
    }

private:
    int m_TB;             // TB
    int m_GB;             // GB
    int m_MB;             // MB
    int m_KB;             // KB
    int m_Bytes;          // Byte
    char m_FilePath[128]; // 目录地址

    // Byte数量增加（自动进位）
    void AddBytes(int bytes)
    {
        m_Bytes += bytes;
        while (m_Bytes >= 1024)
        {
            m_Bytes -= 1024;
            m_KB++;
        }
        while (m_KB >= 1024)
        {
            m_KB -= 1024;
            m_MB++;
        }
        while (m_MB >= 1024)
        {
            m_MB -= 1024;
            m_GB++;
        }
        while (m_GB >= 1024)
        {
            m_GB -= 1024;
            m_TB++;
        }
    }

    // 查看某目录所占空间大小（不含该目录本身的4096Byte）
    void CheckSpaceWithoutDir(char *dir)
    {
        DIR *pDir;
        struct dirent *entry;
        struct stat statbuf;

        if ((pDir = opendir(dir)) == NULL)
        {
            fprintf(stderr, "Cannot open dir: %s\n", dir);
            exit(0);
        }

        chdir(dir);

        while ((entry = readdir(pDir)) != NULL)
        {
            lstat(entry->d_name, &statbuf);
            if (S_ISDIR(statbuf.st_mode))
            {
                if (strcmp(".", entry->d_name) == 0 ||
                    strcmp("..", entry->d_name) == 0)
                {
                    continue;
                }

                AddBytes(statbuf.st_size);
                CheckSpaceWithoutDir(entry->d_name);
            }
            else
            {
                AddBytes(statbuf.st_size);
            }
        }

        chdir("..");
        closedir(pDir);
    }
};

int main()
{
    char cTopDir[100] = "./";
    CheckSpace cs = CheckSpace(cTopDir);
    cs.Display();
    return 0;
}
```

输出信息
```
查询目录路径 ./
占用空间 0TB 0GB 0MB 1021KB 616Byte(s)
```