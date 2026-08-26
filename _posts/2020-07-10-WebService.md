---
layout: post
title: WebService
date: 2020-07-10 00:15:00
categories:
- Personal / Misc
tags:
- 未分类
- Webservice
---

* https://www.cnblogs.com/xdp-gacl/p/4048937.html

<!--more-->
## 一、序言
当前的应用程序开发逐步的呈现了两种迥然不同的倾向：
一种是基于浏览器的瘦客户端应用程序，
一种是基于浏览器的富客户端应用程序（RIA），当然后一种技术相对来说更加的时髦一些（如现在很流行的Html5技术），这里主要讲前者。

基于浏览器的瘦客户端应用程序并不是因为瘦客户能够提供更好的用户界面，而是因为它能够避免花在桌面应用程序发布上的高成本。发布桌面应用程序成本很高，一半是因为应用程序安装和配置的问题，另一半是因为客户和服务器之间通信的问题。传统的Windows富客户应用程序使用DCOM来与服务器进行通信和调用远程对象。配置好DCOM使其在一个大型的网络中正常工作将是一个极富挑战性的工作，同时也是许多IT工程师的噩梦。事实上，许多IT工程师宁愿忍受浏览器所带来的功能限制，也不愿在局域网上去运行一个DCOM。**关于客户端与服务器的通信问题，一个完美的解决方法是使用HTTP协议来通信**。这是因为任何运行Web浏览器的机器都在使用HTTP协议。同时，当前许多防火墙也配置为只允许HTTP连接。许多商用程序还面临另一个问题，那就是与其他程序的互操作性。如果所有的应用程序都是使用COM或.NET语言写的，并且都运行在Windows平台上，那就天下太平了。然而，事实上大多数商业数据仍然在大型主机上以非关系文件(VSAM)的形式存放，并由COBOL语言编写的大型机程序访问。而且，目前还有很多商用程序继续在使用C++、Java、Visual Basic和其他各种各样的语言编写。现在，除了最简单的程序之外，所有的应用程序都需要与运行在其他异构平台上的应用程序集成并进行数据交换。这样的任务通常都是由特殊的方法， 如文件传输和分析，消息队列，还有仅适用于某些情况的API，如IBM的高级程序到程序交流(APPC)等来完成的。在以前，没有一个应用程序通信标准，是独立于平台、组件模型和编程语言的。只有通过Web Service，客户端和服务器才能够自由的用HTTP进行通信，不论两个程序的平台和编程语言是什么。

## 二、WebService到底是什么
**WebService是一种跨编程语言和跨操作系统平台的远程调用技术。**
    所谓**跨编程语言和跨操作平台**，就是说服务端程序采用java编写，客户端程序则可以采用其他编程语言编写，反之亦然！跨操作系统平台则是指服务端程序和客户端程序可以在不同的操作系统上运行。
    
所谓**远程调用**，就是一台计算机a上的一个程序可以调用到另外一台计算机b上的一个对象的方法，譬如，银联提供给商场的pos刷卡系统，商场的POS机转账调用的转账方法的代码其实是跑在银 行服务器上。再比如，amazon，天气预报系统，淘宝网，校内网，百度等把自己的系统服务以webservice服务的形式暴露出来，让第三方网站和程 序可以调用这些服务功能，这样扩展了自己系统的市场占有率，往大的概念上吹，就是所谓的SOA应用。
    
   其实可以从多个角度来理解 WebService，从表面上看，++WebService就是一个应用程序向外界暴露出一个能通过Web进行调用的API，也就是说能用编程的方法通过 Web来调用这个应用程序++。我们把调用这个WebService的应用程序叫做客户端，而把提供这个WebService的应用程序叫做服务端。从深层次 看，WebService是建立可互操作的分布式应用程序的新平台，是一个平台，是一套标准。它定义了应用程序如何在Web上实现互操作性，你可以用任何你喜欢的语言，在任何你喜欢的平台上写Web service ，只要我们可以通过Web service标准对这些服务进行查询和访问。 
   
   WebService平台需要一套协议来实现分布式应用程序的创建。任何平台都有它的数据表示方法和类型系统。要实现互操作性，WebService平台必须提供一套标准的类型系统，用于沟通不同平台、编程语言和组件模型中的不同类型系统。Web service平台必须提供一种标准来描述 Web service，让客户可以得到足够的信息来调用这个Web service。最后，我们还必须有一种方法来对这个Web service进行远程调用,这种方法实际是一种**远程过程调用协议(RPC)**。为了达到互操作性，这种RPC协议还必须与平台和编程语言无关。
   
