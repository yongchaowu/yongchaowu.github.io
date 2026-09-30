---
layout: post
title: "清空 Linux 终端代理环境变量：clear_proxy.sh 背后的 4 个机制"
display_title: "清空 Linux 终端代理环境变量：clear_proxy.sh 背后的 4 个机制"
summary: "讲清楚 clear_proxy.sh 这类\"一键清除代理\"脚本为什么必须 source（还自带守卫拦住误用）、为什么大小写要各清一遍、以及清了环境变量为什么还不等于全局关代理。"
lang: zh-CN
date: 2026-09-25 09:00:00
categories:
  - Systems
  - Developer Tools
tags:
  - "Linux"
  - "Proxy"
  - "Shell"
  - "环境变量"
  - "Bash"
  - "网络"
---

<!--more-->

开关代理工具（Clash / v2rayN / 企业 PAC）之后，终端里经常残留一堆"幽灵代理"：`git pull` 报连接失败、`pip install` 卡死、`curl` 走了早就关掉的 127.0.0.1:7890。最常用的解法是这样一个脚本：

```bash
#!/bin/sh
# clear_proxy.sh —— 用法: source clear_proxy.sh
# 直接 ./clear_proxy.sh 执行改不了父 shell，守卫会提示并退出
case "$0" in
    *clear_proxy.sh)
        echo "环境变量只在当前 shell 生效，请改用: source $0" >&2
        exit 1
        ;;
esac

unset http_proxy https_proxy ftp_proxy all_proxy no_proxy \
      HTTP_PROXY HTTPS_PROXY FTP_PROXY ALL_PROXY NO_PROXY
```

核心仍然只有一行 `unset`，外加一个防误用的 source 守卫；但它的 `unset` 能生效的前提——**在哪执行、清哪些名字、清完覆盖多大范围**——才是它真正的"工作机制"。这篇文章把这 4 个机制讲清楚。

---

## 目录

