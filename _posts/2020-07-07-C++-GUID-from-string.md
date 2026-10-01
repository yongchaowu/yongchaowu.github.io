---
layout: post
title: C++-GUID from string
date: 2020-07-07 22:16:00
categories:
- C & C++
tags:
- GUID
- C++
---
July 7, 2020 9:26 PM

参考 [CLSIDFromString function](https://docs.microsoft.com/zh-cn/windows/win32/api/combaseapi/nf-combaseapi-clsidfromstring?redirectedfrom=MSDN)
```language
#include <string>
GUID Guid = { 0 };
std::wstring strGuid = L"{2C1EB211-1435-4B4D-9144-29168CD22A4C}";
CLSIDFromString((LPCOLESTR)strGuid.c_str(), (LPCLSID)& Guid);
```

<!--more-->

此外以下写法可以获取GUID，但运行结束后报错。
```
GUID guid = {0};
	sscanf_s(
		"2C1EB211-1435-4B4D-9144-29168CD22A4C",
		"%08x-%04hx-%04hx-%02hhx%02hhx-%02hhx%02hhx%02hhx%02hhx%02hhx%02hhx",
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
问题不是 GUID 的 Data4 太小，而是 `sscanf_s` 的格式字段与 GUID 成员类型不匹配。

typedef struct _GUID {
    unsigned long  Data1;
    unsigned short Data2;
    unsigned short Data3;
    unsigned char  Data4[ 8 ];
} GUID;

不能把 `Data4` 改为 `UINT`；这会破坏 Windows SDK 中 `GUID` 的定义。应让格式字段与成员类型匹配：`Data2`/`Data3` 使用 `%hx`，`Data4` 的每个字节使用 `%hhx`。

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

参考：[Microsoft Learn：GUID 结构](https://learn.microsoft.com/en-us/windows/win32/api/guiddef/ns-guiddef-guid)、[`scanf` width specification](https://learn.microsoft.com/en-us/cpp/c-runtime-library/scanf-width-specification?view=msvc-170) 和 [`scanf` type field characters](https://learn.microsoft.com/en-us/cpp/c-runtime-library/scanf-type-field-characters?view=msvc-170)。本文的格式说明针对 Windows SDK 的 `GUID` 定义和 Microsoft CRT。

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 02:41（UTC+08:00）。