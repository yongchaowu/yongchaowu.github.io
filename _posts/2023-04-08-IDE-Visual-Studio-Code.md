---
layout: post
title: "IDE-Visual Studio Code"
date: 2023-04-08 12:40:00
categories: ["IDE"]
tags: ["C++", "Visual Studio Code", "IDE", "Debug"]
---

Visual Studio Code is a lightweight but powerful source code editor which runs on your desktop and is available for Windows, macOS and Linux. It comes with built-in support for JavaScript, TypeScript and Node.js and has a rich ecosystem of extensions for other languages and runtimes (such as C++, C#, Java, Python, PHP, Go, .NET).

<!--more-->
- [https://code.visualstudio.com/download](https://code.visualstudio.com/download "vscode download")
- [https://code.visualstudio.com/docs](https://code.visualstudio.com/docs "vscode docs")
- [https://code.visualstudio.com/docs/getstarted/tips-and-tricks](https://code.visualstudio.com/docs/getstarted/tips-and-tricks "vscode tips-and-tricks")
- [https://code.visualstudio.com/docs/editor/codebasics](https://code.visualstudio.com/docs/editor/codebasics)
- [https://code.visualstudio.com/docs/editor/debugging](https://code.visualstudio.com/docs/editor/debugging "vscode debug")
- [https://code.visualstudio.com/docs/editor/variables-reference](https://code.visualstudio.com/docs/editor/variables-reference "vscode variables-reference")
- [https://code.visualstudio.com/docs/sourcecontrol/overview](https://code.visualstudio.com/docs/sourcecontrol/overview "vscode git")
- [https://code.visualstudio.com/docs/terminal/basics](https://code.visualstudio.com/docs/terminal/basics "vscode terminal")


----------

- [https://code.visualstudio.com/docs/languages/cpp](https://code.visualstudio.com/docs/languages/cpp "vscode language cpp")
- [https://code.visualstudio.com/docs/cpp/introvideos-cpp](https://code.visualstudio.com/docs/cpp/introvideos-cpp)
- [https://code.visualstudio.com/docs/cpp/cpp-ide](https://code.visualstudio.com/docs/cpp/cpp-ide)
- [https://code.visualstudio.com/docs/cpp/config-mingw](https://code.visualstudio.com/docs/cpp/config-mingw "Using GCC with MinGW")
- [https://code.visualstudio.com/docs/cpp/config-msvc](https://code.visualstudio.com/docs/cpp/config-msvc "Configure VS Code for Microsoft C++")
- [https://code.visualstudio.com/docs/cpp/config-linux](https://code.visualstudio.com/docs/cpp/config-linux "Using C++ on Linux in VS Code")
- [https://code.visualstudio.com/docs/cpp/config-wsl](https://code.visualstudio.com/docs/cpp/config-wsl "Using C++ and WSL in VS Code")

----------

- [https://code.visualstudio.com/docs/cpp/cpp-debug](https://code.visualstudio.com/docs/cpp/cpp-debug "Debug C++ in Visual Studio Code")

- [https://code.visualstudio.com/docs/cpp/launch-json-reference](https://code.visualstudio.com/docs/cpp/launch-json-reference "vscode launch.json")

----------

- [https://code.visualstudio.com/api](https://code.visualstudio.com/api "vscode Extension API")


----------

- KeyBingings - keyboard-shortcuts
 `Ctrl+Shift+P` is bound to Show All Commands
  View > Command Palette
https://code.visualstudio.com/docs/getstarted/keybindings 

- User Interface - Introduction to the basic UI, commands, and features of the VS Code editor.
https://code.visualstudio.com/docs/getstarted/userinterface

- Settings - Customize VS Code for how you like to work.
https://code.visualstudio.com/docs/getstarted/settings

- Extension API - Learn how to write a VS Code extension.
https://code.visualstudio.com/api

## Basic Shortcuts
- Open a folder
 - File > Open Folder (Ctrl+K Ctrl+O)
- File Explorer
 - View > Explorer (Ctrl+Shift+E)
- Search view
 - View > Search (Ctrl+Shift+F)
- Source Control
 - View > Source Control (SCM) (Ctrl+Shift+G)
- Run and Debug
 - View > Run (Ctrl+Shift+D)
- Extensions view
 - View > Extensions (Ctrl+Shift+X)
- Open the Command Palette.
 - View > Command Palette... (Ctrl+Shift+P)
- Output panel
 - View > Output (Ctrl+Shift+U)
- Debug Console
 - View > Debug Console (Ctrl+Shift+Y)
- Problems panel
 - View > Problems (Ctrl+Shift+M)
- Integrated Terminal
 - View > Terminal (Ctrl+`)
- Create a new file
 - File > New File (Ctrl+N)
- Save a file
 - File > Save (Ctrl+S)
- Auto Save
 - File > Auto Save
- Run
 - Run > Start Debugging (F5)
- Programming language extensions
 - Python - IntelliSense, linting, debugging, code formatting, refactoring, and more.
 - Live Preview - Hosts a local server to preview your webpages.
- Zoom
 - Zoom out (Ctrl+-)
 - Zoom in (Ctrl+=)
- Customize your editor with color themes.
 - File > Preferences > Theme > Color Theme (Ctrl+K Ctrl+T)
 - Code > Preferences > Theme > Color Theme on macOS

- Automatically format the source code.
 - Format Document command (Shift+Alt+F)

- Find features and keyboard shortcuts in the Command Palette
 - View > Command Palette... (Ctrl+Shift+P)

- Quick Open recent files or search by filename
 - Ctrl+P to show the Quick Open dropdown
- Go to Line in a file
 - type filename:line number
- Go to Symbol in a file
 - type filename@symbol name
- View Quick Open options
 - type ?

- Quick Open multiple files
 - press Right Arrow to open the selected file but leave the dropdown available
- Multi-cursor selection
 - Alt+Click on Windows and Linux, Option+Click on macOS to add a new cursor
 - Ctrl+Alt+Up Ctrl+Alt+Down to add a new cursor above or below the current position
 - Ctrl+Shift+L to add cursors to all matches of the current selection

- Open the Settings editor
 - File > Preferences > Settings (Ctrl+,)
 - Code > Preferences > Settings on macOS
- Set Format On Type
 - check Editor: Format on Type
- Set Format On Paste
 - check Editor: Format on Paste
- IntelliSense smart code completions
 - trigger IntelliSense with Ctrl+Space

----------

- Column (box) selection
 - select blocks of text by holding Shift+Alt (Shift+Option on macOS) while you drag your mouse.

- Fast scrolling
 - Pressing the Alt key enables fast scrolling in the editor and Explorers. By default, fast scrolling uses a 5X speed multiplier 

- Copy line up / down
 - Shift+Alt+Up or Shift+Alt+Down

- Move line up and down
 - Alt+Up or Alt+Down

- Code formatting
 - Currently selected source code: Ctrl+K Ctrl+F
 - Whole document format: Shift+Alt+F

- Code folding
 - Ctrl+Shift+[ and Ctrl+Shift+]

- IntelliSense
 - `Ctrl+Space` to trigger the Suggestions widget.

- Peek
 - Select a symbol then type Alt+F12
 - use the context menu

- Go to Definition
 - Select a symbol then type F12. Alternatively, you can use the context menu or Ctrl+click (Cmd+click on macOS).
 - You can go back to your previous location with the Go > Back command or Alt+Left.
 - You can also see the type definition if you press Ctrl (Cmd on macOS) when you are hovering over the type

- Go to References
 - Select a symbol then type Shift+F12
 - you can use the context menu.

- Find All References view
 - Select a symbol then type Shift+Alt+F12 to open the References view showing all your file's symbols in a dedicated view.

- Rename Symbol
 - Select a symbol then type F2
 - you can use the context menu.

- Open Markdown preview
 - In a Markdown file, use `Ctrl+Shift+V`

----------
- Debugging
 - Configure debugger
From the Run and Debug view (Ctrl+Shift+D), select create a launch.json file, which will prompt you to select the environment that matches your project (Node.js, Python, C++, etc). This will generate a launch.json file.
 
- Preview mode
 - When you single-click or select a file in the Explorer, it is shown in a preview mode and reuses an existing Tab. This is useful if you are quickly browsing files and don't want every visited file to have its own Tab. 
 - When you start editing the file or use double-click to open the file from the Explorer, a new Tab is dedicated to that file.

## Debugging
### launch.json attributes
use IntelliSense (Ctrl+Space) to see the list of available attributes once you have specified a value for the type attribute.

```json
launch.json

{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "C/C++ Runner: Debug Session",
      "type": "cppdbg",
      "request": "launch",
      "args": [],
      "stopAtEntry": false,
      "externalConsole": true,
      "cwd": "d:/Workspace/VSCode",
      "program": "d:/Workspace/VSCode/build/Debug/outDebug",
      "MIMode": "gdb",
      "miDebuggerPath": "gdb",
      "setupCommands": [
        {
          "description": "Enable pretty-printing for gdb",
          "text": "-enable-pretty-printing",
          "ignoreFailures": true
        }
      ]
    }
  ]
}
```
The following attributes are mandatory for every launch configuration:
- type - the type of debugger to use for this launch configuration. Every installed debug extension introduces a type: node for the built-in Node debugger, for example, or php and go for the PHP and Go extensions.
- request - the request type of this launch configuration. Currently, launch and attach are supported.
- name - the reader-friendly name to appear in the Debug launch configuration dropdown.


Here are some optional attributes available to all launch configurations:
- presentation using the order, group, and hidden attributes in the presentation object, you can sort, group, and hide configurations and compounds in the Debug configuration dropdown and in the Debug quick pick.
- preLaunchTask to launch a task before the start of a debug session, set this attribute to the label of a task specified in tasks.json (in the workspace's .vscode folder). Or, this can be set to ${defaultBuildTask} to use your default build task.
- postDebugTask to launch a task at the very end of a debug session, set this attribute to the name of a task specified in tasks.json (in the workspace's .vscode folder).
- internalConsoleOptions this attribute controls the visibility of the Debug Console panel during a debugging session.
- debugServer for debug extension authors only: this attribute allows you to connect to a specified port instead of launching the debug adapter.
- serverReadyAction if you want to open a URL in a web browser whenever the program under debugging outputs a specific message to the debug console or integrated terminal. For details see section Automatically open a URI when debugging a server program below.


Many debuggers support some of the following attributes:
- program executable or file to run when launching the debugger
- args arguments passed to the program to debug
- env environment variables (the value null can be used to "undefine" a variable)
- envFile path to dotenv file with environment variables
- cwd current working directory for finding dependencies and other files
- port port when attaching to a running process
- stopOnEntry break immediately when the program launches
- console what kind of console to use, for example, internalConsole, integratedTerminal, or externalTerminal

#### Variable substitution
- ${workspaceFolder} gives the root path of a workspace folder 
- ${file} the file open in the active editor
- ${env:Name} the environment variable 'Name'. You can see a full list of predefined variables in the [Variables Reference](https://code.visualstudio.com/docs/editor/variables-reference) or by invoking IntelliSense inside the launch.json string attributes.

#### Platform-specific properties
supports defining values (for example, arguments to be passed to the program) that depend on the operating system where the debugger is running. 

Valid operating properties are "windows" for Windows, "linux" for Linux, and "osx" for macOS. Properties defined in an operating system specific scope override properties defined in the global scope.

Please note that the type property cannot be placed inside a platform-specific section, because type indirectly determines the platform in remote debugging scenarios, and that would result in a cyclic dependency.

#### Predefined variables
The following predefined variables are supported:

- ${userHome} the path of the user's home folder
- ${workspaceFolder} the path of the folder opened in VS Code
- ${workspaceFolderBasename} the name of the folder opened in VS Code without any slashes (/)
- ${file} the current opened file
- ${fileWorkspaceFolder} the current opened file's workspace folder
- ${relativeFile} the current opened file relative to workspaceFolder
- ${relativeFileDirname} the current opened file's dirname relative to workspaceFolder
- ${fileBasename} the current opened file's basename
- ${fileBasenameNoExtension} the current opened file's basename with no file extension
- ${fileExtname} the current opened file's extension
- ${fileDirname} the current opened file's folder path
- ${fileDirnameBasename} the current opened file's folder name
- ${cwd} the task runner's current working directory upon the startup of VS Code
- ${lineNumber} the current selected line number in the active file
- ${selectedText} the current selected text in the active file
- ${execPath} the path to the running VS Code executable
- ${defaultBuildTask} the name of the default build task
- ${pathSeparator} the character used by the operating system to separate components in file paths


Predefined variables examples
Supposing that you have the following requirements:

1. A file located at `/home/your-username/your-project/folder/file.ext` opened in your editor;
2. The directory `/home/your-username/your-project` opened as your root workspace.

So you will have the following values for each variable:
- ${userHome} /home/your-username
- ${workspaceFolder} /home/your-username/your-project
- ${workspaceFolderBasename} your-project
- ${file} /home/your-username/your-project/folder/file.ext
- ${fileWorkspaceFolder} /home/your-username/your-project
- ${relativeFile} folder/file.ext
- ${relativeFileDirname} folder
- ${fileBasename} file.ext
- ${fileBasenameNoExtension} file
- ${fileDirname} /home/your-username/your-project/folder
- ${fileExtname} .ext
- ${lineNumber} line number of the cursor
- ${selectedText} text selected in your code editor
- ${execPath} location of Code.exe
- ${pathSeparator} / on macOS or linux, \ on Windows


### tasks.json
[https://code.visualstudio.com/docs/editor/tasks](https://code.visualstudio.com/docs/editor/tasks "vscode tasks.json")

```json
{
  // See https://go.microsoft.com/fwlink/?LinkId=733558
  // for the documentation about the tasks.json format
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Run tests",
      "type": "shell",
      "command": "./scripts/test.sh",
      "windows": {
        "command": ".\\scripts\\test.cmd"
      },
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

The task's properties have the following semantic:

- label: The task's label used in the user interface.
- type: The task's type. For a custom task, this can either be shell or process. If shell is specified, the command is interpreted as a shell command (for example: bash, cmd, or PowerShell). If process is specified, the command is interpreted as a process to execute.
- command: The actual command to execute.
- windows: Any Windows specific properties. Will be used instead of the default properties when the command is executed on the Windows operating system.
- group: Defines to which group the task belongs. In the example, it belongs to the test group. Tasks that belong to the test group can be executed by running Run Test Task from the Command Palette.
- presentation: Defines how the task output is handled in the user interface. In this example, the Integrated Terminal showing the output is always revealed and a new terminal is created on every task run.
- options: Override the defaults for cwd (current working directory), env (environment variables), or shell (default shell). Options can be set per task but also globally or per platform. Environment variables configured here can only be referenced from within your task script or process and will not be resolved if they are part of your args, command, or other task attributes.
- runOptions: Defines when and how a task is run.

[https://code.visualstudio.com/docs/editor/tasks-appendix](https://code.visualstudio.com/docs/editor/tasks-appendix "tasks.json schema")


### Debug C++ in Visual Studio Code
- [https://code.visualstudio.com/docs/cpp/introvideos-cpp](https://code.visualstudio.com/docs/cpp/introvideos-cpp "Debug C++ in Visual Studio Code")
- [https://code.visualstudio.com/docs/cpp/cpp-ide](https://code.visualstudio.com/docs/cpp/cpp-ide)
- [https://code.visualstudio.com/docs/cpp/config-mingw](https://code.visualstudio.com/docs/cpp/config-mingw "Using GCC with MinGW")
- [https://code.visualstudio.com/docs/cpp/config-msvc](https://code.visualstudio.com/docs/cpp/config-msvc "Configure VS Code for Microsoft C++")
- [https://code.visualstudio.com/docs/cpp/config-linux](https://code.visualstudio.com/docs/cpp/config-linux "Using C++ on Linux in VS Code")
- [https://code.visualstudio.com/docs/cpp/config-wsl](https://code.visualstudio.com/docs/cpp/config-wsl "Using C++ and WSL in VS Code")

----------

- [https://code.visualstudio.com/docs/cpp/cpp-debug](https://code.visualstudio.com/docs/cpp/cpp-debug "Debug C++ in Visual Studio Code")

- [https://code.visualstudio.com/docs/cpp/launch-json-reference](https://code.visualstudio.com/docs/cpp/launch-json-reference "vscode launch.json")

#### Memory dump debugging
The C/C++ extension for VS Code also has the ability to debug memory dumps. To debug a memory dump, open your `launch.json` file and add the `coreDumpPath` (for GDB or LLDB) or `dumpPath` (for the Visual Studio Windows Debugger) property to the C++ Launch configuration, set its value to be a string containing the path to the memory dump. This will even work for x86 programs being debugged on an x64 machine.

#### Additional symbols
If there are additional directories where the debugger can find symbol files (for example, `.pd`b files for the Visual Studio Windows Debugger), they can be specified by adding the `additionalSOLibSearchPath` (for GDB or LLDB) or `symbolSearchPath` (for the Visual Studio Windows Debugger).

For example:
`"additionalSOLibSearchPath": "/path/to/symbols;/another/path/to/symbols" `
or
`"symbolSearchPath": "C:\\path\\to\\symbols;C:\\another\\path\\to\\symbols" `

#### Locate source files
The source file location can be changed if the source files are not located in the compilation location. This is done by simple replacement pairs added in the `sourceFileMap` section. The first match in this list will be used.

For example:
```
"sourceFileMap": {
    "/build/gcc-4.8-fNUjSI/gcc-4.8-4.8.4/build/i686-linux-gnu/libstdc++-v3/include/i686-linux-gnu": "/usr/include/i686-linux-gnu/c++/4.8",
    "/build/gcc-4.8-fNUjSI/gcc-4.8-4.8.4/build/i686-linux-gnu/libstdc++-v3/include": "/usr/include/c++/4.8"
}
```

#### GDB, LLDB, and LLDB-MI Commands (GDB/LLDB)
For the `C++` (GDB/LLDB) debugging environment, you can execute GDB, LLDB and LLDB-MI commands directly through the debug console with the `-exec` command, but be careful, executing commands directly in the debug console is untested and might crash VS Code in some cases.


#### Known limitations
##### Symbols and code navigation
- All platforms:

Because the extension doesn't parse function bodies, Peek Definition and Go to Definition don't work for symbols defined inside the body of a function.

##### Debugging
1. Windows:

- GDB on Cygwin and MinGW cannot break a running process. To set a breakpoint when the application is running (not stopped under the debugger), or to pause the application being debugged, press `Ctrl-C` in the application's terminal.
- GDB on Cygwin cannot open core dumps.

2. Linux:

You may see an error saying: `ptrace: Operation not permitted`. This is due to GDB needing elevated permissions in order to attach to a process. This can be solved using the solutions below:
	1. When using attach to process, you need to provide your password before the debugging session can begin.

	2. To disable this error temporarily, use the following command:`echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope`

	3. To remove the error permanently, add a file called `10-ptrace.conf` to `/etc/sysctl.d/` and add the following `kernel.yama.ptrace_scope = 0`.

3. macOS:

- LLDB:
	- When debugging with LLDB, if the Terminal window is closed while in break mode, debugging does not stop. Debugging can be stopped by pressing the Stop button.
	- When debugging is stopped the Terminal window is not closed.
- GDB:
	- Additional manual install steps are required to use GDB on macOS. See Manual Installation of GDB for OS X in the README.
	- When attaching to a process with GDB, the application being debugged cannot be interrupted. GDB will only bind breakpoints set while the application is not running (either before attaching to the application, or while the application is in a stopped state). This is due to a bug in GDB.
	- Core dumps cannot be loaded when debugging with GDB because GDB does not support the core dump format used in macOS.
	- When attached to a process with GDB, break-all will end the process.