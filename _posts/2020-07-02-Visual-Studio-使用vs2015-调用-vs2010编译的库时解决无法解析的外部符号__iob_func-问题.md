---
layout: post
title: "Visual Studio-使用vs2015 调用 vs2010编译的库时解决\"无法解析的外部符号__iob_func 问题\""
date: 2020-07-02 08:47:00
categories: ["Visual Studio"]
tags: ["Visual Studio", "IDE"]
---

当使用高版本的Visual Studio调用低版本lib时，编译器会发生错误
解决方式如下：
```cpp
// 使用vs2015 调用 vs2010编译的库时解决"无法解析的外部符号__iob_func 问题"
#if _MSC_VER>=1900  
#include "stdio.h"   
_ACRTIMP_ALT FILE* __cdecl __acrt_iob_func(unsigned);
#ifdef __cplusplus   
extern "C"
#endif   
FILE* __cdecl __iob_func(unsigned i) {
	return __acrt_iob_func(i);
}
#endif /* _MSC_VER>=1900 */  

```