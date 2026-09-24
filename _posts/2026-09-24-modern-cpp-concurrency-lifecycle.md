---
layout: post
title: "现代 C++ 并发与生命周期：shared_ptr、锁、条件变量与线程池"
display_title: "现代 C++ 并发与生命周期：shared_ptr、锁、条件变量与线程池"
summary: "以所有权和关闭协议为主线，整理智能指针、互斥锁、条件变量、线程池和内存错误排查中的可复用实践。"
lang: zh-CN
date: 2026-09-24 11:20:00
categories:
  - C & C++
tags:
  - C++
  - Concurrency
  - Memory
  - RAII
  - Debugging
  - Thread Pool
curated: true
content_origin: curated
curation_level: deep-dive
version: curated-v1
source_posts:
  - "_posts/2023-05-10-C++-shared_ptr.md"
  - "_posts/2023-04-11-C++-unique_lock与lock_guard区别.md"
  - "_posts/2023-04-11-Code-C++-Linux-利用condition_variable封装event.md"
  - "_posts/2023-06-02-C++-mutex(待验证).md"
  - "_posts/2025-02-27-Code-C++-ThreadPool-BSthread_pool-单例.md"
  - "_posts/2023-05-27-C++-double-free-or-corruption(fasttop).md"
  - "_posts/2024-07-08-Code-OpenMP.md"
  - "_posts/2023-04-29-C++-stdthis_threadget_id()-获取线程id.md"
---

C++ 并发问题通常不是“线程 API 不会用”，而是对象生命周期、锁的保护范围和停止协议没有一起设计。先画出状态转移和所有权，再选择 `std::mutex`、`std::shared_ptr` 或线程池，代码会稳定很多。

> 本文是对历史 C++ 笔记的现代化重组。示例用于说明设计原则，编译器版本、库实现和业务约束仍需在项目中验证。

<!--more-->

## 1. 所有权先于并发

`std::shared_ptr` 解决的是共享所有权，不自动解决循环引用、线程安全和异常传播。两个节点互相持有 `shared_ptr` 会让引用计数永远不归零；此时应重新设计关系，通常用 `weak_ptr` 打破环：

```cpp
struct Node;
struct Observer {
    std::weak_ptr<Node> node;
};

struct Node {
    std::vector<std::shared_ptr<Observer>> observers;
};
```

是否使用智能指针应从“谁最后释放、谁访问对象、对象是否跨线程”开始。历史 [shared_ptr 记录](#source-posts-title) 中如果出现 `new` 后长期保存裸指针的情况，不应直接复制到新代码中。

## 2. 锁的保护范围要写清楚

`lock_guard` 适合固定作用域的互斥锁；`unique_lock` 适合需要延迟加锁、提前解锁或配合条件变量的场景：

```cpp
std::mutex mutex;
bool ready = false;

std::unique_lock<std::mutex> lock(mutex);
if (ready) {
    // 只在受保护的临界区内读取状态
}
lock.unlock(); // 之后不再访问受保护数据
```

不要为了“可能更快”随意缩小锁范围：如果解锁后仍访问共享数据，就会引入竞态。也不要把 `mutex` 设计成全局或静态对象当成通用修复；应根据对象生命周期和并发访问边界选择成员、局部或单例中的位置。

## 3. 条件变量必须配合谓词

条件变量允许虚假唤醒，通知也可能先于等待发生。正确模式是“状态 + 谓词 + 通知”：

```cpp
class Event {
public:
    void wait() {
        std::unique_lock<std::mutex> lock(mutex_);
        condition_.wait(lock, [this] { return ready_; });
    }

    void signal() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            ready_ = true;
        }
        condition_.notify_one();
    }

private:
    std::mutex mutex_;
    std::condition_variable condition_;
    bool ready_ = false;
};
```

通知可以在锁外发生，但修改共享状态必须在锁内完成。把 `condition_variable` 封装成 event 时，还要明确 `reset()`、重复等待、异常和销毁顺序。历史 [condition_variable 封装 event](#source-posts-title) 可作为练习起点。

## 4. 线程池必须有停止协议

线程池的难点不是提交任务，而是：没有任务时如何等待、停止时如何唤醒、任务异常如何记录、队列中的任务怎么办。一个最小的设计约定：

```cpp
class ThreadPool {
public:
    explicit ThreadPool(std::size_t count);
    ~ThreadPool(); // 析构时请求停止并 join

    void submit(std::function<void()> task);
    void shutdown();
};
```

实现时应明确：

- `shutdown` 是否拒绝新任务；
- 工作线程如何退出等待循环；
- 正在执行的任务是否等待完成；
- 任务异常是否在线程内捕获并上报；
- 队列和条件变量的析构顺序。

[BS::thread_pool 单例记录](#source-posts-title) 可以帮助了解第三方库，但单例不是线程池的必需设计；如果组件有独立配置、测试或多个隔离实例，普通对象通常更容易管理。

## 5. 内存错误先用工具定位

`double free`、随机崩溃和数据竞争不一定能从症状反推出根因。按成本从低到高尝试：

```bash
# 编译器/运行时 sanitizer（按工具链支持情况选择）
g++ -std=c++17 -g -fsanitize=address,undefined ...
g++ -std=c++17 -g -fsanitize=thread ...

# 运行时检查
valgrind ./your-program
```

Sanitizer 的报告应保存最小复现、完整命令、编译器版本和线程配置。Valgrind 适合解释非法访问和泄漏，但它会显著改变运行时性能，不能把 slowdown 当成真实基准。

## 6. 并发设计检查表

- [ ] 每个共享状态是否有明确的所有者？
- [ ] 锁保护的字段和不变式是否写在注释或类型中？
- [ ] 条件变量是否始终配合谓词？
- [ ] 线程是否有取消、停止和 join 协议？
- [ ] 任务异常是否有可观测的处理路径？
- [ ] 是否测试了空队列、重复通知、异常任务和关闭竞态？
- [ ] 是否用 ThreadSanitizer/ASan 或压力测试验证过？

[mutex 待验证笔记](#source-posts-title)、[线程 ID](#source-posts-title) 和 [double-free 记录](#source-posts-title) 可以帮助你定位问题，但真正的修复应回到不变量、生命周期和关闭协议。
