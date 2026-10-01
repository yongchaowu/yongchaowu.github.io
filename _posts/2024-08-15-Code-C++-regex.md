---
layout: post
title: C++-regex
date: 2024-08-15 09:52:00
categories:
- Programming
tags:
- C++
- Code
upstream_sync: off
upstream_sync_reason: >-
  cnblogs 侧把这篇几乎清空：924 字符降到 101，只剩 'std::regex;' 'std::smatch;' 'regex_replace();'，其中 std::regex; 不是合法 C++ 语句（缺变量名）。仓库版本含完整可编译示例，覆盖 regex_match / regex_search / regex_replace / regex_iterator 四种用法。属上游质量下降，而非仓库领先。
---

C++ 正则表达式 regex

<!--more-->
```c++
#include <regex>
#include <string>
#include <iostream>

int main() {
    std::string text = "Hello 2024, year 2025";
    std::regex re("\\d{4}");

    // regex_match: 整个字符串匹配
    bool is_match = std::regex_match(text, std::regex("\\d{4}"));
    std::cout << "regex_match: " << is_match << std::endl;

    // regex_search: 搜索第一个匹配
    std::smatch match;
    if (std::regex_search(text, match, re)) {
        std::cout << "regex_search: " << match[0] << std::endl;
    }

    // regex_replace: 替换匹配内容
    std::string result = std::regex_replace(text, re, "XXXX");
    std::cout << "regex_replace: " << result << std::endl;

    // regex_iterator: 遍历所有匹配
    auto begin = std::sregex_iterator(text.begin(), text.end(), re);
    auto end = std::sregex_iterator();
    for (auto it = begin; it != end; ++it) {
        std::cout << "found: " << (*it)[0] << std::endl;
    }

    return 0;
}
```
