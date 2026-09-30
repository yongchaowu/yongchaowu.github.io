---
layout: post
title: "mysql-connector-c++ 26.7：一次 C++ 调用如何变成 socket 上的字节 —— 两套连接栈的 11 个机制"
display_title: "mysql-connector-c++ 26.7：一次 C++ 调用如何变成 socket 上的字节 —— 两套连接栈的 11 个机制"
summary: "拆解 Connector/C++ 26.7.0：一个 tarball 里藏着两套完全不同的连接栈。逐层追 Session 构造、能力协商、5 字节帧头、::send() 叶子调用，并解释 caching_sha2_password 缺口、ssl-mode 默认 REQUIRED、CRUD 不翻译成 SQL 等 22 个实测踩到的坑。"
lang: zh-CN
date: 2026-09-26 18:30:00
categories:
  - Database
  - C & C++
tags:
  - MySQL
  - C++
  - Connector/C++
  - X Protocol
  - Protobuf
  - libmysqlclient
  - JDBC
  - Socket
  - TLS
  - CMake
---

<!--more-->

本文基于 **Connector/C++ 26.7.0（2026-07-29 GA）**，全部 `file:line` 指向该版本源码树。

> **配套仓库：[`yongchaowu/mysql-connector-cpp`](https://github.com/yongchaowu/mysql-connector-cpp)**
>
> 本文提到的 `demo/`（两个可编译运行的 CRUD 程序 + 两份真实抓包）、`docs/`（12 个校验脚本）、
> `docker/`（麒麟容器一条命令出镜像）、`offline-debs/`（离线包）都在那个仓库里。
> 下文所有路径都是**仓库相对路径**，克隆后即可复现本文的每一条实测结论。

> **关于证据强度，先说清楚三件事**——本文的结论不是一个可信度：
>
> 1. **线上字节的论断 = 实测**。所有关于帧格式、握手顺序、消息类型的说法都来自
>    `demo/wire/` 里两份真实抓包（`tcptee.py` 录的，未经改写），
>    可复现。文中用 **【见】/【推】** 区分"抓包看到的"和"由明文那次推断的"。
> 2. **API 用法 = 编译 + 连库跑过**。两个完整 demo 都在真实 MySQL 8.0.46 上跑到
>    `EXIT=0`。凡是"照着文档想当然写"的 API（`as<T>()`、`rows()`、`sql().bind()`…）
>    都在编译或运行时被推翻，已在[「实测踩到的 22 个坑」](#实测踩到的-22-个坑)列出。
> 3. **其余部分 = 读源码，可能滞后于实现**。特别是那些"这个类不存在""这个宏没定义过"
>    之类的断言，来自 grep，不排除我看漏了。
>
> 另外：本文在修订过程中**推翻过自己几次**（"全树零命中""20 轮 challenge"
> "服务端回 `Ok`"都是错的）。这些更正我保留在正文里没删，并标了出处——
> 读到和自己经验冲突的地方，以抓包和编译器为准。

`mysql-connector-c++-26.7.0-src.tar.gz` 解开是一个自举项目（bootstrap CMake，源码带 vendored 依赖）。大多数人用它只写 5 行：

```cpp
#include <mysqlx/xdevapi.h>
using namespace mysqlx;

Session s("root", "pwd", "127.0.0.1", 33060);
auto r = s.sql("SELECT 1").execute();
```

然后就以为"连上 MySQL 了"。但真正决定成败的问题，全藏在这 5 行背后：

1. **`#include` 哪个头，决定了你走的是完全不同的两套栈。** 这个 tarball 里有两个互不相干的连接器，协议、端口、依赖、错误模型全不一样——而你只是换了个头文件。
2. **`Session` 构造函数其实没有连接。** 它只把参数翻译成一个"数据源列表"，真正的 socket 在下一层、另一个文件里创建。
3. **X 协议没有 capability 位图。** 没有 `CLIENT_SSL`／`CLIENT_COMPRESS`／`CLIENT_PLUGIN_AUTH`；连"服务端支不支持 row locking"都是靠发一条会失败的探针消息试出来的。
4. **`ssl-mode` 的默认值是 `REQUIRED`，不是 `PREFERRED`。** 这一个默认值会让大量"本地测试能过、上生产连不上"的案例归零。
5. **这个客户端不支持 `caching_sha2_password`。** MySQL 8 的默认认证插件，它没有实现——而测试代码里明明白白写着 `SKIP_TEST("No caching_sha2_password support")`。
6. **CRUD 操作不翻译成 SQL。** `collection.find().execute()` 发出去的是 protobuf `Mysqlx.Crud.Find`，服务端根本没看到 SQL 文本。
7. **JDBC 风格那条路径是个空壳适配器。** 它一行协议代码都没有，全部转手给外部的 `libmysqlclient`——**而且默认根本不编译**（`WITH_JDBC=OFF`）。

这 7 件事是本文的引子。展开后是 11 个机制：**机制一到机制九**顺着 X DevAPI 那条链往下走（选项 → 数据源 → 能力协商 → 认证 → TLS → 帧头 → CRUD），**机制十和机制十一**切到 classic 那条链。合起来解释了"为什么 C++ 连 MySQL"这件事有两个完全不同的答案。

---

## 目录

- [先看两个 demo：写法风格不同，底下是两套产品](#先看两个-demo写法风格不同底下是两套产品)
- [机制一：include 哪个头，决定了你走哪套栈](#机制一include-哪个头决定了你走哪套栈)
- [机制二：Session 构造时并没有连接](#机制二session-构造时并没有连接)
- [机制三：选项的归一化与数据源排序](#机制三选项的归一化与数据源排序)
- [机制四：能力协商靠"故意发一条会失败的消息"](#机制四能力协商靠故意发一条会失败的消息)
- [机制五：认证只有四种，且没有 caching_sha2_password](#机制五认证只有四种且没有-caching_sha2_password)
  - [抓包实证：一次完整的明文会话](#抓包实证一次完整的明文会话)
- [机制六：ssl-mode 默认 REQUIRED，且 TLS 是"先明文后升级"](#机制六ssl-mode-默认-required且-tls-是先明文后升级)
- [机制七：从 protobuf 消息到 ::send() 的最后一米](#机制七从-protobuf-消息到-send-的最后一米)
- [机制八：结果回来时，帧头是 5 字节不是 4 字节](#机制八结果回来时帧头是-5-字节不是-4-字节)
- [机制九：CRUD 不翻译成 SQL](#机制九crud-不翻译成-sql)
- [机制十：classic 路径是 mysql_real_query 的三层桥](#机制十classic-路径是-mysql_real_query-的三层桥)
- [机制十一：classic 路径默认不编译，还有一堆死代码](#机制十一classic-路径默认不编译还有一堆死代码)
- [两套栈的完整对照表](#两套栈的完整对照表)
- [动手：构建与最小可运行例子](#动手构建与最小可运行例子)
- [版本台账（防腐剂）](#版本台账防腐剂)
- [总结](#总结)

---

## 先看两个 demo：写法风格不同，底下是两套产品

> 这两段都**实测编译通过**。真正的差别不是"能不能编"，而是 demo_b 根本不在
> 默认构建产物里——要 `-DWITH_JDBC=ON` 才会编出来。文末[「动手」](#动手构建与最小可运行例子)
> 一节给出两个**完整可运行**的 CRUD demo（增删改查全流程）。

```cpp
// demo_a.cpp —— X DevAPI，默认构建产物就有
#include <mysqlx/xdevapi.h>
using namespace mysqlx;

int main() {
  Session s("root", "pwd", "127.0.0.1", 33060);
  SqlResult r = s.sql("SELECT 1").execute();
  for (auto row : r) { /* ... */ }
  s.close();
}
```

```cpp
// demo_b.cpp —— JDBC 风格 API，默认构建产物里没有
#include <mysql/jdbc.h>

int main() {
  sql::Driver* d = sql::mysql::get_mysql_driver_instance();
  std::unique_ptr<sql::Connection> c(
      d->connect("tcp://127.0.0.1:3306", "root", "pwd"));
  std::unique_ptr<sql::Statement> st(c->createStatement());
  std::unique_ptr<sql::ResultSet> rs(st->executeQuery("SELECT 1"));
}
```

两段代码看起来只是风格不同——一个是"面向对象 + 文档模型"，一个是"JDBC + 游标"。实际上它们分岔在**编译期**：

```
                        ┌──────────────────────────────────────────┐
                        │  mysql-connector-c++-26.7.0-src.tar.gz   │
                        │  一个 tarball，build 出两个 .so          │
                        └───────────────────┬──────────────────────┘
                                            │
              ┌─────────────────────────────┴─────────────────────────────┐
              │  WITH_JDBC=OFF （默认）        WITH_JDBC=ON（要显式打开）  │
              ▼                                                           ▼
   ┌──────────────────────────┐                            ┌──────────────────────────┐
   │ libmysqlcppconnx.so.2    │                            │ libmysqlcppconn.so.10    │
   │ X DevAPI                 │                            │ classic / JDBC          │
   └────────────┬─────────────┘                            └────────────┬─────────────┘
                │                                                           │
   ┌────────────▼─────────────┐                            ┌────────────▼─────────────┐
   │ cdk/  自己实现 X Protocol │                            │ jdbc/  零行协议代码      │
   │  · protobuf 序列化       │                            │  三层桥：                │
   │  · 3 种压缩算法        │                            │   MySQL_Statement        │
   │  · TLS 状态机            │                            │    → NativeConnectionWrap│
   │  · 4 种认证              │                            │    → IMySQLCAPI          │
   │  · 解析器（表达式/URI）  │                            │    → ::mysql_real_query  │
   └────────────┬─────────────┘                            └────────────┬─────────────┘
                │                                                           │
                │  ldd 实测：只有 libssl/libcrypto/resolv/pthread/dl       │
                │  没有 libprotobuf-lite / libzstd / liblz4                │
                │ 也没有 libmysqlclient                                    │
                │                                                           │ 依赖外部 libmysqlclient
                ▼                                                           ▼
        ┌───────────────────────┐                            ┌───────────────────────┐
        │  127.0.0.1 : 33060    │                            │  127.0.0.1 : 3306      │
        │  ┌──┬──┬──┬──┬──┐      │                            │  ┌──┬──┬──┐            │
        │  │ 4 │ 3 │ 2 │ 1 │ 5B帧 │                            │  │  │  │  │  文本协议  │
        │  └──┴──┴──┴──┴──┘      │                            │  └──┴──┴──┘            │
        │  len(4LE)+type(1)      │                            │  手写字节，无帧头概念  │
        │  + protobuf payload    │                            │                       │
        └───────────────────────┘                            └───────────────────────┘
```

> 压缩算法是 **3 种**（不是 5 种）：`data_source.h:201-206` 的枚举是
> `NONE / DEFLATE_STREAM / LZ4_MESSAGE / ZSTD_STREAM`，去掉 `NONE` 哨兵只剩 3 个。
> 抓包也证实了——建连时客户端依次发 `deflate_stream`、`lz4_message`、`zstd_stream`
> 三个 `CapabilitiesSet` 试过去（见[「抓包实证」](#抓包实证一次完整的明文会话)）。

两段代码的差异对照：

| | demo_a | demo_b |
|---|---|---|
| 头文件 | `<mysqlx/xdevapi.h>` | `<mysql/jdbc.h>` |
| 产物 | `libmysqlcppconnx.so.2.26.7.0` | `libmysqlcppconn.so.10.26.7.0` |
| 端口 | **33060** | **3306** |
| 线上字节 | protobuf，5 字节帧头 | classic MySQL 协议文本 |
| 协议实现者 | **连接器自己**（vendored protobuf 3.19.6） | **外部 libmysqlclient** |
| 默认构建 | ✅ 默认就有 | ❌ 要 `-DWITH_JDBC=ON` 才编 |
| 错误模型 | C++ 异常 `cdk::Error` | C++ 异常 `sql::SQLException` + SQLSTATE |
| 连接池 | ✅ 内置 `Session_pool` | ❌ 无 |

端口不同这一点最容易踩：demo_a 连的是 `33060`（X 协议端口，`DEFAULT_MYSQLX_PORT`，`include/mysqlx/common_constants.h:37`），你把 `3306` 填进去会直接连不上，或者更糟——连上一个不认 X 协议的服务端。

> 后文所有 `file:line` 都相对 `mysql-connector-c++-26.7.0-src/` 根目录，版本取自 `version.cmake:37-39`（`CONCPP_VERSION 26.7.0`）与 `version.cmake:85-90`（`ABI_VERSION 2.1`，与 9.2.0 相同）。

---

## 机制一：include 哪个头，决定了你走哪套栈

> **先说版本，因为它决定了后面所有事。**
>
> 本文基于 **26.7.0（2026-07-29 GA）**。注意 Oracle 在 9.7.x 之后把版本号改成了**日历版本**——`9.7.0`（2026-04-22）之后直接跳到 `26.7.0`，中间没有 `10.x`，也没有 `25.x`。所以"最新版本"不是"9.x 的下一个"，而是 `26.x`。
>
> **如果你的 tarball 是 9.2.0，本文 95% 的结论照样成立**（两个 tarball 之间的结构性变化很小），但**所有 `file:line` 都要重新校准**。方法见[「版本台账」](#版本台账防腐剂)——本文附带了一个自动校准脚本，30 秒能出结果。
>
> 升级动机的补充：9.7.0–9.7.1 受 **CVE-2026-60180**（DoS）影响，涉及 2026-07 的 Oracle 关键补丁更新。如果你在 9.7.x 上，`26.7.0` 才是修好的版本。
>
> **ABI 版本号没变，但"能换库"这件事是单向的。** `version.cmake:85-90` 的 `ABI_VERSION`
> 仍是 `2.1`（JDBC 侧 `10.0`），两版 `.so` 的 soname 也相同（`libmysqlcppconnx.so.2`）。
> 我把 9.2.0 也编出来做了四种组合实测，结论如下——**升级安全，降级会崩**：
>
> | | 配 `9.2.0` 的 `.so` | 配 `26.7.0` 的 `.so` |
> |---|---|---|
> | **用 9.2.0 头编的程序** | ✅ 正常（46 行输出） | ✅ **正常（46 行输出）** |
> | **用 26.7.0 头编的程序** | ❌ **段错误，一行输出都没有** | ✅ 正常 |
>
> 所以：**升级时你只需要换 `.so`，不用重编自己的程序**（这是最省事的一条路）；
> 但**回滚时必须连程序一起换成旧版本**。
>
> 顺带说明为什么"ABI 2.1 没变"这个信号在这里**不足以**保证安全——下面几项全都一致，
> 却照样崩：
>
> | 检查项 | 结果 |
> |---|---|
> | soname | 两版都是 `libmysqlcppconnx.so.2` ✅ 相同 |
> | ABI 命名空间 | 都是 `MYSQLX_ABI_BEGIN(2,0)` / `(2,1)` ✅ 相同 |
> | 导出符号集 | 各 **1760** 个，`comm` 对比**双向零差异** ✅ 相同 |
> | 公开类 `sizeof` | `Column` 16 / `Row` 16 / `SqlResult` 120 / `Value` 136 / `Table` 128 / `SessionSettings` 96 … **全部逐个相同** ✅ |
> | `cdk/devapi/detail/result.h` | 逐行 diff 只差一个宏名（`INTERNAL` → `MYSQLX_INTERNAL`）✅ |
>
> 崩的地方是**私有类型**：gdb 栈顶是
> `std::_Destroy<mysqlx::abi2::r0::internal::Column_storage<Column>>` 里
> **通过空 vtable 指针调虚析构**（`0x0`）。`Column_storage` 持有一个
> `const typename COL::Impl*`，而 `Column::Impl` 是私有的——**它的布局变了，
> 但外部观察不到**（公开头文件里 `sizeof` 一模一样，导出符号也没变）。
>
> **教训**：`ABI_VERSION` 相同 + soname 相同 + 符号表相同，**三者齐平也保证不了二进制兼容**。
> 公开 API 尺寸不变而私有 `Impl` 布局变了，是 C++ 里最典型的静默 ABI 破坏。
> 唯一可靠的判断办法就是像本文这样**把两个版本都编出来、跑一遍交叉矩阵**。

一个 tarball、两个连接器，这在构建系统里是显式的：

```cmake
# CMakeLists.txt:389-395
add_config_option(WITH_JDBC BOOL DEFAULT OFF
  "Whether to build a variant of connector library which implements legacy JDBC API")
if(WITH_JDBC)
  add_subdirectory(jdbc)
endif()
```

`WITH_JDBC` 默认 `OFF`。也就是说 **classic 路径不是"另一种用法"，是"另一种构建"**。默认 `cmake ..` 出来的只有 X DevAPI。

X 侧的产物是这么合出来的：

```cmake
# CMakeLists.txt:456
merge_libraries(connector xapi devapi)

# install_layout.cmake:218-219
set(LIB_NAME_BASE "mysqlcppconnx")
set(LIB_NAME_STATIC "${LIB_NAME_BASE}-static")

# CMakeLists.txt:576-579
VERSION "${ABI_VERSION_MAJOR}.${CONCPP_VERSION}"   # 2.26.7.0
SOVERSION "${ABI_VERSION_MAJOR}"                   # 2
```

`merge_libraries`（`cmake/libutils.cmake:145-339`）把一堆 `STATIC` 中间库折叠成一个 `SHARED`：

```
xapi (STATIC)  ──┐
                 ├── merge_libraries ──> libmysqlcppconnx.so.2.26.7.0
devapi (STATIC) ─┘                            (soname libmysqlcppconnx.so.2)
        │
        └──> common (STATIC)
                └──> cdk (STATIC)
                        └──> cdk_mysqlx (STATIC)  cdk/mysqlx/CMakeLists.txt:36
                                └──> cdk_proto_mysqlx (STATIC)  cdk/protocol/mysqlx/CMakeLists.txt:119
                                        └──> ext::protobuf-lite, ext::z, ext::lz4, ext::zstd
```

注意这条链里**没有 libmysqlclient**。X DevAPI 自己实现了整个 X 协议：protobuf 序列化、3 种压缩算法、TLS 状态机、4 种认证方式，全在 `cdk/` 里。这就是为什么它能独立于 `libmysqlclient` 构建。

一个容易误导的细节：`xapi/CMakeLists.txt:47` 里有个变量叫 `_libmysqlx_cc_src`——

```cmake
# xapi/CMakeLists.txt:47-52
set(_libmysqlx_cc_src  crud.cc  result.cc  mysqlx.cc  session.cc)
add_library(xapi STATIC ${_libmysqlx_cc_src} ${HEADERS})
target_link_libraries(xapi PUBLIC common)
```

全树 grep 一下，"libmysqlx" 这个字符串**只在这一行出现过**。它不指向任何被安装的产物，是个残留的变量名。`xapi/` 是 **C 语言** API（`mysqlx_get_session` 那些 `mysqlx_*` 函数，`xapi/mysqlx.cc:206-265`），C++ 那层在 `devapi/`。

---

## 机制二：Session 构造时并没有连接

`Session s("root", "pwd", "127.0.0.1", 33060);` 走的是变参构造：

```cpp
// include/mysqlx/xdevapi.h:1720-1722
template<typename...T> Session(T...options) : Session(SessionSettings(options...)) {}
```

落到真正干活的地方，只有 7 行：

```cpp
// devapi/session.cc:238-246
Session_detail::Session_detail(common::Settings_impl &settings)
{
  try {
    cdk::ds::Multi_source source;
    settings.get_data_source(source);          // ← 只是把选项翻译成一个数据源列表
    m_impl = std::make_shared<Impl>(source);   // ← 真正建对象，但还没连
  }
```

`Settings_impl::get_data_source()`（`common/session.cc:471`）不碰网络，它只做翻译：把 `host`/`port`/`user`/`password`/`schema`/`ssl-mode`/`auth` 这些散装选项，塞进一个 `cdk::ds::Multi_source`——一个**带优先级权重的候选端点列表**。

真正的连接发生在 `Impl` 的构造函数里（`common/session.h:320`），而且它**第一件事是去要连接池**：

```cpp
// common/session.cc:711
Pooled_session::Pooled_session(cdk::ds::Multi_source &ds) { reset(new cdk::Session(ds)); }

// common/session.cc:980-990
std::shared_ptr<cdk::Session> Session_pool::get_session(Session_cleanup *cleanup)
{
  if (!m_pool_enable)
    return std::shared_ptr<cdk::Session>(new cdk::Session(m_ds));   // 未开池：直接建
  ...
```

所以 `Session` 构造函数的语义其实是"**从池子里取一个会话**"，而不是"建立一个会话"。这一点对写服务端程序影响很大：

- 池开启时（`SessionSettings` 默认开），`new Session(...)` 可能**复用**一条已存在的物理连接；
- 池的默认参数在 `common/session.h:220-222`：`m_max = 25`、`m_timeout = 10 min`、`m_time_to_live = 10 min`；
- 池还有一层 60 秒的端点黑名单（`common/session.h:224-239`），某个端点认证失败后 60 秒内不再尝试（`common/session.cc:1019-1040`）。**这解释了一个经典困惑：改完密码立刻重连还是失败，等一分钟就好了。**

把这段流程画出来（每一步都标了出处）：

```
  Session s("root","pwd","127.0.0.1",33060)
      │  xdevapi.h:1720  变参构造
      ▼
  SessionSettings(options...)                      ← 构造期**不碰网络**
      │  devapi/settings.h:538
      ▼
  Session_detail::Session_detail(Settings_impl&)    devapi/session.cc:238
      │
      ├─► settings.get_data_source(Multi_source&)  common/session.cc:471
      │       │
      │       ├─ prepare_options()   ─────────────► common/session.cc:296
      │       │     · USER 必填，否则 throw_error
      │       │     · ssl-mode 默认 = REQUIRED  ★ 很多人在这里被坑
      │       │     · TLS 开了就把 socket=true → 认证走 PLAIN
      │       │     · unix socket + REQUIRED = 非法组合，直接抛
      │       │     · PRIORITY 取反（100 - prio），cdk 是"权重大者优先"
      │       │
      │       └─ add_prio(TCPIP(host,port), opts, prio)   :590
      │              产出：一个**带权重的候选端点列表**，仍然没有 socket
      │
      └─► m_impl = make_shared<Impl>(source)       devapi/session.cc:244
                │
                ▼
        Session_impl(Multi_source&)                common/session.h:320
                │
                ▼
        Session_pool::get_session()                common/session.cc:980
                │
        ┌───────┴────────────────────────────────┐
        │                                        │
   m_pool_enable == false                   m_pool_enable == true（默认）
   （显式关掉池）                                 │
        │                                        ▼
        │                          ┌───────── 池里有空闲的？ ─────────┐
        │                          │ 是                              │ 否
        ▼                          ▼                                ▼
  new cdk::Session(m_ds)      直接复用物理连接              池未满？──是──► new cdk::Session()
  立刻建连                     （省掉握手）                    │              │
       │                       │                             否             │
       │                       │                             ▼              │
       │                       │                        等一个旧的           │
       │                       │                        或超时腾位          │
       │                       │                             │              │
       │                       └────────────┬────────────────┘              │
       │                                    ▼                               ▼
       │                          ★ 失败端点进 60s 黑名单                 │
       │                            common/session.cc:1019              │
       └────────────────────────────┬───────────────────────────────────┘
                                    ▼
                    cdk::Session(Multi_source&)          cdk/core/session.cc:439
                                    │
                    ds::Multi_source::visit(Session_builder)   ← 故障转移循环
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
          Session_builder::operator()        （下一个端点，权重低的先试）
            (TCPIP)  cdk/core/session.cc:191
                     │
        ┌────────────┼─────────────────────┐
        ▼            ▼                     ▼
   new TCPIP()   tls_connect()        （跳过 TLS）
   connect()     CapabilitiesSet{tls}
        │        ←── 明文 ──→          ★ 抓包证实，见机制六
        │            SSL_connect()
        │            （之后全程加密）
        └────────────┬─────────────────────┘
                     ▼
        new cdk::mysqlx::Session(conn, options)
                     │  cdk/core/session.cc:239 / :251
                     ▼
        ┌────────────────────────────────────────┐
        │ 握手三步（cdk/mysqlx/session.h:261）    │
        │  ① negotiate_compression()             │
        │  ② send_connection_attr()              │
        │  ③ authenticate()                     │
        └────────────────────────────────────────┘
```

**读这张图只需记一件事**：构造函数跑到 `Session_pool::get_session()` 就分叉了。
往上（`get_data_source`）是纯翻译，往下（`cdk::Session`）才是网络。
所以"new 一个 Session 慢"卡在池这一层，而不是参数解析。

---

## 机制三：选项的归一化与数据源排序

`get_data_source()` 之前有一步 `prepare_options()`（`common/session.cc:296-456`），它做三件容易被忽略的事：

**1. 强制要求 USER**

```cpp
// common/session.cc:303-304
if (!settings.has_option(Option::USER))
  throw_error("USER option not defined");
```

**2. TLS 一开就把 `socket` 标记为 true——这是为了让认证走明文通道**

```cpp
// common/session.cc:352-360（节选）
#ifdef WITH_SSL
  ... 构造 TLS_options ...
  socket = true;   // 注释原文：so that PLAIN auth method is used below
```

这个 `socket = true` 有点 hack：它的唯一作用是让 `common/session.cc:417-425` 那段选到 `PLAIN` 认证（明文密码只在加密通道上传送）。理解了这一点，后面机制五才讲得通。

**3. Unix socket + REQUIRED 是非法组合**

```cpp
// common/session.cc:346-350
if (socket && mode_set && mode >= unsigned(SSL_mode::REQUIRED))
  throw_error("SSL connection over Unix domain socket requested.");
```

然后才是数据源排序。`add_host` lambda 里有个值得注意的处理：

```cpp
// common/session.cc:582-600（节选）
if (settings.get(Option::VERIFY_IDENTITY).get_bool())
  tls.set_host_name(host);      // ← 只有 VERIFY_IDENTITY 才做主机名校验
...
src.add_prio(cdk::ds::TCPIP(host, port), opts, prio);
```

`VERIFY_CA` 只验证书链，**不验主机名**；只有 `VERIFY_IDENTITY` 才填 `set_host_name()`。用自签 CA 做 `VERIFY_CA` 时不会因为 hostname 不匹配而失败——这跟 `libmysqlclient` 的 `--ssl-verify-server-cert` 语义不同，是迁移时的一个真实差异点。

另外 `PRIORITY` 是**反的**：

```cpp
// common/session.cc:523-540（节选）
check_prio = [&uri](const SQLString &p) { ... prio = 100 - prio; ... };
```

因为 cdk 内部按"权重越大越优先"排序，而连接串里习惯写"优先级数字小的优先"。

---

## 机制四：能力协商靠"故意发一条会失败的消息"

这是 X 协议跟 classic 协议最本质的区别。

classic MySQL 协议在握手包里带一个 **32 位 capability 位图**，客户端 `SET`、服务端 `AND`，一条报文搞定所有特性协商（`CLIENT_SSL`、`CLIENT_COMPRESS`、`CLIENT_DEPRECATE_EOF`、`CLIENT_PLUGIN_AUTH`……）。

**X 协议代码里这些常量一个都不存在。** 在 X 侧那四个目录（`cdk/` `common/` `devapi/` `xapi/`）里 grep `CLIENT_SSL|CLIENT_COMPRESS|CLIENT_DEPRECATE_EOF|CLIENT_PLUGIN_AUTH` 是零命中。

> ⚠️ **但注意别把范围说成"全树"。** classic 那一侧是有这些位图的——`jdbc/driver/mysql_connection.cpp:212-222` 有一张 `flagsOptions[]` 表，把 8 个 `CLIENT_*` 位（`CLIENT_COMPRESS`、`CLIENT_FOUND_ROWS`、`CLIENT_LOCAL_FILES`、`CLIENT_MULTI_STATEMENTS`……）映射成连接选项；`jdbc/cppconn/connection.h:121` 甚至把 `OPT_CLIENT_COMPRESS "CLIENT_COMPRESS"` 做成了公开选项名。
>
> 准确的说法是：**classic 侧仍然用 capability 位图，X 侧完全不用。** 下面这段只讲 X 侧。

取而代之的是 `Mysqlx.Expect.Open`——客户端**声明"我期望服务端支持 X"**，然后看服务端回不回复错误码：

```cpp
// cdk/mysqlx/session.cc:151-176（节选）
template<> Expectation_processor<Protocol_fields::ROW_LOCKING>::Expectation_processor()
    // Find=17, locking=12
  :  m_data("17.12")
{}

template<> Expectation_processor<Protocol_fields::UPSERT>::Expectation_processor()
    // Insert=18, upsert=6
  : m_data("18.6")
{}

template<> Expectation_processor<Protocol_fields::PREPARED_STATEMENTS>::Expectation_processor()
  : m_data("40")        // Prepare.Prepare
{}

template<> Expectation_processor<Protocol_fields::KEEP_OPEN>::Expectation_processor()
  :  m_data("6.1")      // SessionReset.keep_open=1
{}

template<> Expectation_processor<Protocol_fields::COMPRESSION>::Expectation_processor()
  :  m_data("46")       // Connection.Compression
{}
```

那个 `"17.12"` 就是 X 协议里 protobuf 消息的**编号.字段编号**寻址。协议是按 protobuf message id 编址的：

```
Mysqlx.Connection.CapabilitiesSet  = 2    cdk/include/mysql/cdk/protocol/mysqlx.h:142
Mysqlx.Session.AuthenticateStart    = 4    :146
Mysqlx.Sql.StmtExecute              = 12   :154
Mysqlx.Crud.Find                    = 17   :157
Mysqlx.Crud.Insert                  = 18
Mysqlx.Prepare.Prepare              = 40
Mysqlx.Prepare.Execute              = 41
```

`Expect.Open` 的语义是"从现在起，如果服务端不支持这些特性，就明确报错而不是静默忽略"。于是降级逻辑是**运行时捕获异常再重试**：

```cpp
// common/op_impl.h:303-336（节选）
try { check_errors(); }
catch (cdk::mysqlx::Server_prepare_error&)    { retry = true; }   // 服务端不支持 PS
catch (cdk::mysqlx::Server_expectation_error&) { retry = true; }
if (retry) { reset_state(); wait(); }        // reset_state() 把 stmt_id 归 0 → 改成直接执行
```

所以**"连接器以为在用预处理语句、实际上没在用"是可能发生且静默的**——服务端不支持时它自动退回明文执行。你只能从 `has_prepared_statements()` 的返回值看出来（`common/session.h:393`）。

同样的静默降级也发生在 `collection.find(...).lock("SHARED")`：服务端不支持行锁就退化成无锁读。

---

## 机制五：认证只有四种，且没有 caching_sha2_password

先说结论：**这个客户端没有实现 `caching_sha2_password`，也没有 `mysql_native_password` 和 `sha256_password`。** 这些字符串全树只出现在**测试代码**里，而且是用来在服务端**建账号**的：

```cpp
// devapi/tests/session-t.cc:1573-1576
SKIP_TEST("No caching_sha2_password support")

// testing/test.h:299
xplugin, std::move(name), std::move(pwd), "caching_sha2_password"
```

X 协议用的是自己那套四种机制（`cdk/include/mysql/cdk/data_source.h:187-193`）：

| DevAPI 名 | 实现类 | 线上 `mech_name` | 干什么 |
|---|---|---|---|
| `MYSQL41` | `AuthMysql41` `cdk/mysqlx/session.cc:495` | `"MYSQL41"` | challenge-response，SHA1 |
| `SHA256_MEMORY` | `AuthSha256Memory` `:513` | `"SHA256_MEMORY"` | challenge-response，SHA256 |
| `PLAIN` | `AuthPlain` `:381` | `"PLAIN"` | **一次把密码明文发过去** |
| `EXTERNAL` | `AuthExternal` `:420` | `"EXTERNAL"` | 不发认证数据，交给外部回调 |

**轮数由服务端决定，客户端没有硬编码。** 本文早期版本在这里写过"20 轮 challenge"，
那是把 MySQL *服务端* `caching_sha2_password` 的行为错安到了客户端头上。实际代码里
根本找不到 `20` 这个常量（`grep -rn '\b20\b' cdk/mysqlx/session.cc cdk/mysqlx/auth_hash.cc`
无结果），逻辑只有两行：

```cpp
// cdk/mysqlx/session.cc:350-356  服务端每发一次 AuthenticateContinue，客户端就回一次
void SessionAuth::auth_continue(bytes data) {
  m_state = CONT;
  m_op = &m_sess.m_protocol.snd_AuthenticateContinue(auth_response(++m_round, data));
}

// cdk/mysqlx/session.cc:482-491  round 0 不带数据，其余每轮算一次摘要
virtual bytes auth_response(unsigned round, bytes data) override {
  if (0 == round) return {};
  m_cont_data = build_hash(data);
  return bytes((byte*)m_cont_data.c_str(), m_cont_data.size());
}
```

抓包也印证了：明文那次会话的认证段是 `type=4 → 3 → 5 → 11/4` 四个帧，
轮数完全跟服务端节奏走。**所以"服务端可以任意决定要几轮"——理论上它可以要 100 轮，
客户端就会老实回 100 次。**

**为什么 `PLAIN` 可以明文发密码？** 因为它只在"安全通道"上被选中：

```cpp
// cdk/mysqlx/session.cc:610-612
auto am = original_am;
if (Protocol_options::DEFAULT == am)
  am = secure_conn ? Protocol_options::PLAIN : Protocol_options::MYSQL41;
```

`secure_conn` 来自 `conn.is_secure()`。这个虚函数有两个实现，注意别看错：

| 类 | 位置 | 返回 |
|---|---|---|
| `TCPIP::is_secure()` | `cdk/include/mysql/cdk/foundation/connection_tcpip.h:260-263` | **`false`**（裸 TCP） |
| `Unix_socket::is_secure()` | `cdk/include/mysql/cdk/foundation/connection_tcpip.h:280-283` | `true` |
| `TLS::is_secure()` | `cdk/include/mysql/cdk/foundation/connection_openssl.h:59-62` | `true` |

所以 `is_secure()` 为真只有两种情况：TLS 通道，或 Unix socket。**裸 TCP 永远不会走 `PLAIN`**。回看机制三里那个 `socket = true`：TLS 开了之后 `is_secure()` 为真，默认认证就顺理成章变成 `PLAIN`——因为 TLS 里面已经是密文了，没必要再做一次 challenge。

**默认值下的完整决策过程**：

```
用户没指定 auth=  →  original_am = DEFAULT
  ├─ 连接是 TLS / Unix socket  →  PLAIN          （一次搞定）
  └─ 裸 TCP                    →  MYSQL41        （先试 SHA1 challenge）
                                    └─ 失败且用户没钉死 auth=  →  再试 SHA256_MEMORY
                                                                        （cdk/mysqlx/session.cc:639-651）
```

`PLAIN` 的报文构造（`cdk/mysqlx/session.cc:388-402`）值得看一眼——它是 `authz\0authc\0password` 三段 NUL 分隔，第一段是可选的 schema：

```cpp
std::string user(options.user());
if (options.database()) m_data.append(*options.database());
m_data.push_back('\0');                 // authz
m_data.append(user).push_back('\0');    // authc
if (options.password()) m_data.append(*options.password());   // 明文
```

### 抓包实证：一次完整的明文会话

把 `ssl-mode` 设成 `DISABLED`，整条会话就**全部明文**了。下面是
`demo/wire/capture-plaintext.log` 的完整解码（`len` 已按机制七换算成 payload 长度）：

```
段 方向  字节   帧内容
─── ──── ────── ──────────────────────────────────────────────────────────
 0  -->   324B   3 帧 CapabilitiesSet，压缩算法**按优先级递增逐个试**：
                 len=106 type=2  payload 可见 "…compression…deflate_stream"
                 len=103 type=2  payload 可见 "…compression…lz4_message"
                 len=103 type=2  payload 可见 "…compression…zstd_stream"
                 ↑ 顺序不是随意的：默认向量是 {ZSTD, LZ4, DEFLATE}
                   (data_source.h:272-273)，协商时用 rbegin()→rend() 反向遍历
                   (cdk/mysqlx/session.cc:91-92)，所以发出去是 deflate→lz4→zstd。
                   源码注释原话（:88-89）："must be attempted with increasing
                   priority. The last successful type will be applied."
                   → 三个都成功 = **zstd 生效**（这也解释了段 11/13 的 type=19）
 1  <--     9B   len=5   type=11 Notice
 2  <--    10B   len=1   type=0  Ok   ┐ 三个算法各回一个 Ok
 3  <--     5B   len=1   type=0  Ok   ┘
 4  -->   322B   len=318 type=2  payload 可见 "…session_connect_attrs…
                                     _client_license…"   ← 连接属性
 5  <--     5B   len=1   type=0  Ok
─────── 至此 TLS/压缩/连接属性都谈完了，开始认证 ───────────────────────────
 6  -->    18B   len=14  type=4  payload 明文含 "MYSQL41"   ★ 机制名是字符串
 7  <--    27B   len=23  type=3  AuthenticateContinue       ← 服务端发 challenge
 8  -->    59B   len=55  type=5  客户端回应（SHA1 摘要）
 9  <--    26B   len=15  type=11 Notice
                 len=3   type=4  AuthenticateOk            ★ 认证通过
─────── 业务阶段 ────────────────────────────────────────────────────────
10  -->    20B   len=16  type=12 payload 明文含 "SELECT 1" 和 ns="sql"
11  <--   176B   len=51  type=19 Compression ┐
                 len=32  type=19 Compression │ 结果帧被压缩裹了一层
                 len=29  type=19 Compression │ type=19 就是
                 len=43  type=19 Compression │ Mysqlx.Connection.Compression
                 len=1   type=17 StmtExecuteOk ┘
12  -->    20B   len=16  type=12 payload 明文含 "ROLLBACK" 和 ns="sql"  ★
13  <--    52B   len=43  type=19 Compression
                 len=1   type=17 StmtExecuteOk
14  -->     5B   len=1   type=3  AuthenticateContinue  （关闭会话）
15  <--    11B   len=7   type=0  Ok
```

一次抓包同时证实了文章里 5 条论断：

| 抓包里的证据 | 证伪/证实了哪条 |
|---|---|
| 段 0 三个 `CapabilitiesSet`：`deflate_stream` / `lz4_message` / `zstd_stream` | 压缩算法是 **3 种**不是 5 种；且**按优先级逐个试**（机制四的"试错式协商"在这里也能看到） |
| 段 6 payload 明文含 `MYSQL41` | 认证机制名是**客户端选的一段字符串**，不是位图（机制四/五） |
| 段 6→7→8→9 四帧一轮回 | challenge 轮数由**服务端**驱动，客户端没有硬编码 20（机制五） |
| 段 10 payload 明文含 `SELECT 1` + `sql` | raw SQL 走 `Mysqlx.Sql.StmtExecute`（msg id 12），namespace 字段是 `sql` |
| **段 12 payload 明文含 `ROLLBACK` + `sql`** | **事务确实是普通 SQL**——CRUD 是 `Mysqlx.Crud.*` 结构化消息，事务却是文本，这个不对称是真的（机制九） |
| 段 11/13 结果帧 type=19 | 压缩生效后，结果帧被 `Mysqlx.Connection.Compression`（msg 19）**再包一层**，所以你在抓包里看不到 `ColumnMetaData`(14) / `Row`(13) |

> 段 12 那条尤其值得记：如果你在抓包里看到 `ROLLBACK`，就知道 DevAPI
> **把事务当普通 SQL 发了**——它没有专门的 `Mysqlx.Session.Rollback` 消息。

### 那个致命缺口

**如果你在 MySQL 8 上建了个默认 `caching_sha2_password` 账号，然后用裸 TCP 连 X DevAPI，认证会失败**，而且报错信息会是：

> Authentication failed using MYSQL41 and SHA256_MEMORY, check username and password or try a secure connection

（`cdk/mysqlx/session.cc:641-643`）

这个信息有很强的误导性——它会让人以为是密码错了。真实原因是**客户端根本没实现服务端要求的机制**，重输密码一万次也没用。三条出路：

1. **开 TLS**（`ssl-mode=REQUIRED`，而这本来就是默认值）。这样走 `PLAIN`，绕开 challenge 机制。
2. 改账号的认证插件为 `mysql_native_password`。
3. 用 classic 路径（`libmysqlclient` 自己支持 `caching_sha2_password` 的 full auth / RSA 流程）。

**这是"用 C++ 连 MySQL 有两个答案"最实际的落点**：X DevAPI 在 MySQL 8 + 裸 TCP + `caching_sha2_password` 这个最常见的组合上是有缺口的。

---

## 机制六：ssl-mode 默认 REQUIRED，且 TLS 是"先明文后升级"

先看默认值：

```cpp
// common/session.cc:337
unsigned mode = unsigned(SSL_mode::REQUIRED);
```

**`REQUIRED` 是默认值，不是 `PREFERRED`。** 这意味着你只写 `Session("root","pwd","127.0.0.1",33060)`，就已经在要求 TLS 了。对一个连本地测试库都嫌麻烦的默认配置来说，这个选择很激进，但它是对的——因为机制五里那个 `caching_sha2_password` 缺口，只有 TLS 能绕开。

cdk 层其实有五档（`cdk/include/mysql/cdk/foundation/connection_openssl.h:88-95`）：

```cpp
enum class SSL_MODE { DISABLED, PREFERRED, REQUIRED, VERIFY_CA, VERIFY_IDENTITY };
```

但 DevAPI 暴露出来的只有四档（`include/mysqlx/common_constants.h:196-210`），**没有 `PREFERRED`**。所以 cdk 里那套"服务端不支持 TLS 就降级"的逻辑（`cdk/core/session.cc:369`）在 C++ API 层永远走不到。

### TLS 的握手顺序：先明文，再升级

这是最反直觉的一段。TLS **不是** `connect()` 之后立刻 `SSL_connect()`，而是：

```cpp
// cdk/core/session.cc:305-399（节选）
Session_builder::TLS* Session_builder::tls_connect(Socket_base *connection, const TLS::Options &options)
{
  ...
  cdk::protocol::mysqlx::Protocol proto(*connection);      // ← 临时 Protocol，跑在裸 TCP 上

  api::Any::Document tls_caps;
  tls_caps.add()->scalar()->key_val("tls")->yesno(true);   // CapabilitiesSet { tls: true }

  proto.snd_CapabilitiesSet(tls_caps).wait();              // ← 明文发出去

  Reply_processor prc;
  proto.rcv_Reply(prc).wait();
  // 错误 5001 = "TLS not supported" → PREFERRED 模式下 m_tls = false

  unique_ptr<TLS> tls_conn(new TLS(conn_ptr.release(), options));
  tls_conn->connect();                                     // ← 这时才 SSL_connect()
  return tls_conn.release();
}
```

顺序是——下面是**实测抓包**。图里 **【见】= 抓包直接看到的**，
**【推】= 由明文那次会话推断的**（TLS 之后全是密文，看不见内容）：

```
 客户端                                              mysqld X plugin (:33060)
   │                                                      │
   │  ① TCP connect()                        ──明文──▶     │  此刻还是裸 TCP
   │                                                      │
   │  ② CapabilitiesSet{ tls:true }           ──明文──▶     │  ★ 协议层先握手
   │     【见】24B 帧头 05 00 00 00 14 02 …                │     len=20 type=2
   │     【见】payload 内含明文字段 "tls"                    │     （0a 03 74 6c 73）
   │                                                      │
   │  ③ Notice(type=11) + Ok(type=0)        ◀──明文──      │  ★ 不是裸 Ok，见下
   │     【见】05 00 00 00 0b 08 05 1a 00 …                │
   │                                                      │
   ├──────────── TLS 从这里才开始 ──────────────────────────┤
   │  ④ ClientHello            ──────────────────────────▶ │  ╔══════════════════╗
   │     【见】253B  0x16 03 01 type=1                     │  ║ 之后全是密文，   ║
   │                                                      │  ║ wireshark 只看   ║
   │  ⑤ ServerHello            ◀───────────────────────── │  ║ 得到长度和方向   ║
   │     【见】99B   0x16 03 03 type=2                     │  ╚══════════════════╝
   │                                                      │
   │  ⑥ (Certificate / ServerHelloDone 等，合并在 2196B 段) │
   │     【见】2196B 0x16 …                                │
   │                                                      │
   │  ⑦ ChangeCipherSpec + ClientKeyExchange + Finished    │
   │     【见】292B  14 03 03 00 01 01 16 03 03 01 19 …    │
   │                                                      │
   │  ⑧ AuthenticateStart / AuthenticateContinue / Ok      │  ★ 认证数据在密文里
   │     【推】机制名不可见                                 │
   │                                                      │
   │  ⑨ CapabilitiesSet{session_connect_attrs}            │  （压缩协商也在密文里）
   │     【推】不可见                                      │
   │                                                      │
   │  ⑩ StmtExecute{namespace:"sql", stmt:"SELECT 1"}       │
   │     【推】不可见                                      │
   │  ⑪ Resultset 帧流             ◀────────────────────── │
   │     【见】后续 16 段全是 0x17 ApplicationData         │
```

**抓包原文**（`demo/wire/capture-tls-default.log`，共 22 段，前 7 段）：

```
段  0  C->S    24B   frame  len=20  type=2   payload=0a110a0f0a03746c7312080801120408074001
段  1  S->C    14B   frame  len=5   type=11  payload=08051a0001000000 00
段  2  C->S   253B   *** TLS 0x16(Handshake) ver=0301 type=1  ClientHello
段  3  S->C    99B   *** TLS 0x16(Handshake) ver=0303 type=2  ServerHello
段  4  C->S   292B   14 03 03 00 01 01 | 16 03 03 01 19 …      ← ChangeCipherSpec + 后续握手
段  5  S->C  2196B   *** TLS 0x16(Handshake) … type=11 Certificate
段  6  C->S    88B   *** TLS 0x17 ApplicationData               ← 之后全程加密
段  7..21      …    全部 0x17 ApplicationData
```

### 段 1 不是 `Ok`，而是 `Notice`——这点我一开始也写错了

服务端回的第一帧 **type = 0x0b = 11**，按 `ServerMessages_Type`（`protocol/mysqlx.h:98-114`）是
`Mysqlx::Notice::Frame`，**不是** `Ok`（type 0）。它的 payload 是 `08 05 1a 00`，按
`mysqlx_notice.proto` 解出来是：

```
08 05  →  field 1 (required uint32 type) = 5
1a 00  →  field 3 (optional bytes payload) = 空
```

**但 `Notice.Type` 枚举只定义了 1~4**（`WARNING` / `SESSION_VARIABLE_CHANGED` /
`SESSION_STATE_CHANGED` / `GROUP_REPLICATION_STATE_CHANGED`）。`type=5` 不在客户端的枚举里。

服务端是 MySQL 8.0.46、客户端是 Connector/C++ 26.7.0——**这个 `type=5` 是什么意思，
本文没有结论，也不打算编一个。** 在明文那次抓包里（`capture-plaintext.log` 段 1）
第一帧同样是 `type=11`，随后 4 个 `CapabilitiesSet` 各自收到一个 `type=0` 的 `Ok`。
所以规律是：**`Notice` 先来一条，然后才是每个请求对应的 `Ok`。**

### 三个可以直接从抓包读出来的结论

1. **段 0/1 是明文。** `CapabilitiesSet{tls:true}` 裸奔在第一条 TCP 段里，payload 里能直接
   grep 出 `tls`（`0a 03 74 6c 73`）。中间人能看到你连哪台服务器、发的是什么客户端。
2. **段 2 才第一次出现 `0x16`（TLS Handshake 记录层）。** 也就是 `SSL_connect()` 发生在
   协议层握手**之后**，而不是 `connect()` 之后立刻做。
3. **段 6 之后 16 段全是 `0x17`（ApplicationData）。** 认证数据、SQL、结果全部不可见。

这跟 classic 协议的 `CLIENT_SSL` 旗标语义一致（先用裸连接换加密，再加密跑认证），
但实现方式完全不同——一个是位图协商，一个是 protobuf 消息。X 协议的副作用是
**第 ② 步明文**：攻击者能看到服务端地址、客户端版本和连接属性
（`_client_name` / `_client_version` / `_client_license` / `_os` / `_pid` / `_platform`），
**看不到认证数据和 SQL**。

真实 TLS 握手在 `cdk/foundation/connection_openssl.cc:551-652`：

```cpp
// :593-628（节选）
if (ssl_mode >= VERIFY_CA) {
  SSL_CTX_set_verify(SSL_CTX, SSL_VERIFY_PEER, nullptr);
  SSL_CTX_load_verify_locations(m_tls_ctx, ca, ca_path);
  X509_STORE_load_locations(store, crl);              // CRL 校验
  X509_VERIFY_PARAM_set_flags(param, X509_V_FLAG_CRL_CHECK | X509_V_FLAG_CRL_CHECK_ALL);
} else {
  SSL_CTX_set_verify(m_tls_ctx, SSL_VERIFY_NONE, nullptr);   // ← 不验证书！
}
...
m_tls = SSL_new(m_tls_ctx);
SSL_set_fd(m_tls, fd);
verify_server_cert();                                 // :649
if (SSL_connect(m_tls) != 1) throw_openssl_error();    // :652
```

注意 `VERIFY_CA` 走 `SSL_VERIFY_PEER` + `verify_server_cert()`（`connection_openssl.cc:833`，含 `matches_common_name()` `:740` 和 `matches_alt_name()` `:788`），但结合机制三里说的——**`VERIFY_CA` 时 DevAPI 不调 `tls.set_host_name()`，主机名校验实际是关的**。要真正防中间人，用 `VERIFY_IDENTITY`。

---

## 机制七：从 protobuf 消息到 ::send() 的最后一米

这是整条链最值得逐帧看的部分。从 `.sql("SELECT 1").execute()` 到 `::send()`：

```
mysqlx::SqlStatement::execute()                    include/mysqlx/devapi/executable.h:148
 └─ common::Op_base::execute()                     common/op_impl.h:346
     └─ Op_base::wait()                            common/op_impl.h:303
         └─ Op_sql::send_command()                 common/op_impl.h:1352
             └─ cdk::Session::sql(0, q, args)      cdk/include/mysql/cdk/session.h:222
                 └─ new Cmd_StmtExecute(...)      cdk/mysqlx/stmt.h:609
                     └─ Protocol::snd_StmtExecute() cdk/protocol/mysqlx/stmt.cc:112
                         └─ Msg_builder<cli_StmtExecute>::send()   protocol.h:1013
                             └─ Protocol_impl::snd_start()         protocol.cc:213
                                 └─ Protocol_impl::write_msg()     protocol.cc:371
                                     └─ Protocol_impl::write()     protocol.cc:461
                                         └─ Stream::Impl<C>::write()   protocol/mysqlx.h:835
                                             └─ Socket_base::Write_op::do_wait()  connection_tcpip.cc:395
                                                 └─ detail::send()   socket_detail.cc:950
                                                     └─ send_some() + poll_one()   socket_detail.cc:1021
                                                         └─ ::send()  socket_detail.cc:1039
```

**11 层，从一个 `execute()` 到 `::send()`。** 中间没有任何一步做 I/O 之外的"聪明事"——它们全在拼 protobuf。

`write_msg()` 干的三件事：

```cpp
// cdk/protocol/mysqlx/protocol.cc:371-390, 444-457
void Protocol_impl::write_msg(msg_type_t msg_type, Message &msg)
{
  msg_size_t net_size = static_cast<msg_size_t>(msg.ByteSizeLong()) + 1;   // 376
  resize_buf(CLIENT, header_length + net_size);                            // 378
  msg.SerializeToArray(wr_buffer() + header_length, ...);                  // 385
  ...
  // 396-441: 如果开了压缩且超过阈值，整个包再套一层 Mysqlx.Connection.Compression

  HTONSIZE(net_size);                                          // 444
  memcpy(wr_buf, &net_size, sizeof(net_size));                  // 445  ← 4 字节长度
  wr_buf[header_length - 1] = (byte)msg_type;                  // 446  ← 1 字节消息类型
  NTOHSIZE(net_size);
  total_write_size = net_size + header_length - 1;

  m_pipeline_size += total_write_size;
  if (!m_pipeline) { write(wr_buf); }                          // 454-457
}
```

`header_length` 是 5（`cdk/protocol/mysqlx/protocol.h:108`）。**抓包实测**画出来是这样：

```
                       真实的一帧（StmtExecute，来自 capture-plaintext.log 段 10）
  偏移   0  1  2  3  4  5 ...
        ┌───────────────┬──────┬────────────────────────────────────────┐
        │  len  (4B LE) │ type │  protobuf payload（len-1 字节）          │
        └───────────────┴──────┴────────────────────────────────────────┘
          └─ 含 type 自己 ┘  1B         └─────── len - 1 ────────┘

        实际字节：10 00 00 00  0c  0a 04 73 71 6c 12 07 53 45 4c 45 43 54 20 31
                  └─16─┘  └0c┘  └─ ns="sql" ─┘ └────── "SELECT 1" ──────┘
                  len=16   type=12
                  (小端)   Sql.StmtExecute

  ┌─ 整帧在线上的字节数 = 4 + len = 4 + 16 = 20 ─────────────────────┐
  │ 抓包该 TCP 段恰好 20 字节 ✓                                       │
  └───────────────────────────────────────────────────────────────────┘
```

**最容易搞错的一点**：`len` **包含 type 那 1 个字节**。所以：

| 关系 | 公式 |
|---|---|
| payload 长度 | `len - 1` |
| 整帧长度 | `4 + len` |
| `header_length` 常量 | **5** = 4(len) + 1(type) |

对照 `write_msg()` 的代码（`protocol.cc:444-448`）就完全对上了：

```cpp
HTONSIZE(net_size);                                  // 444
memcpy(wr_buf, &net_size, sizeof(net_size));          // 445  ← 写 4 字节长度
wr_buf[header_length - 1] = (byte)msg_type;           // 446  ← 索引 4，即第 5 字节
NTOHSIZE(net_size);
total_write_size = net_size + header_length - 1;      // = len + 4  ✓
```

抓包里另一帧可以交叉验证 `len-1`：

```
段 6   C->S   18B   len=14  type=4  AuthenticateStart   payload=13B
      payload 可见文本: "..MYSQL41...."
      18 = 4 + 14 ✓   14 - 1 = 13 ✓   且明文里能直接读出机制名 MYSQL41
```

`write()` 本身只有一行有效代码：

```cpp
// cdk/protocol/mysqlx/protocol.cc:461-464
void Protocol_impl::write(byte *buf)
{ m_wr_op.reset(m_str->write(buffers(buf, m_pipeline_size))); clear_Pipeline(); }
```

`m_pipeline_size` 这个变量揭示了一个优化：**pipeline 模式**下多条消息会攒在一起一次 `write()` 出去。看 `send()` 就明白了：

```cpp
// cdk/protocol/mysqlx/protocol.h:1013-1024
Protocol::Op& send() {
  if (m_stmt_id != 0) {                                    // 预处理语句
    m_protocol.start_Pipeline();
    m_protocol.snd_start(m_prepare,        msg_type::cli_PreparePrepare).wait();  // 40
    m_protocol.snd_start(m_prepare_execute, msg_type::cli_PrepareExecute).wait();  // 41
    return m_protocol.snd_Pipeline();                      // 一次 write() 发出两帧
  }
  return m_protocol.snd_start(m_msg, T);                    // 单消息快路径
}
```

预处理语句的执行是**两条消息一次写**：`Prepare.Prepare`(40) + `Prepare.Execute`(41)。这就是 DevAPI 的 PS 状态机 `PS_EXECUTE → PS_PREPARE_EXECUTE → PS_EXECUTE_PREPARED`（`common/op_impl.h:97-102`、`:517-559`）的线上形态。

传输层是模板注入的——这是整个设计里最优雅的一处：

```cpp
// cdk/include/mysql/cdk/protocol/mysqlx.h:822-836
template <class C> class Protocol::Stream::Impl : public Stream {
  typedef typename C::Read_op  Rd_op;
  typedef typename C::Write_op Wr_op;
  Op* read (const buffers &buf) { return new Rd_op (m_conn, buf); }
  Op* write(const buffers &buf) { return new Wr_op(m_conn, buf); }
};
```

`C` 是 `TCPIP`（`connection_tcpip.h:251`）还是 `TLS`（`connection_openssl.h:48`），编译器在实例化时就定好了。**协议层代码完全不知道自己跑在明文 TCP 还是 TLS 上。** 两条路的叶子分别是：

```
TCP:  Socket_base::Write_op → detail::send      → ::send()      socket_detail.cc:1039
TLS:  TLS::Write_op        → common_write      → SSL_write()   connection_openssl.cc:1045
```

---

## 机制八：结果回来时，帧头是 5 字节不是 4 字节

`SELECT` 的回复不是一条消息，是**服务端连续发的一串消息**，客户端按语法状态机逐条吃：

```
Stmt_op::do_cont  cdk/mysqlx/result.cc:58
 └─ Protocol::rcv_MetaData / rcv_Rows / rcv_StmtReply   cdk/protocol/mysqlx/rset.cc:507/513/519
     └─ Op_rcv::do_read_msg  cdk/protocol/mysqlx/protocol.cc:782
         ├─ Protocol_impl::read_header()   ← 读 5 字节帧头    protocol.cc:496
         │    └─ m_str->read(buffers(m_rd_buf, 5))           protocol.cc:530
         ├─ Protocol_impl::read_payload()  ← 读 len 字节      protocol.cc:534
         ├─ MessageLite::ParseFromArray                     protocol.cc:998
         └─ Rcv_result_base::do_next_msg()  ← 语法状态机     rset.cc:304
             └─ process_msg_with(Row | ColumnMetaData | FetchDone | StmtExecuteOk)
                 └─ Cursor::row_begin / col_* / row_end      cdk/mysqlx/result.cc:784
```

读取侧和写入侧是严格对称的：先 `read_header()` 读满 5 字节（`protocol.cc:530`），再 `read_payload()` 按头里的长度读 payload（`protocol.cc:567`）。**顺序不能反，也不能少读**——TCP 是字节流，没有消息边界，一切靠这个 5 字节头。

状态机在 `Rcv_result_base::do_next_msg()`（`rset.cc:304-479`），状态有 `START / MDATA / ROWS / CLOSE / DONE`（`rset.cc:119-120`）。行数据的分发是逐字段回调：

```cpp
// cdk/protocol/mysqlx/rset.cc:569-606
template<>
void Rcv_result_base::process_msg_with(
  Mysqlx::Resultset::Row &row, Row_processor &rp
)
{
  row_count_t rcount = m_rcount++;

  if (!rp.row_begin(rcount))
    return;                                    // 576  ← 处理器不要这行就整行跳过

  col_count_t ccount = 0;
  for (auto it = row.field().begin(); it != row.field().end(); ++it, ++ccount)
  {
    if (it->length() == 0)
    {
      rp.col_null(ccount);                     // 587  ← 零长度字段 == NULL
      continue;                                // 588  ← 注意：直接跳过，col_begin 根本不会被调用
    }

    size_t read_window = rp.col_begin(ccount, it->length());   // 591
    size_t pos = 0;
    while (it->length() > pos && read_window)                   // 594  ← 读窗口循环
    {
      size_t bytes_to_feed = it->length() - pos > read_window ? read_window
                                                            : it->length() - pos;
      size_t read_window_new = rp.col_data(ccount,
          bytes((byte*)(it->c_str() + pos), bytes_to_feed));    // 597
      pos += read_window;
      read_window = read_window_new;
    }
    rp.col_end(ccount, it->length());                           // 602
  }
  rp.row_end(rcount);                                           // 605
}
```

这里有三个容易看漏的细节：

1. **`:587` ——X 协议用"零长度"表示 NULL。** 这是 protobuf 字段的默认行为，客户端必须显式处理，否则空字符串和 NULL 会混淆。
2. **NULL 字段根本不进 `col_begin()`。** 那个 `continue` 意味着处理器的 `col_begin`/`col_end` 不会被调用——如果你自己写 `Row_processor`，`col_begin` 和 `col_end` 的调用次数**不保证成对**，只有非 NULL 字段才成对。
3. **`:594` 的读窗口循环**：`col_begin` 返回一个 `read_window`（消费者一次能吃多少字节），`col_data` 也返回新的窗口，于是大字段被分块投喂。窗口为 0 就停止——这就是"消费者主动限流"的实现。

这个"逐消息驱动"的模型还有个后果：**`Op_rcv` 每读一条消息就回调一次处理器**，所以结果集是**流式消费**的，不是攒齐了才给你。`Result_impl` 靠 `prefetch_size` 控制预取窗口（`common/result.cc:317-319`）：

```cpp
m_cursor->get_rows(*this, prefetch_size);   // 带预取
m_cursor->get_rows(*this);                   // 不带
```

对大结果集来说，这是"能处理超过内存的结果"和"不能"的区别。

---

## 机制九：CRUD 不翻译成 SQL

这一条最容易让人意外。当你写：

```cpp
coll.find("name = 'x'").limit(10).execute();
```

线上**没有任何 SQL 文本**。发出去的是 protobuf：

```
Mysqlx.Crud.Find  (msg id 17)
  ├─ data_model = DOCUMENT
  ├─ collection = "库.表"
  ├─ limit       = 10
  └─ projection  = Mysqlx.Expr.Expr (表达式树，不是字符串)
```

完整的 CRUD 消息映射（`cdk/protocol/mysqlx/crud.cc`）：

| DevAPI 调用 | protobuf 消息 | msg id | 发送函数 |
|---|---|---|---|
| `Session::sql()` | `Mysqlx.Sql.StmtExecute` | 12 | `stmt.cc:112` |
| `Collection::add()` | `Mysqlx.Crud.Insert`（doc 模式，带 upsert flag） | 18 | `cdk/protocol/mysqlx/crud.cc:669` |
| `Collection::find()` | `Mysqlx.Crud.Find` | 17 | `cdk/protocol/mysqlx/crud.cc:568` |
| `Collection::modify()` | `Mysqlx.Crud.Update` | 19 | `cdk/protocol/mysqlx/crud.cc:776` |
| `Collection::remove()` | `Mysqlx.Crud.Delete` | 20 | `cdk/protocol/mysqlx/crud.cc:812` |
| `Table::insert()` | `Mysqlx.Crud.Insert`（table 模式） | 18 | `cdk/protocol/mysqlx/crud.cc:669` |
| `Table::update()` | `Mysqlx.Crud.Update`（table 模式） | 19 | `cdk/protocol/mysqlx/crud.cc:776` |

**这意味着写错字段名不会在客户端报 SQL 语法错**，而是由服务端做 schema 校验后返回一个 protobuf error。如果你把 CRUD 路径当"SQL 的语法糖"来用，会失去 SQL 语法检查这一层保护。

那条件表达式 `name = 'x'` 是怎么变成 protobuf 的？靠 cdk 自带的一个表达式解析器：

```cpp
// cdk/parser/expr_parser.h:1530
Expr_parser_base::parse(...)
```

它把字符串解析成 `Mysqlx.Expr.Expr` 树。`.proto` 定义全在 `cdk/protocol/mysqlx/pb/mysqlx_expr.proto`。所以 DevAPI 那套"点链式"语法（`.find(expr).where(...).order_by(...)`）最终是**客户端本地解析成表达式树**，不是拼字符串。

同样地，**事务是唯一的例外——它确实是普通 SQL**：

```cpp
// cdk/mysqlx/session.cc:883-927
// BEGIN / COMMIT / ROLLBACK / SAVEPOINT 走 SQL 字符串
```

这个不对称有点反直觉：CRUD 是结构化的，事务是文本的。

---

## 机制十：classic 路径是 mysql_real_query 的三层桥

现在切到另一条路。demo_b 的调用链：

```
sql::Connection::createStatement()          jdbc/driver/mysql_connection.cpp:1862
  └─ new MySQL_Statement(...)                jdbc/driver/mysql_statement.h:70
      └─ MySQL_Statement::executeQuery(sql)  jdbc/driver/mysql_statement.cpp:252
          └─ do_query(sql)                   jdbc/driver/mysql_statement.cpp:98
              └─ proxy_p->query(q)           :118
                  └─ MySQL_NativeConnectionWrapper::query()   nativeapi/mysql_native_connection_wrapper.cpp:654
                      └─ api->real_query(mysql, str, len)     :657
                          └─ LibmysqlStaticProxy::real_query()  libmysql_static_proxy.cpp:454
                              └─ ::mysql_real_query()          :456   ◄── 交给 libmysqlclient
```

**整个 `jdbc/driver/` 目录里没有一行协议代码。** `sql::Statement::executeQuery` 到 `::mysql_real_query` 之间全是适配层。

### 三层桥

```
① sql::mysql::MySQL_Statement              jdbc/driver/*
        │  持有 std::weak_ptr<NativeConnectionWrapper>
        ▼
② sql::mysql::NativeAPI::NativeConnectionWrapper      nativeapi/native_connection_wrapper.h:73
        │  virtual connect() / query() / store_result() / stmt_*
        ▼
③ sql::mysql::NativeAPI::IMySQLCAPI                   nativeapi/mysql_client_api.h:190
        │  ~90 个纯虚函数 + 上一层的函数指针 typedef 表（:48-183）
        ▼
   ┌──────────────────────┬──────────────────────────────┐
   │ LibmysqlStaticProxy  │  LibmysqlDynamicProxy        │
   │ 直接 ::mysql_xxx()   │  dlopen + dlsym("mysql_xxx") │
   └──────────────────────┴──────────────────────────────┘
```

第 ③ 层的接口注释写得很直白（`mysql_client_api.h:185-189`）：

> *"Interface MySQL C-API wrapper class should implement. At the moment we must have at least 2 implementation - for static and dynamic mysql client library linking"*

编译期二选一（`nativeapi/mysql_client_api.cpp:39-45`）：

```cpp
#ifdef MYSQLCLIENT_STATIC_BINDING
  #include "libmysql_static_proxy.h"
#else
  #include "libmysql_dynamic_proxy.h"
#endif
```

`MYSQLCLIENT_STATIC_BINDING` 决定"**调用时**怎么拿到函数"（直接符号 vs `dlsym`），`MYSQLCLIENT_STATIC_LINKING` 决定"**链接时**怎么挂上去"（`.a` vs `.so`）——两个不同的开关，名字很像，很容易混。默认在 `jdbc/CMakeLists.txt:89-90`：

```cmake
add_config_option(MYSQLCLIENT_STATIC_LINKING BOOL ADVANCED DEFAULT OFF "enable libmysqlclient static linking")
add_config_option(MYSQLCLIENT_STATIC_BINDING  BOOL ADVANCED DEFAULT ON  "enable libmysqlclient static binding")
```

**默认是"链接期动态 + 调用期静态"**——也就是链接 `libmysqlclient.so`，但代码里直接写 `::mysql_real_query()`。若要 `dlopen`：

```cmake
# jdbc/driver/CMakeLists.txt:215-222
if(MYSQLCLIENT_STATIC_BINDING)
  target_link_libraries(jdbc PRIVATE MySQL::client)      # 硬链接
else()
  target_include_directories(jdbc PRIVATE ${MYSQL_INCLUDE_DIR})
  if(NOT WIN32) target_link_libraries(jdbc PRIVATE dl)    # 运行时 dlopen
endif()
```

动态路径的 SONAME 默认是 `"libmysqlclient_r.so"`（`libmysql_dynamic_proxy.cpp:52`），符号懒解析（`library_loader.cpp:48-50`）：

```cpp
#define LoadLibrary(p)         ::dlopen(p, RTLD_LAZY)
#define FreeLibrary(p)         ::dlclose(p)
#define GetProcAddress(p1,p2)  ::dlsym(p1,p2)
```

`dlopen` 模式的价值是**可替换 libmysqlclient 而不用重编译连接器**。但 `dlsym` 找不到符号时抛的是 `"Couldn't find symbol "`（`library_loader.cpp:113-135`）——这个报错信息本身不告诉你是哪个符号。

### URL 解析：没有 `jdbc:` 前缀

这是个容易踩的细节。`MySQL_Driver::connect()` 的第一个参数名叫 `hostName`（`jdbc/driver/mysql_driver.cpp:126-131`），但**它实际是整个 URL 字符串**。解析器 `parseUri()`（`jdbc/driver/mysql_uri.cpp:124-260`）接受：

| 前缀 | 协议 |
|---|---|
| `tcp://` | TCP |
| `unix://` | Unix socket |
| `pipe://` | Windows 命名管道 |
| `mysql://` | TCP |
| **无前缀** | `host[:port][/schema]` |

`"jdbc:mysql://"` **不被支持**——`"jdbc:"` 在 `jdbc/**/*.cpp` 里零命中。写 `jdbc:mysql://host:3306/db` 会被当成主机名 `jdbc` 后面跟一堆垃圾，解析失败抛：

```
sql::InvalidArgumentException("Invalid hostname URI")     mysql_connection.cpp:828
```

另外**逗号分隔的主机列表是支持的**（`mysql_uri.cpp:231-243`），配合 `OPT_MULTI_HOST` 做故障转移；IPv6 要用方括号 `[::1]:3306`（`mysql_uri.cpp:174-186`）。

### Statement vs PreparedStatement：文本 vs 二进制

`Statement` 路径的结果是**字符串**：

```cpp
// jdbc/driver/mysql_resultset.cpp:742-772（节选）
sql::SQLString MySQL_ResultSet::getString(uint32_t columnIndex) {
  size_t len = result->fetch_lengths()[columnIndex - 1];        // 769
  return sql::SQLString(row[columnIndex-1], len);                // 772
}
```

`row` 是 `MYSQL_ROW`（`char**`），libmysqlclient 已经把线上字节转成了文本。**`getInt()` 是先 `atol()` 那个字符串。**

`PreparedStatement` 路径完全不一样——服务端下发二进制行，客户端用预分配的 `MYSQL_BIND` 缓冲区直接接：

```cpp
// jdbc/driver/mysql_resultbind.cpp:354-369（节选）
for (每个 field) {
  rbind[i].buffer_type   = p.type;                        // 358  按列的真实类型
  rbind[i].buffer        = p.buffer;                      // 359
  rbind[i].length        = &len[i];                       // 361
  rbind[i].is_null       = &is_null[i];                   // 362
  rbind[i].is_unsigned   = field->flags & UNSIGNED_FLAG;  // 364
}
if (proxy->bind_result(rbind.get())) throwSQLException(...); // 366-369
```

读取时 `getInt64_intern()` 直接从 `rbind[i].buffer` 取 8 字节（`mysql_ps_resultset.h:92-93`），**没有字符串中间层**。这是 PS 相对 Statement 的实质性能差异，不只是"能防注入"。

参数侧同理，`setInt()` 是在填 `MYSQL_BIND`（`jdbc/driver/mysql_prepared_statement.cpp:1115-1149`）：

```cpp
--parameterIndex;                                    // 1125  DBC 从 1 开始
enum_field_types t = MYSQL_TYPE_LONG;                 // 1133
BufferSizePair p = allocate_buffer_for_type(t);       // 1135
param->buffer_type   = t;                             // 1140
param->buffer        = p.first;                       // 1142
memcpy(param->buffer, &value, p.second);              // 1148
```

`MySQL_Bind : public MYSQL_BIND`（`jdbc/driver/mysql_resultbind.h:55`）——连接器直接继承 C API 的结构体，靠 `setBigInt`/`setString` 这些薄封装往里填。

---

## 机制十一：classic 路径默认不编译，还有一堆死代码

如果你决定用 classic 路径，构建时要显式打开，并告诉它 libmysqlclient 在哪：

```bash
# ❌ 网上（包括本文早期版本）常见的写法，在 Debian/Ubuntu/麒麟 上必失败
cmake .. -DWITH_JDBC=ON -DWITH_MYSQL=/usr

# ✅✅ 首选：一个 mysql_config 搞定全部（实测）
cmake .. -DWITH_JDBC=ON \
         -DMYSQL_CONFIG_EXECUTABLE=/usr/bin/mysql_config
```

**优先用 `mysql_config`**，因为 `use_mysql_config()`（`DepFindMySQL.cmake:483-511`）会一次性
把四个变量都填对——实测输出：

```
MYSQL_INCLUDE_DIR:PATH=/usr/include/mysql        ← 指向 mysql.h 真正所在
MYSQL_LIB_DIR:PATH=/usr/lib/x86_64-linux-gnu
MYSQL_VERSION:INTERNAL=8.0.42
MYSQL_VERSION_ID:INTERNAL=80042                  ← 各个 #if 守卫就靠它
```

注意 `mysql_config` 报的是**它自己被安装到的位置**，所以离线环境下把 libmysqlclient
解到别的目录也能用——实测把它指向一个 relocatable 目录后，四个变量全部正确指向新位置。

没有 `mysql_config` 时才手工给四个：

```bash
cmake .. -DWITH_JDBC=ON -DCMAKE_BUILD_TYPE=Release \
         -DMYSQL_VERSION=8.0.42 -DMYSQL_VERSION_ID=80042 \
         -DMYSQL_INCLUDE_DIR=/usr/include/mysql \
         -DMYSQL_LIB_DIR=/usr/lib/x86_64-linux-gnu
```

`MYSQL_VERSION_ID` **必须和 `MYSQL_VERSION` 对应**（8.0.42 → `80042`），否则那些
`#if MYSQL_VERSION_ID >= 80300` 守卫会走错分支。

> ⚠️ `MYSQL_INCLUDE_DIR` **只能是单目录**。`DepFindMySQL.cmake:135` 硬查
> `EXISTS ${MYSQL_INCLUDE_DIR}/mysql.h`，给分号列表会直接报
> `Could not find MySQL headers`。但只给 `/usr/include/mysql` 又不够——
> `mysql_com.h` 内部写的是 `#include "mysql/udf_registration_types.h"`（**带前缀**），
> 还需要 `/usr/include` 也在搜索路径上。解法是做一个同时满足两种写法的目录
> （把 `mysql/` 整个链进去，再把每个 `.h` 软链到顶层），实测这样两边都能过。

**为什么 `-DWITH_MYSQL=/usr` 不行**：它会推出 `MYSQL_INCLUDE_DIR=/usr/include`，然后做这个检查（`jdbc/cmake/DepFindMySQL.cmake:134`）：

```cmake
if(NOT MYSQL_INCLUDE_DIR OR NOT EXISTS "${MYSQL_INCLUDE_DIR}/mysql.h")
  message(FATAL_ERROR "Could not find MySQL headers at: ${MYSQL_INCLUDE_DIR}\n" ...)
```

它要求 `${MYSQL_INCLUDE_DIR}/mysql.h` **直接存在**。但发行版的 `libmysqlclient-dev` 装在 `/usr/include/mysql/mysql.h`，`/usr/include/mysql.h` 并不存在 → 直接 `FATAL_ERROR: Could not find MySQL headers at: /usr/include`。

`WITH_MYSQL` / `MYSQL_DIR` 只适合**自编译安装**的 libmysqlclient（那种布局是 `<prefix>/include/mysql.h`）。三个变量都可以用，`WITH_MYSQL` 会覆盖 `MYSQL_DIR`（`DepFindMySQL.cmake:87-89`），再推 `MYSQL_LIB_DIR` / `MYSQL_PLUGIN_DIR`（`:117-127`）。

### ⚠️ classic 路径对 libmysqlclient 版本有硬要求（实测）

这是本文最重要的一条**实践**结论，编译验证过：`libmysql_static_proxy.cpp` **无版本保护地**调用三个符号——

```
libmysql_static_proxy.cpp:376   ::mysql_plugin_get_option(...)
libmysql_static_proxy.cpp:427   ::mysql_real_connect_dns_srv(...)
libmysql_static_proxy.cpp:438   ::mysql_bind_param(...)
```

（9.2.0 的 `:376` / `:427` / `:438` 一模一样，没有 `#if` 保护。）

实测各版本：

| libmysqlclient | 三个符号 | glibc 要求 | OpenSSL | 能否编过 |
|---|---|---|---|---|
| **8.0.19**（focal 初始发行版） | ✗ ✗ ✗ | `>= 2.28` ✅ | `libssl1.1` ✅ | **不能** |
| **8.0.42**（focal-updates） | ✓ ✓ ✓ | `>= 2.28` ✅ | `libssl1.1` ✅ | **能（实测通过）** |
| 8.0.46（jammy-updates） | ✓ ✓ ✓ | `>= 2.34` ❌ | `libssl3` ❌ | 能，但装不上 |

用 8.0.19 编的实际报错：

```
jdbc/driver/nativeapi/libmysql_static_proxy.cpp:376:9: error:
  '::mysql_plugin_get_option' has not been declared; did you mean 'ptr2mysql_plugin_get_option'?
```

> ⚠️ **勘误。** 本文早期版本在这里写的是"对麒麟 V10 SP1 是个死结，只能走 X DevAPI"。
> **那个结论是错的，错因是版本选错了，不是平台不行。**
> 我当时手上只有 `8.0.19`（focal 初始发行版）和 `8.0.46`（jammy），前者太老、后者太新，
> 就误判成"没有可用版本"。
>
> 后来在**真的麒麟 V10 SP1 容器**（`liyaosong/kylin:v10.1-sp1-amd64`，
> glibc `2.31-0kylin9.1k20.3`）里逐个试了一遍，结论是：

| libmysqlclient | 来源 | 三个符号 | 麒麟上编 classic |
|---|---|---|---|
| 8.0.19 | focal 初始发行版 | ✗ ✗ ✗ | ❌ 符号缺失 |
| **8.0.26** | **麒麟自带源** | ✗ ✅ ✅ | ❌ **实测 `make exit=2`** |
| **8.0.42** | **focal-updates** | ✓ ✓ ✓ | ✅ **实测 `make exit=0`** + demo `exit=0` |
| 8.0.46 | jammy-updates | ✓ ✓ ✓ | 装不上（`libc6 >= 2.34` + `libssl3`） |

> **麒麟自己的源里只有 8.0.26，差在 `mysql_plugin_get_option`**——它声明在
> `client_plugin.h`（不是 `mysql.h`），8.0.26 没有：
>
> ```
> jdbc/driver/nativeapi/libmysql_static_proxy.cpp:376:9: error:
>   '::mysql_plugin_get_option' has not been declared; did you mean 'ptr2mysql_plugin_get_option'?
> ```
>
> 换上 focal-updates 的 **8.0.42** 后，**只装 2 个包**（`libmysqlclient21` +
> `libmysqlclient-dev`），`dpkg -i` 退出码 0、`dpkg --audit` 干净、麒麟自带的
> `libssl1.1` / `zlib1g` / `mysql-common` 全部未动；随后在容器内从源码编出
> `libmysqlcppconn.so.10.26.7.0`（最高只要求 `GLIBC_2.14`），CRUD demo 跑通，
> 连 `caching_sha2_password` 账号全绿。
>
> 教训一：手上只有两个候选版本时，容易把"我没试过的那个"当成"不存在的"。
> 教训二：**别只 grep `mysql.h`**。我第一轮查 8.0.26 时只 grep 了 `mysql.h`，
> 得出"三个全无"，实际有两个是有的。判据只能是编译。

| 方案 | 可行性 |
|---|---|
| 源码编 **X DevAPI**（只要目标机自带的 libssl-dev） | ✅ 实测通过，**完全不碰 libmysqlclient** |
| 源码编 **classic** + libmysqlclient **8.0.42** | ✅ **实测通过**（麒麟容器内编 + 跑） |
| 源码编 **classic** + 麒麟自带 8.0.26 | ❌ `libmysql_static_proxy.cpp:376` |
| 源码编 **classic** + libmysqlclient 8.0.19 | ❌ 符号缺失 |
| 源码编 **classic** + libmysqlclient 8.0.46 | ❌ glibc / OpenSSL 不够 |
| 用**预编译**的 `libmysqlcppconn.so` | ✅ 若它是在 glibc ≤ 2.31 上构建的 |

最后一行仍然成立：这些符号只在**编译期**需要。如果你的环境里已有别人编好的 `libmysqlcppconn.so`，运行期不再需要它们，**直接用即可**。

符号检查时注意 `nm` 输出的版本后缀，否则会误判：

```console
$ nm -D --defined-only libmysqlclient.so.21.2.42 | grep mysql_bind_param
0000000000031500 T mysql_bind_param@@libmysqlclient_21.0
#                ^^^^^^^^^^^^^^^^^^^ 带 @@libmysqlclient_21.0 后缀
```

按裸符号名 `mysql_bind_param` 精确匹配会**判成"缺失"**——我第一次就是这么错的。

**选版本判据**：拿 `nm -D` 的输出比 `grep` 裸名字可靠；再对着
`MYSQL_VERSION_ID` 确认 `>= 80300` / `>= 80400` 这类分界，最后才动手编。

Linux 上的最终链接行（`jdbc/driver/CMakeLists.txt:203-222`）：

```
libmysqlcppconn.so  ←  libjdbc.a  +  pthread  +  resolv  +  dl  [+  MySQL::client]
```

### 三个需要知道的坑

**1. `jdbc/thread/` 是死代码。**

目录里有完整的 `my_pthread.c`、`thr_mutex.c`、`my_wincond.c`……还配了个 `CMakeLists.txt` 要生成 `mysqlcppconn_thread` 库。但：

```cmake
# jdbc/CMakeLists.txt:244-245 —— 只有这两个
ADD_SUBDIRECTORY(cppconn)
ADD_SUBDIRECTORY(driver)
```

全树 grep `add_subdirectory(thread)` 零命中，`jdbc/driver/CMakeLists.txt:97-121` 的源文件列表里也没有 `../thread/*.c`。唯一的另一个引用是 `jdbc.cmake:188`——而 `jdbc.cmake` **从来没有被 `include()` 过**，而且它在 `jdbc.cmake:143` 就 `return()` 了，后面 270 行代码不可达。

结论：**这个目录里的东西一个都没被编译、没被打包、没被安装。** 连接器直接链系统 `pthread`（`jdbc/driver/CMakeLists.txt:208`），用 C++17 的 `<mutex>`/`<shared_mutex>`。这是 MySQL 早期 vendored `my_pthread` shim 的历史遗留。

顺带一提，`jdbc/FindMySQL.cmake`（864 行）和 `jdbc.cmake`（413 行）也都是孤儿，实际生效的是 `jdbc/cmake/DepFindMySQL.cmake`。

**2. `get_driver_instance()` 不是线程安全的。**

```cpp
// jdbc/driver/mysql_driver.cpp:79-98（节选）
sql::mysql::MySQL_Driver * _get_driver_instance_by_name(const char * const clientlib)
{
  static std::map<SQLString, std::shared_ptr<MySQL_Driver>> driver;   // 84  无锁
  ...
}
```

函数内 `static` 局部变量的初始化是线程安全的（C++11 起保证），但**之后的 `find` / `operator[]` 插入不是**。`getCApiHandle()` 里的 `static std::map` 也一样（`nativeapi/mysql_client_api.cpp:55`）。官方文档确认了这点（`doc/jdbc_ref.txt:47-50`）：

> *"The `get_driver_instance()` function is not thread-safe. Either avoid invoking
> it from within multiple threads at once, or surround the calls with a mutex to
> prevent simultaneous execution in multiple threads."*  （`doc/jdbc_ref.txt:48-50`，逐字）

**正确姿势是：driver 在 main 里取一次共享给所有线程，connection 每个线程自己建一个。** 官方示例 `jdbc/examples/pthreads.cpp` 前半段正是这么做的——`jdbc/examples/pthreads.cpp:125` 取一次 driver，`jdbc/examples/pthreads.cpp:129` 建连接。

但要注意这个示例**后半段把同一个 `con` 也传给了线程**（`jdbc/examples/pthreads.cpp:147` `param->con = con.get()`，线程里 `jdbc/examples/pthreads.cpp:216` 直接用它 `createStatement()`）。那是为了演示"最小可编译"而写的，**不是推荐做法**：连接器在语句/结果集路径上没有任何互斥（`MySQL_Statement` / `MySQL_ResultSet` 只持 `std::weak_ptr`，不持锁），一个 `MYSQL*` 被两个线程同时用属于未定义行为。

| 对象 | 是否可跨线程共享 |
|---|---|
| `sql::Driver` | ✅ 可以（在 main 取一次） |
| `sql::Connection` | ❌ 不行，一个线程一个 |
| `sql::Statement` / `ResultSet` | ❌ 不行，且生命周期不得长于其 Connection |

**3. 异常层次比 JDBC 少很多。**

```
std::runtime_error
  └── sql::SQLException                          jdbc/cppconn/exception.h:54
        ├── MethodNotImplementedException        :97
        ├── InvalidArgumentException             :103
        ├── InvalidInstanceException             :109
        ├── NonScrollableException               :116
        └── SQLUnsupportedOptionException        :122
```

**没有** `SQLTimeoutException`、`BatchUpdateException`、`NoDataFoundException`、`DataTruncation`——从 JDBC 迁过来的代码会找不到这些类型。

而 `sql::SQLWarning` **根本不是异常**，是独立的抽象接口（`jdbc/cppconn/warning.h:50`），不继承 `SQLException`。想按 JDBC 的习惯 `catch (SQLException&)` 一把抓Warning 是抓不到的。

错误码统一从一个地方转换（`jdbc/driver/mysql_util.cpp:55-58`）：

```cpp
void throwSQLException(NativeConnectionWrapper & proxy) {
  throw sql::SQLException(proxy.error(), proxy.sqlstate(), proxy.errNo()); }
```

三个值分别来自 `mysql_error()` / `mysql_sqlstate()` / `mysql_errno()`。

有意思的是 **Warning 的获取方式**——它不是 C API 给的，而是**再发一条 SQL**（`jdbc/driver/mysql_warning.cpp:229`）：

```cpp
stmt->executeQuery("SHOW WARNINGS");
```

SQLSTATE 还得在客户端**反推**（`mysql_warning.cpp:100-218` 的 `errCode2SqlState()`）。这比 libmysqlclient 直接给结构化的 `MYSQL_WARNING` 差一层。

**4. 还有一批 `throw MethodNotImplementedException` 的坑。**`Connection::setHoldability`、`setCatalog`（no-op）、`Statement::cancel`、`setMaxRows`、`setFetchSize`、`getFetchSize`、`ResultSet::getRowId`……都直接抛。

另外 `MySQL_Savepoint::getSavepointId()` **无条件抛**（`mysql_connection.cpp:122-128`）：

```cpp
int MySQL_Savepoint::getSavepointId()
{
  throw sql::InvalidArgumentException("Only named savepoints are supported.");
  return 0;   // fool compilers
}
```

即**只支持具名 savepoint**。注意那句 `return 0; // fool compilers`——`throw` 之后代码不可达，
但标准不保证编译器知道，所以还得写一句骗它，否则 `-Wreturn-type` 会报。这是"故意不可达"
的常见写法，全树还有几处同款。

还有一个隐蔽的：`WE_SUPPORT_USE_RESULT_WITH_PS` 这个宏**从来没被定义过**（全树 0 处 `#define`），
所以三个 `#if` 分支全被编译掉（`mysql_connection.cpp:1145`、`:2256`，
`mysql_prepared_statement.cpp:1722`——第四处 `jdbc/test/unit/classes/connection.cpp:152`
只是一句注释 `"compiled without -DWE_SUPPORT_USE_RESULT_WITH_PS"`）。
后果是 `defaultPreparedStatementResultType` 作为连接选项会抛
`"parameter still not implemented"`。

**5. 五个类的析构函数是 `protected`。**`sql::Driver`、`DatabaseMetaData`、`ResultSetMetaData`、`ParameterMetaData`、`SQLWarning` 的析构都是 protected（分别在 `jdbc/cppconn/driver.h:46`、`jdbc/cppconn/metadata.h:49`、`jdbc/cppconn/resultset_metadata.h:101`、`jdbc/cppconn/parameter_metadata.h:78`、`jdbc/cppconn/warning.h:68`），所以**不能放进 `std::unique_ptr`**——那要求 public 析构。得用裸指针。而且这些 metadata 的 getter **全是非 const**，指针连 `const` 都不能加：

> ⚠️ **`sql::Driver` 那个 protected 析构不是"编译器较真"，是官方明确要求你别 delete 它。**
> 文档原文（`doc/jdbc_ref.txt:44-45`，逐字，9.2.0 与 26.7.0 一致）：
>
> *"However, the driver instance should not be explicitly deleted,
> the connector takes care of freeing it."*
>
> 也就是说 `get_driver_instance()` 返回的对象**归连接器所有**，生命周期是进程级。
> 正确写法是拿裸指针用着、**永远不 delete**（也别交给 `unique_ptr`）：
>
> ```cpp
> sql::Driver* driver = sql::mysql::get_mysql_driver_instance();  // 不 delete
> std::unique_ptr<sql::Connection> con(driver->connect(url, user, pass));
> ```
>
> 顺带说明为什么这五个类的析构都是 protected 而不是 public：它们要么归库管
> （`Driver`、`SQLWarning`），要么是随 `Connection` 一起死的视图对象
> （三个 `*Metadata`）——都不该由调用方单独 delete。


```cpp
// ❌ 编译不过：protected destructor
std::unique_ptr<sql::DatabaseMetaData> meta(con->getMetaData());

// ✅ 裸指针，非 const
sql::DatabaseMetaData* meta = con->getMetaData();
std::cout << meta->getDatabaseProductVersion();
```

**6. 构建树的 `include/mysql/jdbc.h` 不能直接用来编译。**它内部全是 `#include "../jdbc/xxx.h"`（`jdbc.h:30-49`），而那个扁平布局**只有 `make install` 之后才存在**（源码树里这些头在 `jdbc/driver/` 和 `jdbc/cppconn/`）。所以编译 classic 程序必须对着安装前缀：

```bash
make install                     # 库装到 <prefix>/lib64（不是 lib）
g++ -std=c++17 app.cpp -I<prefix>/include -L<prefix>/lib64 -lmysqlcppconn -lmysqlclient
```

> 顺带印证机制一说的 ABI：安装产物是 `libmysqlcppconn.so.10.26.7.0`——JDBC 侧 ABI 主版本 **10**（`version.cmake` 的 `JDBC_ABI_VERSION`），X 侧是 **2**。两个库 soname 不同，可以并存。

---

## 两套栈的完整对照表

| 维度 | **X DevAPI** | **JDBC 风格** |
|---|---|---|
| 头文件 | `<mysqlx/xdevapi.h>` | `<mysql/jdbc.h>` |
| 库 | `libmysqlcppconnx.so.2.26.7.0` | `libmysqlcppconn.so` |
| 构建开关 | 默认开 | `-DWITH_JDBC=ON` |
| 默认端口 | 33060 | 3306 |
| 协议 | X Protocol（protobuf，5 字节帧头） | classic MySQL 协议 |
| 协议实现 | 连接器自己（`cdk/`，vendored protobuf 3.19.6） | 外部 `libmysqlclient` |
| 特性协商 | `Mysqlx.Expect.Open` + 错误码试错 | 32 位 capability 位图 |
| 认证 | MYSQL41 / SHA256_MEMORY / PLAIN / EXTERNAL | libmysqlclient 的全部插件，含 `caching_sha2_password` |
| `caching_sha2_password` | **不支持** | 支持 |
| `ssl-mode` 默认 | `REQUIRED` | `PREFERRED`（libmysqlclient 默认） |
| 连接字符串 | URI + JSON | `tcp://` / `unix://` / `mysql://` / 裸 `host:port`；**不支持 `jdbc:`** |
| 对象模型 | `Session → Schema → Collection → Document` | `Connection → Statement → ResultSet` |
| CRUD | protobuf `Mysqlx.Crud.*` | 普通 SQL 文本 |
| 事务 | 普通 SQL 文本 | 普通 SQL 文本 |
| 结果类型 | 流式 + 预取窗口 | `MYSQL_RES*` 惰性游标 / `MYSQL_BIND` 二进制 |
| 取值 API | `Row::operator[]` → `Value::get<T>()` | `ResultSet::getString/getInt/...`（都是**字符串**） |
| 结果遍历 | `fetchAll()` / `fetchOne()` | `ResultSet::next()` |
| 参数绑定 | **仅 CRUD 语句**（`sql().bind()` 抛 `Too many arguments`） | `PreparedStatement::setXxx()` 全支持 |
| ABI soname | `libmysqlcppconnx.so.2` | `libmysqlcppconn.so.10` |
| 连接池 | ✅ `Session_pool`（默认 25，TTL 10 min） | ❌ 无 |
| 多主机故障转移 | ✅ `Multi_source` + 优先级 + DNS SRV | ✅ 逗号分隔主机列表 + `OPT_MULTI_HOST` |
| 错误模型 | `cdk::Error` / `Mysqlx_exception` | `sql::SQLException` + 5 子类 + SQLSTATE |
| 线程安全 | 池内部有锁 | `get_driver_instance()` 无锁；语句/结果集无锁 |
| 最低服务端 | 8.0+（`doc/usage.txt:43-45`："MySQL Server 8 or later"） | pre-8.0（`:46-47`："earlier than version 8"） |

---

## 动手：构建与最小可运行例子

### 只构建 X DevAPI

> ⚠️ **`make -j4` 本身不够，必须改两个 CMake 文件。** 这一节是本文实测踩得最疼的地方。
>
> **先看现象**：8 核机上 `make -j4`，`loadavg` 依然冲到 **39.96 ~ 50.44**，
> `cc1plus` 进程 82 个。满核 `-j8` 时 43.78。此时 `systemctl` 会排队甚至超时。
>
> **根因不是"子构建忽略 `-j`"，是参数在 CMake 里被拆坏了。**
> `cdk/cmake/dependency.cmake:334-339` 取满核拼成列表：
>
> ```cmake
> ProcessorCount(prc_cnt)
> list(APPEND build_opt --parallel ${prc_cnt})    # 列表: --parallel;8
> ```
>
> 然后 `cdk/cmake/dependency.cmake:357` 传参时**没加引号**：
>
> ```cmake
> -DOPTS=${build_opt}
> ```
>
> 生成的 Makefile 里实际是 `-DOPTS=--parallel 8`——**一个 argv**。于是
> `cdk/cmake/ext/ext-build.cmake:50` 收到的 `OPTS` 只有 `--parallel`，那个 `8`
> 变成游离参数被丢弃。`cmake --build` 拿到**不带数值的 `--parallel`**，按其文档
> 就是"用 native build tool 的默认并发"，对 Make 即**不限并发**：
>
> ```
> gmake[3]: warning: -j0 forced in submake: resetting jobserver mode.
> ```
>
> **光加引号也不行**——`"-DOPTS=--parallel;8"` 里那个 `;` 会被 Make 当命令分隔符，
> 报 `/bin/sh: 1: 8: not found`。而且这四个 `${NAME}-build` 是**无依赖顺序**的
> `add_custom_target`，protobuf / zstd / zlib / lz4 会**同时**起。
>
> **改法**——把并发数当独立标量传，在脚本里自己拼：
>
> ```cmake
> # cdk/cmake/dependency.cmake：删掉拼 build_opt 那两行
>   ProcessorCount(prc_cnt)
>   if(DEFINED WITH_EXT_BUILD_PARALLEL)
>     set(prc_cnt ${WITH_EXT_BUILD_PARALLEL})
>   elseif(prc_cnt AND prc_cnt GREATER 4)
>     set(prc_cnt 4)
>   endif()
>   add_custom_target(${NAME}-build
>     COMMAND ${CMAKE_COMMAND}
>     -DBIN_DIR=${bin_dir} -DCONFIG=$<CONFIG>
>     -DPARALLEL=${prc_cnt}          # ← 独立标量
>     -DOPTS=${OPTS_EXTRA}           # ← 不再塞 --parallel
>     -P ${EXT_DIR}/ext-build.cmake
> ```
>
> ```cmake
> # cdk/cmake/ext/ext-build.cmake：自己拼 --parallel
> set(build_args --build ${BIN_DIR} --config ${CONFIG})
> if(PARALLEL AND NOT CMAKE_VERSION VERSION_LESS 3.12)
>   list(APPEND build_args --parallel ${PARALLEL})
> endif()
> execute_process(COMMAND ${CMAKE_COMMAND} ${build_args} ${OPTS} RESULT_VARIABLE res)
> ```
>
> 然后 `cmake .. -DWITH_EXT_BUILD_PARALLEL=2` + `make -j4`。
>
> **实测对比**（同一台 8 核机、同一份源码）：
>
> | | 顶层 | 外部子构建 | 峰值 loadavg |
> |---|---|---|---|
> | 改之前 | `make -j4` | 不限并发 × 4 个并行 | **39.96 ~ 50.44** |
> | 改之后 | `make -j4` | `--parallel 2` | **7.33** |
>
> > 打了补丁后 `grep -c 'forced in submake'` 仍可能非 0（protobuf 自己内部还有子构建）。
> > **判据看 loadavg，不要看警告计数。**


```bash
tar -xzf mysql-connector-c++-26.7.0-src.tar.gz
cd mysql-connector-c++-26.7.0-src
mkdir build && cd build

# WITH_SSL 决定能不能开 TLS；关掉它，ssl-mode 就只能 DISABLED
# WITH_EXT_BUILD_PARALLEL 需要先打上面那两个补丁，否则不生效
cmake .. -DCMAKE_BUILD_TYPE=Release -DWITH_SSL=ON -DBUILD_STATIC=OFF \
         -DWITH_EXT_BUILD_PARALLEL=2
make -j4
```

产物：`libmysqlcppconnx.so.2.26.7.0`（soname `libmysqlcppconnx.so.2`）。

验证一下"X 侧不依赖 libmysqlclient"：

```bash
ldd libmysqlcppconnx.so.2.26.7.0 | grep -i mysql
# 只有 libmysqlcppconnx 自己 —— 没有 libmysqlclient
```

### 加上 classic 路径

先装 C API 头和库（classic 路径唯一的硬依赖）：

```bash
sudo apt install libmysqlclient-dev      # Debian/Ubuntu；或 default-libmysqlclient-dev
```

再配置。**注意这里不是 `-DWITH_MYSQL=/usr`**——那个写法在 Debian 系上必失败，
原因见[机制十一](#机制十一classic-路径默认不编译还有一堆死代码)：

```bash
cmake .. -DWITH_JDBC=ON -DMYSQL_CONFIG_EXECUTABLE=/usr/bin/mysql_config
make -j4 && make install          # 同样需要上面那两个补丁
```

> ⚠️ 在**银河麒麟 V10 SP1** 上这一步会因 libmysqlclient 版本不够而**编译失败**
> （缺 `mysql_real_connect_dns_srv` 等三个符号）。详见机制十一那节，
> 以及 `demo/README.md` 的实测记录。**X DevAPI 路径不受影响。**

### 编译你的程序

```bash
g++ -std=c++17 demo_a.cpp -o demo_a \
    -I<prefix>/include/mysqlx \
    -L<prefix>/lib -lmysqlcppconnx -lssl -lcrypto
```

**注意这里不需要 `-lzstd -llz4 -lz -lprotobuf-lite`。** 机制一说过它们是 vendored 的——`cdk/protocol/mysqlx/CMakeLists.txt:135-139` 把 `ext::protobuf-lite` / `ext::z` / `ext::lz4` / `ext::zstd` 以 `PRIVATE` 链进静态库 `cdk_proto_mysqlx`，再由 `merge_libraries` 在 `POST_BUILD` 阶段把这些 `.a` 全部折叠进最终的 `.so`。所以它们是**静态吸收**进去的，链接你的程序时根本不用管。

唯一的外部运行时依赖是 OpenSSL（`libssl` + `libcrypto`）。这一点实测可验：

```bash
ldd libmysqlcppconnx.so.2.26.7.0
# 期望：libssl / libcrypto / libstdc++ / libm / libc ...
# 不期望：libprotobuf-lite / libzstd / liblz4 / libmysqlclient
```

classic 那边（注意 **lib64**，且必须先 `make install`——见机制十一第 6 点）：

```bash
g++ -std=c++17 demo_b.cpp -o demo_b \
    -I<prefix>/include \
    -L<prefix>/lib64 -lmysqlcppconn -lmysqlclient
```

> **本文配套两个可直接运行的 CRUD demo**（增删改查全流程，含实测输出与踩坑记录）：
> `demo/demo_xdevapi_crud.cpp` 和 `demo/demo_jdbc_crud.cpp`，
> 说明见同目录 `README.md`。两者都在真实 MySQL 8.0.46 上验证过 `EXIT=0`。

### 如果你的项目用 CMake

别手写 `-I`/`-L`，包文件已经把 target 备好了（`mysql-concpp-config.cmake.in:38-44`）：

```cmake
find_package(mysql-concpp REQUIRED)

target_link_libraries(my-xdevapi-app  mysql::concpp)          # X DevAPI
target_link_libraries(my-classic-app  mysql::concpp-jdbc)     # classic API
```

别名关系：`mysql::concpp` = `mysql::concpp-xdevapi`，`mysql::concpp-static` = `mysql::concpp-xdevapi-static`（`mysql-concpp-config.cmake.in:43-44`）。

注意 `concpp-jdbc-static` 会让 `libmysqlclient` 变成**传递依赖**（`:123`）——这正是机制十里"classic 路径把协议全部外包"的必然结果。

> 官方文档还提醒：`<mysql/jdbc.h>` 这个头是 **8.0.16** 才有的（`doc/usage.txt:60`）。更早的版本要 include 一堆分散的头。这个坑只影响从很老的版本升上来的人。

### 离线环境（银河麒麟 V10 SP1 / 内网）：JDBC 路径要准备什么

如果你在内网、且用 **classic（JDBC）路径**，那么"导入依赖包"这件事有个明确的最小集。**关键认知：JDBC 路径唯一真正外部的依赖是 `libmysqlclient`**，其余全是系统库。

JDBC 路径的运行时依赖（从 `jdbc/driver/CMakeLists.txt:203-222` 反推）：

| 库 | 来自 | 是否必需 |
|---|---|---|
| `libmysqlclient.so` | `libmysqlclient-dev` / `libmysqlclient21` | **必需**（唯一硬依赖） |
| `libssl.so` / `libcrypto.so` | `libssl-dev` / `libssl1.1` | 必需（`resolv`/`dl`/`pthread` 属 libc） |
| `libz.so` | `zlib1g-dev` | 必需 |
| `mysql.h`、`errmsg.h`、`mysqld_error.h` | `libmysqlclient-dev` | **编译必需** |

而 **X DevAPI 路径不需要 `libmysqlclient`**（机制一已证），它需要的是 OpenSSL + 一个 C++17 编译器；protobuf / zstd / lz4 / rapidjson 全部 vendored 在 `cdk/extra/` 里，会被静态合进产物。

所以两条路径的离线准备清单是**不一样**的，别混：

```
X DevAPI 离线清单          classic 离线清单
─────────────────         ─────────────────
gcc/g++ ≥ 9 (C++17)       gcc/g++ ≥ 9
cmake ≥ 3.16              cmake ≥ 3.16
libssl-dev + libssl1.1     libssl-dev + libssl1.1
（无 libmysqlclient）       zlib1g-dev
                           libmysqlclient-dev   ← 关键，就这一个
                           libmysqlclient21
                           mysql-common
```

**最容易踩的坑：别去凑 Connector/C++ 的 deb，用源码编。** 官方 deb 是针对 Ubuntu jammy/noble 之类构建的，glibc 需求会高于国产发行版（Kylin V10 SP1 是 glibc 2.31，jammy 是 2.35）。硬装会在 `ldd` 阶段报 `GLIBC_2.34 not found`，而且这种错很难一眼看出根因。用 `mysql-connector-c++-26.7.0-src.tar.gz` 在目标机上现编，产物天然匹配它的 glibc。

**第二个坑：`libssl-dev` 无法被关掉。** 你可能以为 `-DWITH_SSL=OFF` 就不需要 OpenSSL 了——**不是**：

```cmake
# CMakeLists.txt:348-351
# Note: Find OpenSSL early because it is needed by both CDK and JDBC (in case
# of static linking with the client library)
find_dependency(SSL)          # ← 无条件，不受 WITH_SSL 保护
```

`cdk/CMakeLists.txt:96` 还有一次。所以即使 `WITH_SSL=OFF`，缺 `libssl-dev` 也会在 configure 阶段直接失败：

```
CMake Error at cdk/cmake/DepFindSSL.cmake:76 (message):
  Cannot find appropriate system libraries for SSL. ...
```

**第三个坑：configure 会拿 `SHA512_DIGEST_LENGTH` 探测 OpenSSL 版本**（`cdk/cmake/DepFindSSL.cmake:96-101`）：

```cmake
CHECK_SYMBOL_EXISTS(SHA512_DIGEST_LENGTH "openssl/sha.h" HAVE_SHA512_DIGEST_LENGTH)
if(NOT HAVE_SHA512_DIGEST_LENGTH)
  message(SEND_ERROR "Could not find SHA512_DIGEST_LENGTH symbol in sha.h header of OpenSSL library")
endif()
```

这个宏**确实存在于 OpenSSL 1.1.1**（OpenSSL 自带头文件 `openssl/sha.h:71`），所以麒麟 V10 SP1 自带的 OpenSSL 1.1.1 能过——**但只有当头文件装对位置时**。`CHECK_SYMBOL_EXISTS` 只加一个 include 目录（`CMAKE_REQUIRED_INCLUDES`），而 Debian 系把 `opensslconf.h` 放在 multiarch 路径下（`/usr/include/x86_64-linux-gnu/openssl/opensslconf.h`），所以手工指定 `OPENSSL_INCLUDE_DIR` 时**必须把两个目录都带上**，否则会误报成"OpenSSL 版本不支持"：

```bash
# ❌ 少了 multiarch 那一段，会误报 SHA512_DIGEST_LENGTH 找不到
-DOPENSSL_INCLUDE_DIR=/usr/include

# ✅ 正常情况直接 dpkg -i 装 libssl-dev 即可，不需要手工指定
-DOPENSSL_INCLUDE_DIR="/usr/include;/usr/include/x86_64-linux-gnu"
```

正常路径下 `dpkg -i libssl-dev*.deb` 就够了——`FindOpenSSL` 自己会处理 multiarch 目录。上面那行只是在你必须手工指路时的写法。

> **本文的构建步骤已实测**：`cmake -DWITH_SSL=ON` 在 OpenSSL 1.1.1 下 configure 通过（`-- Configuring done`），`make` 编出 174 个目标文件与全部四个 vendored 静态库（`libprotobuf-lite.a` / `liblz4.a` / `libzlib.a` / `libzstd.a`）。这四条印证了机制一那句"X 侧不依赖 libmysqlclient"——protobuf 是源码树里编出来的。

**`libmysqlclient` 的版本怎么选？** 26.7.0 的 `jdbc/driver/mysql_connection_options.h:44` 用 `MYCPPCONN_STATIC_MYSQL_VERSION_ID >= 80000` 分叉出两套枚举。`libmysqlclient` 8.0.x 走 `>= 8.0` 分支，是当前唯一稳妥的选择。

还有一个很贴心的细节——**绑定函数按 libmysqlclient 版本在编译期二选一**（`jdbc/driver/nativeapi/libmysql_static_proxy.cpp:525-535`）：

```cpp
my_bool LibmysqlStaticProxy::stmt_bind_named_param(MYSQL_STMT* stmt, MYSQL_BIND* bind,
                                                  unsigned n_params, const char** names)
{
#if MYSQL_VERSION_ID >= 80300
  return ::mysql_stmt_bind_named_param(stmt, bind, n_params, names);
#else
  throw ::sql::MethodNotImplementedException("::mysql_stmt_bind_named_param()");
#endif
}
```

也就是说：**对这一类符号，用老 libmysqlclient 编不会失败**——`mysql_stmt_bind_named_param`（8.3 才有的符号）被 `#if` 挡住了，运行时抛 `MethodNotImplementedException`，上层 `mysql_prepared_statement.cpp` 的 try/catch 自动回退到 `mysql_stmt_bind_param()`。反过来 8.4+ 删掉了 `mysql_stmt_bind_param`，同一个 `#if` 的另一侧（`libmysql_static_proxy.cpp:537-545`）也在处理。

这意味着**对这一类符号**，你在离线机上把 libmysqlclient 从 8.0 换到 8.4/9.x，Connector/C++ 侧不需要重新编译——两个方向的退路都写好了。前提是你用**源码编** Connector/C++（因为 `MYSQL_VERSION_ID` 是编译期宏）。

⚠️ **但别把它推广到所有符号。** 另一类调用**没有**这种守卫（`libmysql_static_proxy.cpp:376/427/438`），老版本直接编不过——所以 8.0.19 编 26.7.0 整体仍然是失败的，见上一节。**判据是"这个调用点外面有没有 `#if MYSQL_VERSION_ID`"，不是"这个函数名里有没有 bind"。**

<!-- BEGIN INLINE DEMO: main -->
### 实测踩到的 22 个坑

下面两个 demo 是**编译 + 实际连库跑通**的（MySQL 8.0.46，X 协议 13360 / classic 13306，
`EXIT=0`）。过程中撞到的坑一并列在这里——大部分是"照着文档想当然写就会错"的。

#### X DevAPI

| # | 坑 | 正解 |
|---|---|---|
| 1 | `Value` 没有 `as<T>()` | 用 `row[0].get<T>()`。`get_string()` 在**不可继承**的基类 `common::Value` 上（`include/mysqlx/devapi/document.h:227-229` 是 `protected` 继承），外部根本调不到 |
| 2 | `SqlResult` 没有 `rows()` | 用 `fetchAll()` / `fetchOne()`；它本身也有 `begin()/end()`（`include/mysqlx/devapi/result.h:684`/`692`），可直接 range-for |
| 3 | `SessionSettings` 没有默认构造 | 用 `SessionSettings(host, port, user, pwd, db)`（`include/mysqlx/devapi/settings.h:540`） |
| 4 | 枚举名不是 `SSL_mode` | 顶层 `enum class SSLMode`（`include/mysqlx/devapi/settings.h:226`），`SessionOption::SSLMode` 只是别名；选项名要写全 `SessionOption::SSL_MODE` |
| 5 | `Table::insert().values(Row{...})` → `Column count doesn't match value count` | Table API 此时不知道列定义，必须具名列：`insert("name","age","city").values("dave",28,"chengdu")` |
| 6 | `Table::modify()` 不存在 | 叫 `Table::update()` |
| 7 | `Table::update()` / `remove()` 不收条件 | 参数一律 `.where(expr)`；且 `set()` 返回 `TableUpdate&`、`where()` 返回终结的 `Operation&`，**必须先 set 再 where** |
| 8 | **`sql().bind(...)` 抛 `Too many arguments`** | raw SQL 不支持参数绑定（`:name` 和 `:1` 都不行）。绑定只在 CRUD 语句上 |
| 9 | ⚠️ **`execute()` 后再链 `fetchAll()` → 段错误** | `for (Row r : stmt.execute())` ✅（range-for 延长临时对象）<br>`for (Row r : stmt.execute().fetchAll())` ❌ **崩**——`fetchAll()` 的 holder 引用临时 Result **内部**，而 range-for 只延长最外层<br>`auto res = stmt.execute(); …res.fetchAll()` ✅ |
| 10 | ⚠️ **Table 链式调用一条写完 → 段错误** | `TableSelect` 要存具名变量；`orderBy()` 返回**新 wrapper 对象**，必须**按值**持有 |

> 坑 9/10 是 gdb 复现的段错误，栈顶都是 `common::Result_impl::get_row()`。

#### classic / JDBC

| # | 坑 | 正解 |
|---|---|---|
| 11 | `ResultSet::getColumnLabel()` 不存在 | 在 `ResultSetMetaData` 上：`rs->getMetaData()->getColumnLabel(i)` |
| 12 | `sql::Driver` / `DatabaseMetaData` / `ResultSetMetaData` / `ParameterMetaData` / `SQLWarning` **析构是 protected** | 不能放进 `std::unique_ptr`（那要求 public 析构），用裸指针 |
| 13 | 这些 metadata 的 getter **全非 const** | 指针连 `const` 都不能加 |
| 14 | `driver` 忘了赋值 → 段错误 | `driver = sql::mysql::get_mysql_driver_instance();` |

#### 构建 / 离线

| # | 坑 | 正解 |
|---|---|---|
| 15 | **`-DWITH_MYSQL=/usr` 必失败** | `DepFindMySQL.cmake:134` 要求 `${MYSQL_INCLUDE_DIR}/mysql.h` **直接存在**；发行版装在 `/usr/include/mysql/mysql.h`。用 `-DMYSQL_INCLUDE_DIR=/usr/include/mysql` |
| 16 | **不能用构建树的 `include/mysql/jdbc.h`** | 它内部是 `#include "../jdbc/xxx.h"`，那个扁平布局只有 `make install` 后才存在。库装在 **`lib64`** 不是 `lib` |
| 17 | `mysql.h` 需要**两个** include 目录 | `<mysql.h>` 要 `include/mysql`；`mysql_com.h` 里 `#include <mysql/udf_registration_types.h>` 要 `include`。真实装机 `/usr/include` 隐式在路径里，只有自定义前缀才撞上 |
| 18 | configure 会**编译并运行**探针取版本 | `DepFindMySQL.cmake:396-453` 的 `try_run`。`.so` 不在 `LD_LIBRARY_PATH` 就失败（`Could not determine the MySQL client library version.`）。**用 `-DMYSQL_CONFIG_EXECUTABLE=<mysql_config>` 一步绕过**（它直接跑 `mysql_config --version`，`DepFindMySQL.cmake:509`），或 `-DMYSQL_VERSION=<ver>` 手动指定 |
| 19 | **X DevAPI 编译要加构建树的头路径** | `version_info.h` 是生成的，`-I<build>/include/mysqlx` 必需，源码树里没有 |
| 20 | 手工给 `MYSQL_INCLUDE_DIR` 容易给错 | 优先 `-DMYSQL_CONFIG_EXECUTABLE=<mysql_config>`：一次填好 `MYSQL_INCLUDE_DIR`/`MYSQL_LIB_DIR`/`MYSQL_VERSION`/`MYSQL_VERSION_ID`，且路径跟着安装位置走（relocatable 目录也实测可用） |
| 21 | **`make -j4` 挡不住 vendored 子构建** | `cdk/cmake/dependency.cmake:357` 的 `-DOPTS=${build_opt}` 没加引号，列表被空格并成**一个 argv**，`ext-build.cmake:50` 只收到 `--parallel`，数值变游离 argv → 裸 `--parallel` = **不限并发**。加引号也不行（`;` 被 Make 当命令分隔符，报 `/bin/sh: 1: 8: not found`）。改法：改成传 `-DPARALLEL=<n>` 标量，在 `ext-build.cmake` 里 `list(APPEND build_args --parallel ${PARALLEL})`。实测 loadavg **50 → 7.3** |
| 22 | **classic 要 libmysqlclient ≥ 8.0.42**（真麒麟实测） | `libmysql_static_proxy.cpp:376/427/438` 无版本保护地调 `mysql_plugin_get_option`（在 `client_plugin.h`）/ `mysql_real_connect_dns_srv` / `mysql_bind_param`。**麒麟自带源只有 8.0.26，缺 `mysql_plugin_get_option` → `make exit=2`**；focal-updates 的 8.0.42 三个齐全且只要 `libc6>=2.28`+`libssl1.1` → 麒麟容器内 `exit=0`+demo `exit=0`。8.0.46 不行（`libc6>=2.34`+`libssl3`）。**判据是编译不是 grep**（`mysql_plugin_get_option` 不在 `mysql.h` 里）；`nm -D` 输出带 `@@libmysqlclient_21.0` 后缀，按裸名精确匹配会误判成"缺失" |

### 完整 demo：X DevAPI

下面的代码就是 `demo/demo_xdevapi_crud.cpp` 的全文
（编译运行均验证过）。它同时演示两种写法：普通 SQL，以及走 `Mysqlx.Crud.*`
protobuf 的 Table API——后者**不经过 SQL 文本**，和机制九讲的是一回事。

```cpp
// demo_xdevapi_crud.cpp —— X DevAPI 的完整 CRUD
//
// 演示：连接 -> 建表 -> 新增(add) -> 查询(search) -> 修改(modify) -> 删除(delete)
//
// 编译（注意只需要 2 个 -l，protobuf/zstd/lz4 是静态合进 .so 的）：
//   g++ -std=c++17 demo_xdevapi_crud.cpp -o demo_x \
//       -I<build>/include/mysqlx -I<src>/include/mysqlx -I<src>/include \
//       -L<build> -lmysqlcppconnx -lssl -lcrypto
//
//   第一个 -I 是必需的：version_info.h 是构建时生成的，只在构建树里。
//
// 运行：
//   ./demo_x 127.0.0.1 33060 xuser 'Xuser#Pass1' demo
//
// 两个容易踩的点：
//   1. 端口是 33060（X 协议），不是 3306。
//   2. X DevAPI **不支持 caching_sha2_password**。裸 TCP 下账号必须用
//      mysql_native_password，否则报 "Authentication failed using
//      MYSQL41 and SHA256_MEMORY"。开 TLS 可以绕开（走 PLAIN 机制）。
//
// API 备注（都是实际编译验证过的）：
//   - SessionSettings 没有默认构造函数，必须用带参构造
//   - 取值用 Row::operator[](pos) -> Value，再 .get<T>()，**没有 as<T>()**
//   - 结果集遍历用 fetchAll() / fetchOne()，**没有 rows()**
//   - Table::remove() 不收条件，要链 .where(expr)
//   - Table 的改方法叫 update()（不是 modify()），且**不收条件**，要链 .where(expr)
//   - fetchAll() 的返回类型是 internal 里的 RowList，别在签名里写它，用 auto
//   - ⚠️ for (Row r : stmt.execute())            ✅ 安全（range-for 会延长临时对象）
//     for (Row r : stmt.execute().fetchAll())   ❌ 段错误（fetchAll 返回的 holder
//                                                 引用的是临时 Result 的内部对象，
//                                                 而 range-for 只延长最外层临时）
//     auto res = stmt.execute(); for (Row r : res.fetchAll())   ✅ 安全
//   - sql().bind(...) 不支持（抛 "Too many arguments"），绑定只在 CRUD 语句上
//   - Table::insert() 走 .values(Row{...}) 会报 "Column count doesn't match",
//     要用 insert("col1","col2",...).values(v1, v2, ...) 的具名列形式

#include <mysqlx/xdevapi.h>

#include <iostream>
#include <string>

using namespace mysqlx;

namespace {

template <typename Rows>
void print_rows(Rows rows) {   // 按值收：fetchAll() 返回的 List_initializer 不能绑定到 const&
  for (const Row& row : rows) {
    std::cout << "  " << row[0].get<uint64_t>() << " | "
              << row[1].get<std::string>() << " | " << row[2].get<int64_t>()
              << " | " << row[3].get<std::string>() << "\n";
  }
}

void print_header() {
  std::cout << "  id | name | age | city\n";
}

}  // namespace

int main(int argc, char** argv) {
  const std::string host = (argc > 1) ? argv[1] : "127.0.0.1";
  const unsigned port = (argc > 2) ? std::stoul(argv[2]) : 33060;
  const std::string user = (argc > 3) ? argv[3] : "root";
  const std::string pass = (argc > 4) ? argv[4] : "";
  const std::string db = (argc > 5) ? argv[5] : "demo";

  try {
    // ============ 1. 连接 ============
    // ssl-mode 默认是 REQUIRED（不是 PREFERRED）。这里显式设 DISABLED
    // 以便本地明文测试；生产请用 SSLMode::VERIFY_CA + SessionOption::SSL_CA。
    SessionSettings opt(host, port, user, pass, db);
    opt.set(SessionOption::SSL_MODE, SSLMode::DISABLED);

    Session session(opt);
    std::cout << "== 连接成功 ==\n";
    std::cout << "  server: "
              << session.sql("SELECT VERSION()").execute().fetchOne()[0].get<std::string>()
              << "\n\n";

    // ============ 2. 建表 ============
    session.sql("DROP TABLE IF EXISTS person").execute();
    session.sql(
        "CREATE TABLE person ("
        "  id   INT PRIMARY KEY AUTO_INCREMENT,"
        "  name VARCHAR(64) NOT NULL,"
        "  age  INT,"
        "  city VARCHAR(64)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4")
        .execute();
    std::cout << "== 建表 person ==\n\n";

    // ============ 3. 新增 (add) ============
    std::cout << "== 新增 (add) ==\n";
    // 3a. 普通 SQL 批量插入
    session.sql(
        "INSERT INTO person(name, age, city) VALUES"
        "('alice', 30, 'beijing'),"
        "('bob', 25, 'shanghai'),"
        "('carol', 35, 'guangzhou')")
        .execute();
    std::cout << "  +3 rows via SQL\n";

    // 3b. Table API —— 发的是 Mysqlx.Crud.Insert(msg id 18)，不是 SQL
    Table table = session.getSchema(db).getTable("person");
    // 注意：必须显式给列名。直接 .values(Row{...}) 走的是"按位置"形式，
    // 而 Table API 此时并不知道表的列定义，会报
    // "Column count doesn't match value count"。
    table.insert("name", "age", "city")
        .values("dave", 28, "chengdu")
        .execute();
    std::cout << "  +1 row  via Mysqlx.Crud.Insert\n\n";

    // ============ 4. 查询 (search) ============
    // 4a. 全表
    {
      std::cout << "== 查询 (search) 全表 ==\n";
      print_header();
      // for (auto row : stmt.execute()) 是安全的 —— range-for 会延长 execute()
      // 返回的临时 SqlResult。但**不能**再链 .fetchAll()，那个 holder 引用的是
      // 临时对象内部，临时一析构就悬垂（实测段错误）。
      print_rows(session.sql("SELECT id, name, age, city FROM person ORDER BY id")
                     .execute());
      std::cout << "\n";
    }

    // 4b. 命名参数绑定（占位符 :min_age），不拼字符串
    //
    // ⚠️ 重要：sql().bind(...) 在 X DevAPI 里**不可用**，会抛
    //    "CDK Error: Too many arguments"（无论 :name 还是 :1 形式）。
    //    参数绑定只在 CRUD 语句（Table/Collection 的 select/find/update/
    //    remove）上支持。所以下面用 Table::select 演示绑定。
    {
      std::cout << "== 查询 age > 26（Table::select + :min_age 绑定）==\n";
      // ⚠️ 必须把 TableSelect 存进具名变量再链式调用。
      //    写成一条链  table.select(...).where(...).orderBy(...).bind(...)
      //    在 26.7.0 上会 **段错误**（where() 返回的是指向临时对象的
      //    Operation&，orderBy() 又包一层临时 wrapper，临时对象析构后悬垂）。
      //    这是实测复现的，不是理论问题。
      //    安全写法：**每一步都存成具名变量**，尤其 orderBy() 要按值持有
      //    （它返回的是一个新的 wrapper 类型，不是引用）。
      TableSelect sel = table.select("id", "name", "age", "city");
      auto& filtered = sel.where("age > :min_age");
      auto ordered = filtered.orderBy("age");        // 必须按值存
      auto& bound = ordered.bind("min_age", 26);
      //    execute() 的返回值也必须存成具名变量：fetchAll() 返回的是
      //    **持有 Result 引用的 List_initializer**，直接写进 range-for
      //    会让 Result 临时对象提前析构 → get_row() 段错误。
      RowResult res = bound.execute();
      for (const Row& row : res.fetchAll()) {
        std::cout << "  " << row[0].get<uint64_t>() << " | "
                  << row[1].get<std::string>() << " | "
                  << row[2].get<int64_t>() << " | " << row[3].get<std::string>()
                  << "\n";
      }
      std::cout << "\n";
    }

    // 4c. 单行 + 聚合
    {
      SqlResult agg =
          session.sql("SELECT COUNT(*) AS n, AVG(age) AS a FROM person").execute();
      Row r = agg.fetchOne();
      std::cout << "== 统计 ==\n";
      std::cout << "  count   : " << r[0].get<uint64_t>() << "\n";
      std::cout << "  avg_age : " << r[1].get<double>() << "\n\n";
    }

    // ============ 5. 修改 (modify) ============
    std::cout << "== 修改 (modify) ==\n";
    // 5a. SQL UPDATE
    session.sql("UPDATE person SET age = 31 WHERE name = 'alice'").execute();
    std::cout << "  alice.age -> 31            (SQL UPDATE)\n";
    session.sql("UPDATE person SET city = 'shenzhen' WHERE age < 30").execute();
    std::cout << "  city(age<30) -> shenzhen  (SQL UPDATE)\n";

    // 5b. Table API —— Mysqlx.Crud.Update(msg id 19)
    // 注意顺序：set() 返回 TableUpdate&，where() 返回终结的 Operation&，
    // 所以必须先 set 再 where，反过来就编译不过。
    table.update().set("city", "hangzhou").where("name = 'bob'").execute();
    std::cout << "  bob.city -> hangzhou      (Mysqlx.Crud.Update)\n\n";

    // 5c. 验证
    {
      std::cout << "== 修改后 ==\n";
      print_header();
      // for (auto row : stmt.execute()) 是安全的 —— range-for 会延长 execute()
      // 返回的临时 SqlResult。但**不能**再链 .fetchAll()，那个 holder 引用的是
      // 临时对象内部，临时一析构就悬垂（实测段错误）。
      print_rows(session.sql("SELECT id, name, age, city FROM person ORDER BY id")
                     .execute());
      std::cout << "\n";
    }

    // ============ 6. 删除 (delete) ============
    std::cout << "== 删除 (delete) ==\n";
    session.sql("DELETE FROM person WHERE name = 'carol'").execute();
    std::cout << "  - carol (SQL DELETE)\n";
    // Table API —— Mysqlx.Crud.Delete(msg id 20)
    table.remove().where("name = 'dave'").execute();
    std::cout << "  - dave  (Mysqlx.Crud.Delete)\n\n";

    {
      std::cout << "== 删除后 ==\n";
      SqlResult left =
          session.sql("SELECT name FROM person ORDER BY id").execute();
      for (const Row& row : left.fetchAll()) {
        std::cout << "  " << row[0].get<std::string>() << "\n";
      }
      std::cout << "\n";
    }

    // ============ 7. 清理 ============
    session.sql("DROP TABLE person").execute();
    session.close();
    std::cout << "== 全部完成 ==\n";
    return 0;

  } catch (const Error& e) {
    std::cerr << "X DevAPI 错误: " << e << "\n";
    return 1;
  } catch (const std::exception& e) {
    std::cerr << "标准异常: " << e.what() << "\n";
    return 1;
  }
}
```

### 完整 demo：classic / JDBC

对应 `demo/demo_jdbc_crud.cpp`，端口是 **3306** 而非 33060。

```cpp
// demo_jdbc_crud.cpp —— classic (JDBC 风格) API 的完整 CRUD
//
// 演示：连接 -> 建表 -> 新增(add) -> 查询(search) -> 修改(modify) -> 删除(delete)
// 依赖：libmysqlcppconn.so + libmysqlclient.so
//
// 编译（注意：库在 lib64 不是 lib；且必须先 make install —— 原因见 README 坑 16）：
//   g++ -std=c++17 demo_jdbc_crud.cpp -o demo_jdbc \
//       -I<prefix>/include -I<prefix>/include/mysql \
//       -L<prefix>/lib64 -lmysqlcppconn -lmysqlclient
//
// 运行：
//   ./demo_jdbc 127.0.0.1 13306 sha2user 'Sha2#Pass1' demo
//
// 注意端口：classic 协议走 3306（X 协议才是 33060）。

#include <mysql/jdbc.h>

#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>

namespace {

// ---- 小工具：把一行按 | 分隔打印出来 --------------------------------------
void print_row(sql::ResultSet* rs) {
  const auto cols = rs->getMetaData()->getColumnCount();
  std::cout << "  ";
  for (uint32_t i = 1; i <= cols; ++i) {
    std::cout << (i > 1 ? " | " : "") << rs->getString(i);
  }
  std::cout << "\n";
}

// 注意：列名/标签在 **ResultSetMetaData** 上，不在 ResultSet 上。
// sql::ResultSet 没有 getColumnLabel()。
void print_header(sql::ResultSet* rs) {
  // 同样不能 unique_ptr：sql::ResultSetMetaData 析构也是 protected，
  // 且它的 getter 都非 const，所以这里也不能声明成 const 指针。
  sql::ResultSetMetaData* md = rs->getMetaData();
  const auto cols = md->getColumnCount();
  std::cout << "  ";
  for (uint32_t i = 1; i <= cols; ++i) {
    std::cout << (i > 1 ? " | " : "") << md->getColumnLabel(i);
  }
  std::cout << "\n";
}

}  // namespace

int main(int argc, char** argv) {
  const std::string host = (argc > 1) ? argv[1] : "127.0.0.1";
  const std::string port = (argc > 2) ? argv[2] : "3306";
  const std::string user = (argc > 3) ? argv[3] : "root";
  const std::string pass = (argc > 4) ? argv[4] : "";
  const std::string db   = (argc > 5) ? argv[5] : "demo";

  // classic 路径的 URL 用 tcp://，**不要写 jdbc: 前缀**（不支持）
  const std::string url = "tcp://" + host + ":" + port;

  // sql::Driver 和 sql::DatabaseMetaData 的析构函数是 **protected**，
  // 所以不能放进 std::unique_ptr（那会要求 public 析构）。
  // Driver 由 get_driver_instance() 返回、生命周期归库管，不用管；
  // DatabaseMetaData 等也用裸指针。
  sql::Driver* driver = nullptr;
  std::unique_ptr<sql::Connection> con;
  std::unique_ptr<sql::Statement> stmt;

  try {
    // ============ 1. 连接 ============
    // get_driver_instance() 不是线程安全的，在 main 里取一次即可
    driver = sql::mysql::get_mysql_driver_instance();
    con.reset(driver->connect(url, user, pass));
    con->setSchema(db);

    std::cout << "== 连接成功 ==\n";
    {
      // 非 const 指针：getDatabaseProductVersion() 等 getter 都非 const
      sql::DatabaseMetaData* meta = con->getMetaData();
      std::cout << "  server  : " << meta->getDatabaseProductVersion() << "\n";
      std::cout << "  driver  : " << meta->getDriverVersion() << "\n";
    }
    std::cout << "  schema  : " << con->getSchema() << "\n\n";

    stmt.reset(con->createStatement());

    // ============ 2. 建表 ============
    stmt->execute("DROP TABLE IF EXISTS person");
    stmt->execute(
        "CREATE TABLE person ("
        "  id   INT PRIMARY KEY AUTO_INCREMENT,"
        "  name VARCHAR(64) NOT NULL,"
        "  age  INT,"
        "  city VARCHAR(64)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4");
    std::cout << "== 建表 person ==\n\n";

    // ============ 3. 新增 (add) ============
    // 用 PreparedStatement，避免拼字符串
    {
      std::unique_ptr<sql::PreparedStatement> ps(
          con->prepareStatement(
              "INSERT INTO person(name, age, city) VALUES(?, ?, ?)"));
      ps->setString(1, "alice");
      ps->setInt(2, 30);
      ps->setString(3, "beijing");
      std::cout << "== 新增 (add) ==\n";
      std::cout << "  inserted rows: " << ps->executeUpdate() << "\n";

      ps->setString(1, "bob");
      ps->setInt(2, 25);
      ps->setString(3, "shanghai");
      std::cout << "  inserted rows: " << ps->executeUpdate() << "\n";

      ps->setString(1, "carol");
      ps->setInt(2, 35);
      ps->setString(3, "guangzhou");
      std::cout << "  inserted rows: " << ps->executeUpdate() << "\n\n";
    }

    // ============ 4. 查询 (search) ============
    // 4a. 全表
    {
      std::unique_ptr<sql::ResultSet> rs(stmt->executeQuery(
          "SELECT id, name, age, city FROM person ORDER BY id"));
      std::cout << "== 查询 (search) 全表 ==\n";
      print_header(rs.get());
      while (rs->next()) print_row(rs.get());
      std::cout << "\n";
    }

    // 4b. 条件查询
    {
      std::unique_ptr<sql::PreparedStatement> ps(
          con->prepareStatement(
              "SELECT name, age FROM person WHERE age > ? ORDER BY age"));
      ps->setInt(1, 26);
      std::unique_ptr<sql::ResultSet> rs(ps->executeQuery());
      std::cout << "== 查询 age > 26 ==\n";
      print_header(rs.get());
      while (rs->next()) print_row(rs.get());
      std::cout << "\n";
    }

    // 4c. 统计
    {
      std::unique_ptr<sql::ResultSet> rs(
          stmt->executeQuery("SELECT COUNT(*) AS n, AVG(age) AS avg_age FROM person"));
      rs->next();
      std::cout << "== 统计 ==\n";
      std::cout << "  count   : " << rs->getInt("n") << "\n";
      std::cout << "  avg_age : " << rs->getDouble("avg_age") << "\n\n";
    }

    // ============ 5. 修改 (modify) ============
    // 5a. PreparedStatement UPDATE（可重复执行）
    {
      std::unique_ptr<sql::PreparedStatement> ps(
          con->prepareStatement("UPDATE person SET age = ? WHERE name = ?"));
      ps->setInt(1, 31);
      ps->setString(2, "alice");
      const int n = ps->executeUpdate();
      std::cout << "== 修改 (modify) alice.age -> 31 ==\n";
      std::cout << "  updated rows: " << n << "\n\n";
    }

    // 5b. Statement UPDATE
    {
      const int n = stmt->executeUpdate(
          "UPDATE person SET city = 'shenzhen' WHERE age < 30");
      std::cout << "== 修改 city (age<30) -> shenzhen ==\n";
      std::cout << "  updated rows: " << n << "\n\n";
    }

    // 5c. 验证修改结果
    {
      std::unique_ptr<sql::ResultSet> rs(
          stmt->executeQuery("SELECT name, age, city FROM person ORDER BY id"));
      std::cout << "== 修改后 ==\n";
      print_header(rs.get());
      while (rs->next()) print_row(rs.get());
      std::cout << "\n";
    }

    // ============ 6. 删除 (delete) ============
    {
      std::unique_ptr<sql::PreparedStatement> ps(
          con->prepareStatement("DELETE FROM person WHERE name = ?"));
      ps->setString(1, "carol");
      const int n = ps->executeUpdate();
      std::cout << "== 删除 (delete) carol ==\n";
      std::cout << "  deleted rows: " << n << "\n\n";
    }

    {
      std::unique_ptr<sql::ResultSet> rs(
          stmt->executeQuery("SELECT name FROM person ORDER BY id"));
      std::cout << "== 删除后 ==\n";
      while (rs->next()) std::cout << "  " << rs->getString(1) << "\n";
      std::cout << "\n";
    }

    // ============ 7. 清理 ============
    stmt->execute("DROP TABLE person");
    con->close();
    std::cout << "== 全部完成 ==\n";
    return 0;

  } catch (const sql::SQLException& e) {
    // SQLException 带 SQLSTATE 与厂商错误码，来自 mysql_error/sqlstate/errno
    std::cerr << "SQL 错误: " << e.what() << "\n"
              << "  SQLSTATE: " << e.getSQLState() << "\n"
              << "  errno   : " << e.getErrorCode() << "\n";
    return 1;
  } catch (const std::exception& e) {
    std::cerr << "标准异常: " << e.what() << "\n";
    return 1;
  }
}
```

<!-- END INLINE DEMO: main -->
### 选型决策

| 你的情况 | 选 | 理由 |
|---|---|---|
| 新项目、MySQL 8+、能开 TLS | **X DevAPI** | 自带连接池、多主机故障转移、文档模型 |
| 需要 `caching_sha2_password` over 裸 TCP | **classic** | X DevAPI 没实现（机制五） |
| 要兼容 JDBC 风格的老代码 | **classic** | 唯一选择 |
| 已有大量 `sql::ResultSet` 字符串处理代码 | **classic** | X DevAPI 是流式 + 类型化结果，迁移成本高 |
| 要 `SELECT` 以外的任意 SQL | 两边都行 | X 的 `sql()` 走 `StmtExecute`，和 CRUD 独立 |
| 只要读写关系表、不用文档模型 | **classic** 或 X 的 `Table` API | X 的 `Table` 模式（`data_model=TABLE`）不为 SQL 让路 |

一句话判断：**如果你在 MySQL 8 上遇到一个奇怪的认证失败，先问自己是不是选了 X DevAPI。**

---

## 版本台账（防腐剂）

这篇文章的结论全部锚定在具体版本号上。换版本时按下表重新校准：

| 事实 | 依据 | 怎么复核 |
|---|---|---|
| Connector 版本 26.7.0 | `version.cmake:37-39` | `cat version.cmake \| grep CONCPP_VERSION_MAJOR` |
| ABI 版本 2.1，soname 主版本 2 | `version.cmake:85-90`；`CMakeLists.txt:576-579` | `ls -l libmysqlcppconnx.so*` |
| `WITH_JDBC` 默认 OFF | `CMakeLists.txt:389-391` | `grep -rn "WITH_JDBC" CMakeLists.txt` |
| 库名 `mysqlcppconnx` | `install_layout.cmake:218-219` | `grep -n LIB_NAME_BASE install_layout.cmake` |
| X 协议端口 33060 | `include/mysqlx/common_constants.h:37` | `grep -rn DEFAULT_MYSQLX_PORT` |
| 帧头 5 字节 | `cdk/protocol/mysqlx/protocol.h:108` | `grep -n header_length cdk/protocol/mysqlx/protocol.h` |
| `ssl-mode` 默认 REQUIRED | `common/session.cc:337` | `sed -n '325,335p' common/session.cc` |
| 不支持 `caching_sha2_password` | `devapi/tests/session-t.cc:1573-1576` | `grep -rn caching_sha2 --include=*.cc . \| grep -v tests/` |
| X 侧不依赖 libmysqlclient | `CMakeLists.txt:456` 的 merge 链 | `ldd libmysqlcppconnx.so* \| grep mysqlclient` |
| `jdbc/thread/` 是死代码 | `jdbc/CMakeLists.txt:244-245` | `grep -rn add_subdirectory.*thread` |

**9.2.0 → 26.7.0 的实际漂移量（实测）：** 首轮迁移时 139 处引用里 **27 处行号失效**，但**0 处文件消失、0 处结论翻转**。全部 27 处都是纯粹的**行号平移**，没有一个机制发生变化。（本文定稿时引用数已涨到 187 处，全部校验通过。）最典型的一批：

> 下表左列是 **9.2.0 的行号**，在 26.7.0 源码树里已经指不到东西了——这是**故意**留着的失效样本，用来演示漂移长什么样。右列才是 26.7.0 的正确位置。

| 事实 | 9.2.0（已失效） | 26.7.0（本文采用） |
|---|---|---|
| `WITH_JDBC` 开关 | `CMakeLists.txt:350` | `CMakeLists.txt:389-391` |
| `merge_libraries(connector …)` | `CMakeLists.txt:416` | `CMakeLists.txt:456` |
| `ssl-mode` 默认 `REQUIRED` | `common/session.cc:329` | `common/session.cc:337` |
| `get_data_source()` | `common/session.cc:463` | `common/session.cc:471` |
| `::send()` 叶子 | `socket_detail.cc:1020` | `socket_detail.cc:1039` |
| `ParseFromArray` | `protocol.cc:961` | `protocol.cc:998` |
| `Msg_builder::send()` | `protocol.h:1004` | `protocol.h:1013-1024` |
| `Session_pool::get_session()` | `common/session.cc:971` | `common/session.cc:980` |

`cdk/mysqlx/session.cc` 的 `Expectation_processor` 甚至只是从"结构体内联 `set()`"重构成了"构造函数初始化 `m_data`"，`"17.12"` 这些路径字符串一个没变。**这说明 X DevAPI 这条链在 9.x → 26.x 之间是稳定的**——版本号大跳不等于架构大改。

**高频失效点：**

- **行号会漂，结论不会。** 上表 27 处全是平移。所以看到一篇带 `file:line` 的文章，**先假设行号过期、结论有效**，然后抽查两三条——这比整篇重新调研便宜一个数量级。
- **自动校准脚本。** 本文配套的 `docs/verify_citations.py` 会把文章里所有 `file:line` 解析出来，逐条打印该行实际内容；加 `-d <另一个源码树>` 参数还能做**跨版本漂移检测**，只报内容不一致的引用；`docs/relocate.py` 则按内容锚点给出新行号；`docs/spotcheck.py` 做最终的逐条语义核对（**236 处引用、0 问题**）。30 秒出结果：

  ```bash
  # 1. 文章引用的文件是否都还存在
  python3 docs/verify_citations.py src/mysql-connector-c++-26.7.0-src mysql-connector-cpp-26.7-call-to-bytes.md

  # 2. 相对 9.2.0，哪些引用的行号漂了
  python3 docs/verify_citations.py src/mysql-connector-c++-26.7.0-src mysql-connector-cpp-26.7-call-to-bytes.md -d src/mysql-connector-c++-9.2.0-src

  # 3. 漂了的行，新行号在哪
  python3 docs/relocate.py src/mysql-connector-c++-26.7.0-src src/mysql-connector-c++-9.2.0-src mysql-connector-cpp-26.7-call-to-bytes.md

  # 4. 最终语义核对（应为 0 problem）
  python3 docs/spotcheck.py src/mysql-connector-c++-26.7.0-src mysql-connector-cpp-26.7-call-to-bytes.md
  ```

  全部脚本在 `docs/`（12 个）。**这些是本文唯一真正可靠的防腐剂**
  ——比任何手工维护的版本对照表都强，因为它把"校准"从体力活变成了 grep：

  | 脚本 | 作用 |
  |---|---|
  | `verify_citations.py` | 被引文件是否存在；加 `-d <另一棵源码树>` 做跨版本漂移检测 |
  | `relocate.py` | 按内容锚点给出漂移后的新行号 |
  | `spotcheck.py` | **逐条语义核对**——打印每个 `file:line` 的实际内容，应为 `0 problem` |
  | `abi_matrix.sh` | **跨版本 ABI 交叉矩阵**，回答"能不能只换 `.so` 不重编程序" |
  | `resolve_debs.py` | 从 apt `Packages` 算依赖闭包（离线打包用） |
  | `inline_demos.py` / `inline_demos2.py` | 把 demo 源码同步进本文（幂等；坑表在 `inline_demos2.py` 里，是唯一来源） |
  | `tcptee.py` | 录线上字节用的 TCP tee（副本在 `demo/wire/`） |
  | `check_markdown.py` | 校验本文的栅栏配对/嵌套、表格列数、内部锚点（转义感知） |
  | `prep_src.sh` | 校验 `src/` 树与「tarball + patches」一致——**跑上面几条之前先跑它** |
  | `test_offline_install.sh` | 在纯净 Ubuntu rootfs 里真跑 `dpkg -i` |
  | `test_kylin_docker.sh` | 在真麒麟 V10 SP1 容器里验整条链（自带源失败 → 换 8.0.42 → 编 → 跑 demo） |

- **想自己抓一遍线上字节？** 用 `demo/wire/` 里的现成件：

  ```bash
  # 1. 起一个 TCP tee（把 23390 转发到 13360，同时落盘双向字节）
  python3 demo/wire/tcptee.py 23390 13360 /tmp/wire.log &

  # 2. 让程序连 tee 的端口
  g++ -std=c++17 demo/wire/probe_sslmode_disabled.cc -o probe \
      -I<build>/include/mysqlx -I<src>/include/mysqlx -I<src>/include \
      -L<build> -lmysqlcppconnx -lssl -lcrypto
  ./probe        # 里面是 ssl-mode=DISABLED，整条会话明文

  # 3. 按 4 字节长度 + 1 字节类型切帧，就能看到机制六/七/九说的每一步
  ```

  现成的两份抓包也在同目录：`capture-tls-default.log`（默认 `ssl-mode`，前 6 段明文、
  之后 `0x17` 加密）与 `capture-plaintext.log`（全程明文，15 段全解出来了）。
  **文章里所有关于"线上字节"的论断都出自这两份文件，不是读代码猜的。**

- **`ngs` 命名空间已经不存在了。** 网上大量 8.0.x 时代的文章讲 `ngs::Client` / `ngs::Session` / `ngs::Auth`，9.x 起全部换成了 `cdk::mysqlx::*`；26.7.0 全树 grep `\bngs\b` **零命中**。任何引用 `ngs::` 的教程对 9.2.0 之后的版本都是错的。
- **类名和文件名对不上。** C++ 的 `Session` 构造函数在 `devapi/session.cc`（不是 `xapi/session.cc`——那是 C API 层）；`Settings_impl` 在 `common/settings.h`；`Session_impl` 在 `common/session.h`。按名字找文件会全部找错地方。
- **`SessionConfig` 这个类在 26.7.0 里不存在。** 对应物是 `SessionSettings`（公开）+ `common::Settings_impl`（内部）。`ds::TCPIP_old` 变体也在 visitor 里直接抛异常（`cdk/core/session.cc:291-300`），是纯历史包袱。
- **X DevAPI 没有 session search path / session-state-tracker。** 全树 grep `search_path` 零命中。session 状态只在 `SessionReset` 时刷新。

---

## 总结

`mysql-connector-c++-26.7.0-src.tar.gz` 里有两个连接器，而"用 C++ 连 MySQL"这个问题因此有两个答案。核心结论：

1. **`#include` 决定命运。** `<mysqlx/xdevapi.h>` → `libmysqlcppconnx.so` / 33060 / protobuf / 自实现协议；`<mysql/jdbc.h>` → `libmysqlcppconn.so` / 3306 / classic 协议 / 转手 `libmysqlclient`。而且后者**默认不编译**（`WITH_JDBC=OFF`）。
2. **`Session` 构造不等于连接。** 它把选项翻译成一个带优先级的 `Multi_source`，然后**向连接池要一条连接**——所以它可能复用物理连接，池默认 25 条、TTL 10 分钟、失败端点 60 秒黑名单。
3. **X 协议没有 capability 位图。** 一切特性（含预处理语句、行锁、upsert、压缩）靠 `Mysqlx.Expect.Open` 声明 + 捕获服务端错误码来协商，**降级是静默的**。
4. **认证只有四种机制，且没有 `caching_sha2_password`。** 裸 TCP 走 MYSQL41→SHA256_MEMORY 两轮尝试；TLS/Unix socket 走 `PLAIN` 明文（在加密通道内）。`ssl-mode` 默认 `REQUIRED` 不是巧合——它是绕开这个缺口的唯一办法。
5. **TLS 是"先明文协商再升级"**：裸连接上先发 `CapabilitiesSet{tls:true}`，拿到 `Ok` 才 `SSL_connect()`。第 2 步是明文的。
6. **叶子是 `::send()`。** 11 层，从 `execute()` 到 `::send()`（`socket_detail.cc:1039`）或 `SSL_write()`（`connection_openssl.cc:1045`）；传输层靠模板注入，协议层不知道自己跑在明文还是密文上。
7. **帧头是 5 字节**：4 字节小端长度 + 1 字节消息号，后跟 protobuf。读侧必须先读满 5 字节再读 payload——TCP 无边界，全靠这个头。
8. **CRUD 不翻译成 SQL。** 发的是 `Mysqlx.Crud.Find/Insert/Update/Delete`，条件字符串在客户端被解析成 `Mysqlx.Expr.Expr` 树。但**事务是普通 SQL**——这个不对称很反直觉。
9. **classic 路径是三层桥**（`MySQL_Statement` → `NativeConnectionWrapper` → `IMySQLCAPI` → `::mysql_real_query`），且 `MYSQLCLIENT_STATIC_LINKING`（链接期）和 `MYSQLCLIENT_STATIC_BINDING`（调用期）是两个不同开关、默认一开一关。别把 `jdbc:` 前缀写进 URL，它不被支持。
10. **classic 路径对 libmysqlclient 版本有硬要求**（实测）：无保护地调用 `mysql_plugin_get_option` / `mysql_real_connect_dns_srv` / `mysql_bind_param`，8.0.19 三个全没有、编不过。**8.0.42 三个齐全且只要 glibc ≥ 2.28 + libssl1.1，麒麟 V10 SP1 上实测编过并跑通**；8.0.46 虽然也有，但要 glibc ≥ 2.34 + OpenSSL 3，装不上。另外 `-DWITH_MYSQL=/usr` 在 Debian 系上必失败，要用 `-DMYSQL_CONFIG_EXECUTABLE=<mysql_config>`。

还有四条不算机制但会咬人的常识：**`jdbc/thread/` 是死代码**（`add_subdirectory(thread)` 零命中）；**`get_driver_instance()` 不线程安全**（无锁 static map，要在 main 取一次）；**异常层次比 JDBC 少**（没有 `SQLTimeoutException`/`BatchUpdateException`，`SQLWarning` 压根不是异常）；**`sql::Driver` 等 5 个类析构是 protected**，别塞进 `unique_ptr`。

> **本文所有 API 结论都经过编译 + 实际连库运行验证**，配套 demo 在
> `demo/`。写作过程中靠"读代码猜"出的 API（`as<T>()`、
> `rows()`、`sql().bind()`、`Table::modify()` 等）在编译或运行时就暴露了——
> **没有一条是照着文档想当然写上去的。**

最后一句实用建议：**在 MySQL 8 上遇到一个语义不明的认证失败、或者一个"连上了但行为不对"的怪问题，先确认你用的是哪一套栈。** X DevAPI 和 `libmysqlclient` 的默认值不一样（`ssl-mode` 一个 `REQUIRED` 一个 `PREFERRED`），能力不一样（`caching_sha2_password` 一个没有一个有），错误信息也不一样。把这条排掉，剩下的问题通常就自己浮出来了。
