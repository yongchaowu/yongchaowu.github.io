---
layout: post
title: "Linux-C-信号&信号量"
date: 2020-07-10 00:53:00
categories: ["Linux"]
tags: ["信号量", "signal", "Linux", "C#", "C"]
---

July 10, 2020 12:49 AM

<!--more-->
## signal(SIGHUP, SIG_IGN);
signal(SIGHUP, SIG_IGN);
signal信号函数，第一个参数表示需要处理的信号值（SIGHUP），第二个参数为处理函数或者是一个表示，这里，SIG_IGN表示忽略SIGHUP那个注册的信号。

SIGHUP和控制台操作有关，当控制台被关闭时系统会向拥有控制台sessionID的所有进程发送HUP信号，默认HUP信号的action是 exit，如果远程登陆启动某个服务进程并在程序运行时关闭连接的话会导致服务进程退出，所以一般服务进程都会用nohup工具启动或写成一个 daemon。

## sem_t
C语言中，信号量的数据类型为结构sem_t，它本质上是一个长整型的数。
它的原型为：　
```
extern int sem_init __P ((sem_t *__sem, int __pshared, unsigned int __value));
```

头文件为： #include <semaphore.h>
sem为指向信号量结构的一个指针；
pshared不为0时此信号量在进程间共享，否则只能为当前进程的所有线程共享；
value给出了信号量的初始值。
函数`sem_post( sem_t *sem )`用来增加信号量的值当有线程阻塞在这个信号量上时，调用这个函数会使其中的一个线程不再阻塞，选择机制同样是由线程的调度策略决定的。
函数`sem_wait( sem_t *sem )`被用来阻塞当前线程直到信号量sem的值大于0，解除阻塞后将sem的值减一，表明公共资源经使用后减少。
函数`sem_trywait ( sem_t *sem )`是函数`sem_wait（）`的非阻塞版本，它直接将信号量sem的值减一。
函数`sem_destroy(sem_t *sem)`用来释放信号量sem。

相关应用
（1）信号量用sem_init函数创建的，下面是它的说明：
```cpp
#include<semaphore.h>
int sem_init (sem_t *sem, int pshared, unsigned int value);
```
这个函数的作用是对由sem指定的信号量进行初始化，设置好它的共享选项，并指定一个整数类型的初始值。pshared参数控制着信号量的类型。如果 pshared的值是0，就表示它是当前进程的局部信号量；否则，其它进程就能够共享这个信号量。只对不让进程共享的信号量感兴趣。（这个参数受版本影响），　Linux线程一般不支持进程间共享信号量，pshared传递一个非零将会使函数返回ENOSYS错误。
（2）这两个函数控制着信号量的值，它们的定义如下所示：
```cpp
#include <semaphore.h>
int sem_wait(sem_t * sem);
int sem_post(sem_t * sem);
```
这两个函数都要用一个由sem_init调用初始化的信号量对象的指针做参数。
sem_post函数的作用是给信号量的值加上一个“1”，它是一个“原子操作"即同时对同一个信号量做加“1”操作的两个线程是不会冲突的；而同时对同一个文件进行读、加和写操作的两个程序就有可能会引起冲突。信号量的值永远会正确地加一个“2”－－因为有两个线程试图改变它。
sem_wait函数也是一个原子操作，它的作用是从信号量的值减去一个“1”，但它永远会先等待该信号量为一个非零值才开始做减法。也就是说，如果你对一个值为2的信号量调用sem_wait(),线程将会继续执行，信号量的值将减到1。如果对一个值为0的信号量调用sem_wait()，这个函数就会地等待直到有其它线程增加了这个值使它不再是0为止。如果有两个线程都在sem_wait()中等待同一个信号量变成非零值，那么当它被第三个线程增加一个“1”时，等待线程中只有一个能够对信号量做减法并继续执行，另一个还将处于等待状态。
信号量这种“只用一个函数就能原子化地测试和设置”的能力下正是它的价值所在。还有另外一个信号量函数sem_trywait，它是sem_wait的非阻塞搭档。sem_trywait是一个立即返回函数，不会因为任何事情阻塞。根据其返回值得到不同的信息。如果返回值为0，说明信号量在该函数调用之前大于0，但是调用之后会被该函数自动减1，至于调用之后是否为零则不得而知了。如果返回值为EAGAIN说明信号量计数为0。
（3） 获得信号量sem的值，并保存到valp中。下面的定义：
```cpp
#include<semaphore.h>
int sem_getvalue(sem_t *sem, int *valp);
```
（4） 最后一个信号量函数是sem_destroy。这个函数的作用是在我们用完信号量对它进行清理。下面的定义：
```cpp
#include<semaphore.h>
int sem_destroy (sem_t *sem);
```
这个函数也使用一个信号量指针做参数，归还自己占据的一切资源。在清理信号量的时候如果还有线程在等待它，用户就会收到一个错误。
然而在linux的线程中，其实是没有任何资源关联到信号量对象需要释放的，因此在linux中，销毁信号量对象的作用仅仅是测试是否有线程因为该信号量在等待。如果函数返回0说明没有，正常注销信号量，如果返回EBUSY，说明还有线程正在等待该信号量的信号。
与其它的函数一样，这些函数在成功时都返回“0”。

使用步骤
1.声明信号量sem_t sem1;
2.初始化信号量sem_init(&sem1,0,1);
3.sem_post和sem_wait函数配合使用来达到线程同步
4.释放信号量int sem_destroy (&sem1);