## 三、WebService平台技术
XML+XSD,SOAP和WSDL就是构成WebService平台的三大技术。
3.1、XML+XSD

　　WebService采用HTTP协议传输数据，采用XML格式封装数据（即XML中说明调用远程服务对象的哪个方法，传递的参数是什么，以及服务对象的返回结果是什么）。XML是WebService平台中表示数据的格式。除了易于建立和易于分析外，XML主要的优点在于它既是平台无关的，又是厂商无关的。无关性是比技术优越性更重要的：软件厂商是不会选择一个由竞争对手所发明的技术的。 

　　XML解决了数据表示的问题，但它没有定义一套标准的数据类型，更没有说怎么去扩展这套数据类型。例如，整型数到底代表什么？16位，32位，64位？这些细节对实现互操作性很重要。XML Schema(XSD)就是专门解决这个问题的一套标准。它定义了一套标准的数据类型，并给出了一种语言来扩展这套数据类型。WebService平台就是用XSD来作为其数据类型系统的。当你用某种语言(如VB.NET或C#)来构造一个Web service时，为了符合WebService标准，所有你使用的数据类型都必须被转换为XSD类型。你用的工具可能已经自动帮你完成了这个转换，但你很可能会根据你的需要修改一下转换过程。

  3.2、SOAP

 WebService通过HTTP协议发送请求和接收结果时，发送的请求内容和结果内容都采用XML格式封装，并增加了一些特定的HTTP消息头，以说明 HTTP消息的内容格式，这些特定的HTTP消息头和XML内容格式就是SOAP协议。SOAP提供了标准的RPC方法来调用Web Service。

  **SOAP协议 = HTTP协议 + XML数据格式**

  SOAP协议定义了SOAP消息的格式，SOAP协议是基于HTTP协议的，SOAP也是基于XML和XSD的，XML是SOAP的数据编码方式。打个比喻：HTTP就是普通公路，XML就是中间的绿色隔离带和两边的防护栏，SOAP就是普通公路经过加隔离带和防护栏改造过的高速公路。

3.3、WSDL

　　好比我们去商店买东西，首先要知道商店里有什么东西可买，然后再来购买，商家的做法就是张贴广告海报。 WebService也一样，WebService客户端要调用一个WebService服务，首先要知道这个服务的地址在哪，以及这个服务里有什么方法可以调用，所以，WebService服务器端首先要通过一个WSDL文件来说明自己家里有啥服务可以对外调用，服务是什么（服务中有哪些方法，方法接受的参数是什么，返回值是什么），服务的网络地址用哪个url地址表示，服务通过什么方式来调用。

　　WSDL(Web Services Description Language)就是这样一个基于XML的语言，用于描述Web Service及其函数、参数和返回值。它是WebService客户端和服务器端都能理解的标准格式。因为是基于XML的，所以WSDL既是机器可阅读的，又是人可阅读的，这将是一个很大的好处。一些最新的开发工具既能根据你的 Web service生成WSDL文档，又能导入WSDL文档，生成调用相应WebService的代理类代码。

　　WSDL 文件保存在Web服务器上，通过一个url地址就可以访问到它。客户端要调用一个WebService服务之前，要知道该服务的WSDL文件的地址。 WebService服务提供商可以通过++两种方式++来暴露它的WSDL文件地址：**1.注册到UDDI服务器，以便被人查找；2.直接告诉给客户端调用者。**

## 四、WebService开发

　　WebService开发可以分为服务器端开发和客户端开发两个方面

### 4.1、服务端开发

　　把公司内部系统的业务方法发布成WebService服务，供远程合作单位和个人调用。(借助一些WebService框架可以很轻松地把自己的业务对象发布成WebService服务，Java方面的典型WebService框架包括：axis，xfire，cxf 等，java ee服务器通常也支持发布WebService服务，例如JBoss。)

### 4.2、客户端开发 

　　调用别人发布的WebService服务，大多数人从事的开发都属于这个方面，例如，调用天气预报WebService服务。（使用厂商的WSDL2Java之类的工具生成静态调用的代理类代码；使用厂商提供的客户端编程API类；使用SUN公司早期标准的jax-rpc开发包；使用 SUN公司最新标准的jax-ws开发包。当然SUN已被ORACLE收购)

