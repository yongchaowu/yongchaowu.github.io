---
layout: post
title: "Tool-CMake-How CMake simplifies the build process by Bruno Abinader"
date: 2023-04-29 12:59:00
categories: ["Tool"]
tags: ["CMake", "Tool"]
---

>https://gitlab.kitware.com/cmake/community/-/wikis/home

<!--more-->
>https://brunoabinader.github.io/2009/12/07/how-cmake-simplifies-the-build-process-part-1-basic-build-system/

>https://brunoabinader.github.io/2009/12/09/how-cmake-simplifies-the-build-process-part-2-advanced-build-system/


----------

## Part 1: Basic build system
https://brunoabinader.github.io/2009/12/07/how-cmake-simplifies-the-build-process-part-1-basic-build-system/

CMake macro `MacroOutOfSourceBuild.cmake` which requires the user to build the source code outside its base directory, ensuring the developer uses a shadow build directory.

### example project
two directories (base directory and src/ directory)
```bash
$ find helloworld
helloworld/
helloworld/src
helloworld/src/main.cpp
helloworld/src/helloworld.cpp
helloworld/src/CMakeLists.txt
helloworld/src/helloworld.h
helloworld/cmake
helloworld/cmake/modules
helloworld/cmake/modules/MacroOutOfSourceBuild.cmake
helloworld/CMakeLists.txt
```

#### helloworld/CMakeLists.txt (base directory)
```
# Project name is not mandatory, but you should use it
project(helloworld)

# States that CMake required version must be greater than 2.6
cmake_minimum_required(VERSION 2.6)

# Appends the cmake/modules path inside the MAKE_MODULE_PATH variable which stores the
# directories of additional CMake modules (ie. MacroOutOfSourceBuild.cmake):
set(CMAKE_MODULE_PATH ${helloworld_SOURCE_DIR}/cmake/modules ${CMAKE_MODULE_PATH})

# The macro below forces the build directory to be different from source directory:
include(MacroOutOfSourceBuild)

macro_ensure_out_of_source_build("${PROJECT_NAME} requires an out of source build.")

add_subdirectory(src)
```

#### helloworld/src/CMakeLists.txt
```
# Include the directory itself as a path to include directories
set(CMAKE_INCLUDE_CURRENT_DIR ON)

# Create a variable called helloworld_SOURCES containing all .cpp files:
set(helloworld_SOURCES helloworld.cpp main.cpp)

# For a large number of source files you can create it in a simpler way
# using file() function:
# file(GLOB hellworld_SOURCES *.cpp)

# Create an executable file called helloworld from sources:
add_executable(helloworld ${helloworld_SOURCES})
```

#### create a shadow build directory (i.e. build/) 
```bash
$ mkdir build
$ cd build
$ cmake ..
-- The C compiler identification is GNU
-- The CXX compiler identification is GNU
-- Check for working C compiler: /usr/bin/gcc
-- Check for working C compiler: /usr/bin/gcc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Configuring done
-- Generating done
-- Build files have been written to: /home/bruno/helloworld/build

$ make
[ 50%] Building CXX object src/CMakeFiles/helloworld.dir/helloworld.cpp.o
[100%] Building CXX object src/CMakeFiles/helloworld.dir/main.cpp.o
Linking CXX executable helloworld
[100%] Built target helloworld
```

----------

## Part 2: Advanced build system
https://brunoabinader.github.io/2009/12/09/how-cmake-simplifies-the-build-process-part-2-advanced-build-system/


#### ./src/CMakeLists.txt
`# Installs the header files into the {build_dir}/include/itemviews-ng directory
install(FILES ${itemviews-ng_HEADERS} DESTINATION include/itemviews-ng)`
 
`# Installs the target file (libitemviews-ng.so) into the {build_dir}/lib directory
install(TARGETS itemviews-ng LIBRARY DESTINATION lib)`

```
set(CMAKE_INCLUDE_CURRENT_DIR ON)

# Create a variable containing a list of all implementation files
file(GLOB itemviews-ng_SOURCES *.cpp)
 
# The same applies for headers which generates MOC files (excluding private implementation ones)
file(GLOB itemviews-ng HEADERS *[^_p].h)
 
# Now the magic happens: The function below is responsible for generating the MOC files)
automoc4_moc_headers(itemviews-ng ${itemviews-ng_HEADERS})
 
# Creates a target itemviews-ng which creates a shard library with the given sources
automoc4_add_library(itemviews-ng SHARED ${itemviews-ng_SOURCES})
 
# Tells the shared library to be linked against Qt ones
target_link_libraries(itemviews-ng ${QT_LIBRARIES})
 
# Installs the header files into the {build_dir}/include/itemviews-ng directory
install(FILES ${itemviews-ng_HEADERS} DESTINATION include/itemviews-ng)
 
# Installs the target file (libitemviews-ng.so) into the {build_dir}/lib directory
install(TARGETS itemviews-ng LIBRARY DESTINATION lib)
```