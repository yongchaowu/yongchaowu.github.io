---
layout: post
title: "Tool-Python package and project manager-uv"
date: 2026-06-02 06:51:00
categories: ["Tool"]
tags: ["Python", "Tool", "uv"]
---

- [Home](https://docs.astral.sh/uv/)
- [GitHub Releases](https://github.com/astral-sh/uv/releases)

<!--more-->
---
An extremely fast Python package and project manager, written in Rust.

Install uv with our official standalone installer:
- Linux/macOS:`curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows:`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`


```shell
~$ uv
An extremely fast Python package manager.

Usage: uv [OPTIONS] <COMMAND>

Commands:
  auth       Manage authentication
  run        Run a command or script
  init       Create a new project
  add        Add dependencies to the project
  remove     Remove dependencies from the project
  version    Read or update the project's version
  sync       Update the project's environment
  lock       Update the project's lockfile
  export     Export the project's lockfile to an alternate format
  tree       Display the project's dependency tree
  format     Format Python code in the project
  audit      Audit the project's dependencies
  tool       Run and install commands provided by Python packages
  python     Manage Python versions and installations
  pip        Manage Python packages with a pip-compatible interface
  venv       Create a virtual environment
  build      Build Python packages into source distributions and wheels
  publish    Upload distributions to an index
  workspace  Inspect uv workspaces
  cache      Manage uv's cache
  self       Manage the uv executable
  help       Display documentation for a command

Cache options:
  -n, --no-cache               Avoid reading from or writing to the cache,
                               instead using a temporary directory for the
                               duration of the operation [env: UV_NO_CACHE=]
      --cache-dir <CACHE_DIR>  Path to the cache directory [env: UV_CACHE_DIR=]

Python options:
      --managed-python       Require use of uv-managed Python versions [env:
                             UV_MANAGED_PYTHON=]
      --no-managed-python    Disable use of uv-managed Python versions [env:
                             UV_NO_MANAGED_PYTHON=]
      --no-python-downloads  Disable automatic downloads of Python. [env:
                             "UV_PYTHON_DOWNLOADS=never"]

Global options:
  -q, --quiet...
          Use quiet output
  -v, --verbose...
          Use verbose output
      --color <COLOR_CHOICE>
          Control the use of color in output [possible values: auto, always,
          never]
      --system-certs
          Whether to load TLS certificates from the platform's native
          certificate store [env: UV_SYSTEM_CERTS=]
      --offline
          Disable network access [env: UV_OFFLINE=]
      --allow-insecure-host <ALLOW_INSECURE_HOST>
          Allow insecure connections to a host [env: UV_INSECURE_HOST=]
      --no-progress
          Hide all progress outputs [env: UV_NO_PROGRESS=]
      --directory <DIRECTORY>
          Change to the given directory prior to running the command [env:
          UV_WORKING_DIR=]
      --project <PROJECT>
          Discover a project in the given directory [env: UV_PROJECT=]
      --config-file <CONFIG_FILE>
          The path to a `uv.toml` file to use for configuration [env:
          UV_CONFIG_FILE=]
      --no-config
          Avoid discovering configuration files (`pyproject.toml`, `uv.toml`)
          [env: UV_NO_CONFIG=]
  -h, --help
          Display the concise help for this command
  -V, --version
          Display the uv version

Use `uv help` for more details.

```

Run a tool in an ephemeral environment using `uvx` (an alias for `uv tool run`)


## Features

### Python versions
Installing and managing Python itself.

- `uv python install`: Install Python versions.
- `uv python list`: View available Python versions.
- `uv python find`: Find an installed Python version.
- `uv python pin`: Pin the current project to use a specific Python version.
- `uv python uninstall`: Uninstall a Python version.

[Installing Python](https://docs.astral.sh/uv/guides/install-python/#next-steps)

### Scripts
Executing standalone Python scripts, e.g., example.py.

- `uv run`: Run a script.
- `uv add --script`: Add a dependency to a script.
- `uv remove --script`: Remove a dependency from a script.

[Running scripts](https://docs.astral.sh/uv/guides/scripts/)

### Projects
Creating and working on Python projects, i.e., with a `pyproject.toml`.

- `uv init`: Create a new Python project.
- `uv add`: Add a dependency to the project.
- `uv remove`: Remove a dependency from the project.
- `uv sync`: Sync the project's dependencies with the environment.
- `uv lock`: Create a lockfile for the project's dependencies.
- `uv run:` Run a command in the project environment.
- `uv tree`: View the dependency tree for the project.
- `uv build`: Build the project into distribution archives.
- `uv publish`: Publish the project to a package index.

[Working on projects](https://docs.astral.sh/uv/guides/projects/)

### Tools
Running and installing tools published to Python package indexes, e.g., ruff or black.

- `uvx / uv tool run`: Run a tool in a temporary environment.
- `uv tool install`: Install a tool user-wide.
- `uv tool uninstall`: Uninstall a tool.
- `uv tool list`: List installed tools.
- `uv tool update-shell`: Update the shell to include tool executables.

[Using tools](https://docs.astral.sh/uv/guides/tools/)

### The pip interface
Manually managing environments and packages — intended to be used in legacy workflows or cases where the high-level commands do not provide enough control.

Creating virtual environments (replacing venv and virtualenv):
- `uv venv`: Create a new virtual environment.

[Using Python environments](https://docs.astral.sh/uv/pip/environments/)

Managing packages in an environment (replacing pip and pipdeptree):

- `uv pip install`: Install packages into the current environment.
- `uv pip show`: Show details about an installed package.
- `uv pip freeze`: List installed packages and their versions.
- `uv pip check`: Check that the current environment has compatible packages.
- `uv pip list`: List installed packages.
- `uv pip uninstall`: Uninstall packages.
- `uv pip tree`: View the dependency tree for the environment.

[Managing packages](https://docs.astral.sh/uv/pip/packages/)


Locking packages in an environment (replacing pip-tools):
- `uv pip compile`: Compile requirements into a lockfile.
- `uv pip sync`: Sync an environment with a lockfile.

[Locking environments](https://docs.astral.sh/uv/pip/compile/)


###  Utility
Managing and inspecting uv's state, such as the cache, storage directories, or performing a self-update:

- `uv cache clean`: Remove cache entries.
- `uv cache prune`: Remove outdated cache entries.
- `uv cache dir`: Show the uv cache directory path.
- `uv tool dir`: Show the uv tool directory path.
- `uv python dir`: Show the uv installed Python versions path.
- `uv self update`: Update uv to the latest version.
