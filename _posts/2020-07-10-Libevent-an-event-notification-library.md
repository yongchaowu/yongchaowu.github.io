---
layout: post
title: Libevent - an event notification library
date: 2020-07-10 01:00:00
categories:
- C & C++
tags:
- Open Source
- Libevent
---

>[https://libevent.org/](https://libevent.org/)
>[https://libevent.org/libevent-book/](https://libevent.org/libevent-book/ "Book Libevent")
>[https://github.com/libevent/libevent](https://github.com/libevent/libevent "Github Libevent")

<!--more-->
Libevent 是一个用C语言编写的、轻量级的开源高性能事件通知库，主要有以下几个亮点：
- 事件驱动（ event-driven），高性能；
- 轻量级，专注于网络，不如 ACE 那么臃肿庞大；
- 源代码相当精炼、易读；
- 跨平台，支持 Windows、 Linux、 *BSD 和 Mac OS；
- 支持多种 I/O 多路复用技术， epoll、 poll、 /dev/poll、select 和 kqueue 等；
- 支持 I/O，定时器和信号等事件；注册事件优先级。

## Introduce
The *libevent* API provides a mechanism to execute a callback function when a specific event occurs on a file descriptor or after a timeout has been reached. Furthermore, *libevent* also supports callbacks due to `signals` or regular `timeouts`.

*libevent* is meant to replace the event loop found in event driven network servers. An application just needs to call `event_dispatch()` and then add or remove events dynamically without having to change the event loop.

Currently, *libevent* supports `/dev/poll`, `kqueue(2)`, `event ports`, `POSIX select(2)`, `Windows select()`, `poll(2)`, and `epoll(4)`. The internal event mechanism is completely independent of the exposed event API, and a simple update of libevent can provide new functionality without having to redesign the applications. As a result, *Libevent* allows for portable application development and provides the most scalable event notification mechanism available on an operating system. Libevent can also be used for multi-threaded applications, either by isolating each event_base so that only a single thread accesses it, or by locked access to a single shared event_base. *Libevent* should compile on Linux, *BSD, Mac OS X, Solaris, Windows, and more.

Libevent additionally provides a sophisticated framework for buffered network IO, with support for sockets, filters, rate-limiting, SSL, zero-copy file transmission, and IOCP. Libevent includes support for several useful protocols, including DNS, HTTP, and a minimal RPC framework.

## Programs using libevent
>[https://libevent.org/](https://libevent.org/)

The usefulness of libevent API is demonstrated by the following applications:
- Chromium – Google's open-source web browser (uses Libevent)
- Memcached – a high-performance, distributed memory object caching system
- Transmission – a fast, easy, and free BitTorrent client
- NTP – the network time protocol that makes your clock right (uses Libevent in SNTP)
- tmux – A clean, modern, BSD-licensed terminal multiplexer, similar to GNU screen
- Tor – an anonymous Internet communication system.
- libevhtp – A fast and flexible replacement for libevent's http client/server API
- Prosody – A Jabber/XMPP server written in Lua
- PgBouncer – Lightweight connection pooler for PostgreSQL
- redsocks – a simple transparent TCP -> Socks5/HTTPS proxy daemon.
- Vomit – Voice Over Misconfigured Internet Telephones
- Crawl – A Small and Efficient HTTP Crawler
- Libio – an input/output abstraction library
- Honeyd – a virtual honeynet daemon – can be used to fight Internet worms.
- Fragroute – an IDS testing tool
- Nylon – nested proxy server
- Disconcert – a Distributed Computing Framework for Loosely-Coupled Workstations.
- Trickle – a lightweight userspace bandwidth shaper.
- watchcatd – software watchdog designed to take actions not as drastic as the usual solutions, which reset the machine.
- ScanSSH – a fast SSH server and open proxy scanner.
- Nttlscan – a network topology scanner for Honeyd.
- NetChat – a combination of netcat and ppp's chat.
- Io – a small programming language; uses libevent for network communication.
- Systrace – a system call sandbox.
- SpyBye – detect malware on web pages.
- GreenSQL – an SQL database firewall.
- dnsscan – a fast scanner for identifying open recursive dns resolvers
- Kargo Event – a PHP extension for libevent.
- Scytale – a database encryption tool.
- Coturn – Free open source implementation of TURN and STUN Server.

## Working with events 
>https://libevent.org/libevent-book/Ref4_event.html

Libevent’s basic unit of operation is the event. Every event represents a set of conditions, including:
- A file descriptor being ready to read from or write to.
- A file descriptor becoming ready to read from or write to (Edge-triggered IO only).
- A timeout expiring.
- A signal occurring.
- A user-triggered event.

Events have similar lifecycles. Once you call a Libevent function to set up an event and associate it with an event base, it becomes `initialized`. At this point, you can add, which makes it `pending` in the base. When the event is pending, if the conditions that would trigger an event occur (e.g., its file descriptor changes state or its timeout expires), the event becomes `active`, and its (user-provided) callback function is run. If the event is configured `persistent`, it remains pending. If it is not persistent, it stops being pending when its callback runs. You can make a pending event non-pending by deleting it, and you can add a non-pending event to make it pending again.


`#include <event2/event.h>`


----------

## A tiny introduction to asynchronous IO
>https://libevent.org/libevent-book/01_intro.html
