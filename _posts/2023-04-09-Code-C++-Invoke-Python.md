---
layout: post
title: C++ Invoke Python
date: 2023-04-09 10:46:00
categories:
- Programming
tags:
- C++
- Code
- Python
---

>[https://www.cnblogs.com/yongchao/p/17299892.html](https://www.cnblogs.com/yongchao/p/17299892.html "C++ invoke Python")

<!--more-->
- [使用 C 或 C++ 扩展 Python](https://docs.python.org/zh-cn/3.10/extending/extending.html#extracting-parameters-in-extension-functions "使用 C 或 C++ 扩展 Python")
- [扩展和嵌入 Python 解释器](https://docs.python.org/zh-cn/3.10/extending/index.html "扩展和嵌入 Python 解释器")
- [Python 3.10.11 Python/C API 参考手册](https://docs.python.org/zh-cn/3.10/c-api/index.html#c-api-index "Python 3.10.11 Python/C API 参考手册")
- [Python 3.11.3 Python/C API 参考手册](https://docs.python.org/zh-cn/3/c-api/index.html#c-api-index "Python 3.11.3 Python/C API 参考手册")

>1. https://www.cnblogs.com/lidabo/p/17043302.html
>2. https://blog.csdn.net/zong596568821xp/article/details/115690713

在调试过程中遇到以下问题：
1.Windows环境中，由于只有python39.lib，所以需要使用Release版本运行
2.Linux环境中，Ubuntu22.04系统自带的python缺少Python.h文件，需要安装Python-dev。参考文章：[https://www.cnblogs.com/yongchao/p/17299892.html](https://www.cnblogs.com/yongchao/p/17299892.html "C++ invoke Python")


## Code Demo
main.cpp
```cpp
// main.cpp

////c++调用流程
//c++ 调用 python ，本质上是在 c++ 中启动了一个 python 解释器，由解释器对 python 相关的代码进行执行，执行完毕后释放资源，达到调用目的

#include <Python.h>
int main(int argc, char *argv[]) {
  // 初始化python解释器.C/C++中调用Python之前必须先初始化解释器
  Py_Initialize();
  
  // 执行一个简单的执行python脚本命令
  PyRun_SimpleString("print('hello world')\n");
 
  // 撤销Py_Initialize()和随后使用Python/C API函数进行的所有初始化
  Py_Finalize();
  return 0;
}

//---------------------------------------------------------------

//调用 python 模块以及模块中的函数，并且有可能需要参数传递以及返回值获取

//--------------------------------
//无参数传递的函数调用功能
//./script/inittest.py  init
#include <Python.h>
#include <iostream>
 
using namespace std;
 
int main(){
    // 初始化python接口  
	Py_Initialize();
	if(!Py_IsInitialized()){
		cout << "python init fail" << endl;
		return 0;
	}
    // 初始化python系统文件路径，保证可以访问到 .py文件，python文件在当前目录的script文件夹中，当前调用python文件为inittest.py，当前调用inittest.py中函数名为init
	PyRun_SimpleString("import sys");
	PyRun_SimpleString("sys.path.append('./script')");
 
    // 调用python文件名，不用写后缀
	PyObject* pModule = PyImport_ImportModule("inittest");
	if( pModule == NULL ){
		cout <<"module not found" << endl;
		return 1;
	}
    // 调用函数
	PyObject* pFunc = PyObject_GetAttrString(pModule, "init");
	if( !pFunc || !PyCallable_Check(pFunc)){
		cout <<"not found function add_num" << endl;
		return 0;
	}
    // 
    PyObject_CallObject(pFunc, NULL);
    // 结束python接口初始化
	Py_Finalize();
	return 0;
}

//--------------------------------

//有参函数调用
// test2.cpp
#include <Python.h> 
#include <iostream>
using namespace std;
 
int main()
{
    //初始化python接口
    Py_Initialize(); 
    
    //初始化使用的变量
    PyObject* pModule = NULL;
    PyObject* pFunc = NULL;
    PyObject* pName = NULL;
    
    //初始化python系统文件路径，保证可以访问到 .py文件
    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('./script')");
    
    //调用python文件名，只需要写文件的名称就可以了，不用写后缀。
    pModule = PyImport_ImportModule("inittest");
    
    //调用函数add
    pFunc = PyObject_GetAttrString(pModule, "add");
    
    //给python传参数
    // 函数调用的参数传递均是以元组的形式打包的,2表示参数个数
    PyObject* pArgs = PyTuple_New(2);
 
    // 0：第一个参数，传入 int 类型的值 1
    PyTuple_SetItem(pArgs, 0, Py_BuildValue("i", 1)); 
    // 1：第二个参数，传入 int 类型的值 2
    PyTuple_SetItem(pArgs, 1, Py_BuildValue("i", 2)); 
    
    //使用C++的python接口调用该函数
    PyObject* pReturn = PyEval_CallObject(pFunc, pArgs);
    
    //接收python计算好的返回值
    int nResult;
    // i表示转换成int型变量。
    // 在这里，最需要注意的是：PyArg_Parse的最后一个参数，必须加上“&”符号
    PyArg_Parse(pReturn, "i", &nResult);
    cout << "return result is " << nResult << endl;
    
    //结束python接口初始化
    Py_Finalize();

    return 0;
}
```

./script/inittest.py
```python
def init():
    print("init test.")

def add(a,b):
    print("Now is in python module inittest/function add.")
    print("{} + {} = {}".format(a, b, a+b))
    return a + b
```

## Others（待更新）
>https://www.cnblogs.com/lidabo/p/17043302.html
参数类型、结构体等相关操作。

### 数字与字符串处理

在Python/C API中提供了`Py_BuildValue()`函数对数字和字符串进行转换处理，使之变成Python中相应的数据类型。其函数原型如下所示。
`PyObject* Py_BuildValue( const char *format, ...)`
其参数含义如下。
`·format：格式化字符串`
`Py_BuildValue()`函数中剩余的参数即要转换的C语言中的整型、浮点型或者字符串等。其返回值为`PyObject`型的指针。在C语言中，所有的Python类型都被声明为`PyObject`型。

### 列表操作

在Python/C API中提供了`PyList_New()`函数用以创建一个新的Python列表。
`PyList_New()`函数的返回值为所创建的列表。其函数原型如下所示。
`PyObject* PyList_New( Py_ssize_t len)`

其参数含义如下。
`·len：所创建列表的长度。`

----------

当列表创建以后，可以使用`PyList_SetItem()`函数向列表中添加项。其函数原型如下所示。
`int PyList_SetItem( PyObject *list, Py_ssize_t index, PyObject *item)`

其参数含义如下。
`·list：要添加项的列表。`
`·index：所添加项的位置索引。`
`·item：所添加项的值。`


同样可以使用Python/C API中`PyList_GetItem()`函数来获取列表中某项的值。`PyList_GetItem()`函数返回项的值。其函数原型如下所示。
`PyObject* PyList_GetItem( PyObject *list, Py_ssize_t index)`

其参数含义如下。
`·list：要进行操作的列表。`
`·index：项的位置索引。`


----------

Python/C API中提供了与Python中列表操作相对应的函数。例如列表的append方法对应于`PyList_Append()`函数。列表的sort方法对应于`PyList_Sort()`函数。列表的reverse方法对应于`PyList_Reverse()`函数。其函数原型分别如下所示。
```
int PyList_Append( PyObject *list, PyObject *item)
int PyList_Sort( PyObject *list)
int PyList_Reverse( PyObject *list)
```
对于PyList_Append()函数，其参数含义如下。
`·list：要进行操作的列表。`
`·item：要添加的项。`

对于PyList_Sort()和PyList_Reverse()函数，其参数含义相同。
`·list：要进行操作的列表。`


### 元组操作

在Python/C API中提供了`PyTuple_New()`函数，用以创建一个新的Python元组。
`PyTuple_New()`函数返回所创建的元组。其函数原型如下所示。
`PyObject* PyTuple_New( Py_ssize_t len)`

其参数含义如下。
`·len：所创建元组的长度。`

----------

当元组创建以后，可以使用`PyTuple_SetItem()`函数向元组中添加项。其函数原型如下所示。
`int PyTuple_SetItem( PyObject *p, Py_ssize_t pos, PyObject *o)`

其参数含义如下所示。
`·p：所进行操作的元组。`
`·pos：所添加项的位置索引。`
`·o：所添加的项值。`

可以使用Python/C API中`PyTuple_GetItem()`函数来获取元组中某项的值。`PyTuple_GetItem()`函数返回项的值。其函数原型如下所示。
`PyObject* PyTuple_GetItem( PyObject *p, Py_ssize_t pos)`

其参数含义如下。
`·p：要进行操作的元组。`
`·pos：项的位置索引。`

----------

当元组创建以后可以使用`_PyTuple_Resize()`函数重新调整元组的大小。其函数原型如下所示。
`int _PyTuple_Resize( PyObject **p, Py_ssize_t newsize)`

其参数含义如下。
`·p：指向要进行操作的元组的指针。`
`·newsize：新元组的大小。`


### 字典操作

在Python/C API中提供了`PyDict_New()`函数用以创建一个新的字典。
`PyDict_New()`函数返回所创建的字典。其函数原型如下所示。
`PyObject* PyDict_New()`


----------

当字典创建后，可以使用`PyDict_SetItem()`函数和`PyDict_SetItemString()`函数向字典中添加项。其函数原型分别如下所示。
`int PyDict_SetItem( PyObject *p, PyObject *key, PyObject *val)`
`int PyDict_SetItemString( PyObject *p, const char *key, PyObject *val)`

其参数含义如下。
`·p：要进行操作的字典。`
`·key：添加项的关键字，对于PyDict_SetItem()函数其为PyObject型，对于PyDict_SetItemString()函数其为char型。`
`·val：添加项的值。`

使用Python/C API中的`PyDict_GetItem()`函数和`PyDict_GetItemString()`函数来获取字典中某项的值。它们都返回项的值。其函数原型分别如下所示。
`PyObject* PyDict_GetItem( PyObject *p, PyObject *key)`
`PyObject* PyDict_GetItemString( PyObject *p, const char *key)`

其参数含义如下。
`·p：要进行操作的字典。`
`·key：添加项的关键字，对于PyDict_GetItem()函数其为PyObject型，对于PyDict_GetItemString()函数其为char型。`

----------

使用Python/C API中的`PyDict_DelItem()`函数和`PyDict_DelItemString()`函数可以删除字典中的某一项。其函数原型如下所示。
`int PyDict_DelItem( PyObject *p, PyObject *key)`
`int PyDict_DelItemString( PyObject *p, char *key)`

其参数含义如下。
`·p：要进行操作的字典。`
`·key：添加项的关键字，对于PyDict_DelItem()函数其为PyObject型，对于PyDict_DelItemString()函数其为char型。`

----------

使用Python/C API中的`PyDict_Next()`函数可以对字典进行遍历。其函数原型如下所示。
`int PyDict_Next( PyObject *p, Py_ssize_t *ppos, PyObject **pkey, PyObject **pvalue)`

其参数含义如下。
`·p：要进行遍历的字典。`
`·ppos：字典中项的位置，应该被初始化为0。`
`·pkey：返回字典的关键字。`
`·pvalue：返回字典的值。`

----------

在Python/C API中提供了与Python中字典操作相对应的函数。例如字典的item方法对应于`PyDict_Items()`函数。字典的keys方法对应于`PyDict_Keys()`函数。字典的values方法对应于`PyDict_Values()`函数。其函数原型分别如下所示。
```
PyObject* PyDict_Items( PyObject *p)
PyObject* PyDict_Keys( PyObject *p)
PyObject* PyDict_Values( PyObject *p)
```
其参数含义如下。
`·p：要进行操作的字典。`


### 释放资源

Python使用引用计数机制对内存进行管理，实现自动垃圾回收。
在C/C++中使用Python对象时，应正确地处理引用计数，否则容易导致内存泄漏。
在Python/C API中提供了`Py_CLEAR()`、`Py_DECREF()`等宏来对引用计数进行操作。

当使用Python/C API中的函数创建列表、元组、字典等后，就在内存中生成了这些对象的引用计数。在对其完成操作后应该使用`Py_CLEAR()`、`Py_DECREF()`等宏来销毁这些对象。其原型分别如下所示。
`void Py_CLEAR( PyObject *o)`
`void Py_DECREF( PyObject *o)`

其参数含义如下。
`·o：要进行操作的对象。`

对于`Py_CLEAR()`其参数可以为NULL指针，此时，`Py_CLEAR()`不进行任何操作。
而对于`Py_DECREF()`其参数不能为NULL指针，否则将导致错误。

### 模块与函数

使用Python/C API中的`PyImport_Import()`函数可以在C程序中导入Python模块。
`PyImport_Import()`函数返回一个模块对象。其函数原型如下所示。
`PyObject* PyImport_Import( PyObject *name)`

其参数含义如下。
`·name：要导入的模块名。`

使用Python/C API中的`PyObject_CallObject()`函数和`PyObject_CallFunction()`函数，可以在C程序中调用Python中的函数。其参数原型分别如下所示。
`PyObject* PyObject_CallObject( PyObject *callable_object, PyObject *args)`
`PyObject* PyObject_CallFunction( PyObject *callable, char *format, ...)`

对于`PyObject_CallObject()`函数，其参数含义如下。
`·callable_object：要调用的函数对象。`
`·args：元组形式的参数列表。`

对于`PyObject_CallFunction()`函数，其参数含义如下。
`·callable_object：要调用的函数对象。`
`·format：指定参数的类型。`
`·...：向函数传递的参数。`

----------

使用Python/C API中的`PyModule_GetDict()`函数可以获得Python模块中的函数列表。
`PyModule_GetDict()`函数返回一个字典。字典中的关键字为函数名，值为函数的调用地址。其函数原型如下所示。
`PyObject* PyModule_GetDict( PyObject *module)`

其参数含义如下。
`·module：已导入的模块对象。`
