---
layout: post
title: CMake-A Simple CMake Example
date: 2023-04-29 10:12:00
categories:
- Developer Tools
tags:
- CMake
- Tool
---

https://cmake.org/examples/

<!--more-->
There are three directories involved. The top level directory has two subdirectories called ./Demo and ./Hello. In the directory ./Hello, a library is built. In the directory ./Demo, an executable is built by linking to the library. A total of three CMakeLists.txt files are created: one for each directory.
```
./
./Demo
./Hello
```
## top-level directory 

```
./CMakeLists.txt

# CMakeLists files in this project can
# refer to the root source directory of the project as ${HELLO_SOURCE_DIR} and
# to the root binary directory of the project as ${HELLO_BINARY_DIR}.
cmake_minimum_required (VERSION 2.8.11)
project (HELLO)

# Recurse into the "Hello" and "Demo" subdirectories. This does not actually
# cause another cmake executable to run. The same process will walk through
# the project's entire directory structure.
add_subdirectory (Hello)
add_subdirectory (Demo)
```

## subdirectory specified
### ./Hello

```
./Hello/CMakeLists.txt

# Create a library called "Hello" which includes the source file "hello.cxx".
# The extension is already found. Any number of sources could be listed here.
add_library (Hello hello.cxx)

# Make sure the compiler can find include files for our Hello library
# when other libraries or executables link to Hello
target_include_directories (Hello PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
```

### ./Demo

```
./Demo/CMakeLists.txt

# Add executable called "helloDemo" that is built from the source files
# "demo.cxx" and "demo_b.cxx". The extensions are automatically found.
add_executable (helloDemo demo.cxx demo_b.cxx)

# Link the executable to the Hello library. Since the Hello library has
# public include directories we will use those link directories when building
# helloDemo
target_link_libraries (helloDemo LINK_PUBLIC Hello)
```