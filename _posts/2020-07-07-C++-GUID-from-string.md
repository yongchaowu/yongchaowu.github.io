---
layout: post
title: "C++-GUID from string"
date: 2020-07-07 22:16:00
categories: ["C++"]
tags: ["GUID", "C++"]
---

July 7, 2020 9:26 PM

<!--more-->
参考 [CLSIDFromString function](https://docs.microsoft.com/zh-cn/windows/win32/api/combaseapi/nf-combaseapi-clsidfromstring?redirectedfrom=MSDN)
```cpp
#include <string>
GUID Guid = { 0 };
std::wstring strGuid = L"{2C1EB211-1435-4B4D-9144-29168CD22A4C}";
CLSIDFromString((LPCOLESTR)strGuid.c_str(), (LPCLSID)& Guid);
```

此外以下写法可以获取GUID，但运行结束后报错。
```
GUID guid = {0};
	sscanf_s(
		"2C1EB211-1435-4B4D-9144-29168CD22A4C",
		"%08x-%04x-%04x-%02x%02x-%02x%02x%02x%02x%02x%02x",
		&(guid.Data1),
		&(guid.Data2),
		&(guid.Data3),
		&(guid.Data4[0]),
		&(guid.Data4[1]),
		&(guid.Data4[2]),
		&(guid.Data4[3]),
		&(guid.Data4[4]),
		&(guid.Data4[5]),
		&(guid.Data4[6]),
		&(guid.Data4[7])
	);
运行报错：Run-Time Check Failure #2 - Stack around the variable 'guid' was corrupted.

```
分析：
因为使用的GUID结构体中Data4为unsigned char，通过sscanf_s操作时导致缓冲区不足或溢出

typedef struct _GUID {
    unsigned long  Data1;
    unsigned short Data2;
    unsigned short Data3;
    unsigned char  Data4[ 8 ];
} GUID;

Data4为unsigned char，经测试，Data4改为unsigned int(UINT)不再报错。

之后，仔细查看编译信息：
```language
warning C4477:  “sscanf_s”: 格式字符串“%04x”需要类型“unsigned int *”的参数，但可变参数 3 拥有了类型“unsigned short *”
message :  请考虑在格式字符串中使用“%hx”

warning C4477:  “sscanf_s”: 格式字符串“%02hx”需要类型“unsigned short *”的参数，但可变参数 4 拥有了类型“unsigned char *”
message :  请考虑在格式字符串中使用“%hhx”

warning C4477:  “sscanf_s”: 格式字符串“%02hx”需要类型“unsigned short *”的参数，但可变参数 11 拥有了类型“unsigned char *”
message :  请考虑在格式字符串中使用“%hhx”
```


测试中发现当改为以下写法时，编译运行未报错：
`"%08x-%04hx-%04hx-%02hhx%02hhx-%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx",`

此时，编译器警告中还存在以下警告：
```language
警告	C6328	大小不匹配: 已将“unsigned char”作为 _Param_(8) 传递，但需要使用“16 bit operand”来调用“sscanf_s”。这表示可能存在严重错误。若针对像 scanf 这样的函数报告此信息，可能表示发生缓冲区不足或溢出.

```