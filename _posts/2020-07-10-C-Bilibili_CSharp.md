---
layout: post
title: "C#-Bilibili_CSharp"
date: 2020-07-10 00:03:00
categories: ["C#"]
tags: ["C#"]
---

https://www.bilibili.com/video/av2357992
C#本质论.pdf

<!--more-->
文件以.cs保存
C#支持中文

输出 `System.Console.WriteLine();`
输入 `System.Console.Read();`
占位符` System.Console.WriteLine("{0}{1}",,);`

字面值有默认类型 int double
`1.1f//float`
`1.1m//decimal`
指数写法 2E2 //200
十六进制 0xff //255
字符串中 使用@ 可以不使用转义（写路径时）

//判断代码执行时间
```csharp
using System.Diagnostics;
Stopwatch 计时器=new Stopwatch(); //支持中文
计时器.Start();
....
计时器.Start();
System.Console.WriteLine(计时器.ElapsedMilliseconds);
```

//StringBuilder 在多次操作string时 可能比string 快，需要测试
`StringBuilder sb=new StringBuilder();`

//string 的空值
`string.Empty`
`""`

null //含义不固定，需要设置

//可空修饰
`int? number=null; （和数据库交互）`

//
var //声明

//类型转换
//显式转换  高到低
`int.MaxValue;// int 最大值`
`checked{} //检测溢出。`
//隐式转换 低到高
//转换函数
`Parse();//解析字符串，非数字会出问题，考虑TryParse`
`System.Convert();`
`ToString();`
`TryParse`

//运算符
`?:`
`??`//空接合运算符，检查是否为空，A??B A若为空 输出B

//循环
`foreach(long x in a){};`

//随机数
`var r=new Random(); r.Next();`

//C#预处理指令
`#region    #endregion  //折叠代码段`

//list
```language
var nums =new List<int>();
nums.Add(3);
nums.Sort();
nums.Remove();
```

// 命名空间 类 方法 参数
//静态方法 只能调用静态方法
//传值、传引用ref、out参数
ref string//字符串不变性

重载 参数  //操作符重载，赋值操作符不能被重载
重载自定义的类型转换操作符，须用implicit（隐式转换）或 explicit（显式转换）关键字

泛型 模板 T   Func<T>()
可变参数 关键字：params 必须放在参数的最后 //  int Func(params int[] nums);

//-Exception
捕获并处理异常  `try{} catch(){}finally{}`  //try 然后两次tab键 try 1/catch */finally 1
catch(){ throw;}//抛出异常，外层函数处理。 
   没有throw时，程序遇到异常会继续执行。
```csharp
/*
long FileOrDirCount(string path){
	long count=0;
	try
	{
		//
	var files =Directory.GetFiles(path);
	count += files.Length;	
	  	//
	var dirs = Directory.GetDirectories(path);
	foreach(var dir in dirs)
	{
 		count += FileOrDirCount(dir);
	}
	}
	catch( UnauthorizedAccessException ex)
	{
	 System.Console.WriteLine(ex.Message);
	//throw;
	}
	return count;
}
*/
```

默认参数
命名参数

main的参数和返回值

//类
面向对象： 封装 继承 多态
类的修饰符 默认是private
//public、 protected、 protected  、internal  、protected internal
属性 中get、set； // prop 两次tab自动生成get、 set
```language
/*
public string Name{get; set;}
*/
/*
 public string Name
{
 	get{return _Name;}
	set{_Name=value;}//这里可以抛出异常
}
*/
```

在同一个类中(针对同一个对象实例),从一个构造器中调用另一个构造器，C#采取的语法格式是在一个冒号后面添加this关键字，再添加与被调用构造器对应的一个参数列表

静态成员  具有全局性，属于类型，非实例
其字段属性访问时不需要实例
其方法内部不能使用this
其构造器，初始化内部成员
其类 Main

