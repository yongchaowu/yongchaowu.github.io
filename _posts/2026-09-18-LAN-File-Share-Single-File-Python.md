---

layout: post
title: '一个文件搞定局域网传输：零依赖 Python 文件共享服务'
summary: '用 500 行纯标准库 Python 实现浏览器上传/下载/删除的局域网文件共享，解析 multipart、防路径穿越、HTTP Basic 认证一个不落。'
lang: zh-CN
date: 2026-09-18 22:00:00
categories:
- Programming
tags:
- Python
- HTTP
- 局域网
- 文件传输
- 标准库
- 源码解析
---
手机里拍了一堆照片想传到电脑上，没有数据线，不想装微信传文件助手，也不放心把文件丢到公网网盘。最省事的办法是：电脑和手机连同一个 WiFi，在电脑上跑一个服务，手机浏览器打开一个地址，直接上传下载。

听起来要装 Flask、写模板、配路由，其实不用。`file_share.py` 是一个单文件、零第三方依赖的小工具——**只用 Python 标准库**，把 HTTP 服务器、multipart 解析、认证、页面渲染全塞进约 500 行代码里。

这篇文章既是一份使用手册，也是一次源码拆解。看完你会知道它为什么能用、边界在哪、以及怎么把它改成自己的版本。

---

<!--more-->

## 目录

