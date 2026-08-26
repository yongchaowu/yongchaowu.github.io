---
layout: post
title: OpenMP
date: 2024-07-08 21:06:00
categories:
- Programming
tags:
- Code
- OpenMP
---

- [openmp home](https://www.openmp.org/)
- [OpenMP 入门指南 - 离心的文章 - 知乎](https://zhuanlan.zhihu.com/p/658770855)

<!--more-->
---
以下转自[OpenMP 入门指南 - 离心的文章 - 知乎](https://zhuanlan.zhihu.com/p/658770855)
## OpenMP 入门指南

OpenMP是由OpenMP Architecture Review Board牵头提出的，并已被广泛接受，用于共享内存并行系统的多处理器程序设计的一套指导性编译处理方案(Compiler Directive)。OpenMP支持的编程语言包括C、C++和Fortran；而支持OpenMP的编译器包括Sun Compiler，GNU Compiler和Intel Compiler等。OpenMP提供了对并行算法的高层的抽象描述，程序员通过在源代码中加入专用的pragma来指明自己的意图，由此编译器可以自动将程序进行并行化，并在必要之处加入同步互斥以及通信。当选择忽略这些pragma，或者编译器不支持OpenMP时，程序又可退化为通常的程序(一般为串行)，代码仍然可以正常运作，只是不能利用多线程来加速程序执行。

### Header
- `omp.h`

### Vscode 配置
- `-fopenmp`


### 常用线程相关的函数调用库
```c++
// #include <omp.h>
omp_set_num_threads(3); // 设置进程的线程数为 3（在此后的分支区，一共会有三个线程参与进行）
int thread_num = omp_get_thread_num(); // 获取当前进程中的线程数，此处 thread_num = 3
int max_thread_num = omp_get_max_threads(); // 获取最多可以用于并行计算的线程数目
int thread_id = omp_get_thread_num();  // 获取当前线程的 id
int curTime = omp_get_wtime(); // 获取当前时间，秒为单位
int is_in_parallel = omp_in_parallel(); // 当前程序是否在并行中，1 表示并行，0表示串行
omp_set_nested(1); // 设置允许嵌套并行
int is_nested =  omp_get_nested(); // 获取当前程序是否允许嵌套并行
```

### 常用线程相关的环境变量
常用的 OpenMP 环境变量有：
- `OMP_NUM_THREADS`，它指明并行区域中最大的线程数目。
- `OMP_SCHEDULE`，它指明使用 schedule(runtime) 语句时将采取的调用策略。
- `OMP_NESTED`，它指明是否允许 OpenMP 采取嵌套并行。

### 常用编译指导语句
如果编译指导语句语法不对，会被当作一条注释。
格式如下：`#pragma omp 指令 [子句1] [子句2] [...]`

#### 编译指导语句常用指令

##### parallel 指令
parallel 的作用是划定一块并行区域。

parallel 用在一个结构块之前，表示这段代码将被多个线程并行执行。

所谓结构块，就是用花括号框起来的代码块。这个结构块被 parallel 设置为“并行区域”，并行区域中的代码将由所有线程各执行一次。

并行区域中的函数调用也会被分别执行一次。
```c++
omp_set_num_threads(3);
#pragma omp parallel 
{   // 并行区域-------------------------------
    for (int i = 0; i < 3; ++i) {
        printf("hhh, here is thread %d\n", omp_get_thread_num());
    }
}   // 并行区域结束------------------------
```

##### for 指令
for 指令一般使用在并行域（外部嵌套有 parallel）中，其作用是让多个线程合作完成同一个循环。

for 指令可以直接和 parallel 连用，既创建并行区域，又指导线程共同完成循环
```c++
omp_set_num_threads(3);
#pragma omp parallel for 
{
    for (int i = 0; i < 3; ++i) {
        printf("hhh, here is thread %d\n", omp_get_thread_num());
    }
}
```

for 也可以单独使用，比如上面的语句可以修改为：
```c++
omp_set_num_threads(3);
#pragma omp parallel 
{
    #pragma omp for 
    {
        for (int i = 0; i < 3; ++i) {
            printf("hhh, here is thread %d\n", omp_get_thread_num());
        }
    }
}
```

##### sections 指令
sections 指令一般使用在并行域（外部嵌套有 parallel）中，并且可以和 parallel 连用，成为 parallel sections

sections 的作用是划定一块代码区域，在代码区域内指定 section 代码块，不同的线程将会执行不同的代码块（每个代码块只会被一个线程执行），通过这种方式来指导线程进行分工。

```c++
#pragma omp parallel sections 
{
    #pragma omp section 
    {
        for (int i = 0; i < 3; ++i) {
            printf("hhh, here is thread %d and section 1\n", omp_get_thread_num());
        }
    }
    #pragma omp section 
    {
        for (int i = 0; i < 3; ++i) {
            printf("hhh, here is thread %d and section 2\n", omp_get_thread_num());
        }
    }
    #pragma omp section 
    {
        for (int i = 0; i < 3; ++i) {
            printf("hhh, here is thread %d and section 3\n", omp_get_thread_num());
        }
    }
}
```
每个线程会负责一个代码块，不同线程负责不同的代码块，代码块中不会受到其它代码块的干扰。

和 for 一样，sections 也能写成单独列出，嵌套在外层 parallel 中的形式。

注意：没有加 parallel 的 sections 里面的 section 是串行的。


##### single 和 master 指令
single 和用在并行域内（外部嵌套有 parallel），表示一段只被单个线程执行的代码；

使用 single 时执行这段代码的线程不一定是 master （编号为 $0$）线程，而是第一个到达 single 语句的线程，具有一定随机性；

而使用 master 时执行这段代码的线程一定是 master 线程。

在 single 和 master 划定的代码块执行时，其他的线程会等待直到 single 和 master 语句对应的区域执行完成。

```c++
#pragma omp parallel
{
#pragma omp for
        for (int i = 0; i < 3; ++i) {
            printf("hhh, here is thread %d\n", omp_get_thread_num());
        }
#pragma omp master
        for (int i = 0; i < 3; ++i) {
            printf("master %d\n run", omp_get_thread_num());
        }
#pragma omp single
        for (int i = 0; i < 3; ++i) {
            printf("the only thread to run single is %d\n", omp_get_thread_num());
        }
}
```

##### flush 指令
flush 保证各个 OpenMP 线程的数据影像的一致性

##### barrier 指令
barrier 用于并行域内代码的线程同步，线程执行到 barrier 时要停下等待，直到所有线程都执行到 barrier 时才继续往下执行。

parallel 和 for 创建区域结束时都有隐式同步 barrier

如下代码，会在所有线程都执行完 barrier 前的语句后才执行 barrier 语句
```c++
#pragma omp parallel
{
    printf("hhh, here is thread %d\n", omp_get_thread_num());
#pragma omp barrier
    printf("thread %d cross barrier\n", omp_get_thread_num());
}
```

##### atomic 指令
atomic 用于指定一个数据操作需要原子性地完成。即保证内存中的共享存储变量在某时刻只被同一线程修改。

这里指的数据操作就是类似于 ++、-- 这类操作。
```c++
#pragma omp parallel shared(a)
{
    #pragma omp atomic
    ++a;
    printf("thread %d : ++a is %d\n", omp_get_thread_num(), a);
}
```

##### critical 指令
critical 用在一段代码临界区之前，保证每次只有一个 OpenMP 线程进入，即保证程序的特定区域一次（时刻）只有一个线程执行

critical 的作用和 atomic 非常相似，区别是 atomic 只作用于单个数据操作（原子操作），而 critical 作用域是一段代码块。

理论上，只要是正确的代码块都可以使用 critical 划定区域。

```c++
#pragma omp parallel shared(a)
{
    #pragma omp critical
    {
        a++;
        printf("thread %d : ++a is %d\n", omp_get_thread_num(), a);
    }
}
```

##### threadprivate 指令
threadprivate 用于指定一个或多个变量是线程专用，将全局变量的副本与线程绑定，即使跨越多个并行区域这种关系也不会改变。

简单而言，就是为每个线程定义私有变量时增加一个保留性质——

假设有一个变量 a 经过了 threadprivate(a) 处理，保留就是让并行区域结束以后线程中的私有变量不被清除，它的值仍然被相应的线程“记忆”，并且可以在下一个并行区域中调用。如下：
```c++
int a;
#pragma omp threadprivate(a)
int main()
{
    omp_set_num_threads(3);
    omp_set_dynamic(0); // 关闭动态线程
#pragma omp parallel    // 第一个并行区域
    {
        a = omp_get_thread_num();
    }
#pragma omp parallel // 第二个并行区域
    {
        printf("thread %d : a is %d\n", omp_get_thread_num(), a);
    }
    return 0;
}
```
- 注意1：a 应该设置成一个全局变量否则会被编译器报错
- 注意2：使用 threadprivate ，必须关闭动态线程机制，同时不同并行区域中的线程数保持不变，以确保结果正确。
- 注意3：尽管在第二个并行区域中并没有给变量 a 赋值，但是变量 a 的值还是保留了第一个并行区域的设置结果。


#### 编译指导语句的子句

#####  if 子句
if(val) 子句能够通过 val 的值来指定并行区域内的代码是应该并行执行还是串行执行（非零值：并行），如下：
```c++
void test(int val) {
    #pragma omp parallel if (val) 
    {
        if (omp_in_parallel()) {
            #pragma omp single 
            {
                printf_s("val = %d, parallelized with %d threads\n", val, omp_get_num_threads());
            }
        }
        else {
            printf_s("val = %d, serialized\n", val);
        }
    }
}

int main( ) {
    omp_set_num_threads(2);
    test(0);
    test(2);
}
```
第一个 test 函数调用不会采用并行，第二个会。

---
以下是关于数据共享和保护的子句 
- 数据共享：共享的数据可以在多个线程中使用 
- 数据保护：被保护的数据只能在个别线程中使用

##### private 子句
private：该子句声明列表中的所有变量都是进程私有的（变量列表列举在尾随圆括号中），如下：
```c++
int x;   // 先对 x 进行定义
#pragma omp parallel private(x)
```
声明成线程私有变量以后，每个线程都有一个该变量的副本，这些副本可以有不相同的值，并且线程之间对这些值的操作不会互相影响。

注意1：原变量在并行部分不起任何作用，原变量也不会受到并行部分内部操作的影响——并行部分操作的始终不是原变量的本体，而是在每个线程的 stack 中存有该变量的拷贝，这有点类似于函数的“值传递”。

注意2：private 子句的本质只是为了名字的重用——它创建的变量储存在相应线程的栈中，而不是公共的区域。它将被默认初始化或是一个不确定的值。

下面这段代码中，a 变量在创建以后被声明为线程私有，每个线程中的 a 经过各自的自增操作，因此它们的值都是 2。

```c++
int a = 3;
#pragma omp parallel private(a) 
{
    a = 1;
    a++;
    #pragma omp for 
    {
        for (int i = 1; i <= 3; i++) {
            printf("hhh, here is thread %d and a is %d\n", omp_get_thread_num(), a);
        }
    }
}
```
默认情况下，在并行区域中定义的变量属于私有变量。

##### firstprivate 子句
firstprivate 的特性和 private 基本一致，只是多了一个附加功能——它能把所有线程私有变量（也就是原变量的副本）的初始值都设置成原变量的值，相当于 private 加一个初始化。

将 private 例子的代码修改为：
```c++
int a = 3;
#pragma omp parallel firstprivate(a) 
{
    a++;
    #pragma omp for 
    {
        for (int i = 1; i <= 3; i++) {
            printf("hhh, here is thread %d and a is %d\n", omp_get_thread_num(), a);
        }
    }
}
```
运行结果是（每个线程中的局部变量 a 都会被先初始化为 3）。

##### lastprivate 子句
lastprivate 的特性和 private 基本一致，只是多了一个附加功能——它能在退出并行部分时将计算结果赋值回原变量。

如果所有线程同时操作一个变量，究竟将哪个线程操作后的变量值赋值给原变量:
OpenMP 规范明确了这一点——在 for 循环迭代中，将程序语法逻辑上最后一次迭代的值赋值给原变量；在 sections 结构，将程序语法上的最后一个 section 语句赋值给原变量。

也就是说，lastprivate 能确保最终赋值回原变量的值是逻辑上产生的最后一个值。
下面代码演示了这一点：
```c++
a = 0;
#pragma omp parallel for firstprivate(a), lastprivate(a) 
{
    for (int i = 0; i < 3; i++) {
        a += i;
        printf("hhh, here is thread %d and a is %d\n", omp_get_thread_num(), a);
    }
}
printf("at last,  a is %d", a);
```
输出结果如下，这个 for 循环逻辑上的最后一次操作必然是`a += 2`

##### shared 子句
该子句用于声明变量列表中的所有变量都是进程公共的。

一般情况下，除非逻辑上非常严密，或者对变量有着严格的保护，否则使用 shared 子句都是需要非常谨慎的。
```c++
a = 3;
#pragma omp parallel for shared(a) 
{
    for (int i = 1; i <= 3; i++) {
        a += i;
        printf("hhh, here is thread %d, a is %d and i is %d\n", omp_get_thread_num(), a, i);
    }
}
printf("at last, a is %d\n", a);
```
shared 子句是带有继承初值和将最终值传回给原变量的作用的。

##### default 子句
default 子句用来指定并行域内的变量的使用方式，比如 default(shared) 子句将所有并行区域外的变量的数据共享属性设置为共享

注意：在并行区域内声明的变量不受 default(shared) 影响。

default(none) 子句并不设置变量的数据共享属性，但是它会强制程序员去指定所有变量的数据共享属性以确保程序的正确性。换言之，这个子句并没有实际上的作用，而是强制程序员更加严格地编程。

##### copyin 子句
而 copyin 子句专门用于 threadprivate 变量，可以为所有线程的 threadprivate 变量分配相同的值。

用 copyin 子句设置的 threadprivate 变量，在进入并行区域时，会用主线程变量值为每个线程的该变量副本初始化。

如下代码所示，所有线程中储存的副本变量 a 都会被修改为 0
```c++
int a;
#pragma omp threadprivate(a)
int main()
{
    omp_set_num_threads(3);
    omp_set_dynamic(0); // 关闭动态线程
    #pragma omp parallel    // 第一个并行区域
    {
        a = omp_get_thread_num();
    }
    #pragma omp parallel copyin(a)// 第二个并行区域
    {
        printf("thread %d : a is %d\n", omp_get_thread_num(), a);
    }
    return 0;
}
```

##### reduction 子句
reduction 子句相当于两个过程——
1. 在每个线程为全局的原始变量创建属性为 private 的线程局部变量副本
2. 将各个线程的局部变量副本进行指定的操作，并将操作后的结果返回全局的原始变量

注意：reduction 和 private

reduction 子句的语法结构是这样的：`reduction(操作符 : 进行该操作的变量列表)`
```c++
int a = 2;
#pragma omp parallel reduction(+ : a) 
{
    a = 4;
    #pragma omp for 
    {
        for (int i = 1; i <= 3; i++) {
            a += i;
            printf("hhh, here is thread %d, a is %d and i is %d\n", omp_get_thread_num(), a, i);
        }
    }
}
printf("at last, a is %d\n", a);
```
上述代码经历的过程是这样的：先将 a 变量拷贝到每个线程中作为线程私有变量，每个线程中均初始化为 4。然后线程共同完成 for 循环，即三个线程中的 a 分别加上 1、2 和 3 而得到 5、6 和 7。最后进行 reduction 操作，即加和操作——全局的原始变量 a 赋值为各个线程中的私有副本之和 `2 + 5 + 6 + 7 = 20`。

##### nowait 子句
nowait 子句即用于取消 parallel 和 for 中的默认隐含 barrier ，使一个线程完成指定工作后无需等待其它线程，直接进行后续的工作，如下：
```c++
#pragma omp parallel // 第一个并行区域
{
    #pragma omp for nowait
    for (int i = 1; i <= 3; i++) {
        printf("thread %d : hhh\n", omp_get_thread_num());
    }
    printf("thread %d : www\n", omp_get_thread_num());
 }
```

##### num_threads 子句
`num_threads(cnt)` 效果等同函数 `omp_set_num_threads(cnt)`

##### schedule 子句
schedule 子句的语法规则是：`schedule(strategy, chunk_size)`

schedule 子句用来描述如何将循环任务划分给一组线程，包含四种 strategy：

- static ：static 划分策略会将循环任务分成多个块，块的大小 chunk_size 由程序员指定，然后按循环顺序将各个块静态地分配给各线程，即在执行前就指派好每个线程完成对应的块。（显然，哪个线程执行哪个块是可以提前预判的）。
  如果未指定块大小，则循环迭代将在线程之间尽量均匀连续地划分。
- dynamic：dynamic 划分策略会将循环任务分成多个块，块的大小 chunk_size 由程序员指定，各线程完成对应的块后会申请执行新的块。即在执行前并不固定哪个线程执行哪个块，而是在每个线程完成手头工作后，当即为其指派一个新的块任务。（显然，哪个线程执行哪个块是无法提前预判的）。
  如果未指定块大小，则默认块大小为 1。
- guided：guided 划分策略采用指导性的启发式自调度方法，开始时每个线程会分配到较大的迭代块，之后分配到的迭代块会逐渐递减。迭代块的大小会按指数级下降到指定的块大小，这个指定的最小块 chunk_size 可以由程序员自行指定。
- runtime：runtime 表示根据环境变量值 OMP_SCHEDULE （默认为 static）确定上述调度策略中的某一种。


##### ordered 子句
ordered 子句的作用是指定 for 循环必须按照正常的顺序执行，比如下面这个 for 循环中：
```c++
#pragma omp parallel for ordered
{
    for (int i = 0; i < 10; ++i) {
        printf("%d ", i);
    }
}
```
输出为：0 1 2 3 4 5 6 7 8 9，这些数字总会是有序的。