### 4.3、WebService 的工作调用原理

   对客户端而言，我们给这各类WebService客户端API传递wsdl文件的url地址，这些API就会创建出底层的代理类，我调用这些代理，就可以访问到webservice服务。代理类把客户端的方法调用变成soap格式的请求数据再通过HTTP协议发出去，并把接收到的soap 数据变成返回值返回。对服务端而言，各类WebService框架的本质就是一个大大的Servlet，当远程调用客户端给它通过http协议发送过来 soap格式的请求数据时，它分析这个数据，就知道要调用哪个java类的哪个方法，于是去查找或创建这个对象，并调用其方法，再把方法返回的结果包装成 soap格式的数据，通过http响应消息回给客户端。

## 五、适用场合

### 1、跨防火墙通信

　　如果应用程序有成千上万的用户，而且分布在世界各地，那么客户端和服务器之间的通信将是一个棘手的问题。因为客户端和服务器之间通常会有防火墙或者代理服务器。在这种情况下，使用DCOM就不是那么简单，通常也不便于把客户端程序发布到数量如此庞大的每一个用户手中。传统的做法是，选择用浏览器作为客户端，写下一大堆ASP页面，把应用程序的中间层暴露给最终用户。这样做的结果是开发难度大，程序很难维护。如果中间层组件换成WebService的话，就可以从用户界面直接调用中间层组件。从大多数人的经验来看，在一个用户界面和中间层有较多交互的应用程序中，使用WebService这种结构，可以节省花在用户界面编程上20%的开发时间。

### 2、应用程序集成

　　企业级的应用程序开发者都知道，企业里经常都要把用不同语言写成的、在不同平台上运行的各种程序集成起来，而这种集成将花费很大的开发力量。应用程序经常需要从运行在IBM主机上的程序中获取数据；或者把数据发送到主机或UNIX应用程序中去。即使在同一个平台上，不同软件厂商生产的各种软件也常常需要集成起来。通过WebService，可以很容易的集成不同结构的应用程序。

### 3、B2B集成

　　用WebService集成应用程序，可以使公司内部的商务处理更加自动化。但当交易跨越供应商和客户、突破公司的界限时会怎么样呢？跨公司的商务交易集成通常叫做B2B集成。WebService是B2B集成成功的关键。通过WebService，公司可以把关键的商务应用“暴露”给指定的供应商和客户。例如，把电子下单系统和电子发票系统“暴露”出来，客户就可以以电子的方式发送订单，供应商则可以以电子的方式发送原料采购发票。当然，这并不是一个新的概念，EDI(电子文档交换)早就是这样了。但是，WebService的实现要比EDI简单得多，而且WebService运行在Internet 上，在世界任何地方都可轻易实现，其运行成本就相对较低。不过，WebService并不像EDI那样，是文档交换或B2B集成的完整解决方案。 WebService只是B2B集成的一个关键部分，还需要许多其它的部分才能实现集成。

　　用WebService来实现B2B集成的最大好处在于可以轻易实现互操作性。只要把商务逻辑“暴露”出来，成为WebService，就可以让任何指定的合作伙伴调用这些商务逻辑，而不管他们的系统在什么平台上运行，使用什么开发语言。这样就大大减少了花在B2B集成上的时间和成本，让许多原本无法承受 EDI的中小企业也能实现B2B集成。

### 4、软件和数据重用

   软件重用是一个很大的主题，重用的形式很多，重用的程度有大有小。最基本的形式是源代码模块或者类一级的重用，一种形式是二进制形式的组件重用。采用 WebService应用程序可以用标准的方法把功能和数据“暴露”出来，供其它应用程序使用，达到业务级重用。

## 六、不适用场合

