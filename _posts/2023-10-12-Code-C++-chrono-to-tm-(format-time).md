---
layout: post
title: C++-chrono to tm (format time)
date: 2023-10-12 12:54:00
categories:
- Programming
tags:
- C++
- Code
- Time
---

```cpp
    std::chrono::system_clock::time_point now = std::chrono::system_clock::now();
	std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
	std::tm* now_tm = std::localtime(&now_time_t);
	char buffer[128];
	strftime(buffer, sizeof(buffer), "%F %T", now_tm);

std::ostringstream ss;
	ss.fill('0');
ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
		ss << buffer << ":" << ms.count();
//  tm : ms
```