---
layout: post
title: "现代 CMake 工程化：Targets、依赖发现、安装与 CPack"
display_title: "现代 CMake 工程化：Targets、依赖发现、安装与 CPack"
summary: "把零散的 CMake 记录整理成以 target 为中心、可安装、可测试、可打包的现代 C/C++ 构建流程。"
lang: zh-CN
date: 2026-09-24 11:00:00
categories:
  - Developer Tools
tags:
  - CMake
  - C++
  - Build System
  - Packaging
  - Cross-compilation
  - CPack
curated: true
content_origin: curated
curation_level: synthesis
version: curated-v1
source_posts:
  - "_posts/2023-04-12-Tool-CMake.md"
  - "_posts/2023-04-29-Tool-CMake-A-Simple-CMake-Example.md"
  - "_posts/2023-05-09-Tool-CMake-find_library.md"
  - "_posts/2023-05-09-Tool-CMake-add_custom_command-copy.md"
  - "_posts/2023-04-29-Tool-CMake-list.md"
  - "_posts/2023-04-29-Tool-CMake-OPTION.md"
  - "_posts/2023-07-24-Tool-CMake-添加自定义宏定义.md"
  - "_posts/2023-10-12-Tool-CMake-设置SONAME.md"
  - "_posts/2024-07-08-Tool-CMake-CPack.md"
  - "_posts/2024-07-20-Tool-CMake-Cpack-生成版本信息文件.md"
  - "_posts/2024-07-15-Tool-Cross-compilation-Toolchain-ARM-Linaro.md"
  - "_posts/2023-05-27-Tool-CMake-vscode-cmake-tools.md"
---

CMake 记录通常从“怎样编译一个可执行文件”开始，但真正可维护的工程还需要回答：依赖如何传递、安装后的库如何被找到、测试如何运行、交叉编译如何隔离、发布包如何生成。现代 CMake 的核心是 **target**：把目标的属性、依赖和用法写成显式关系。

> 本文是基于历史 CMake 笔记的重组稿，不要求某个固定的最低 CMake 版本。实际项目应以所用工具链和支持矩阵为准。

<!--more-->

## 1. 先写 target，再写全局变量

一个最小的库和可执行文件可以这样表达：

```cmake
cmake_minimum_required(VERSION 3.21)
project(demo LANGUAGES CXX)

add_library(core
    src/parser.cpp
    src/parser.hpp
)
target_include_directories(core PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_compile_features(core PUBLIC cxx_std_17)

add_executable(app src/main.cpp)
target_link_libraries(app PRIVATE core)
```

这里有三个重要关系：

- `core` 的公共头文件目录属于使用者和构建者；
- `app` 只在本地使用 `core`，不应把依赖无意义地扩散出去；
- 安装接口与构建接口分开，避免把源码树路径泄漏到安装包。

不要从旧式全局 `include_directories()`、全局编译选项和目录级变量开始新项目；历史项目可以先保持兼容，再逐步迁移到 target 语义。

## 2. 依赖发现的失败要显式处理

`find_package` 和 `find_library` 的结果必须检查，尤其要处理 `*-NOTFOUND`：

```cmake
find_package(Threads REQUIRED)

find_path(JSON_INCLUDE_DIR nlohmann_json.hpp)
find_library(JSON_LIBRARY nlohmann_json)

if(NOT JSON_INCLUDE_DIR OR NOT JSON_LIBRARY)
    message(FATAL_ERROR "nlohmann_json was not found")
endif()

add_library(json_adapter INTERFACE)
target_include_directories(json_adapter INTERFACE "${JSON_INCLUDE_DIR}")
target_link_libraries(json_adapter INTERFACE "${JSON_LIBRARY}")
```

查找结果应支持用户传入 `CMAKE_PREFIX_PATH`、toolchain 或 package registry，而不是把开发机路径硬编码进项目。相关历史记录见 [find_library](#source-posts-title)、[CMake 总览](#source-posts-title) 和 [交叉编译工具链](#source-posts-title)。

## 3. 自定义命令要声明输入输出

构建规则最常见的问题是隐式依赖：文件变了，命令却没有重新运行；命令失败了，构建系统却以为成功。`add_custom_command` 应尽量同时声明 `OUTPUT`、`DEPENDS` 和 `COMMENT`：

```cmake
add_custom_command(
    OUTPUT generated/version.hpp
    COMMAND ${CMAKE_COMMAND}
            -DVERSION=${PROJECT_VERSION}
            -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/write_version.cmake
    DEPENDS cmake/write_version.cmake
    COMMENT "Generating version header"
    VERBATIM
)
add_custom_target(generate_version DEPENDS generated/version.hpp)
add_library(core_dependencies INTERFACE)
add_dependencies(core_dependencies generate_version)
```

生成文件、复制资源、编译代码生成器和打包前检查都可以采用这个模式，但不要把所有逻辑都塞进一个巨大的 `add_custom_target`。

## 4. 安装、导出和测试

一个库要真正被其他项目消费，至少需要：

- `install(TARGETS ...)` 并明确库、运行时和归档目标；
- `install(DIRECTORY ...)` 安装公共头文件；
- `install(EXPORT ...)` 导出 target 配置；
- 提供 `CMakePackageConfigHelpers` 生成的配置文件；
- 用 `find_package(OwnProject CONFIG REQUIRED)` 做消费端测试。

测试应通过 `enable_testing()`、`add_test()` 或 CTest 接入，测试命令不能依赖 IDE 当前打开的工作目录。`CMAKE_CXX_STANDARD` 等全局设置能工作，但 target 级的 `target_compile_features` 更容易表达真实依赖。

## 5. 交叉编译要和本机构建隔离

交叉编译时，工具链文件负责编译器、sysroot 和目标平台；项目逻辑不应通过 `if(CMAKE_HOST_WIN32)` 猜测目标平台。至少记录：

```text
目标架构 / ABI：
编译器与工具链版本：
sysroot：
依赖库来源：
CMake generator：
测试运行方式（原生或 emulator）：
```

[ARM/Linaro 工具链记录](#source-posts-title) 可以作为离线环境的起点，但应在 CI 或干净容器中验证完整 configure、build、install 和 package 流程。

## 6. CPack 是发布流程的一部分

CPack 适合从已经安装的 staging 目录生成压缩包或安装包。推荐流程是：

```text
configure → build → test → install 到 staging → package → 在干净环境安装并运行 smoke test
```

版本信息、依赖清单、许可证和校验值应进入发布元数据，而不是只写在聊天记录里。历史 [CPack 记录](#source-posts-title) 和 [版本文件生成记录](#source-posts-title) 可以作为起点，但不要把开发机绝对路径写进包。

## 7. 交付前检查

- [ ] 新项目是否以 target 为中心传递依赖？
- [ ] 依赖找不到时是否明确失败？
- [ ] 自定义规则是否声明输入、输出和失败传播？
- [ ] 安装后的头文件、库和 CMake 配置是否完整？
- [ ] 交叉编译是否没有误用宿主机库？
- [ ] CTest 是否能在干净环境运行？
- [ ] 安装包能否在另一台机器安装并通过 smoke test？

当这些问题都有答案时，CMake 才从“能在本机编译”变成“能被团队和发布流程依赖”。