### 1、单机应用程序

 目前，企业和个人还使用着很多桌面应用程序。其中一些只需要与本机上的其它程序通信。在这种情况下，最好就不要用WebService，只要用本地的 API就可以了。COM非常适合于在这种情况下工作，因为它既小又快。运行在同一台服务器上的服务器软件也是这样。最好直接用COM或其它本地的API来 进行应用程序间的调用。当然WebService也能用在这些场合，但那样不仅消耗太大，而且不会带来任何好处。

### 2、局域网的同构应用程序

 在许多应用中，所有的程序都是用VB或VC开发的，都在Windows平台下使用COM，都运行在同一个局域网上。例如，有两个服务器应用程序需要相互通信，或者有一个Win32或WinForm的客户程序要连接局域网上另一个服务器的程序。在这些程序里，使用DCOM会比SOAP/HTTP有效得多。与此相类似，如果一个.NET程序要连接到局域网上的另一个.NET程序，应该使用.NET Remoting。有趣的是，在.NET Remoting 中，也可以指定使用SOAP/HTTP来进行WebService调用。不过最好还是直接通过TCP进行RPC调用，那样会有效得多。


# 归纳
## 一、WebService是什么？
　　1\. 基于Web的服务：服务器端整出一些资源让客户端应用访问（获取数据）
　　2\. 一个跨语言、跨平台的规范（抽象）
　　3\. 多个跨平台、跨语言的应用间通信整合的方案（实际）

## 二、为什么要用Web service？
web service能解决：
1.  跨平台调用
2.  跨语言调用
3.  远程调用

## 三、什么时候使用web Service?
　　1\. 同一家公司的新旧应用之间
　　2\. 不同公司的应用之间
　　3\. 一些提供数据的内容聚合应用：天气预报、股票行情

## 四、Web Service中的几个重要术语

### 4.1、WSDL(web service definition language)

WSDL是webservice定义语言, 对应.wsdl文档, 一个webservice会对应一个唯一的wsdl文档, 定义了客户端与服务端发送请求和响应的数据格式和过程

### 4.2、SOAP(simple object access protocol)

　　SOAP是"**简单对象访问协议**"

