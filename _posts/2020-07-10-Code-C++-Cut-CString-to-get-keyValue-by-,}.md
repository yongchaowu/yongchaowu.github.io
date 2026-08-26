---
layout: post
title: "Code-C++-Cut CString to get keyValue by \",\"||\"}\""
date: 2020-07-10 02:21:00
categories: ["Code"]
tags: ["Code", "C++"]
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

<!--more-->
