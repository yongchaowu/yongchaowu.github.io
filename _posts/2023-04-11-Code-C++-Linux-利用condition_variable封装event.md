---
layout: post
title: C++-Linux-利用condition_variable封装event
date: 2023-04-11 00:09:00
categories:
- Programming
tags:
- C++
- Code
---
C++11 使用 `condition_variable` 加上 `mutex` 封装了一个基于状态标志的等待/通知类，并非 Windows 事件的完全等价实现。
`NotifyOne()` 只唤醒一个当前等待者，`NotifyAll()` 唤醒全部当前等待者；两者都会将 `bNotifyTick` 置为 `true`，需显式调用 `Reset()` 清除。
>从网上百度到的以下代码实现，具体网址搞丢了。

```
#include <iostream>
#include <string>
#include <thread> //-std=0x -pthead
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <queue>

<!--more-->

using namespace std;

class Event{
    public:
        Event()=default;

        void Wait(){
            std::unique_lock<std::mutex> lock(mu);
            con.wait(lock,[this](){return this->bNotifyTick;});
        };

        template<typename _Rep, typename _Period>
        bool WaitFor(const std::chrono::duration<_Rep, _Period> &duration){
            std::unique_lock<std::mutex> lock(mu);
            bool ret = true;
            ret = con.wait_for(lock, duration, [this](){return this->bNotifyTick;});
            return ret;
        }

        template<typename _Clock, typename _Duration>
        bool WaitUntil(const std::chrono::time_point<_Clock, _Duration> &point){
            std::unique_lock<std::mutex> lock(mu);
            bool ret = true;
            ret = con.wait_until(lock, point, [this](){return this->bNotifyTick;});
            return ret;
        }

        void NotifyOne(){
            std::lock_guard<std::mutex> lock(mu);
            bNotifyTick = true;
            con.notify_one();
        }

        void NotifyAll(){
            std::lock_guard<std::mutex> lock(mu);
            bNotifyTick = true;
            con.notify_all();
        }

        void Reset(){
            std::lock_guard<std::mutex> lock(mu);
            bNotifyTick = false;
        }

    private:
        Event(const Event&)=delete;
        Event &operator=(const Event &)=delete;

    private:
        bool bNotifyTick=false;

        std::mutex mu;
        std::condition_variable con;
};

Event event;
std::queue<int> que;
std::mutex mu;

#define Produce_Count 1e9
#define Consume_Count 1e9
#define Produce_Usleep 1e3
#define Consume_Usleep 1e3
#define Consume_Err_Usleep 3e3

void produce(){
    std::lock_guard<std::mutex> lock(mu);
    auto t = std::rand();
    que.push(t);
    event.NotifyOne();
}

void consume(){
    event.Wait();
    std::lock_guard<std::mutex> lock(mu);
    auto t = que.front();//if(que.empty()) {event.NotifyOne();return}
    que.pop();
}

bool poll(){
    std::lock_guard<std::mutex> lock(mu);
    if(!que.empty()){
        auto t = que.front();
        que.pop();
        return true;
    }
    return false;
}

int main(){
    auto thConsume = std::thread(consume);
    std::this_thread::sleep_for(std::chrono::seconds(2));
    auto thProduce = std::thread(produce);
    thProduce.join();
    bool bRet = poll();
    thConsume.join();
    return 0;
}
```

本文修订依据：C++11 工作草案 [N3337 `condition_variable`](https://timsong-cpp.github.io/cppwp/n3337/thread.condition.condvar) 和 Microsoft Learn [`CreateEventA`](https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-createeventa)。`notify_one()` 只解除一个等待线程，`notify_all()` 解除全部等待线程；本文代码还把通知状态保存为 `bNotifyTick`，必须显式 `Reset()` 才会清除。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 08:56（UTC+08:00）。修订仅说明该条件变量封装与 Windows 事件的区别及状态标志语义。