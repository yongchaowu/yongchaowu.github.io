---
layout: post
title: "JSON的简单介绍以及C语言的JSON库使用"
date: 2020-07-10 02:13:00
categories: ["Json"]
tags: ["Json", "Open Source Library", "C"]
---

# [JSON的简单介绍以及C语言的JSON库使用](https://www.cnblogs.com/liunianshiwei/p/6087596.html)

<!--more-->
## JSON概述
　　JSON： JavaScript 对象表示法（ JavaScript Object Notation） 。是一种轻量级的数据交换格式。 它基于ECMAScript的一个子集。 JSON采用完全独立于语言的文本格式， 但是也使用了类似于C语言家族的习惯（ 包括C、 C++、 C#、 Java、 JavaScript、 Perl、 Python等） 。这些特性使JSON成为理想的数据交换语言。 易于人阅读和编写， 同时也易于机器解析和生成(一般用于提升网络传输速率)。
　　JSON 解析器和 JSON 库支持许多不同的编程语言。 JSON 文本格式在语法上与创建 JavaScript 对象的代码相同。 由于这种相似性， 无需解析器， JavaScript 程序能够使用内建的 eval() 函数， 用 JSON 数据来生成原生的 JavaScript 对象。
　　JSON 是存储和交换文本信息的语法。 类似 XML。 JSON 比 XML 更小、 更快， 更易解析。
　　JSON 具有自我描述性， 语法简洁， 易于理解。


## JSON语法说明
```json
{
  "stars": [
    {
      "name": "Faye",
      "address": "北京"
    },
    {
      "name": "andy",
      "address": "香港"
    },
    {
      "name": "eddie",
      "address": "台湾"
    },
    
  ]
}
```

JSON 语法是 JavaScript 对象表示法语法的子集。
          　数据在键/值对中；
          　数据由逗号分隔；
          　花括号保存对象， 也称一个文档对象；
          　方括号保存数组， 每个数组成员用逗号隔开， 并且每个数组成员可以是文档对象或者数组或者键值对 。

JSON基于两种结构：
　　　　“名称/值”对的集合（A collection of name/value pairs）。不同的编程语言中，它被理解为对象（object），纪录（record），结构（struct），字（dictionary），哈希表（hashtable），有键列表（keyed list），或者关联数组 （associative array）。
　　　　值的有序列表（An ordered list of values）。在大部分语言中，它被实现为数组（array），矢量（vector），列表（list），序列（sequence）。

JSON的三种语法： 
键/值对 key:value，用半角冒号分割。 比如 "name":"Faye" 　　　　
文档对象 JSON对象写在花括号中，可以包含多个键/值对。比如{ "name":"Faye" ,"address":"北京" }。 
数组 JSON 数组在方括号中书写： 数组成员可以是对象，值，也可以是数组(只要有意义)。 {"love": ["乒乓球","高尔夫","斯诺克","羽毛球","LOL","撩妹"]}

## cJson
附cJSON库下载地址 https://github.com/DaveGamble/cJSON 
cJSON库在使用的时候只需要如下两步:将cJSON.c(或者库文件) 和 cJSON.h添加到项目中即可;如果在命令行中进行链接 还需要加上-lm 表示链接math库 .

### C语言函数库写JSON文件 ： 

从缓冲区中解析出JSON结构：extern cJSON *cJSON_Parse(const char *value); 　　　　　　　　
解析一块JSON数据返回cJSON结构， 在使用完之后调用cJSON_Delete函数释放json对象结构。

将传入的JSON结构转化为字符串 ：extern char *cJSON_Print(cJSON *item); 　　　　　　　　
可用于输出到输出设备， 使用完之后free(char *) 。

将JSON结构所占用的数据空间释放 ：void cJSON_Delete(cJSON *c)

创建一个值类型的数据 ：
extern cJSON *cJSON_CreateNumber(double num);
extern cJSON *cJSON_CreateString(const char *string);
extern cJSON *cJSON_CreateArray(void);

创建一个对象（文档） ：extern cJSON *cJSON_CreateObject(void);

