---
layout: post
title: "Tool-CMake-find_library"
date: 2023-05-09 06:09:00
categories: ["Tool"]
tags: ["CMake", "Tool"]
---

>https://cmake.org/cmake/help/latest/command/find_library.html?highlight=find_library

<!--more-->
If nothing is found, the result will be <VAR>-NOTFOUND

## short-hand signature

`find_library (<VAR> name1 [path1 path2 ...])`
## general signature
```
find_library (
          <VAR>
          name | NAMES name1 [name2 ...] [NAMES_PER_DIR]
          [HINTS [path | ENV var]... ]
          [PATHS [path | ENV var]... ]
          [REGISTRY_VIEW (64|32|64_32|32_64|HOST|TARGET|BOTH)]
          [PATH_SUFFIXES suffix1 [suffix2 ...]]
          [VALIDATOR function]
          [DOC "cache documentation string"]
          [NO_CACHE]
          [REQUIRED]
          [NO_DEFAULT_PATH]
          [NO_PACKAGE_ROOT_PATH]
          [NO_CMAKE_PATH]
          [NO_CMAKE_ENVIRONMENT_PATH]
          [NO_SYSTEM_ENVIRONMENT_PATH]
          [NO_CMAKE_SYSTEM_PATH]
          [NO_CMAKE_INSTALL_PREFIX]
          [CMAKE_FIND_ROOT_PATH_BOTH |
           ONLY_CMAKE_FIND_ROOT_PATH |
           NO_CMAKE_FIND_ROOT_PATH]
         )
```

## example
```
unset(LibPath CACHE)
find_library(LibPath 
	NAMES libname
	PATHS ${PROJECT_SOURCE_CIR}
	NO_DEFAULT_PATH
	)
message("LibPath::${LibPath}")

target_link_libraries(${NAME}  ${LibPath})
```