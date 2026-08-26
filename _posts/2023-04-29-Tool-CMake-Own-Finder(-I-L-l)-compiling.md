---
layout: post
title: CMake-Own Finder(-I -L -l)-compiling
date: 2023-04-29 13:52:00
categories:
- Developer Tools
tags:
- CMake
- Tool
---

What is a finder

<!--more-->
- When compiling a piece of software which 
links to third-party libraries, we need to know:
	- Where to find the .h files (-I in gcc)
	- Where to find the libraries (.so/.dll/.lib/.dylib/...) (-L
in gcc)
	- The filenames of the libraries we want to link to (-l
in gcc)
- That's the basic information a finder needs to 
return