1.  是一种简单的、基于HTTP和XML(http://baike.baidu.com/view/63.htm)的协议, 用于在WEB上交换结构化的数据
2.  soap消息：请求消息和响应消息

### 4.3、SEI(WebService EndPoint Interface)

　　SEI是web service的终端接口，就是WebService服务器端用来处理请求的接口

### 4.4、CXF(Celtix + XFire)

　　一个apache的用于开发webservice服务器端和客户端的框架。

# [调用第三方提供的webService服务](https://www.cnblogs.com/xdp-gacl/p/4260627.html)

http://www.webxml.com.cn/zh_cn/web_services.aspx
- WebService的wsdl描述
- wsimport命令工具自动生成客户端代码
- "wsimport -keep http://webservice.webxml.com.cn/WebServices/WeatherWS.asmx?wsdl"生成客户端代码
- 结果显示，使用wsimport工具直接生成客户端代码会抛异常, 无法生成客户端代码, 只是因为我们要调用的WebService是用.net写的，这个是Java调用net的webservice都有的问题，这个问题的解决办法如下：
	1.  将对应的wsdl文档保存到本地
	2. 修改wsdl文档的部分内容:将 <s:element ref="s:schema" /><s:any /> 替换成 <s:any minOccurs="2" maxOccurs="2"/>
	3. 再次执行wsimport生成代码，这次使用保存在本地的WeatherWS.wsdl文件来进行生成

https://blog.csdn.net/c99463904/article/details/76018436

WebService交互的过程就是,WebService遵循SOAP协议通过XML封装数据，然后由Http协议来传输数据。

JAVA WebService规范
Java 中共有三种WebService 规范，分别是JAXM&SAAJ、JAX-WS（JAX-RPC）、JAX-RS。

(1)JAX-WS：
JAX-WS（Java API For XML-WebService）。早期的基于SOAP 的JAVA 的Web 服务规范JAX-RPC（java API For XML-Remote Procedure Call）目前已经被JAX-WS 规范取代，JAX-WS 是JAX-RPC 的演进版本，但JAX-WS 并不完全向后兼容JAX-RPC，二者最大的区别就是RPC/encoded 样式的WSDL，JAX-WS 已经不提供这种支持。JAX-RPC 的API 从JAVA EE5 开始已经移除，如果你使用J2EE1.4，其API 位于javax.xml.rpc.包。JAX-WS（JSR 224）规范的API 位于javax.xml.ws.包，其中大部分都是注解，提供API 操作Web 服务（通常在客户端使用的较多，由于客户端可以借助SDK 生成，因此这个包中的API 我们较少会直接使用）。

(2)JAXM&SAAJ：
JAXM（JAVA API For XML Message）主要定义了包含了发送和接收消息所需的API，相当于Web 服务的服务器端，其API 位于javax.messaging.*包，它是Java EE 的可选包，因此你需要单独下载。

SAAJ（SOAP With Attachment API For Java，JSR 67）是与JAXM 搭配使用的API，为构建SOAP 包和解析SOAP 包提供了重要的支持，支持附件传输，它在服务器端、客户端都需要使用。这里还要提到的是SAAJ 规范，其API 位于javax.xml.soap.*包。

JAXM&SAAJ 与JAX-WS 都是基于SOAP 的Web 服务，相比之下JAXM&SAAJ 暴漏了SOAP更多的底层细节，编码比较麻烦，而JAX-WS 更加抽象，隐藏了更多的细节，更加面向对象，实现起来你基本上不需要关心SOAP 的任何细节。那么如果你想控制SOAP 消息的更多细节，可以使用JAXM&SAAJ。

(3)JAX-RS：
JAX-RS 是JAVA 针对REST(Representation State Transfer)风格制定的一套Web 服务规范，由于推出的较晚，该规范（JSR 311，目前JAX-RS 的版本为1.0）并未随JDK1.6 一起发行。

---------------------
作者：春水上行
来源：CSDN
原文：https://blog.csdn.net/c99463904/article/details/76018436 
版权声明：本文为博主原创文章，转载请附上博文链接！


## **WSDL**

**WSDL(Web Services Description Language), web服务描述语言，它是webservice服务端使用说明书，说明服务端接口、方法、参数和返回值，WSDL是随服务发布成功，自动生成，无需编写。**

**文档结构**
![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710001344875-634610450.png)

Service：相关端口的集合，包括其关联的接口、操作、消息等。
Binding：特定端口类型的具体协议和数据格式规范
portType: 服务端点，描述 web service可被执行的操作方法，以及相关的消息，通过binding指向portType
message: 定义一个操作（方法）的数据参数
types: 定义 web service 使用的全部数据类型

**阅读方式**

WSDL文档应该从下往上阅读。
1.先看service标签，看相应port的binding属性，然后通过值查找上面的binding标签。
2.通过binding标签可以获得具体协议等信息，然后查看binding的type属性
3.通过binding的type属性，查找对应的portType，可以获得可操作的方法和参数、返回值等。
4.通过portType下的operation标签的message属性，可以向上查找message获取具体的数据参数信息。

---------------------
作者：春水上行
来源：CSDN
原文：https://blog.csdn.net/c99463904/article/details/76018436 
版权声明：本文为博主原创文章，转载请附上博文链接！

**SOAP**

**SOAP即简单对象访问协议，它是使用http发送的XML格式的数据，它可以跨平台，跨防火墙，SOAP不是webservice的专有协议。**

**SOAP=http+xml**

**SOAP结构**
```
必需的 Envelope 元素，可把此 XML 文档标识为一条 SOAP 消息
可选的 Header 元素，包含头部信息
必需的 Body 元素，包含所有的调用和响应信息
可选的 Fault 元素，提供有关在处理此消息所发生错误的信息
```

![](https://img2020.cnblogs.com/blog/1488227/202007/1488227-20200710001321685-1012064511.png)

**UDDI**
**UDDI 是一种目录服务，企业可以使用它对 Web services 进行注册和搜索。**
**如果我们要使用一种服务，但是不知道地址（wsdl等），我们就可以在UDDI中查找。**
**大部分情况下，我们都是知道服务地址的。**
