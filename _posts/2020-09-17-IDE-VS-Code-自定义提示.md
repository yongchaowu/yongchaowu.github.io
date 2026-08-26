---
layout: post
title: VS Code-自定义提示
date: 2020-09-17 08:42:00
categories:
- Developer Tools
tags:
- Visual Studio Code
- IDE
---

September 16, 2020 2:52 PM

<!--more-->
## 用户片段

1.文件->首选项->用户片段
2.选择当前要配置的语言
```json
{
	// Place your snippets for c here. Each snippet is defined under a snippet name and has a prefix, body and 
	// description. The prefix is what is used to trigger the snippet and the body will be expanded and inserted. Possible variables are:
	// $1, $2 for tab stops, $0 for the final cursor position, and ${1:label}, ${2:another} for placeholders. Placeholders with the 
	// same ids are connected.
	// Example:
	// "Print to console": {
	// 	"prefix": "log",
	// 	"body": [
	// 		"console.log('$1');",
	// 		"$2"
	// 	],
	// 	"description": "Log output to console"
	// }
}
```

## Class形式
以类的形式提供函数和成员。
### 当前文件使用
```language
Demo.js：
class Demo {
    // constructor(height, width) {
    //   this.area = height * width;
    // }
    member = 0;
    create(strName);
    del(nID);
    query(nID);
    modify(nID,strInfo);
  }

var testObj = new Demo();
```

### 封装后使用
```language
Demo.js：
class Demo {
    // constructor(height, width) {
    //   this.area = height * width;
    // }
    member = 0;
    create(strName);
    del(nID);
    query(nID);
    modify(nID,strInfo);
  }

module.exports = Demo;

------------------------------------------

Test.js:
var currClass1 = require('./Demo.js');
var test = new currClass1();
test.create("Name");
test.member1;

```

## function形式-使自定义的数据类型颜色不同
定义一个不写实现的function，利用function的关键字高亮。
如：	 `function int64(){}`

## 修改vscode的配置文件
比如JavaScript类型的，配置文件地址如下：
`Microsoft VS Code\resources\app\extensions\javascript\syntaxes\JavaScript.tmLanguage.json`
具体信息可以参考ReadMe。源码是在github上，本地文件经过后缀替换。
内部匹配规则依赖于正则，因为没有vscode源码，所以这里是复制已有的项进行的实现，如下：
```language
原有的关于变量类型显示-显示为深绿色
{"name":"support.class.builtin.js","match":"(?x)(?<![_$[:alnum:]])(?:(?<=\\.\\.\\.)|(?<!\\.))(Array|ArrayBuffer|Atomics|BigInt|BigInt64Array|BigUint64Array|Boolean|DataView|Date|Float32Array\n  |Float64Array|Function|Generator|GeneratorFunction|Int8Array|Int16Array|Int32Array|Intl|Map|Number|Object|Proxy\n  |Reflect|RegExp|Set|SharedArrayBuffer|SIMD|String|Symbol|TypedArray\n  |Uint8Array|Uint16Array|Uint32Array|Uint8ClampedArray|WeakMap|WeakSet)\\b(?!\\$)"},
增加的自己定义的变量类型显示，验证后同样是深绿色
{"name":"support.class.variabletype.yongchao.js","match":"(?x)(?<![_$[:alnum:]])(?:(?<=\\.\\.\\.)|(?<!\\.))(bool|int8|uint8|int16|uint16|int32|uint32|int64|uint64|float|double|numeric|string|blob|array|JSONObject|datetime|timespan)\\b(?!\\$)"},
```


##vs code 插件
自己搞一个自定义的插件，给需要的关键字赋值。
实现可能性：
    1.有大量的语言配置主题，说明可以做；
    2.有一个智能路径匹配的插件，可以基于此基础实现
    3.插件开发说明：https://code.visualstudio.com/api
ps:晚上有事，没有做验证，插件部分是看的资料总结。