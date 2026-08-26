---
layout: post
title: "Tool-CMake-OPTION"
date: 2023-04-29 13:26:00
categories: ["Tool"]
tags: ["CMake", "Tool"]
---

>https://clubjuggler.livejournal.com/138364.html

<!--more-->
## includes a component
As an example, consider a project that optionally includes a component that communicates via USB and allows the user, at compile time, to specify whether to include that component or not. 
The CMakeLists.txt file to do that looks like this:
```
PROJECT(myproject)
OPTION(WITH_USB "Include our USB component" OFF)
SET(SRCS file1.c file2.c file3.c)
IF(WITH_USB)
  SET(SRCS ${SRCS} usbfile1.c usbfile2.c)
ENDIF(WITH_USB)
ADD_EXECUTABLE(myproject ${SRCS})
```

The `OPTION(...)` line creates a parameter `WITH_USB` and sets its default value to `OFF`. CMake also includes a help string to describe what the option does. Based on the value of `WITH_USB`, the variable `SRCS` either includes or excludes the two USB-related files `usbfile1.c` and `usbfile2.c`. `SRCS` is then passed to the `ADD_EXECUTABLE` call to define the program’s source files. 
To include USB support, simply enable `WITH_USB` like this:
`$ cmake -DWITH_USB=ON /path/to/source/files`


----------

## the optional USB support a library in a subdirectory

```
PROJECT(myproject)
OPTION(WITH_USB "Include our USB component" OFF)
SET(SRCS file1.c file2.c file3.c)
ADD_EXECUTABLE(myproject ${SRCS})
IF(WITH_USB)
  ADD_SUBDIRECTORY(usblib)
  TARGET_LINK_LIBRARIES(myproject usblib)
ENDIF(WITH_USB)
```
Given this file, the USB source files would be placed in a subdirectory called usblib along with a new CMakeLists.txt file:
```
PROJECT(usblib)
SET(SRCS usbfile1.c usbfile2.c)
ADD_LIBRARY(usblib ${SRCS})
```
Now, if USB support is enabled, CMake builds the USB library and links it into the executable.

### But how does the code know to use the optional USB code?
First, the USB-specific code should be surrounded with a `#ifdef WITH_USB`. 
Next, CMake processes a special configuration file, substituting placeholders with CMake variables.

Let’s make a new file called `config.h.cmake` that contains this:
```
#ifndef TEST_CONFIG_H
#define TEST_CONFIG_H

#cmakedefine WITH_USB

#endif
```

Then, in the `CMakeLists.txt` file, modify the first part to look like this:

```
PROJECT(myproject)
OPTION(WITH_USB "Include our USB component" OFF)
CONFIGURE_FILE(${CMAKE_SOURCE_DIR}/config.h.cmake 
  ${CMAKE_BINARY_DIR}/config.h)
INCLUDE_DIRECTORIES(${CMAKE_SOURCE_DIR} ${CMAKE_BINARY_DIR})
```
Given this, CMake translates `config.h.cmake` to create `config.h` in the build directory. The `INCLUDE_DIRECTORIES` command tells the compiler to add both the source directory and the build directory to the include path. If `WITH_USB` is enabled, CMake replaces `#cmakedefine WITH_USB` with `#define WITH_USB`. Otherwise, it replaces `#cmakedefine WITH_USB` with `/*#undef WITH_USB*/`. As long as you `#include config.h` and surround the USB code with `#ifdef WITH_USB`, everything just works. The only downside at the moment is that `config.h.cmake` must be created manually.
 