数组创建以及添加 ：
cJSON *cJSON_CreateIntArray(const int *numbers,int count);
void cJSON_AddItemToArray(cJSON *array, cJSON *item);

JSON嵌套 ：
【 向对象中增加键值对】 cJSON_AddItemToObject(root, "rows", 值类型数据相关函数());
【 向对象中增加数组】 cJSON_AddItemToObject(root, "rows", cJSON_CreateArray());
【 向数组中增加对象】 cJSON_AddItemToArray(rows, cJSON_CreateObject());

几个能提高操作效率的宏函数 ：
```language
#define cJSON_AddNumberToObject(object,name,n) \
cJSON_AddItemToObject(object, name,cJSON_CreateNumber(n))
#define cJSON_AddStringToObject(object,name,s)\
cJSON_AddItemToObject(object, name, cJSON_CreateString(s))
```

### C语言库函数解析JSON文件 ：

根据键找json结点 ：extern cJSON *cJSON_GetObjectItem(cJSON *object,const char *string)

判断是否有key是string的项 如果有返回1 否则返回0 ：extern int cJSON_HasObjectItem(cJSON *object,const char *string)
{ return cJSON_GetObjectItem(object,string)?1:0; }

返回数组结点array中成员的个数 ：extern int cJSON_GetArraySize(cJSON *array);

根据数组下标index取array数组结点的第index个成员 返回该成员节点 ：extern cJSON *cJSON_GetArrayItem(cJSON *array,int index);

遍历数组 ：
```language
#define cJSON_ArrayForEach(pos, head)        
for(pos = (head)->child; pos != NULL; pos = pos->next)
```

### other

#### JSON.stringify()
```javascript
JSON.stringify(value[, replacer [, space]])
将一个JavaScript值(对象或者数组)转换为一个 JSON字符串，如果指定了replacer是一个函数，则可以选择性的替换值，或者如果指定了replacer是一个数组，可选择性的仅包含数组指定的属性。

参数
`value`

将要序列化成 一个JSON 字符串的值。

`replacer` 可选

如果该参数是一个函数，则在序列化过程中，被序列化的值的每个属性都会经过该函数的转换和处理；如果该参数是一个数组，则只有包含在这个数组中的属性名才会被序列化到最终的 JSON 字符串中；如果该参数为null或者未提供，则对象所有的属性都会被序列化；关于该参数更详细的解释和示例，请参考[使用原生的 JSON 对象](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Guide/Using_native_JSON#The_replacer_parameter)一文。

`space` 可选

指定缩进用的空白字符串，用于美化输出（pretty-print）；如果参数是个数字，它代表有多少的空格；上限为10。该值若小于1，则意味着没有空格；如果该参数为字符串(字符串的前十个字母)，该字符串将被作为空格；如果该参数没有提供（或者为null）将没有空格。

返回值
一个表示给定值的JSON字符串。

描述
JSON.stringify()将值转换为相应的JSON格式：

*   转换值如果有toJSON()方法，该方法定义什么值将被序列化。
*   非数组对象的属性不能保证以特定的顺序出现在序列化后的字符串中。
*   布尔值、数字、字符串的包装对象在序列化过程中会自动转换成对应的原始值。
*   `undefined、`任意的函数以及 symbol 值，在序列化过程中会被忽略（出现在非数组对象的属性值中时）或者被转换成 `null`（出现在数组中时）。函数、undefined被单独转换时，会返回undefined，如`JSON.stringify(function(){})` or `JSON.stringify(undefined).`
*   对包含循环引用的对象（对象之间相互引用，形成无限循环）执行此方法，会抛出错误。
*   所有以 symbol 为属性键的属性都会被完全忽略掉，即便 `replacer` 参数中强制指定包含了它们。
*   Date日期调用了toJSON()将其转换为了string字符串（同Date.toISOString()），因此会被当做字符串处理。
*   NaN和Infinity格式的数值及null都会被当做null。
*   其他类型的对象，包括Map/Set/weakMap/weakSet，仅会序列化可枚举的属性。
```

#### 判断JSON对象是否为空对象
```
JSON.stringify(object) === '{}'
```
