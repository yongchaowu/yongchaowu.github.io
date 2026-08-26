---
layout: post
title: "Web-Session"
date: 2020-07-09 00:09:00
categories: ["Web"]
tags: ["Session", "Web"]
---

[Session原理](https://blog.csdn.net/weixin_42217767/article/details/92760353)

<!--more-->
Web三大概念：cookie，session，application

## 
Session：记录一系列状态
Session与cookie功能效果相同。Session与Cookie的区别在于Session是记录在服务端的，而Cookie是记录在客户端的。

**解释session**：当访问服务器否个网页的时候，会在服务器端的内存里开辟一块内存，这块内存就叫做session，而这个内存是跟浏览器关联在一起的。这个浏览器指的是浏览器窗口，或者是浏览器的子窗口，意思就是，只允许当前这个session对应的浏览器访问，就算是在同一个机器上新启的浏览器也是无法访问的。而另外一个浏览器也需要记录session的话，就会再启一个属于自己的session

**原理**：HTTP协议是非连接性的，取完当前浏览器的内容，然后关闭浏览器后，链接就断开了，而没有任何机制去记录取出后的信息。而当需要访问同一个网站的另外一个页面时(就好比如在第一个页面选择购买的商品后，跳转到第二个页面去进行付款)这个时候取出来的信息，就读不出来了。所以必须要有一种机制让页面知道原理页面的session内容。

**问题**：如何知道浏览器和这个服务器中的session是一一对应的呢？又如何保证不会去访问其它的session呢？

**原理解答**：就是当访问一个页面的时候给浏览器创建一个独一无二的号码，也给同时创建的session赋予同样的号码。这样就可以在打开同一个网站的第二个页面时获取到第一个页面中session保留下来的对应信息（理解：当访问第二个页面时将号码同时传递到第二个页面。找到对应的session。）。这个号码也叫sessionID，session的ID号码，session的独一无二号码。


**ession的两种实现方式（也就是传递方式）：第一种通过cookies实现。第二种通过URL重写来实现**

第一种方式的理解：就是把session的id 放在cookie里面（为什么是使用cookies存放呢，因为cookie有临时的，也有定时的，临时的就是当前浏览器什么时候关掉即消失，也就是说session本来就是当浏览器关闭即消失的，所以可以用临时的cookie存放。保存再cookie里的sessionID一定不会重复，因为是独一无二的。），当允许浏览器使用cookie的时候，session就会依赖于cookies，当浏览器不支持cookie后，就可以通过第二种方式获取session内存中的数据资源。

第二种方式的理解：在客户端不支持cookie的情况下使用。为了以防万一，也可以同时使用。

如果不支持cookie，必须自己编程使用URL重写的方式实现。

   如何重写URL：通过response.encodeURL()方法

   encodeURL()的两个作用
    第一个作用：转码（说明：转中文的编码，或者一些其他特殊的编码。就好比如网页的链接中存在中文字符，就会转换成为一些百分号或者其他的符号代替。）
    第二个作用：URL后面加入sessionID，当不支持cookie的时候，可以使用encodeURL()方法，encodeUTL()后面跟上sessionID，这样的话，在禁用cookie的浏览器中同时也可以使用session了。但是需要自己编程，只要链接支持，想用session就必须加上encodeURL()。

提示：若想程序中永远支持session，那就必须加上encodeURL()，当别人禁用了cookie，一样可以使用session。


	规则：
    - 如果浏览器支持cookie，创建session多大的时候，会被sessionID保存再cookie里。只要允许cookie，session就不会改变，如果不允许使用cookie，每刷新一次浏览器就会换一个session（因为浏览器以为这是一个新的链接）
    - 如果不支持cookie，必须自己编程使用URL重写的方式实现session
    - Session不像cookie一样拥有路径访问的问题，同一个application下的servlet/jsp都可以共享同一个session，前提下是同一个客户端窗口。


	Session中的一些常用方法说明
        isNew()：是否是新的Session，一般在第一次访问的时候出现
        getid()：拿到session，获取ID
        getCreationTime()：当前session创建的时间
        getLastAccessedTime()：最近的一次访问这个session的时间。
        getRrquestedSessionid： 跟随上个网页cookies或者URL传过来的session
        isRequestedSessionIdFromCookie()：是否通过Cookies传过来的
        isRequestedSessionIdFromURL()：是否通过重写URL传过来的
        isRequestedSessionIdValid()：是不是有效的sessionID

**session有期限：**
当一个网站的第一个窗口关掉了，而没有继续接着访问第二个页面，就没有使用到session。那么session会在中断程序后立刻关闭session吗？这个时候session就需要给它保留的时间，当最近一次访问的时候开始计时，每刷新一次重写开始计时。当隔了这么久的时间，没有访问这个session后，对不起，要关闭这个session了。session有过期时间，session什么时候过期，要看配置，

**session能干什么：**
session就是服务器里面的一块内存，内存里面能放任何东西，只要是名值对就可以了。

**session里面的名字永远都是String类型**
————————————————
版权声明：本文为CSDN博主「广小白」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/weixin_42217767/java/article/details/92760353