//设计模式 23种  ////《设计模式之禅》
之一 单例模式 // ...
之二 工厂模式 // 用到抽象
之三 策略模式
之四 订阅/发布模式
之五 GRASP

readonly  运行时 //仅能在声明、构造函数中赋值
const  编译时

嵌套类
分部类 ，partial
分部方法，在分部类中  partial void Func();// 必须是void

//继承  冒号：
单一继承
private 不能被继承
protected 可以用于继承派生
密封类 ，sealed
base 访问基类的成员、构造函数
类型转换 基类 A = new 子类();//反向，会有问题

多态：一个类型，多种状态
virtual override //用于属性、方法； 将变化封闭  ；override 可以 继续继承

abstract 抽象类  ，实例化后无意义
代表抽象的实体
定义抽象成员后 属性、方法 不再需要提供 默认实现了
并强制派生类 提供实现

Thread.Sleep(1000); //1000ms

所有类 是从System.Object 派生
is  //判断
as  //转换

//接口   ///方法的集合，隐式接口常用
弥补单一继承的缺陷   跨继承的多态
interface
跨继承
继承（作用是共享代码）只能一次，接口（首选）>抽象类
接口可以继承接口
注意：
	接口的语义
	一个类可以实现多个接口，无限制
	所有方法、属性必须实现
	成员都是public
	标准术语：实现接口
	无法实例化一个接口
显式/隐式接口
	隐式的接口,必须要有public访问修饰符
	显式的接口不能有任何的访问修饰符
	隐式实现对象声明为接口和类都可以访问到其行为
	显式实现只有声明为接口可以访问

//UML Unified Modeling Language (_UML_)又称统一建模语言或标准建模语言
vs可以查看类图  需要安装时选择类设计器组件

struct 值类型
enum   值类型

//泛型
where T:struct//约束，值类型
泛型使用在类、方法、接口
最常用泛型，集合

//vs的程序结构
解决方案 .sln
项目（程序集[Assembly]包 模块）dll exe
命名空间 （避免一个项目中 重命名）

dll// 动态链接库
	导入dll： 1.手动   2.[DllImport(...)],仅用于方法

//垃圾回收
内存管理的一种方式
栈 堆（new 托管堆）

//资源清理
确定性终结
using
IDisposable

//写入 读取文件  流
```language
/*
StreamWriter sw=new StreamWriter(new FileStream("filename",FileMode.Create,FileAccess.Write));
sw.WriteLine("123");
sw.Close();
*/
/*
using(var sw=new StreamWriter(new FileStream("filename",FileMode.Create,FileAccess.Write))
{sw.WriteLine("123");}
*/

```

装箱 拆箱
弱引用
延迟初始化

//委托  匿名函数
回调函数
Lambda
简化：
```javascript
语句Lambda	:
		(type var,...)=>{...};
		(var,..)=>{...};
		var=>{...};
		()=>{...};
	表达式 Lambda
		没有{}，只能有一条语句
```

系统自带的 泛型委托
```language
	Action<>  ，例List<T>.ForEach();
	Func<>	  ，例List<T>.Sum();
	Predicate<>，例List<T>.FindAll();    List<T>.Find();
```
Lambda访问外部变量
表达式树
//多播委托  ///链表式+= -=
将公共操作统一到接口实现。
订阅、注册
退订、取消注册

包容类、外部类
//关键字event
```language
/*
public delegate void XX(Newspaper n);
public event XX xx;
*/
```
提供两个额外封装
提供更加抽象

//迭代器
```language
yield return;
yield break;
```


//集合
实现IEnumerable接口的类
foreach 具有不可修改的特性  //与for相比
常用集合:
```language
List<T>
Dictionary<TKey,TValue>
  字典的遍历  字典的字典  键值数据库
SortedList SortedDic...
Stack<T>
Queue<T>
LinkedList<T>
```

匿名类型 new{...}
隐式类型 var
集合初始化器
对象初始化器

扩展方法
扩展已经封闭的代码
使用方法:
	1.定义静态类
	2.定义静态方法	
	3.使用this关键字指示实例化对象

