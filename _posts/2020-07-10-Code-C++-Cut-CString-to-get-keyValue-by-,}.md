---
layout: post
title: C++-Cut CString to get keyValue by ","||"}"
date: 2020-07-10 02:21:00
categories:
- Programming
tags:
- Code
- C++
---
July 10, 2020 2:19 AM
```
// cut CString to get keyValue
void GetKeyValue(CString strSource, CString strKey, CString& strValue)
{
	CString strTemp = strSource;
	int n = strTemp.Find(strKey.GetString(), 0);

	if (n == -1)
	{
		strValue = _T("0");
		return;
	}

	strTemp = strTemp.Mid(n + strKey.GetLength() + 2); //"AA":BB
	int n1 = strTemp.ReverseFind(',');//End Flag
	int n2 = strTemp.ReverseFind('}');//End Flag

	if (n1 >= 0 && n2 >= 0)
	{
		n = n1 > n2 ? n2 : n1;
	}
	else if (n1 == -1)
	{
		n = n2;
	}
	else if (n2 == -1)
	{
		n = n1;
	}

	strValue = strTemp.Left(n);

}
```

本文修订依据：CommonMark `0.31.2`（2024-01-28）§4.2 的 ATX heading 语法。规范要求起始 `#` 后使用空格或 tab；本文仅在文章标题的 `#` 后补入必需空格，使其解析为一级标题，代码块未改动。

<!--more-->

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 16:14（UTC+08:00）。修订仅补齐文章一级标题的 CommonMark 必需空格。
