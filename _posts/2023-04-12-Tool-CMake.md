---
layout: post
title: CMake
date: 2023-04-12 22:48:00
categories:
- Developer Tools
tags:
- Tool
- CMake
---

>[https://cmake.org/](https://cmake.org/)
>[https://cmake.org/download/](https://cmake.org/download/ "cmake download")
>[https://cmake.org/documentation/](https://cmake.org/documentation/)
>[https://cmake.org/runningcmake/](https://cmake.org/runningcmake/)
>Book: Mastering CMake 3.1 Edition by Ken Martin (Author), Bill Hoffman (Author)
>[https://github.com/Kitware/CMake](https://github.com/Kitware/CMake)
>

<!--more-->
----------

>[https://gitlab.kitware.com/cmake/community/-/wikis/home](https://gitlab.kitware.com/cmake/community/-/wikis/home)
>[https://cmake.org/cmake/help/latest/index.html](https://cmake.org/cmake/help/latest/index.html)

----------

>[https://cmake.org/cmake/help/latest/guide/tutorial/index.html](https://cmake.org/cmake/help/latest/guide/tutorial/index.html)


## Intro
CMake is an open-source, cross-platform family of tools designed to build, test and package software. CMake is used to control the software compilation process using simple platform and compiler independent configuration files, and generate native makefiles and workspaces that can be used in the compiler environment of your choice. The suite of CMake tools were created by Kitware in response to the need for a powerful, cross-platform build environment for open-source projects such as ITK and VTK.
CMake is part of Kitware’s collection of commercially supported open-source platforms for software development.

----------

In the C/C++ ecosystem, the best tool for project configuration is CMake. CMake allows you to specify the build of a project, in files named CMakeLists.txt, with a simple syntax (much simpler than writing Makefiles). From those files, CMake can generate projects for the most popular IDEs and build systems on different OSs. It is a must-have tool. It is the de-facto standard in the industry for the C/C++ multiplatform and even for single OS development. 

## Building CMake from Scratch
1.UNIX/Mac OSX/MinGW/MSYS/Cygwin
You need to have a C++ compiler (supporting C++11) and a `make` installed. Run the `bootstrap` script you find in the source directory of CMake. You can use the `--help` option to see the supported options. You may use the `--prefix=<install_prefix>` option to specify a custom installation directory for CMake. Once this has finished successfully, run `make` and `make install`.

For example, if you simply want to build and install CMake from source, you can build directly in the source tree:

`$ ./bootstrap && make && sudo make install`
Or, if you plan to develop CMake or otherwise run the test suite, create a separate build tree:
```bash
$ mkdir cmake-build && cd cmake-build
$ ../cmake-source/bootstrap && make
```

2.Windows
There are two ways for building CMake under Windows:

a.Compile with MSVC from VS 2015 or later. You need to download and install a binary release of CMake. You can get these releases from the CMake Download Page. Then proceed with the instructions below for Building CMake with CMake.

b.Bootstrap with MinGW under MSYS2. Download and install MSYS2. Then install the required build tools:

`$ pacman -S --needed git base-devel mingw-w64-x86_64-gcc`
and bootstrap as above.

## Building CMake with CMake
You can build CMake as any other project with a CMake-based build system: run the installed CMake on the sources of this CMake with your preferred options and generators. Then build it and install it. For instructions how to do this, see documentation on [Running CMake](https://cmake.org/runningcmake/).

To build the documentation, install `Sphinx` and configure CMake with `-DSPHINX_HTML=ON` and/or `-DSPHINX_MAN=ON` to enable the "html" or "man" builder. Add `-DSPHINX_EXECUTABLE=/path/to/sphinx-build` if the tool is not found automatically.

## Running CMake
>https://cmake.org/runningcmake/

1. Running CMake for Windows / Microsoft Visual C++ (MSVC)
2. Running CMake on Unix
3. Running CMake from the command line
4. CMake cache

## CMake Wiki
[https://gitlab.kitware.com/cmake/community/-/wikis/home](https://gitlab.kitware.com/cmake/community/-/wikis/home)

## CMake Reference Documentation
[https://cmake.org/cmake/help/latest/index.html](https://cmake.org/cmake/help/latest/index.html)

- User Interaction Guide: build a source code package downloaded from the internet
- Using Dependencies Guide: using a third-party library.
- CMake Tutorial: start a project using CMake
[https://cmake.org/cmake/help/latest/guide/tutorial/index.html](https://cmake.org/cmake/help/latest/guide/tutorial/index.html)

### Command-Line Tools
- cmake(1)
- ctest(1)
- cpack(1)
### Interactive Dialogs
- cmake-gui(1)
- ccmake(1)
### Reference Manuals
- cmake-buildsystem(7)
- cmake-commands(7)
- cmake-compile-features(7)
- cmake-configure-log(7)
- cmake-developer(7)
- cmake-env-variables(7)
- cmake-file-api(7)
- cmake-generator-expressions(7)
- cmake-generators(7)
- cmake-language(7)
- cmake-modules(7)
- cmake-packages(7)
- cmake-policies(7)
- cmake-presets(7)
- cmake-properties(7)
- cmake-qt(7)
- cmake-server(7)
- cmake-toolchains(7)
- cmake-variables(7)
- cpack-generators(7)
### Guides
- CMake Tutorial
- User Interaction Guide
- Using Dependencies Guide
- Importing and Exporting Guide
- IDE Integration Guide


## CMake Tutorial
https://cmake.org/cmake/help/latest/guide/tutorial/index.html

### Build&Run

```bash
mkdir build
cd build
cmake ..
cmake --build .

```

### CMakeLists.txt

#### Step 1: A Basic Starting Point
Exercise 1 - Building a Basic Project
Exercise 2 - Specifying the C++ Standard
Exercise 3 - Adding a Version Number and Configured Header File

```
#/.Tutorial
cmake_minimum_required(VERSION 3.10)

project(Tutorial)
#project(Tutorial VERSION 1.0)
#configure_file(TutorialConfig.h.in TutorialConfig.h)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)


target_include_directories(Tutorial PUBLIC
                           "${PROJECT_BINARY_DIR}"
                           )

add_executable(Tutorial tutorial.cxx)
```

- TutorialConfig.h.in  TutorialConfig.h

```cpp
TutorialConfig.h.in
// the configured options and settings for Tutorial
#define Tutorial_VERSION_MAJOR @Tutorial_VERSION_MAJOR@
#define Tutorial_VERSION_MINOR @Tutorial_VERSION_MINOR@

tutorial.cxx
#include "TutorialConfig.h"
  if (argc < 2) {
    // report version
    std::cout << argv[0] << " Version " << Tutorial_VERSION_MAJOR << "."
              << Tutorial_VERSION_MINOR << std::endl;
    std::cout << "Usage: " << argv[0] << " number" << std::endl;
    return 1;
  }
```

#### Step 2: Adding a Library
Exercise 1 - Creating a Library
Exercise 2 - Making Our Library Optional

```
#MathFunctions library  Tutorial/MathFunctions
add_library(MathFunctions mysqrt.cxx)

add_subdirectory(MathFunctions)

target_link_libraries(Tutorial PUBLIC MathFunctions)

target_include_directories(Tutorial PUBLIC
                          "${PROJECT_BINARY_DIR}"
                          "${PROJECT_SOURCE_DIR}/MathFunctions"
                          )

option(USE_MYMATH "Use tutorial provided math implementation" ON)

if(USE_MYMATH)
  add_subdirectory(MathFunctions)
  list(APPEND EXTRA_LIBS MathFunctions)
  list(APPEND EXTRA_INCLUDES "${PROJECT_SOURCE_DIR}/MathFunctions")
endif()

target_link_libraries(Tutorial PUBLIC ${EXTRA_LIBS})
target_include_directories(Tutorial PUBLIC
                           "${PROJECT_BINARY_DIR}"
                           ${EXTRA_INCLUDES}
                           )

```

- TutorialConfig.h.in tutorial.cxx

```
TutorialConfig.h.in
#cmakedefine USE_MYMATH

tutorial.cxx
#ifdef USE_MYMATH
#  include "MathFunctions.h"
#endif

tutorial.cxx
#ifdef USE_MYMATH
  const double outputValue = mysqrt(inputValue);
#else
  const double outputValue = sqrt(inputValue);
#endif
```

#### Step 3: Adding Usage Requirements for a Library
Exercise 1 - Adding Usage Requirements for a Library
```
MathFunctions/CMakeLists.txt
target_include_directories(MathFunctions
          INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}
          )

CMakeLists.txt
if(USE_MYMATH)
  add_subdirectory(MathFunctions)
  list(APPEND EXTRA_LIBS MathFunctions)
endif()

CMakeLists.txt
target_include_directories(Tutorial PUBLIC
                           "${PROJECT_BINARY_DIR}"
                           )
```

#### Step 4: Adding Generator Expressions
Exercise 1 - Setting the C++ Standard with Interface Libraries
Exercise 2 - Adding Compiler Warning Flags with Generator Expressions


```
CMakeLists.txt
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

CMakeLists.txt
add_library(tutorial_compiler_flags INTERFACE)
target_compile_features(tutorial_compiler_flags INTERFACE cxx_std_11)

CMakeLists.txt
target_link_libraries(Tutorial PUBLIC ${EXTRA_LIBS} tutorial_compiler_flags)

MathFunctions/CMakeLists.txt
target_link_libraries(MathFunctions tutorial_compiler_flags)
```

```
CMakeLists.txt
cmake_minimum_required(VERSION 3.15)

CMakeLists.txt
set(gcc_like_cxx "$<COMPILE_LANG_AND_ID:CXX,ARMClang,AppleClang,Clang,GNU,LCC>")
set(msvc_cxx "$<COMPILE_LANG_AND_ID:CXX,MSVC>")

target_compile_options(tutorial_compiler_flags INTERFACE
  "$<${gcc_like_cxx}:-Wall;-Wextra;-Wshadow;-Wformat=2;-Wunused>"
  "$<${msvc_cxx}:-W3>"
)

 CMakeLists.txt
target_compile_options(tutorial_compiler_flags INTERFACE
  "$<${gcc_like_cxx}:$<BUILD_INTERFACE:-Wall;-Wextra;-Wshadow;-Wformat=2;-Wunused>>"
  "$<${msvc_cxx}:$<BUILD_INTERFACE:-W3>>"
)
```

#### Step 5: Installing and Testing
Exercise 1 - Install Rules
Exercise 2 - Testing Support

```bash
cmake --install .
cmake --install . --config Release
cmake --build . --target install --config Debug
cmake --install . --prefix "/home/myuser/installdir"
#CMAKE_INSTALL_PREFIX
```

```
MathFunctions/CMakeLists.txt
set(installable_libs MathFunctions tutorial_compiler_flags)
install(TARGETS ${installable_libs} DESTINATION lib)

MathFunctions/CMakeLists.txt
install(FILES MathFunctions.h DESTINATION include)


CMakeLists.txt
install(TARGETS Tutorial DESTINATION bin)
install(FILES "${PROJECT_BINARY_DIR}/TutorialConfig.h"
  DESTINATION include
  )
```


```bash
ctest -N 
ctest -VV
ctest -C <mode>
ctest -C Debug -VV

CMakeLists.txt
enable_testing()

add_test(NAME Runs COMMAND Tutorial 25)


add_test(NAME Usage COMMAND Tutorial)
set_tests_properties(Usage
  PROPERTIES PASS_REGULAR_EXPRESSION "Usage:.*number"
  )


add_test(NAME StandardUse COMMAND Tutorial 4)
set_tests_properties(StandardUse
  PROPERTIES PASS_REGULAR_EXPRESSION "4 is 2"
  )


function(do_test target arg result)
  add_test(NAME Comp${arg} COMMAND ${target} ${arg})
  set_tests_properties(Comp${arg}
    PROPERTIES PASS_REGULAR_EXPRESSION ${result}
    )
endfunction()

# do a bunch of result based tests
do_test(Tutorial 4 "4 is 2")
do_test(Tutorial 9 "9 is 3")
do_test(Tutorial 5 "5 is 2.236")
do_test(Tutorial 7 "7 is 2.645")
do_test(Tutorial 25 "25 is 5")
do_test(Tutorial -25 "-25 is (-nan|nan|0)")
```

#### Step 6: Adding Support for a Testing Dashboard
Exercise 1 - Send Results to a Testing Dashboard

```
CTestConfig.cmake
set(CTEST_PROJECT_NAME "CMakeTutorial")
set(CTEST_NIGHTLY_START_TIME "00:00:00 EST")

set(CTEST_DROP_METHOD "http")
set(CTEST_DROP_SITE "my.cdash.org")
set(CTEST_DROP_LOCATION "/submit.php?project=CMakeTutorial")
set(CTEST_DROP_SITE_CDASH TRUE)
##############################################
ctest [-VV] -D Experimental
ctest [-VV] -C Debug -D Experimental
https://my.cdash.org/index.php?project=CMakeTutorial

CMakeLists.txt
include(CTest)
```

#### Step 7: Adding System Introspection
Exercise 1 - Assessing Dependency Availability
```cpp
MathFunctions/CMakeLists.txt
include(CheckCXXSourceCompiles)

MathFunctions/CMakeLists.txt
check_cxx_source_compiles("
  #include <cmath>
  int main() {
    std::log(1.0);
    return 0;
  }
" HAVE_LOG)
check_cxx_source_compiles("
  #include <cmath>
  int main() {
    std::exp(1.0);
    return 0;
  }
" HAVE_EXP)


MathFunctions/CMakeLists.txt
if(HAVE_LOG AND HAVE_EXP)
  target_compile_definitions(MathFunctions
                             PRIVATE "HAVE_LOG" "HAVE_EXP")
endif()


MathFunctions/mysqrt.cxx
#include <cmath>

MathFunctions/mysqrt.cxx
#if defined(HAVE_LOG) && defined(HAVE_EXP)
  double result = std::exp(std::log(x) * 0.5);
  std::cout << "Computing sqrt of " << x << " to be " << result
            << " using log and exp" << std::endl;
#else
  double result = x;

```

#### Step 8: Adding a Custom Command and Generated File
```cpp
MathFunctions/CMakeLists.txt
add_executable(MakeTable MakeTable.cxx)

MathFunctions/CMakeLists.txt
add_custom_command(
  OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/Table.h
  COMMAND MakeTable ${CMAKE_CURRENT_BINARY_DIR}/Table.h
  DEPENDS MakeTable
  )

MathFunctions/CMakeLists.txt
add_library(MathFunctions
            mysqrt.cxx
            ${CMAKE_CURRENT_BINARY_DIR}/Table.h
            )
target_include_directories(MathFunctions
          INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}
          PRIVATE   ${CMAKE_CURRENT_BINARY_DIR}
          )

# link our compiler flags interface library
target_link_libraries(MathFunctions tutorial_compiler_flags)



MathFunctions/mysqrt.cxx
double mysqrt(double x)
{
  if (x <= 0) {
    return 0;
  }

  // use the table to help find an initial value
  double result = x;
  if (x >= 1 && x < 10) {
    std::cout << "Use the table to help find an initial value " << std::endl;
    result = sqrtTable[static_cast<int>(x)];
  }

  // do ten iterations
  for (int i = 0; i < 10; ++i) {
    if (result <= 0) {
      result = 0.1;
    }
    double delta = x - (result * result);
    result = result + 0.5 * delta / result;
    std::cout << "Computing sqrt of " << x << " to be " << result << std::endl;
  }

  return result;
}
```

#### Step 9: Packaging an Installer
```bash
CMakeLists.txt
include(InstallRequiredSystemLibraries)
set(CPACK_RESOURCE_FILE_LICENSE "${CMAKE_CURRENT_SOURCE_DIR}/License.txt")
set(CPACK_PACKAGE_VERSION_MAJOR "${Tutorial_VERSION_MAJOR}")
set(CPACK_PACKAGE_VERSION_MINOR "${Tutorial_VERSION_MINOR}")
set(CPACK_SOURCE_GENERATOR "TGZ")
include(CPack)

cpack
cpack -G ZIP -C Debug

cpack --config CPackSourceConfig.cmake


make package
right click the Package target and Build Project from an IDE.
```

#### Step 10: Selecting Static or Shared Libraries
```
CMakeLists.txt
cmake_minimum_required(VERSION 3.15)

# set the project name and version
project(Tutorial VERSION 1.0)

# specify the C++ standard
add_library(tutorial_compiler_flags INTERFACE)
target_compile_features(tutorial_compiler_flags INTERFACE cxx_std_11)

# add compiler warning flags just when building this project via
# the BUILD_INTERFACE genex
set(gcc_like_cxx "$<COMPILE_LANG_AND_ID:CXX,ARMClang,AppleClang,Clang,GNU,LCC>")
set(msvc_cxx "$<COMPILE_LANG_AND_ID:CXX,MSVC>")
target_compile_options(tutorial_compiler_flags INTERFACE
  "$<${gcc_like_cxx}:$<BUILD_INTERFACE:-Wall;-Wextra;-Wshadow;-Wformat=2;-Wunused>>"
  "$<${msvc_cxx}:$<BUILD_INTERFACE:-W3>>"
)

# control where the static and shared libraries are built so that on windows
# we don't need to tinker with the path to run the executable
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${PROJECT_BINARY_DIR}")

option(BUILD_SHARED_LIBS "Build using shared libraries" ON)

# configure a header file to pass the version number only
configure_file(TutorialConfig.h.in TutorialConfig.h)

# add the MathFunctions library
add_subdirectory(MathFunctions)

# add the executable
add_executable(Tutorial tutorial.cxx)
target_link_libraries(Tutorial PUBLIC MathFunctions tutorial_compiler_flags)

```

----------
```
MathFunctions/CMakeLists.txt
# add the library that runs
add_library(MathFunctions MathFunctions.cxx)

# state that anybody linking to us needs to include the current source dir
# to find MathFunctions.h, while we don't.
target_include_directories(MathFunctions
                           INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}
                           )

# should we use our own math functions
option(USE_MYMATH "Use tutorial provided math implementation" ON)
if(USE_MYMATH)

  target_compile_definitions(MathFunctions PRIVATE "USE_MYMATH")

  # first we add the executable that generates the table
  add_executable(MakeTable MakeTable.cxx)
  target_link_libraries(MakeTable PRIVATE tutorial_compiler_flags)

  # add the command to generate the source code
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/Table.h
    COMMAND MakeTable ${CMAKE_CURRENT_BINARY_DIR}/Table.h
    DEPENDS MakeTable
    )

  # library that just does sqrt
  add_library(SqrtLibrary STATIC
              mysqrt.cxx
              ${CMAKE_CURRENT_BINARY_DIR}/Table.h
              )

  # state that we depend on our binary dir to find Table.h
  target_include_directories(SqrtLibrary PRIVATE
                             ${CMAKE_CURRENT_BINARY_DIR}
                             )

  target_link_libraries(SqrtLibrary PUBLIC tutorial_compiler_flags)
  target_link_libraries(MathFunctions PRIVATE SqrtLibrary)
endif()

target_link_libraries(MathFunctions PUBLIC tutorial_compiler_flags)

# define the symbol stating we are using the declspec(dllexport) when
# building on windows
target_compile_definitions(MathFunctions PRIVATE "EXPORTING_MYMATH")

# install libs
set(installable_libs MathFunctions tutorial_compiler_flags)
if(TARGET SqrtLibrary)
  list(APPEND installable_libs SqrtLibrary)
endif()
install(TARGETS ${installable_libs} DESTINATION lib)
# install include headers
install(FILES MathFunctions.h DESTINATION include)
```

----------

```cpp
MathFunctions/mysqrt.cxx
#include <iostream>

#include "MathFunctions.h"

// include the generated table
#include "Table.h"

namespace mathfunctions {
namespace detail {
// a hack square root calculation using simple operations
double mysqrt(double x)
{
  if (x <= 0) {
    return 0;
  }

  // use the table to help find an initial value
  double result = x;
  if (x >= 1 && x < 10) {
    std::cout << "Use the table to help find an initial value " << std::endl;
    result = sqrtTable[static_cast<int>(x)];
  }

  // do ten iterations
  for (int i = 0; i < 10; ++i) {
    if (result <= 0) {
      result = 0.1;
    }
    double delta = x - (result * result);
    result = result + 0.5 * delta / result;
    std::cout << "Computing sqrt of " << x << " to be " << result << std::endl;
  }

  return result;
}
}
}

```


----------
```
MathFunctions/MathFunctions.h
#if defined(_WIN32)
#  if defined(EXPORTING_MYMATH)
#    define DECLSPEC __declspec(dllexport)
#  else
#    define DECLSPEC __declspec(dllimport)
#  endif
#else // non windows
#  define DECLSPEC
#endif

namespace mathfunctions {
double DECLSPEC sqrt(double x);
}
```
```
MathFunctions/CMakeLists.txt
  # state that SqrtLibrary need PIC when the default is shared libraries
  set_target_properties(SqrtLibrary PROPERTIES
                        POSITION_INDEPENDENT_CODE ${BUILD_SHARED_LIBS}
                        )
```

#### Step 11: Adding Export Configuration

```
MathFunctions/CMakeLists.txt
set(installable_libs MathFunctions tutorial_compiler_flags)
if(TARGET SqrtLibrary)
  list(APPEND installable_libs SqrtLibrary)
endif()
install(TARGETS ${installable_libs}
        EXPORT MathFunctionsTargets
        DESTINATION lib)
# install include headers
install(FILES MathFunctions.h DESTINATION include)


CMakeLists.txt
install(EXPORT MathFunctionsTargets
  FILE MathFunctionsTargets.cmake
  DESTINATION lib/cmake/MathFunctions
)


MathFunctions/CMakeLists.txt
target_include_directories(MathFunctions
                           INTERFACE
                            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
                            $<INSTALL_INTERFACE:include>
                           )


Config.cmake.in

@PACKAGE_INIT@

include ( "${CMAKE_CURRENT_LIST_DIR}/MathFunctionsTargets.cmake" )


CMakeLists.txt
install(EXPORT MathFunctionsTargets
  FILE MathFunctionsTargets.cmake
  DESTINATION lib/cmake/MathFunctions
)

include(CMakePackageConfigHelpers)





CMakeLists.txt
install(EXPORT MathFunctionsTargets
  FILE MathFunctionsTargets.cmake
  DESTINATION lib/cmake/MathFunctions
)

include(CMakePackageConfigHelpers)
# generate the config file that includes the exports
configure_package_config_file(${CMAKE_CURRENT_SOURCE_DIR}/Config.cmake.in
  "${CMAKE_CURRENT_BINARY_DIR}/MathFunctionsConfig.cmake"
  INSTALL_DESTINATION "lib/cmake/example"
  NO_SET_AND_CHECK_MACRO
  NO_CHECK_REQUIRED_COMPONENTS_MACRO
  )


CMakeLists.txt
write_basic_package_version_file(
  "${CMAKE_CURRENT_BINARY_DIR}/MathFunctionsConfigVersion.cmake"
  VERSION "${Tutorial_VERSION_MAJOR}.${Tutorial_VERSION_MINOR}"
  COMPATIBILITY AnyNewerVersion
)



install(FILES
  ${CMAKE_CURRENT_BINARY_DIR}/MathFunctionsConfig.cmake
  ${CMAKE_CURRENT_BINARY_DIR}/MathFunctionsConfigVersion.cmake
  DESTINATION lib/cmake/MathFunctions
  )


```

```
export(EXPORT MathFunctionsTargets
  FILE "${CMAKE_CURRENT_BINARY_DIR}/MathFunctionsTargets.cmake"
)
```

#### Step 12: Packaging Debug and Release
```bash
CMakeLists.txt
set(CMAKE_DEBUG_POSTFIX d)

add_library(tutorial_compiler_flags INTERFACE)


CMakeLists.txt
add_executable(Tutorial tutorial.cxx)
set_target_properties(Tutorial PROPERTIES DEBUG_POSTFIX ${CMAKE_DEBUG_POSTFIX})

target_link_libraries(Tutorial PUBLIC MathFunctions tutorial_compiler_flags)


MathFunctions/CMakeLists.txt
set_property(TARGET MathFunctions PROPERTY VERSION "1.0.0")
set_property(TARGET MathFunctions PROPERTY SOVERSION "1")

create debug and release subdirectories
- Step12
   - debug
   - release

cd debug
cmake -DCMAKE_BUILD_TYPE=Debug ..
cmake --build .
cd ../release
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build .
```

----------
```
MultiCPackConfig.cmake
include("release/CPackConfig.cmake")

set(CPACK_INSTALL_CMAKE_PROJECTS
    "debug;Tutorial;ALL;/"
    "release;Tutorial;ALL;/"
)

cpack --config MultiCPackConfig.cmake
```