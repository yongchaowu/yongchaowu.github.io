---
layout: post
title: C++-regex
date: 2024-08-15 09:52:00
categories:
- Programming
tags:
- C++
- Code
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
