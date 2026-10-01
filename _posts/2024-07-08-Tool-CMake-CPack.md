---
layout: post
title: CMake-CPack
display_title: 'CMake CPack'
date: 2024-07-08 13:32:00
categories:
- Developer Tools
tags:
- CMake
- Tool
---
参考：[CMake CPack 官方文档](https://cmake.org/cmake/help/latest/module/CPack.html)

`CMakeList.txt:Cpack`

<!--more-->

```shell
project(CpackDemo)
#project(CpackDemo VERSION 0.0.1)

set(CPACK_PACKAGE_NAME XXX)

set(CPACK_PACKAGE_VERSION 0.0.1) #Default value is 0.1.1

set(CPACK_PACKAGE_VERSION_MAJOR 0)# Default depends on the project version; see CPack documentation
set(CPACK_PACKAGE_VERSION_MINOR 0)# Default depends on the project version; see CPack documentation
set(CPACK_PACKAGE_VERSION_PATCH 1)# Default depends on the project version; see CPack documentation

set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Brief")

set(CPACK_PACKAGE_VENDOR "Company")

string(TIMESTAMP TIMESTAMP "%Y-%m-%d_%H-%M-%S")

# 获取提交ID
execute_process(
  COMMAND git rev-parse HEAD
  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
  OUTPUT_VARIABLE COMMIT_ID
  OUTPUT_STRIP_TRAILING_WHITESPACE
)

# 使用 STRING 命令的 SUBSTRING 选项来截取前八个字符
string(SUBSTRING ${COMMIT_ID} 0 8 SHORT_COMMIT_ID)

set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}-${TIMESTAMP}-${SHORT_COMMIT_ID}")

set(CPACK_PACKAGE_DIRECTORY ..)

set(CPACK_GENERATOR "TGZ;ZIP")
# 7Z (7-Zip file format)
# DEB (Debian packages)
# External (CPack External packages)
# IFW (Qt Installer Framework)
# NSIS (Null Soft Installer)
# NSIS64 (Null Soft Installer (64-bit))
# NuGet (NuGet packages)
# RPM (RPM packages)
# STGZ (Self extracting Tar GZip compression
# TBZ2 (Tar GZip compression)
# TXZ (Tar XZ compression)
# TZ (Tar Compress compression)
# ZIP (ZIP file format)

#FILE
install(TARGETS xx DESTINATION  bin)
install(DIRECTORY xx DESTINATION  .)
install(FILES xx DESTINATION  .)

#END
include(CPack)

```

---

> **AI 修改声明：** 本文由 LLM 协助校对，最近修改时间：2026-09-25 00:05（UTC+08:00）。
