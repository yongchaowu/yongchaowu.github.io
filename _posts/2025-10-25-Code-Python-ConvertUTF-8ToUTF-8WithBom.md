---
layout: post
title: 'Python: Convert UTF-8 to UTF-8 with BOM'
date: 2025-10-25 09:34:00
categories:
- Programming
tags:
- Code
- Python
---
`UTF-8 With Bom` 与 `UTF-8` 格式相比，文件开头多3个字节`\xef\xbb\xbf`

## 转换方案

<!--more-->

1. 在文件首，写入二进制`b'\xef\xbb\xbf'`
2. 使用`utf-8-sig`，重新保存文件

Demo:

    def is_utf8_encoding(file_path):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                content.decode('utf-8') #utf-8-sig
                if content.startswith(b'\xef\xbb\xbf'):
                    print(file_path + " is UTF-8 With Bom")
                    return False
            return True
        except(UnicodeDecodeError, TypeError):
            return False

    def conver_utf8_to_utf8_bom(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(file_path, 'wb') as f:
            f.write(b'\xef\xbb\xbf')
            f.write(content.encode('utf-8'))

    import os
    def traverse_dir(dir):
        for dirpath,dirnames,filenames in os.walk(dir):
            print(dirpath, dirnames, filenames)
            for fn in filenames:
                if fn[-4:] == ".cpp" or fn[-2:] == ".h":
                    if is_utf8_encoding(dirpath + os.sep + fn):
                        conver_utf8_to_utf8_bom(dirpath + os.sep + fn)
                    else:
                        print(dirpath + os.sep + fn + " 不是UTF-8格式")

    import sys
    dir = "."
    if len(sys.argv) >=2:
      dir = sys.argv[1]
    traverse_dir(dir)

本文修订依据：Python 3.14.7 文档 [`String and Bytes literals`](https://docs.python.org/3.14/reference/lexical_analysis.html#string-and-bytes-literals)，尤其是 §§2.5.2 和 2.5.5。bytes literal 需要 `b`/`B` 前缀后紧跟引号；本文仅补全该字面量的引号。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 09:39（UTC+08:00）。修订仅将 UTF-8 BOM 示例改为合法的 `b'\xef\xbb\xbf'` bytes literal。