- [机制一：环境变量是进程属性，只向下继承](#机制一环境变量是进程属性只向下继承)
- [机制二：为什么必须 source，直接执行没用](#机制二为什么必须-source直接执行没用)
- [机制三：为什么大小写要各清一遍](#机制三为什么大小写要各清一遍)
- [机制四：清了环境变量 ≠ 全局关闭代理](#机制四清了环境变量--全局关闭代理)
- [验证与常用姿势](#验证与常用姿势)
- [总结](#总结)

---

## 机制一：环境变量是进程属性，只向下继承

`http_proxy` 不是"系统设置"，它只是**每个进程自己内存里的一张键值表**。Shell 启动时从父进程（登录会话、systemd user session）继承一张表，之后 `export http_proxy=...` 只是往**当前 shell 这个进程**的表里写了一条。

进程创建子进程时（fork + exec），环境表被**完整复制**给子进程；子进程再往下传，形成一条继承链：

```
systemd --user
   └─ bash (你的终端)          ← 环境表在这里
        ├─ curl / git / pip    ← 启动瞬间拷贝走这张表
        └─ clear_proxy.sh      ← 也是一次 fork，拷贝的是副本
```

所以两个直接推论：

1. **对环境变量的修改永远只影响"持有这张表"的进程**；
2. **已经在跑的进程（curl、GUI 程序、IDE 内置终端）不会因为你后来 unset 而忘掉它启动时拿到的值**——环境表没有"全局广播更新"机制。

---

## 机制二：为什么必须 source，直接执行没用

`./clear_proxy.sh` 的执行过程是：当前 shell fork 出一个**子 shell** → 子 shell 再 exec 这个脚本 → `unset` 在**脚本进程的环境副本**里删掉变量 → 脚本退出，进程消失。

父 shell 的环境表从头到尾没被碰过。这就是新手最常见的坑——旧版脚本一声不吭地"成功"，实际什么都没清：

```bash
$ export http_proxy=http://127.0.0.1:7890
$ ./clear_proxy.sh        # 旧版：没报错，但……
$ echo $http_proxy
http://127.0.0.1:7890     # 毫发无损
```

所以脚本开头加了一个 **source 守卫**，把这个"无声失败"变成"有声反馈"：

```bash
case "$0" in
    *clear_proxy.sh)
        echo "环境变量只在当前 shell 生效，请改用: source $0" >&2
        exit 1
        ;;
esac
```

原理就是机制一的推论：**`$0` 是"当前进程怎么被调起的"的名字**——直接执行时 `$0` 就是脚本路径（`./clear_proxy.sh`），而 `source` 时当前进程还是那个交互 shell，`$0` 是 `bash`（或 `-bash`），不匹配脚本名，守卫直接放行。现在的行为：

```bash
$ ./clear_proxy.sh
环境变量只在当前 shell 生效，请改用: source ./clear_proxy.sh
$ echo $http_proxy
http://127.0.0.1:7890     # 被拦下了，但变量还在——按提示改用 source
```

正确用法是让脚本在**当前 shell 进程里**执行，而不是 fork 出去：

```bash
source clear_proxy.sh      # 或等价的 . clear_proxy.sh
```

`source` 的语义是"读取文件内容，当作当前 shell 的输入逐条执行"——`unset` 于是直接作用于当前进程的环境表，立刻生效，且对之后 fork 的所有子进程可见。

> 守卫用的是 POSIX 的 `case "$0"` 而不是 bash 的 `${BASH_SOURCE[0]}`，所以 `sh clear_proxy.sh`（dash）也能正确提示；`source` 时脚本里的 `#!/bin/sh` 只是被当作普通注释，不影响"读入当前 shell"的语义。

---

## 机制三：为什么大小写要各清一遍

Linux 环境变量名**大小写敏感**，`http_proxy` 和 `HTTP_PROXY` 是两条独立的记录。不同工具的读取规则并不统一（以下规则均以官方 man page 为准）：

| 工具 | 读取规则 |
|---|---|
| **curl** | 大小写都认，**小写优先**；但 `http_proxy` 是例外——**只认小写**（man curl: *"The lower case version has precedence. http_proxy is an exception as it is only available in lower case."*） |
| **wget** | **只认小写**：`http_proxy` / `https_proxy` / `ftp_proxy` / `no_proxy` |
| **git** | 底层走 curl，同时受 `http.proxy` 配置项覆盖 |
| **Go 系工具**（docker、containerd 等） | 大小写都认，但历史上 uppercase `HTTP_PROXY` 曾有 CGI 注入争议，行为随版本变化 |
| **部分 Python / Java 库** | 只认大写 `HTTP_PROXY` / `HTTPS_PROXY` |

也就是说：**只清小写会漏掉一批工具，只清大写会漏掉另一批**。脚本把两套共 10 个名字（`http/https/ftp/all/no` × 大小写）全 unset，是最稳妥的"地毯式清理"。

三个细节：

- **`ftp_proxy` / `FTP_PROXY` 必须包含**——curl 的环境变量规则是 `[url-protocol]_PROXY`（man curl: *"[url-protocol]_PROXY ... as specified in a URL"*），ftp://、socks:// 等协议各有自己的变量名；wget 则明确只认小写 `ftp_proxy`。
- **`no_proxy` / `NO_PROXY` 也要清**——它是"哪些地址绕过代理"的白名单。代理本体没了它看似无害，但**白名单是为下一次开代理准备的语义**：残留的旧规则（比如 `192.168.0.0/16` 或某公司内网域名）会在你下次开代理时静默生效，造成"一部分地址莫名直连"的半开状态，极难排查。彻底清理 = 把这次开关周期的状态全部归零。
- **`all_proxy`（小写）不能漏**，它通常给 SOCKS 代理用（`socks5://`），漏掉它会导致 ssh / 部分 CLI 仍走 SOCKS。

---

## 机制四：清了环境变量 ≠ 全局关闭代理

环境变量只是代理配置的**其中一条通道**。这个脚本的边界非常清晰——它只覆盖"启动时从环境表里读代理"的命令行工具。以下几处它**完全管不到**：

### 1. GNOME / 桌面应用的系统代理（dconf）

```bash
gsettings get org.gnome.system.proxy mode        # 'none' / 'manual' / 'auto'
gsettings get org.gnome.system.proxy autoconfig-url
```

桌面设置里配置的代理（含 PAC 自动代理）存在 dconf 里，被使用 GNetwork 代理解析的 GTK/GNOME 应用读取，与 shell 环境变量是两套独立系统。关掉环境变量后浏览器、软件中心仍可能继续走代理。

### 2. apt 的配置文件

```bash
# /etc/apt/apt.conf.d/ 下可能有：
Acquire::http::Proxy "http://127.0.0.1:7890";
```

apt 优先读自己的配置文件，`unset` 对它无效。检查方法：

```bash
apt-config dump | grep -i proxy
```

### 3. git 的持久配置

```bash
git config --global --get-regexp -i proxy
# 若有输出，即使环境清干净，git 依然走代理：
git config --global --unset http.proxy
```

### 4. docker 客户端配置

`~/.docker/config.json` 里的 `proxies` 字段会给容器/构建过程注入代理，同样不受 shell 环境影响。

### 5. 已经在运行的进程

如机制一所述：IDE 内置终端、已打开的 GUI 程序在启动时拿到的环境表不会被追溯修改。**改完环境变量后，新开的终端/重启的应用才干净。**

---

## 验证与常用姿势

确认当前 shell 是否还有残留：

```bash
env | grep -i proxy          # 无输出 = 当前 shell 已干净
curl -vI https://example.com 2>&1 | grep -i 'proxy\|Connected'   # 看实际连接走向
```

让脚本顺手可用的两种姿势：

```bash
# 方式一：写成函数/别名放进 ~/.bashrc（注意别名默认不展开，函数最稳）
clearproxy() { unset http_proxy https_proxy ftp_proxy all_proxy no_proxy \
                     HTTP_PROXY HTTPS_PROXY FTP_PROXY ALL_PROXY NO_PROXY; }

# 方式二：保留脚本，用 source 调用（脚本自带守卫，误执行会提示）
alias cp='source ~/Desktop/clear_proxy.sh'
```

> 想反过来"一键开代理"也同理：`export` 必须发生在当前 shell（source 或直接敲），写进脚本执行同样会丢失。

---

## 总结

`clear_proxy.sh` 的核心是一行 `unset` 加一个守卫，但它的正确使用依赖 4 个机制：

1. **环境变量是进程私有属性**，只随 fork/exec 向下继承，没有全局更新；
2. **必须 `source`**——直接执行是在子进程的副本上改，父 shell 毫不知情；脚本用 `$0` 守卫把这种无声失败变成明确提示；
3. **大小写必须各清一遍，且 10 个名字一个不能少**——curl/wget 偏好小写，部分库只认大写，`no_proxy` 白名单还会影响下一次开代理的语义；
4. **作用域仅限命令行工具的环境通道**——桌面代理（dconf）、apt 配置、git 全局配置、docker 配置、已运行进程都在它能力范围之外，需要单独处理。

一句话：这个脚本是"当前 shell 及其未来子进程"的精准外科手术，而不是"这台机器关代理"的开关。知道边界在哪，才不会在下次 `git pull` 失败时怀疑脚本坏了。
