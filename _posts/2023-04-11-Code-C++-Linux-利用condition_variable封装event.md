---
layout: post
title: "Code-C++-Linux-利用condition_variable封装event"
date: 2023-04-11 00:09:00
categories: ["Code"]
tags: ["C++", "Code"]
---

C++11使用condition_variable加上mutex封装event类，实现等同于windows的事件功能。
>从网上百度到的以下代码实现，具体网址搞丢了。

<!--more-->
```cpp
#include <iostream>
#include <string>
#include <thread> //-std=c++0x -pthread
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <queue>

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