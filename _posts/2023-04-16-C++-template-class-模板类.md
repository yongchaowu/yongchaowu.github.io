---
layout: post
title: "C++-template class-模板类"
date: 2023-04-16 23:31:00
categories: ["C++"]
tags: ["C++"]
---

>【C++高级教程，C++类模板一次讲透，必须收藏！】 https://www.bilibili.com/video/BV1v84y1x7Qp/?share_source=copy_web&vd_source=3809390a14c335e7731c9e076c03eeba

<!--more-->
##类模板概念
类模板是用于生成类的模板。
在编译阶段，编译器会根据类模板的使用情况创建出仅部分成员数据类型，和部分成员函数的参数类型不同，其他完全相同的若干类。
通过类模板的这些特性我们可以尝试写出用于存放不同类型数据的容器。

##类模板使用
- 类模板的声明如下，其中T表示任何类型，由用户指定：
```
template<typename T,...>
class 类名
{
	//成员
};
```

- 类模板的成员函数定义如下，一般类模板的定义也应该写在头文件中：
```
template<typename T,...>
返回类型 类名<T,...>::成员函数名(形参列表)
{
	//函数体
}
```

### Demo
```cpp
#ifndef __DEMOARRAY_H
#define __DEMOARRAY_H

#include <iostream>

template <typename T>
class DemoArray
{
private:
	T data[20];
	int len;
public:
	DemoArray();
	T indexof(int index);
	void addValue(T value);
}

template <typename T>
DemoArray<T>::DemoArray()
	:len(0)
{

}

template <typename T>
DemoArray<T>::indexof(int index)
{
	return data[index];
}

template <typename T>
DemoArray<T>::addValue(T value)
{
	if(len<20)
		data[len++] = vale;
}


/////////////////////////////
//特化类 指定类型float
template<>
class DemoArray<float>
{
public:
	DemoArray();
};

DemoArray<float>::DemoArray()
{
	std::cout<<"DemoArray<float>::DemoArray()"<<std::endl;
}



#endif
```

##类模板特化和偏特化
### 类模板的特化
类模板特化是指在实例化类模板时，对特定类型的泛型进行特殊的处理，即用户指定所有特定类型的类模板时，通过特化过类模板生成的类可能与其他类有完全不同的结构。

特化类模板是需要对整个类模板进行声明定义：
```
template<>
class 类名<指定类型,指定类型,...>{//类成员}；
```

### 类模板的偏特化
偏特化与特化类似，只是特化会指定所有的泛型，而偏特化只指定部分泛型。
偏特化类模板是需要对整个类模板进行声明定义：
```
template<typename T,...不需要特化的泛型...>
class 类名<指定类型,...,不需要特化的泛型名,...>{//类成员}；
```

### 偏特化Demo
```cpp
#ifndef _PAIR_H
#define _PAIR_H
#include <iostream>

template <typename T1, typename T2>
class Pair
{
private:
	T1 first;
	T2 second;
public:
	Pair();
};

template <typename T1, typename T2>
Pair<T1,T2>::Pair()
{
	std::cout<<"Pair<T1,T2>::Pair"<<std::endl;
}

////////////////////////
//偏特化
template<typename T2>
class Pair<char, T2>
{
public:
	Pair();
};
template<typename T2>//偏特化，这里不能省略
Pair<char,T2>::Pair()
{
	std::cout<<"Pair<char,T2>::Pair"<<std::endl;
}

#endif
```