//标准查询运算符
IEnumerable<T>中每一个方法
所有的方法定义在System.Linq.Enumerable中
使用时，只需要using System.Linq

//Linq ////http://web.archive.org/web/20171028111558/http://www.bilibili.com:80/video/av2357992/
Language INtegrated Query  语言集成查询
查询表达式
Where
投影 Select  得到指定路径的 文件名 和大小
Count
  如果if(list.Count()>0){...} 可以使用list.Any
排序 OrderBy  ThenBy //只能有一个OrderBy，后面的会覆盖之前
分组 GroupBy
连接 Join
删除重复Distinct、
并集 Union
交集 Intersect
连接 Concat
延迟查询 
SelectMany() 处理集合的集合
左外连接 右外连接 全外连接
///《LINQ IN ACTION》

//反射
运行时 操作某个类型的元数据
两种方法：
  	实例.GetType()
	typeof(类型)
注 一个类型只有一个type
  func.Invoke

根据字符串 创建类 
Assembly
	.Load("程序集名称")
	.CreateInstance("命名空间.类名")
配合接口使用
封闭变化的利器

//特性
展示一下程序集文件中的 特性 
用途：提供一个额外元数据
AttributeUsage

```java
/*
public class RequiredAttribute:System.Attribute
{
	public static bool IsPropertyRequired(object obj)
	{
	var type =obj.GetType();
	var properties =type.GetProperties();
 	
	foreach(var propetry in properties)
	{
		var attributes = 		propetry.GetCustomAttributes(typeof(RequiredAttribute),false);
		if(attributes.Length>0)
		{
			if(propetry.GetValue(obj,null)==null) return false;
		}
	}
		return true;
	}
}
*/
```

//序列化、反序列化
```language
BinaryFormatter.Serialize
BinaryFormatter.Deserialize
```

//动态编程  ///可以解析xml
dynamic


//多线程 
进程--〉线程 
线程间可以共享数据
线程是切换执行的
创建线程 、
第一种方法，无返回值
```language
	var task = new Task(..);
  注  task.Start()   
	  task.Wait()
```
第二种方法，可有可无返回值
```language
 	var task = Task.Factory.StartNew(..);
  注  task.Result()会阻塞   
	  直接执行，无需Start();
```

线程上的异常处理，//线程内的异常被抑制
方法一
```language
try 下面的语句，即可捕获
  task.Wait()
  task.Result()
  task.WaitAll()
  task.WaitAny()
```
方法二
`使用task.ContinueWith(..)`

//并行处理
```language
Parallel.For()
Parallel.ForEach()
PLINQ -- x.AsParallel().x
```

//同步
原子性 线程安全
使用lock关键字
  使得操作具有 原子性
对可变的状态进行同步
不更改的东西不需要同步
个线程访问同一个对象时，必须加锁
```language
/*
private static readonly object Syn= new object();
*/
//Interlocked
/*
Interlocked.Increment();
*/
```

`//Debug.Assert();///断言`

```language
//DateTime
var dt=DateTime.Now;
dt.ToString("格式")
使用前导0格式。 ///可以比较大小
DateTime.Parse();
```

//internal   ///用于dll修饰
修饰的类只能在包内部使用

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710000512251-1491700614.png)



//GUID
全局唯一标识符
`var guid=Guid.NewGuid().ToString("D");`

//访问excel
com组件
OleDbConnection
引用别人的DLL，如NPOI

//正则表达式
....

//访问剪贴板
`Clipboard.SetText(...)`
对于控制台稍微要麻烦点
添加了Forms引用后，还需将Main函数头上加上[STAThread]特性
对于多线程使用Clipboard这个类也是要将线程模式设置为STA


//避免硬编码，参数化配置
常用反射 配置文件 数据库
因为CS项目重新部署 很麻烦
《敏捷软件开发 原则模式与实践》

版本控制  多人协作
