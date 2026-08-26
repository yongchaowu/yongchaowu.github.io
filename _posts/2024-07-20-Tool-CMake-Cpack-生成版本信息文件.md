---
layout: post
title: "Tool-CMake-Cpack-生成版本信息文件"
date: 2024-07-20 16:30:00
categories: ["Tool"]
tags: ["CMake", "Tool", "CPack"]
---

在使用 CPack 打包过程中自动生成一个文件，其包含存储特定信息，比如版本号或者其他元数据。

<!--more-->
1. 在项目源码目录中创建一个模板文件，如 `info_template`。这个文件将包含想要填充动态信息的占位符。
例如：
    ```plaintext
    Project Name: @PROJECT_NAME@
    Version: @PROJECT_VERSION@
    XXXX: @XXXX@
    ```
注意：其中 `@XXXX@`为CMakeLists.txt中的变量或CMAKE的参数。

2. 使用 `configure_file` 配置信息文件

在 `CMakeLists.txt` 中，使用 `configure_file` 命令基于模板生成实际的 info 文件，并填充相应的变量值。

```cmake
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/info_template
    ${CMAKE_CURRENT_BINARY_DIR}/package_info
    @ONLY
)
```

3. 通过 CPack 包含该文件

确保 CPack 配置时包含了刚生成的 `package_info` 文件。
具体方法取决于你打包的目标格式。以下是针对几种常见格式的例子：

#### 对于 DEB 包:

```cmake
set(CPACK_DEBIAN_PACKAGE_CONTROL_EXTRA "${CMAKE_CURRENT_BINARY_DIR}/package_info")
```

#### 对于 RPM 包:

```cmake
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/package_info DESTINATION /usr/share/doc/${PROJECT_NAME}-${CPACK_PACKAGE_VERSION})
```

#### 对于 ZIP/TGZ 等通用归档格式:

```cmake
install(FILES ${CMAKE_CURRENT_BINARY_DIR}/package_info DESTINATION .)
```

确保安装指令在 `install` 块内，并且 CPACK 配置已经正确设置了对应的包类型和安装规则。

4. 执行 CPack

执行 CPack 命令来生成你的包。确保在 `CMakeLists.txt` 中已经设置了 CPack 相关的基本配置，例如 `CPACK_GENERATOR` 和 `CPACK_PACKAGE_NAME` 等。

```bash
cmake --build . --target package
```

经过上述步骤，生成的包中将包含一个 `package_info` 文件，其中存储了在模板中定义的所有信息。