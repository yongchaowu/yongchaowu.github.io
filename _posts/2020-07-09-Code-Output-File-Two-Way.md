---
layout: post
title: "Code-Output File-Two Way"
date: 2020-07-09 21:29:00
categories: ["Code"]
tags: ["Code", "C++"]
---

July 9, 2020 9:25 PM
##1.使用ofstream 输出
```cpp
#include <fstream>
SYSTEMTIME st;
GetLocalTime(&st);

CString strTime;
strTime.Format(_T(" %d-%02d-%02d %02d:%02d:%02d.%03d"),st.wYear,st.wMonth,st.wDay,st.wHour,st.wMinute,st.wSecond,st.wMilliseconds);

string strIPAddr="192.168.0.1"
string temp = "D://mess//"+strIPAddr + ".txt";
ofstream outfile(temp.c_str(),std::ios::app|std::ios::out); 
outfile<<strIPAddr<<"-"<<GetCurrentThreadId()<<"-"<<"TryConnect"<<"-"<<"errorNum"<<m_ierrNum<<strTime.GetBuffer()<<endl;
outfile.close();
strTime.ReleaseBuffer();
```

<!--more-->
##2.使用Class 输出
```cpp

class CExportLog
{
public:
	CExportLog()
	{
		InitializeCriticalSection(&m_csLock);

		//获取模块运行路径
		wchar_t wFilePath[_MAX_FNAME] = {0};
		wchar_t wDrive[_MAX_FNAME] = {0};
		wchar_t wDir[_MAX_FNAME] = {0};
		wchar_t wFileName[_MAX_FNAME] = {0};
		wchar_t wExe[_MAX_FNAME] = {0};

		GetModuleFileName(NULL, wFilePath, _MAX_FNAME);
		_tsplitpath(wFilePath,   wDrive,   wDir,   wFileName,   wExe);

		std::wstring strFilePath;
		strFilePath.append(wDrive);
		strFilePath.append(wDir);
		strFilePath.append(L"Log\\log.log");
		m_strFilePath = strFilePath.c_str();
	}

	virtual ~CExportLog()
	{
		DeleteCriticalSection(&m_csLock);
	}

	void ExportMsg(CString strMsg)
	{
		CStdioFile LogFile;
		setlocale( LC_CTYPE, "chs" );
		EnterCriticalSection(&m_csLock);
		if (LogFile.Open(m_strFilePath, CFile::modeCreate|CFile::modeReadWrite|CFile::typeText|CFile::modeNoTruncate))
		{
			LogFile.SeekToEnd();

			SYSTEMTIME st;
			GetLocalTime(&st);
		CString strText, strBackupTime;
	strBackupTime.Format(_T("%04d%02d%02d%02d%02d%02d%03d"), st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond, st.wMilliseconds);
		strText.Format(_T("%04d-%02d-%02d %02d:%02d:%02d.%03d  "), st.wYear, st.wMonth, st.wDay, st.wHour, st.wMinute, st.wSecond, st.wMilliseconds);
		
		strText += strMsg;
		strText += _T("\n");
		LogFile.WriteString(strText);

		ULONGLONG dFileSize = LogFile.GetLength();
		if (dFileSize > 20*1024*1024)
		{
			LogFile.Close();
			CString strNewFile;
			strNewFile = m_strFilePath;
			strBackupTime += _T(".log");
			strNewFile.Replace(_T(".log"), strBackupTime.GetString());
			CopyFile(m_strFilePath.GetString(), strNewFile.GetString(), FALSE);
			DeleteFile(m_strFilePath.GetString());
			}
			else
			{
				LogFile.Close();
			}
		}
		LeaveCriticalSection(&m_csLock);
	}

private:
	CRITICAL_SECTION  m_csLock;
	CString m_strFilePath;
};

```
