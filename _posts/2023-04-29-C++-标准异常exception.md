---
layout: post
title: "C++-标准异常`<exception>`"
date: 2023-04-29 18:03:00
categories: ["C++"]
tags: ["C++"]
---

std::exception 定义于头文件 `<exception>` class exception;
>https://www.apiref.com/cpp-zh/cpp/error/exception.html

<!--more-->
标准库头文件 `<stdexcept>`
>https://www.apiref.com/cpp-zh/cpp/header/stdexcept.html

## 
std::exception
std::bad_alloc
std::bad_cast
std::bad_exception
std::bad_typeid

std::logic_error			指示违背逻辑前提条件或类不变量的异常类
std::invalid_argument		报告非法参数的异常类
std::domain_error			报告定义域错误的异常类
std::length_error			报告试图超出最大允许大小的异常类
std::out_of_range			报告参数落在期待范围外的异常类
std::runtime_error			指示条件只可于运行时检测的异常类
std::range_error			报告内部计算中值域错误的异常类
std::overflow_error			报告算术上溢的异常类
std::underflow_error		报告算术下溢的异常类


----------
## `<exception>`
https://www.apiref.com/cpp-zh/cpp/error/exception.html

std::exception 
定义于头文件 `<exception> `
class exception;
提供一致的接口，以通过 throw 表达式处理错误。
标准库所生成的所有异常继承自 std::exception

```
- logic_error
	- invalid_argument
	- domain_error
	- length_error
	- out_of_range
	- future_error(C++11)
	- bad_optional_access(C++17)
- runtime_error
	- range_error
	- overflow_error
	- underflow_error
	- regex_error(C++11)
	- system_error(C++11)
		- ios_base::failure(C++11)
		- filesystem::filesystem_error(C++17)
	- nonexistent_local_time(C++20)
	- ambiguous_local_time(C++20)
	- tx_exception(TM TS)
	- format_error(C++20)
- bad_typeid
- bad_cast
	- bad_any_cast(C++17)
- bad_weak_ptr(C++11)
- bad_function_call(C++11)
- bad_alloc
	- bad_array_new_length(C++11)
- bad_exception
- ios_base::failure(C++11 前)
- bad_variant_access(C++17)
```

成员函数
```
成员函数

(构造函数)		构造异常对象(公开成员函数)
(析构函数)[虚]	析构该异常对象(虚公开成员函数)
operator=		复制异常对象(公开成员函数)
what[虚]			返回解释性字符串(虚公开成员函数)
```
## `<stdexcept>`
https://www.apiref.com/cpp-zh/cpp/header/stdexcept.html
```
namespace std {
  class logic_error;
    class domain_error;
    class invalid_argument;
    class length_error;
    class out_of_range;
  class runtime_error;
    class range_error;
    class overflow_error;
    class underflow_error;
}
```