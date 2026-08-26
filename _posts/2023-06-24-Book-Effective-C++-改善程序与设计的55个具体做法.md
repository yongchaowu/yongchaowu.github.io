---
layout: post
title: Book-Effective C++ 改善程序与设计的55个具体做法
date: 2023-06-24 15:24:00
categories:
- Computer Science
tags:
- Book
- C++
---

1. 让自己习惯C++
Accustoming Yourself to C++

<!--more-->
- 条款 01:视 C++ 为一个语言联邦/View C++ as a federation of languages.
- 条款 02:尽量以`const,enum, inline`替换`#define` /Prefer consts, enums, and inlines to #defines.
- 条款 03:尽可能使用 const/Use const whenever possible.
- 条款 04:确定对象被使用前已先被初始化/Make sure that objects are initialized before they're used.

---
2. 构造/析构/赋值运算
Constructors, Destructors, and Assignment Operators.

- 条款 05:了解 C++ 默默编写并调用哪些函数/Know what functions C++ silently writes and calls.
- 条款 06:若不想使用编译器自动生成的函数，就该明确拒绝/Explicitly disallow the use of compiler-generated functions you do not want.
- 条款 07:为多态基类声明 virtual 析构函数/Declare destructors virtual in polymorphic base classes.
- 条款 08: 别让异常逃离析构函数/Prevent exceptions from leaving destructors.
- 条款 09: 绝不在构造和析构过程中调用 virtual 函数/Never call virtual functions during construction or destruction.
- 条款 10: 令 `operator=` 返回一个 `reference to *this`/Have assignment operators return a reference to *this.
- 条款 11: 在 `operator=` 中处理“自我赋值”/Handle assignment to self in `operator=`.
- 条款 12: 复制对象时勿忘其每一个成分/Copy all parts of an object.

---
3. 资源管理
Resource Management

- 条款 13:以对象管理资源/Use objects to manage resources.
- 条款 14:在资源管理类中小心 copying 行为/Think carefully about copying behavior in resource-managing classes.
- 条款 15:在资源管理类中提供对原始资源的访问/Provide access to raw resources in resource-managing classes.
- 条款 16:成对使用 new 和 delete 时要采取相同形式/Use the same form in corresponding uses of new and delete.
- 条款 17:以独立语句将 newed 对象置入智能指针/Store newed objects in smart pointers in standalone statements.

---
4. 设计与声明
Designs and Declarations

- 条款 18:让接口容易被正确使用，不易被误用/Make interfaces easy to use correctly and hard to use incorrectly.
- 条款 19:设计 class 犹如设计 type/Treat class design as type design.
- 条款 20:宁以 pass-by-reference-to-const 替换 pass-by-value/Prefer pass-by-reference-to-const to pass-by-value.
- 条款 21:必须返回对象时，别妄想返回其 reference/Don't try to return a reference when you must return an object.
- 条款 22:将成员变量声明为 private./Declare data members private.
- 条款 23:宁以 non-member、non-friend 替换 member 函数/Prefer non-member non-friend functions to member functions.
- 条款 24:若所有参数皆需类型转换，请为此采用 non-member 函数/Declare non-member functions when type conversions should apply to all parameters.
- 条款 25:考虑写出一个不抛异常的 swap 函数/Consider support for a non-throwing swap.

---
5. 实现
Implementations

- 条款 26: 尽可能延后变量定义式的出现时间/Postpone variable definitions as long as possible.
- 条款 27: 尽量少做转型动作./Minimize casting.
- 条款 28: 避免返回 handles 指向对象内部成分/Avoid returning "handles" to object internals.
- 条款 29: 为“异常安全”而努力是值得的/Strive for exception-safe code.
- 条款 30: 透彻了解 inlining 的里里外外/Understand the ins and outs of inlining.
- 条款 31: 将文件间的编译依存关系降至最低/Minimize compilation dependencies between files.

---
6. 继承与面向对象设计
Inheritance and Object-Oriented Design

- 条款 32:确定你的 public 继承塑模出 is-a 关系/Make sure public inheritance models "is-a."
- 条款 33:避免遮掩继承而来的名称/Avoid hiding inherited names.
- 条款 34:区分接口继承和实现继承/Differentiate between inheritance of interface and inheritance of implementation.
- 条款 35:考虑 virtual 函数以外的其他选择/Consider alternatives to virtual functions.
- 条款 36:绝不重新定义继承而来的 non-virtual 函数/Never redefine an inherited non-virtual function.
- 条款 37:绝不重新定义继承而来的缺省参数值/Never redefine a function's inherited default parameter value.
- 条款 38:通过复合塑模出 has-a 或"根据某物实现出"/Model "has-a" or "is-implemented-in-terms-of" through composition.
- 条款 39:明智而审慎地使用 private 继承/Use private inheritance judiciously.
- 条款 40:明智而审慎地使用多重继承/Use multiple inheritance judiciously.

---
7. 模板与泛型编程
Templates and Generic Programming

- 条款 41:了解隐式接口和编译期多态/Understand implicit interfaces and compile-time polymorphism.
- 条款 42:了解 typename 的双重意义/Understand the two meanings of typename.
- 条款 43:学习处理模板化基类内的名称/Know how to access names in templatized base classes.
- 条款 44:将与参数无关的代码抽离 templates/Factor parameter-independent code out of templates.
- 条款 45:运用成员函数模板接受所有兼容类型/Use member function templates to accept all compatible types.
- 条款 46:需要类型转换时请为模板定义非成员函数/Define non-member functions inside templates when type conversions are desired.
- 条款 47:请使用 traits classes 表现类型信息/Use traits classes for information about types.
- 条款 48:认识 template 元编程/Be aware of template metaprogramming.

---
8. 定制new和delete
Customizing new and delete

- 条款 49:了解 new-handler 的行为/Understand the behavior of the new-handler.
- 条款 50:了解 new 和 delete 的合理替换时机/Understand when it makes sense to replace new and delete.
- 条款 51:编写 new 和 delete 时需固守常规/Adhere to convention when writing new and delete.
- 条款 52:写了 placement new 也要写 placement delete/Write placement delete if you write placement new.

---
9. 杂项讨论
Miscellany

- 条款 53:不要轻忽编译器的警告/Pay attention to compiler warnings.
- 条款 54:让自己熟悉包括 TR1 在内的标准程序库/Familiarize yourself with the standard library, including TR1.
- 条款 55:让自己熟悉 Boost/Familiarize yourself with Boost.