- [它长什么样](#它长什么样)
- [快速上手](#快速上手)
- [命令行参数详解](#命令行参数详解)
- [源码拆解](#源码拆解)
  - [1. 为什么不用 cgi 模块了](#1-为什么不用-cgi-模块了)
  - [2. 手写 multipart 解析器](#2-手写-multipart-解析器)
  - [3. safe_join：挡住路径穿越](#3-safe_join挡住路径穿越)
  - [4. HTTP Basic 认证](#4-http-basic-认证)
  - [5. 多线程服务器](#5-多线程服务器)
- [下载时的一个细节：inline 还是 attachment](#下载时的一个细节inline-还是-attachment)
- [安全边界：它不是什么](#安全边界它不是什么)
- [可以怎么改](#可以怎么改)
- [总结](#总结)

---

## 它长什么样

跑起来之后，终端会打印出所有可访问的局域网地址：

```
====================================================
局域网文件共享已启动
共享目录: /home/user/Pictures
访问密码: 已启用
在手机/电脑浏览器打开以下地址:
  http://192.168.1.5:8000/
按 Ctrl+C 停止
====================================================
```

手机浏览器打开 `http://192.168.1.5:8000/`，看到一个极简页面：一个上传表单、一张文件列表。点文件名下载，点「删除」移除文件。没有前端框架，没有 CDN，页面直接由字符串模板拼出来。

---

## 快速上手

脚本要求 **Python 3.7+**，无需 `pip install` 任何东西。

```bash
# 共享当前目录，监听 0.0.0.0:8000
python3 file_share.py

# 指定要共享的目录
python3 file_share.py -d /path/to/dir

# 指定目录和端口
python3 file_share.py -d ~/Pictures -p 8080

# 加访问密码，打开网页需输入（用户名随便填）
python3 file_share.py --password 1234

# 只允许本机访问
python3 file_share.py --host 127.0.0.1
```

使用步骤只有三步：

1. 电脑和手机连接同一个 WiFi。
2. 运行脚本，记下终端打印的 `http://<局域网IP>:8000/`。
3. 手机浏览器打开该地址，上传 / 下载 / 删除。

Windows 上把 `python3` 换成 `python` 即可。

---

## 命令行参数详解

参数定义集中在 `build_parser()`，用的是标准库 `argparse`，还配了 `RawDescriptionHelpFormatter` 保留 epilog 里的换行排版：

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `-d, --dir` | `.` | 要共享的目录 |
| `-p, --port` | `8000` | 监听端口，被占用就换一个 |
| `--host` | `0.0.0.0` | `0.0.0.0` 允许局域网，`127.0.0.1` 仅本机 |
| `--password` | 无 | 启用 HTTP Basic 认证 |
| `-v, --version` | - | 显示版本号 |

启动时对目录做了 `os.path.realpath(os.path.expanduser(...))`，所以 `~/Pictures` 这种写法没问题；目录不存在会直接 `parser.error` 报错退出。

---

## 源码拆解

### 1. 为什么不用 cgi 模块了

很多老的 Python 文件服务器教程会让你用 `cgi.FieldStorage` 来解析表单。但 **`cgi` 模块在 Python 3.13 中已被正式移除**。如果还依赖它，脚本在新版本 Python 上直接跑不起来。

`file_share.py` 的做法是自己实现一个极简 multipart 解析器，因此它对 Python 版本的兼容性反而更好——只要 3.7 以上都能用。

### 2. 手写 multipart 解析器

浏览器上传文件时，请求体是 `multipart/form-data`，格式由 boundary 分隔：

```
--boundary\r\n
Content-Disposition: form-data; name="file"; filename="photo.jpg"\r\n
Content-Type: image/jpeg\r\n
\r\n
<二进制内容>\r\n
--boundary--
```

核心解析逻辑只有几十行 `parse_multipart()`：

```python
def parse_multipart(body, boundary):
    delimiter = b"--" + boundary.encode("latin-1")
    for part in body.split(delimiter)[1:]:
        if part.startswith(b"--"):  # 结束边界
            break
        if part.startswith(b"\r\n"):
            part = part[2:]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        if b"\r\n\r\n" not in part:
            continue
        raw_headers, content = part.split(b"\r\n\r\n", 1)
        ...
        yield name, filename, content
```

几个关键点：

- **按 boundary 切分**，第 `[1:]` 段跳过前导，末尾的 `--` 表示结束。
- **只剥帧边界自带的 CRLF**，中间的文件内容原样保留——这点很重要，否则下载回来的二进制文件会被破坏。
- **头部与内容用第一个 `\r\n\r\n` 分割**，内容里也可能出现同样字节序列，所以用 `split(..., 1)` 只切一次。

解析 `Content-Disposition` 时，`parse_disposition()` 额外处理了 `filename*=`（RFC 5987 的 UTF-8 编码文件名），保证中文文件名不乱码：

```python
elif lowered.startswith("filename*="):
    raw = field[10:].strip()
    if "''" in raw:
        raw = raw.split("''", 1)[1]
    filename = urllib.parse.unquote(raw)
```

> 注意：这个解析器一次把整个请求体读进内存（`self.rfile.read(length)`），所以**不适合上传超大文件**。想支持大文件，得改成流式扫描 boundary，见后文「可以怎么改」。

### 3. safe_join：挡住路径穿越

这是整个服务里最不能省的安全函数。如果用户请求 `f=../../etc/passwd`，简单拼接就会读到共享目录之外的文件。

```python
def safe_join(base, rel):
    base = os.path.realpath(base)
    target = os.path.realpath(os.path.join(base, rel))
    if target != base and not target.startswith(base + os.sep):
        raise ValueError("非法路径")
    return target
```

思路是：两边都取 `realpath`（会解析 `..` 和符号链接），再判断目标是否等于根目录、或位于 `根目录 + 分隔符` 之下。这样即使攻击者用 `../`、绝对路径、或者指向外部的软链接，都会被拦下来。

上传时还额外做了一次文件名清洗，避免写入子路径：

```python
name = os.path.basename(filename.replace("\\", "/"))
```

先统一把 Windows 反斜杠转成正斜杠，再 `basename` 取最后一段，得到纯文件名。

### 4. HTTP Basic 认证

`--password` 启用后，`_authenticate()` 会检查 `Authorization: Basic` 头。用户名被忽略，只比对密码，且用 `hmac.compare_digest()` 做**恒定时间比较**，避免时序侧信道：

```python
if hmac.compare_digest(given, password):
    return True
self._respond(
    HTTPStatus.UNAUTHORIZED,
    {"WWW-Authenticate": 'Basic realm="FileShare"', "Content-Length": "0"},
)
```

失败时返回 `401` 加 `WWW-Authenticate`，浏览器就会弹出原生的用户名/密码框。

### 5. 多线程服务器

服务器用的是 `ThreadingHTTPServer`，每个请求一个线程，手机传文件时电脑自己访问不会被阻塞：

```python
class FileShareServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
```

- `daemon_threads = True`：主进程退出时工作线程不会挂着不结束，Ctrl+C 能干净退出。
- `allow_reuse_address = True`：重启时不会因为 `TIME_WAIT` 报端口占用。

共享目录和密码通过构造函数注入到 `server` 对象上，handler 里用 `self.server.root` / `self.server.password` 取用，避免全局变量。

---

## 下载时的一个细节：inline 还是 attachment

下载文件时，服务根据 MIME 类型决定浏览器是直接预览还是弹出下载框：

```python
INLINE_TYPES = ("text/", "image/", "video/", "audio/", "application/pdf")
...
disposition = "inline" if ctype.startswith(INLINE_TYPES) else "attachment"
```

图片、视频、PDF 会直接在浏览器里打开（`inline`），其它类型则触发下载（`attachment`）。文件名用 `filename*=UTF-8''...` 编码，中文名也能正确显示。

下载走 `shutil.copyfileobj(fh, self.wfile, CHUNK_SIZE)`，按 64 KB 分块写，不会把大文件整个读进内存；同时捕获 `BrokenPipeError` / `ConnectionResetError`，用户中途取消下载不会抛异常刷屏。

另外 `_send_bytes()` 对 `HEAD` 请求做了处理——只发头部不发 body，符合 HTTP 规范。

---

## 安全边界：它不是什么

写得很克制这点值得表扬，但用它之前要清楚它的定位——**这是一个可信局域网内的小工具，不是生产级文件服务**：

- **明文 HTTP**：密码是 Base64 传输的，不是加密。公共 WiFi 下别裸奔。
- **无 TLS**：不要暴露到公网，也不要做端口转发。
- **所有文件对局域网内所有人可见**：加 `--password` 后仍需在可信网络内使用。
- **上传大小受内存限制**：整包读入内存，别传几 GB 的镜像。
- **无断点续传 / 无 Range 支持**：大文件下载中断就得重来。

共享敏感文件时，务必加 `--password`，用完 `Ctrl+C` 停止。

---

## 可以怎么改

如果你想把它当练手项目继续扩展，几个方向：

1. **流式上传**：不再 `split(body, delimiter)` 全量解析，而是从 `rfile` 增量读取、滑动窗口匹配 boundary，就能支持大文件。
2. **Range 请求**：实现 `Range: bytes=` 响应 `206 Partial Content`，支持视频拖动进度条和断点续传。
3. **子目录浏览**：目前只列出根目录下的文件（`e.is_file()`），可以加上目录导航，同时继续用 `safe_join` 兜住路径。
4. **HTTPS**：用 `ssl.SSLContext` 包一层 `socket`，自签名证书也能让传输加密。
5. **二维码**：启动时把地址生成 ASCII 二维码，手机扫一下直达，省得手输 IP。
6. **过期清理**：给上传文件加时间戳，后台线程定期删除旧文件。

这几个改动都不会引入第三方依赖，是理解 HTTP 协议细节的好练习。

---

## 总结

`file_share.py` 用最朴素的工具解决了一个很具体的痛点：**在没有数据线、不想装软件的局域网里快速倒腾文件**。它值得学习的不是功能多复杂，而是取舍：

- 用标准库而不是框架，换来「拷一个文件就能跑」；
- 自己写 multipart，换来对新版 Python 的兼容；
- 用 `realpath` + 前缀校验，用几行代码堵住路径穿越；
- 用 `hmac.compare_digest`，在白盒工具里也不放过时序攻击。

下次手机和电脑之间要传文件时，不妨试试这一行命令：

```bash
python3 file_share.py -d ~/Downloads --password 1234
```

> 源码见下方附录，共 526 行，Python 3.7+，零第三方依赖。

---

## 附录：完整源码 `file_share.py`

```python
#!/usr/bin/env python3
"""局域网 WiFi 文件共享：浏览器上传 / 下载 / 删除文件。"""

# ============================================================================
# 局域网 WiFi 文件共享 —— 使用说明
# ============================================================================
#
# 一句话简介
#   在电脑上运行本脚本，同一个 WiFi 局域网内的手机 / 平板 / 其它电脑
#   用浏览器打开提示的网址，即可上传、下载、删除共享目录里的文件。
#   零第三方依赖，只用 Python 标准库。
#
# 运行环境
#   Python 3.7+（上传解析为自实现，不依赖已被 3.13 移除的 cgi 模块）
#
# 基本用法
#   python3 file_share.py
#       共享「当前目录」，监听 0.0.0.0:8000。
#
#   python3 file_share.py -d /path/to/dir
#       指定要共享的目录。
#
#   python3 file_share.py -d ~/Pictures -p 8080
#       指定目录和端口（端口被占用时换一个，如 8080 / 8888）。
#
#   python3 file_share.py --password 1234
#       启用访问密码（HTTP Basic 认证），打开网页时需输入，
#       用户名随便填，密码填 1234。
#
#   python3 file_share.py --host 127.0.0.1
#       只允许本机访问（默认 0.0.0.0 允许局域网访问）。
#
# 查看帮助
#   python3 file_share.py -h        # 或 --help
#   python3 file_share.py -v        # 查看版本
#
# 使用步骤
#   1. 电脑和手机连接同一个 WiFi。
#   2. 运行脚本，终端会打印形如 http://192.168.1.5:8000/ 的地址。
#   3. 在手机浏览器输入该地址，即可看到文件列表。
#   4. 选择文件点「上传」；点文件名下载；点「删除」移除文件。
#
# 常见问题
#   * 打不开网页？
#       - 确认手机和电脑在同一 WiFi（不是手机流量）。
#       - 关闭电脑防火墙，或放行 8000 端口。
#       - 确认地址里的 IP 是电脑的局域网 IP（脚本已自动列出）。
#   * 端口被占用（Address already in use）？
#       换端口：python3 file_share.py -p 8080
#   * Windows 上运行？
#       把 python3 换成 python 即可。
#
# 安全提示
#   * 本工具使用明文 HTTP，仅适合可信的局域网环境，请勿在公共 WiFi 裸奔。
#   * 共享敏感文件时务必加 --password。
#   * 共享目录内的文件对局域网内所有人可见，用完请 Ctrl+C 停止。
# ============================================================================

import argparse
import base64
import hmac
import html
import mimetypes
import os
import shutil
import socket
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from string import Template

VERSION = "1.1"
CHUNK_SIZE = 64 * 1024
INLINE_TYPES = ("text/", "image/", "video/", "audio/", "application/pdf")

# ---------------------------------------------------------------------------
# 页面模板
# ---------------------------------------------------------------------------
INDEX_TEMPLATE = Template(
    """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>局域网文件共享</title>
<style>
  body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
         max-width: 860px; margin: 0 auto; padding: 16px; background: #f6f7f9; }
  h1 { font-size: 20px; }
  .card { background: #fff; border-radius: 10px; padding: 16px;
          box-shadow: 0 1px 4px rgba(0, 0, 0, .08); margin-bottom: 16px; }
  table { width: 100%; border-collapse: collapse; }
  td, th { padding: 8px; border-bottom: 1px solid #eee; text-align: left; font-size: 14px; }
  a { color: #2563eb; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .btn { background: #2563eb; color: #fff; border: none; border-radius: 6px;
         padding: 8px 14px; cursor: pointer; font-size: 14px; }
  .danger { background: #dc2626; }
  input[type=file] { margin-right: 8px; }
  .muted { color: #888; font-size: 13px; }
</style>
</head>
<body>
<h1>局域网文件共享</h1>
<div class="card">
  <form method="post" action="/upload" enctype="multipart/form-data">
    <input type="file" name="file" multiple required>
    <button class="btn" type="submit">上传</button>
  </form>
</div>
<div class="card">
  <table>
    <tr><th>文件名</th><th>大小</th><th>操作</th></tr>
    $rows
  </table>
</div>
<p class="muted">共享目录: $shared_dir</p>
</body>
</html>"""
)

EMPTY_ROW = "<tr><td colspan='3' class='muted'>暂无文件</td></tr>"

FILE_ROW = Template(
    "<tr>"
    "<td><a href='/download?f=$quoted'>$name</a></td>"
    "<td>$size</td>"
    "<td><form method='post' action='/delete' style='display:inline' "
    "onsubmit=\"return confirm('确定删除 $name_js ?')\">"
    "<input type='hidden' name='f' value='$name'>"
    "<button class='btn danger' type='submit'>删除</button>"
    "</form></td>"
    "</tr>"
)


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def human_size(num):
    """把字节数格式化为易读字符串。"""
    value = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} PB"


def local_ips():
    """返回本机所有非回环 IPv4 地址。"""
    ips = set()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0.5)
            sock.connect(("8.8.8.8", 80))
            ips.add(sock.getsockname()[0])
    except OSError:
        pass
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            ips.add(info[4][0])
    except OSError:
        pass
    return sorted(ip for ip in ips if not ip.startswith("127."))


def safe_join(base, rel):
    """把相对路径安全地拼到 base 下，阻止路径穿越。"""
    base = os.path.realpath(base)
    target = os.path.realpath(os.path.join(base, rel))
    if target != base and not target.startswith(base + os.sep):
        raise ValueError("非法路径")
    return target


def guess_type(name):
    ctype, _ = mimetypes.guess_type(name, strict=False)
    return ctype or "application/octet-stream"


def parse_disposition(value):
    """解析 Content-Disposition，返回 (field_name, filename)。"""
    name = filename = None
    for field in value.split(";"):
        field = field.strip()
        lowered = field.lower()
        if lowered.startswith("name="):
            name = field[5:].strip().strip('"')
        elif lowered.startswith("filename*="):
            raw = field[10:].strip()
            if "''" in raw:
                raw = raw.split("''", 1)[1]
            filename = urllib.parse.unquote(raw)
        elif lowered.startswith("filename=") and filename is None:
            filename = field[9:].strip().strip('"')
    return name, filename


def parse_multipart(body, boundary):
    """极简 multipart/form-data 解析器，逐个 yield (字段名, 文件名, 内容)。

    仅处理表单上传场景：按 boundary 切分，去掉帧边界自带的 CRLF，
    内容按原样返回，不触碰文件数据本身。
    """
    delimiter = b"--" + boundary.encode("latin-1")
    for part in body.split(delimiter)[1:]:
        if part.startswith(b"--"):  # 结束边界
            break
        if part.startswith(b"\r\n"):
            part = part[2:]
        if part.endswith(b"\r\n"):
            part = part[:-2]
        if b"\r\n\r\n" not in part:
            continue
        raw_headers, content = part.split(b"\r\n\r\n", 1)

        name = filename = None
        for line in raw_headers.split(b"\r\n"):
            if b":" not in line:
                continue
            key, _, val = line.partition(b":")
            if key.strip().lower() == b"content-disposition":
                name, filename = parse_disposition(val.decode("utf-8", "replace").strip())
        yield name, filename, content


# ---------------------------------------------------------------------------
# HTTP 处理
# ---------------------------------------------------------------------------
class FileShareHandler(BaseHTTPRequestHandler):
    server_version = f"FileShare/{VERSION}"
    protocol_version = "HTTP/1.1"

    # -- 基础响应 ---------------------------------------------------------
    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.address_string(), fmt % args))

    def _respond(self, status, headers):
        self.send_response(status)
        self.send_header("X-Content-Type-Options", "nosniff")
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()

    def _send_bytes(self, status, body=b"", content_type="text/plain; charset=utf-8", extra=None):
        headers = {"Content-Type": content_type, "Content-Length": str(len(body))}
        if extra:
            headers.update(extra)
        self._respond(status, headers)
        if self.command != "HEAD" and body:
            self._write(body)

    def _redirect(self, location):
        self._send_bytes(HTTPStatus.SEE_OTHER, extra={"Location": location})

    def _error(self, status, message=None):
        text = message or HTTPStatus(status).phrase
        self._send_bytes(status, text.encode("utf-8"))

    def _write(self, data):
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _read_body(self, limit=0):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return b""
        if length <= 0 or (limit and length > limit):
            return b""
        return self.rfile.read(length)

    # -- 认证 -------------------------------------------------------------
    def _authenticate(self):
        password = self.server.password
        if not password:
            return True
        header = self.headers.get("Authorization", "")
        if header.startswith("Basic "):
            try:
                decoded = base64.b64decode(header[6:]).decode("utf-8", "replace")
                _, _, given = decoded.partition(":")
            except Exception:
                given = ""
            if hmac.compare_digest(given, password):
                return True
        self._respond(
            HTTPStatus.UNAUTHORIZED,
            {"WWW-Authenticate": 'Basic realm="FileShare"', "Content-Length": "0"},
        )
        return False

    # -- 路由 -------------------------------------------------------------
    def do_GET(self):
        if not self._authenticate():
            return
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            self._render_index()
        elif path == "/download":
            self._serve_download()
        else:
            self._error(HTTPStatus.NOT_FOUND)

    do_HEAD = do_GET

    def do_POST(self):
        if not self._authenticate():
            return
        path = urllib.parse.urlparse(self.path).path
        if path == "/upload":
            self._handle_upload()
        elif path == "/delete":
            self._handle_delete()
        else:
            self._error(HTTPStatus.NOT_FOUND)

    # -- GET: 列表 / 下载 --------------------------------------------------
    def _render_index(self):
        root = self.server.root
        rows = []
        with os.scandir(root) as entries:
            files = sorted(
                (e for e in entries if e.is_file()), key=lambda e: e.name.lower()
            )
        for entry in files:
            rows.append(
                FILE_ROW.substitute(
                    quoted=urllib.parse.quote(entry.name),
                    name=html.escape(entry.name, quote=True),
                    name_js=entry.name.replace("\\", "\\\\").replace("'", "\\'"),
                    size=human_size(entry.stat().st_size),
                )
            )
        page = INDEX_TEMPLATE.substitute(
            rows="\n".join(rows) or EMPTY_ROW,
            shared_dir=html.escape(root),
        )
        self._send_bytes(HTTPStatus.OK, page.encode("utf-8"), "text/html; charset=utf-8")

    def _serve_download(self):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        rel = query.get("f", [""])[0]
        self._send_file(rel)

    def _send_file(self, rel):
        try:
            target = safe_join(self.server.root, rel)
        except ValueError:
            return self._error(HTTPStatus.FORBIDDEN)
        if not os.path.isfile(target):
            return self._error(HTTPStatus.NOT_FOUND)

        name = os.path.basename(target)
        ctype = guess_type(name)
        disposition = "inline" if ctype.startswith(INLINE_TYPES) else "attachment"
        headers = {
            "Content-Type": ctype,
            "Content-Length": str(os.path.getsize(target)),
            "Content-Disposition": "{}; filename*=UTF-8''{}".format(
                disposition, urllib.parse.quote(name)
            ),
        }
        self._respond(HTTPStatus.OK, headers)
        if self.command == "HEAD":
            return
        try:
            with open(target, "rb") as fh:
                shutil.copyfileobj(fh, self.wfile, CHUNK_SIZE)
        except (BrokenPipeError, ConnectionResetError):
            pass

    # -- POST: 上传 / 删除 -------------------------------------------------
    def _handle_upload(self):
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            return self._error(HTTPStatus.BAD_REQUEST, "需要 multipart/form-data")
        boundary = None
        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("boundary="):
                boundary = part[len("boundary="):].strip('"')
        if not boundary:
            return self._error(HTTPStatus.BAD_REQUEST, "缺少 boundary")

        body = self._read_body()
        if not body:
            return self._error(HTTPStatus.BAD_REQUEST, "请求体为空")

        root = self.server.root
        for field, filename, content in parse_multipart(body, boundary):
            if field != "file" or not filename:
                continue
            name = os.path.basename(filename.replace("\\", "/"))
            if not name:
                continue
            target = safe_join(root, name)
            with open(target, "wb") as out:
                out.write(content)
        self._redirect("/")

    def _handle_delete(self):
        data = self._read_body().decode("utf-8", "replace")
        name = urllib.parse.parse_qs(data).get("f", [""])[0]
        try:
            target = safe_join(self.server.root, name)
        except ValueError:
            return self._error(HTTPStatus.FORBIDDEN)
        if os.path.isfile(target):
            try:
                os.remove(target)
            except OSError:
                pass
        self._redirect("/")


# ---------------------------------------------------------------------------
# 服务器
# ---------------------------------------------------------------------------
class FileShareServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, address, handler, *, root, password=None):
        super().__init__(address, handler)
        self.root = os.path.realpath(root)
        self.password = password


# ---------------------------------------------------------------------------
# 命令行
# ---------------------------------------------------------------------------
EPILOG = """\
使用示例:
  python3 file_share.py                      共享当前目录, 端口 8000
  python3 file_share.py -d ~/Pictures        指定共享目录
  python3 file_share.py -d ~/Downloads -p 8080
  python3 file_share.py --password 1234      启用访问密码
  python3 file_share.py --host 127.0.0.1     仅本机可访问

使用步骤:
  1. 电脑与手机连接同一个 WiFi。
  2. 运行脚本, 终端会打印形如 http://192.168.1.5:8000/ 的地址。
  3. 手机/电脑浏览器打开该地址, 即可上传、下载、删除文件。

常见问题:
  打不开网页: 确认在同一 WiFi; 关闭防火墙或放行对应端口。
  端口被占用: 换一个端口, 例如 -p 8080。
  Windows 用户: 把 python3 换成 python 运行。

安全提示:
  本工具使用明文 HTTP, 仅适合可信局域网; 共享敏感文件请加 --password;
  用完按 Ctrl+C 停止服务。
"""


def build_parser():
    parser = argparse.ArgumentParser(
        prog="file_share.py",
        description="局域网 WiFi 文件共享: 浏览器上传 / 下载 / 删除文件 (零第三方依赖)。",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-d", "--dir", default=".", metavar="DIR",
        help="要共享的目录 (默认: 当前目录)",
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8000, metavar="PORT",
        help="监听端口 (默认: 8000)",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", metavar="HOST",
        help="监听地址, 0.0.0.0 允许局域网访问, 127.0.0.1 仅本机 (默认: 0.0.0.0)",
    )
    parser.add_argument(
        "--password", default=None, metavar="PWD",
        help="访问密码, 启用 HTTP Basic 认证 (默认: 无)",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {VERSION}",
        help="显示版本号并退出",
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    root = os.path.realpath(os.path.expanduser(args.dir))
    if not os.path.isdir(root):
        parser.error(f"目录不存在: {root}")

    try:
        server = FileShareServer(
            (args.host, args.port), FileShareHandler, root=root, password=args.password
        )
    except OSError as exc:
        parser.error(f"无法绑定 {args.host}:{args.port} ({exc})，请换端口 -p 8080")

    line = "=" * 52
    print(line)
    print("局域网文件共享已启动")
    print(f"共享目录: {root}")
    print(f"访问密码: {'已启用' if args.password else '未启用'}")
    print("在手机/电脑浏览器打开以下地址:")
    for ip in local_ips():
        print(f"  http://{ip}:{args.port}/")
    print("按 Ctrl+C 停止")
    print(line)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
```
