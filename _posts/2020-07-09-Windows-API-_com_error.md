---
layout: post
title: Windows API-_com_error
date: 2020-07-09 21:07:00
categories:
- Systems
tags:
- Windows API
---

July 9, 2020 9:06 PM
[_com_error 类](https://docs.microsoft.com/zh-cn/cpp/cpp/com-error-class?view=vs-2019)

<!--more-->
```language
try
{
	....
}
catch (_com_error &e)
{
	CString erromessage;
	erromessage = e.ErrorMessage();
	AfxMessageBox(erromessage); 
	//return S_FALSE;
}
```
