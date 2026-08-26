---
layout: post
title: "Tool-CMake-add_custom_command-copy"
date: 2023-05-09 05:58:00
categories: ["Tool"]
tags: ["CMake", "Tool"]
---

>https://cmake.org/cmake/help/latest/command/add_custom_command.html?highlight=add_custom_command

<!--more-->
```
add_custom_command(TARGET <target>
                   PRE_BUILD | PRE_LINK | POST_BUILD
                   COMMAND command1 [ARGS] [args1...]
                   [COMMAND command2 [ARGS] [args2...] ...]
                   [BYPRODUCTS [files...]]
                   [WORKING_DIRECTORY dir]
                   [COMMENT comment]
                   [VERBATIM] [USES_TERMINAL]
                   [COMMAND_EXPAND_LISTS])
```

## copy
```
add_custom_command(
	TARGET ${CURR_EXE_NAME}
	POST_BUILD
	COMMAND ${CMAKE_COMMAND} ARGS -E copy ${CURR_EXE_NAME} ${PROJECT_BINARY_DIR}
)
```

## copy_directory
