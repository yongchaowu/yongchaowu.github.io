---
layout: post
title: "Anaconda 与 Conda 入门：发行版、Channels、环境复现与版本敏感点"
display_title: "Anaconda 与 Conda 入门：发行版、Channels、环境复现与版本敏感点"
summary: "讲清 Anaconda / Conda / Miniconda / Miniforge 的区别，逐个走完 Channels、包管理、环境创建与重命名、environment.yml 生命周期、Shell 初始化、镜像与 IDE 集成，并单列一张版本敏感功能速查表（auto_activate、增强版 conda export、多平台锁文件等），以 2026-09-25 的官方 latest 文档为核对基线。"
lang: zh-CN
date: 2026-09-27 10:00:00
categories:
  - Developer Tools
  - Programming
tags:
  - "Anaconda"
  - "Conda"
  - "Python"
  - "环境管理"
  - "虚拟环境"
  - "Shell"
  - "Linux"
---

<!--more-->


> 本文根据 `ref/anacoda-introduce.md` 整理，介绍 Anaconda、Miniconda、Miniforge、Channels、包管理、环境复现、Shell 初始化、镜像和 IDE 集成。

Anaconda 和 Conda 经常一起出现，但它们并不是同一个概念：

- **Anaconda Distribution** 是面向科学计算和数据分析的 Python 发行版，预装 Conda、Python、Anaconda Navigator 以及大量常用包。
- **Conda** 是一个跨平台的软件包和 Python 环境管理工具。它不仅能管理 Python 包，也能管理 Python、编译工具、CUDA Runtime 等非 Python 软件。
- **Miniconda** 和 **Miniforge** 是更精简的发行版；前者由 Anaconda 维护并默认使用 `defaults`，后者由 conda-forge 社区维护并默认使用 `conda-forge`。

> 提示：Conda 的命令、配置项和求解器会随版本变化。本文以 **2026-09-25 的 Conda 官方 latest 文档**为核对基线；截至该日期，正式发布的 Conda 最新版本为 26.7.x，文档中提前描述的 26.9+ 功能仍应视为前瞻信息。命令未在所有操作系统和发行版上逐一执行。实际使用前请检查本机版本：
>
> ```bash
> conda --version
> conda info
> conda <command> --help
> ```
>
> 对长期维护的文档，应以本机帮助输出和[官方文档](https://docs.conda.io/projects/conda/en/latest/)为准。

## 版本敏感功能速查

| 功能 | 最低版本或说明 |
| --- | --- |
| `auto_activate`、`conda init --condabin` | Conda 25.5+；旧键 `auto_activate_base` 已于 26.3 移除 |
| 增强版 `conda export` | Conda 25.7+ |
| `conda create --file environment.yml`，以及用 `--name`/`--prefix` 覆盖 YAML 中的 `name` | Conda 26.3+；旧版本使用 `conda env create -f` |
| `custom_multichannels.defaults`、`conda doctor --fix`、`conda run -s` | Conda 26.1+ |
| 原生多平台锁文件 | Conda 26.5+ |
| `conda-pypi` | 官方文档标记为 Conda 26.9+ 的前瞻功能，基线时点尚未正式发布；并要求 Rattler solver |

## 快速开始

下面是一条适合开发项目的最短路径；下载和安装发行版后即可开始：

```bash
# 创建独立环境
conda create -n myapp python=3.12
conda activate myapp

# 安装项目依赖
conda install numpy

# 导出一个便于维护的 Conda 规格
conda env export --from-history > environment.from-history.yml
```

`--from-history` 不会导出普通 pip 依赖，也不会覆盖原有 `pip:` 区域。它通常仍会写入本机 `prefix:`；检查并删除该行后，再与项目的 `requirements.txt` 或现有 `environment.yml` 合并。使用 26.3+ 的 `conda create --file` 时，如果文件保留了 `prefix:` 而命令行没有 `-n` 或 `-p`，该路径可能被当作目标环境路径。

## 1. 选择发行版

### 1.1 Anaconda、Miniconda 和 Miniforge

| 发行版 | 默认 Channel | 特点 | 适合场景 |
| --- | --- | --- | --- |
| Anaconda Distribution | `defaults` | 预装大量科学计算包，并提供 Navigator 图形界面 | 教学、学习和快速体验数据科学工具 |
| Miniconda | `defaults` | 只预装 Python、Conda 及必要依赖 | 熟悉命令行、需要官方默认仓库的通用环境 |
| Miniforge | `conda-forge` | 精简，并提供 Conda 和 Mamba；默认不使用 `defaults` | 开源项目、服务器、CI 和希望明确使用 conda-forge 的环境 |

下载入口：

- [Anaconda Distribution](https://www.anaconda.com/download)
- [Miniconda](https://docs.anaconda.com/miniconda/)
- [Miniforge](https://conda-forge.org/download/)
- [PyCharm](https://www.jetbrains.com/zh-cn/pycharm/)

Anaconda 官方仓库（`defaults`）受 [Anaconda 服务条款](https://www.anaconda.com/legal/terms-of-service)约束。商业或组织使用前应先确认适用条款；安装 Miniconda 并不代表使用 `defaults` 时可以忽略这些条款。Miniforge 默认不访问 `defaults`，除非用户主动添加。

> Mambaforge 已于 2024 年弃用，并于 2025 年停止发布；新安装应选择 Miniforge。

### 1.2 不要把发行版和 Channel 混为一谈

- 安装 Miniconda 后，可以改用 `conda-forge`。
- 安装 Miniforge 后，也可以按需添加其他 Channel。
- 发行版决定初始安装内容和默认配置，Channel 决定后续软件包从哪里获取。
- Channel 混用可能产生 ABI 不兼容，不能仅靠“安装体积更小”判断哪个发行版更安全或更稳定。

### 1.3 安装路径和平台

- Windows 安装路径尽量避免空格、中文和特殊字符。
- Apple Silicon 优先使用原生 `osx-arm64` 构建；在 Rosetta 终端中运行时可使用 `osx-64`，但不要无意混用两种架构。
- 常见 Linux 架构分别对应 `linux-64` 和 `linux-aarch64`。
- 使用 `conda info` 查看当前平台、架构和环境目录。

可以在创建时显式指定目标平台：

```bash
conda create --platform osx-arm64 --name native-arm python=3.11
```

跨操作系统创建环境可能缺少虚拟包信息或发生文件布局不兼容；除 `--dry-run`、导出锁文件等场景外，不建议为了“跨平台”强行创建与当前主机不一致的环境。

## 2. Conda Channels

Channel（频道）是存放 Conda 软件包的位置。Conda 安装、更新或搜索软件包时，会按照配置的 Channel 列表进行查询。

常见公共 Channel 包括：

| Channel | 说明 |
| --- | --- |
| `defaults` | 内置的多 Channel 集合，通常包含 Anaconda 官方维护的 `main`、`r`，以及 Windows 上的 `msys2` |
| `conda-forge` | 社区维护的 Channel，包含大量 Python、R、GPU 和科学计算相关构建 |
| `bioconda` | 面向生物信息学软件包的社区 Channel，通常与 `conda-forge` 配合使用 |
| `pytorch` | PyTorch 官方维护的 Conda Channel，具体可用版本应查询 PyTorch 官方文档 |

原始笔记中的 `community` 不是一个固定的 Channel 名称；通常指 `conda-forge`、`bioconda` 这类社区维护渠道。

### 2.1 查看当前 Channel

```bash
conda config --show channels
conda config --show channel_priority
conda config --show-sources
```

`--show-sources` 会显示配置的来源及优先级，排查“本机配置为什么与文档不同”时非常有用。

### 2.2 选择一个默认 Channel

Conda 官方当前建议将 `defaults` 和 `conda-forge` **二选一**作为默认来源，而不是长期放在同一个列表中混用。

只使用 conda-forge：

```yaml
channels:
  - conda-forge
  - nodefaults
```

只使用 Anaconda 官方仓库：

```yaml
channels:
  - defaults
```

如果确实必须混用 Channel，可以启用严格优先级：

```yaml
channel_priority: strict
```

`strict` 的含义是：某个包如果出现在高优先级 Channel 中，就不会再从低优先级 Channel 选择同名包。它可以降低混用风险，但也可能使原本可解的环境变成无解。

Conda 的默认 `channel_priority` 是 `flexible`；`disabled` 会忽略 Channel 优先级并优先选择版本，通常不建议在可复现环境中使用。

### 2.3 添加、调整和删除 Channel

```bash
# 添加到 Channel 列表开头
conda config --add channels conda-forge

# 等价写法
conda config --prepend channels conda-forge

# 添加到 Channel 列表末尾
conda config --append channels some-channel

# 删除一个 Channel 值
conda config --remove channels conda-forge
```

如果只是临时从某个 Channel 安装，可以不修改全局配置：

```bash
conda install -c conda-forge websocket-client
```

如果希望该包及其依赖都只从指定 Channel 解析：

```bash
conda install -c conda-forge --override-channels websocket-client
```

也可以只指定某个包的来源，但依赖仍会从已配置的其他 Channel 解析：

```bash
conda install conda-forge::websocket-client
```

后一种方式在 Channel 不兼容时仍可能产生混用问题，应谨慎使用。

### 2.4 环境级配置

先激活目标环境，再使用 `--env` 将配置写入该环境的 `$CONDA_PREFIX/.condarc`：

```bash
conda activate demo
conda config --env --prepend channels conda-forge
conda config --env --set channel_priority strict
conda config --show-sources
```

环境级配置只对当前机器上的这个环境生效，不能替代需要提交和共享的 `environment.yml`。如果没有激活环境就使用 `conda config --env`，Conda 可能退回写入用户级配置。

## 3. 软件包管理

### 3.1 查看 Conda、当前环境和软件包

```bash
conda --version
conda info
conda list
conda env list
```

查看未激活环境中的软件包：

```bash
conda list -n demo
```

查看依赖信息：

```bash
conda search numpy --info
```

### 3.2 搜索软件包

```bash
conda search numpy
conda search -c conda-forge websocket-client
```

只搜索指定 Channel 和当前平台：

```bash
conda search -c conda-forge --override-channels websocket-client
```

软件包名称、版本、构建、Python 版本和可用平台都会随 Channel 与时间变化。长期文档不应依赖一个已经过时的固定版本示例。

### 3.3 安装软件包

```bash
conda install numpy
conda install "numpy>=1.26"
conda install scipy pandas
conda install grpcio-tools tensorboard websocket-client
```

指定 Channel：

```bash
conda install -c conda-forge websocket-client
```

安装一组已知存在兼容性关系的软件包时，尽量在同一次事务中安装，让求解器看到完整约束：

```bash
conda install python=3.11 numpy scipy
```

PyTorch、TensorFlow 等框架对 Python、CUDA 和构建版本有严格组合要求，应优先使用项目官方安装器生成的命令，不要从多个不兼容的 Channel 随意拼接依赖。

### 3.4 更新

```bash
# 更新当前环境中的指定包
conda update numpy

# 更新 base 中的 Conda
conda update -n base conda

# 预览环境整体更新计划
conda update --all --dry-run

# 执行环境整体更新
conda update --all
```

`conda update --all` 只会在现有 Channel 和版本约束允许的范围内更新。执行前建议导出环境规格或显式规格，重要环境应准备重建方案。

### 3.5 使用修订历史回滚

Conda 会记录由 Conda 事务造成的环境修订：

```bash
conda list -n demo --revisions
conda install -n demo --revision 2
```

修订历史不能完整撤销普通 pip、文件修改或环境外操作；重要环境仍应保留声明式规格或锁文件。

## 4. 创建和管理环境

建议为不同项目创建独立环境，并尽量不要把项目依赖安装到 `base` 中。

`base` 主要用于运行 Conda 自身、创建和维护环境，以及安装少量环境管理工具。项目依赖应属于各自的项目环境：

```text
base
├── project-a-env
└── project-b-env
```

这样可以避免不同项目互相升级、卸载或覆盖同一包。

```bash
# 创建指定 Python 版本的环境
conda create --name demo python=3.11

# 激活和退出
conda activate demo
conda deactivate

# 查看环境及路径
conda env list

# 删除环境
conda env remove --name demo

# 重命名环境
conda rename --name demo demo-old
```

### 4.1 使用 `--prefix` 创建项目本地环境

使用 `--prefix` 可以把环境放在项目目录中：

```bash
conda create --prefix ./.conda-env python=3.11
conda activate ./.conda-env
```

也可以让 `--prefix` 覆盖环境文件中的 `name`（Conda 26.3+）：

```bash
conda create --prefix ./.conda-env --file environment.yml
```

注意：

- 路径环境在列表中通常显示为完整路径，不能再用 `--name` 直接引用。
- 解释器位于 `./.conda-env/bin/python`（macOS/Linux）或 `./.conda-env/python.exe`（Windows）。
- 必须把整个环境目录加入 `.gitignore`，不要提交到版本库。
- 项目迁移时应重新创建环境，而不是直接复制包含绝对路径的环境目录。

### 4.2 创建、克隆和运行

也可以在创建时一次安装多个包：

```bash
conda create --name demo python=3.11 numpy scipy
```

克隆一个 Conda 环境：

```bash
conda create --name demo-copy --clone demo
```

克隆适合快速复制本机环境，但不应替代项目规格或锁文件；尤其是需要迁移到其他机器、操作系统或架构时，应使用导出文件。

`conda rename` 主要更新 Conda 自身记录的环境名称，不会自动更新所有外部引用，例如已注册的 Jupyter Kernel、定时任务或硬编码解释器路径。重要环境优先使用“导出规格后重建”。

不激活环境，直接运行其中的一条命令：

```bash
conda run -n demo python script.py
```

## 5. `environment.yml` 的完整生命周期

### 5.1 创建 `environment.yml`

建议每个项目只选择一个主要 Channel，并显式记录 pip 依赖：

```yaml
name: demo
channels:
  - conda-forge
  - nodefaults
dependencies:
  - python=3.11
  - numpy
  - pip
  - pip:
      - requests
```

根据文件创建环境：

```bash
conda create --file environment.yml
conda activate demo
```

> Conda 26.3 及之后支持并推荐使用 `conda create --file environment.yml`。更早的 Conda 应使用：
>
> ```bash
> conda env create -f environment.yml
> ```
>
> 当前版本仍保留 `conda env create` 以兼容已有脚本。命令行传入 `--name` 或 `--prefix` 时，它们会覆盖文件中的 `name`。

更新已有环境，并在不再需要某些依赖时移除它们：

```bash
conda env update -f environment.yml --prune
```

`--prune` 主要处理 Conda 管理的依赖，不会因为从 `pip:` 列表中删除一项就自动卸载对应的 pip 包。删除 pip 依赖后，应单独执行卸载命令，或从声明式文件重新创建环境。

### 5.2 导出可维护的环境规格

如果希望文件中只保留显式请求的 Conda 包，而不是全部传递依赖：

```bash
conda env export --from-history > environment.from-history.yml
```

`--from-history` 读取 Conda 的事务历史，**不会导出普通 `python -m pip` 安装的包，也不会保留原文件中的 `pip:` 区域**。这种方式更适合跨平台共享，但不会保证与原环境逐包完全一致。它和完整导出都可能包含本机 `prefix:`，应先删除该行，再与原 `environment.yml` 或 `requirements.txt` 合并，避免直接覆盖并丢失 pip 依赖。

导出当前环境解析后的完整状态，包括普通 pip 包：

```bash
conda env export > environment.resolved.yml
```

完整导出和 `--from-history` 导出的 YAML 都可能包含本机 `prefix`、具体构建和 Channel 信息。提交到版本库前应检查并删除不应共享的 `prefix`，且不要把本机绝对路径或凭据写入文件。

### 5.3 使用新版导出命令

Conda 25.7 及之后增强了 `conda export`：

```bash
# 可维护的 YAML；先导出到新文件，再人工合并 pip 依赖
conda export --name demo --from-history \
  --format=environment-yaml --file environment.from-history.yml

# 当前平台的完整显式规格
conda export --name demo \
  --format=explicit --file demo-explicit.txt
```

同平台精确复现也可以使用传统显式规格：

```bash
conda list -n demo --explicit > demo-explicit.txt
conda create -n demo --file demo-explicit.txt
```

显式规格通常绑定一个操作系统和架构，不应直接当作跨平台文件使用。它主要记录 Conda 管理的包，pip 安装的包仍应单独导出到 `requirements.txt` 或其他声明式文件。

Conda 26.5 及之后还支持原生多平台锁文件：

```bash
conda export --name demo --file conda-lock.yaml \
  --platform linux-64 \
  --platform osx-64 \
  --platform win-64

conda create --name demo --file conda-lock.yaml
```

锁文件适合 CI 和生产环境，但生成时必须确认各平台都有对应构建。原生 Conda 锁文件主要覆盖 Conda 管理的包，不应假定它已经完整记录普通 pip 或 uv 安装的依赖；这类依赖仍应保留独立的锁定文件或 `requirements.txt`。此外，精确复现仍要求原 Channel 中的固定构建持续可用。

### 5.4 如何选择环境文件

| 文件 | 主要用途 | 跨平台 | 普通 pip 依赖 |
| --- | --- | --- | --- |
| 手工维护的 `environment.yml` | 日常开发和团队协作 | 较好，取决于各平台是否有对应构建 | 可通过 `pip:` 显式记录 |
| `--from-history` 导出的 YAML | 保留 Conda 显式安装请求 | 较好，但不完整；应删除 `prefix:` | 不会导出 |
| 完整 `conda env export` YAML | 记录解析后的 Conda 和 pip 状态 | 中等，可能包含构建和本机 `prefix` | 会列出 |
| `explicit.txt` | 同操作系统和架构的精确复现 | 差，不应跨平台使用 | 不包含 |
| 原生 `conda-lock.yaml` | 指定平台的精确锁定 | 对已列出的平台最好 | 仍需独立记录 |

`environment.from-history.yml` 只是本文使用的导出文件名，并不是一种独立格式。旧版 Conda 或需要额外锁文件能力时，也可以评估第三方 `conda-lock` 工具，但它与 Conda 26.5+ 的原生锁文件不是同一实现。

### 5.5 环境专属变量

Conda 可以把项目变量保存到环境中：

```bash
conda env config vars set MY_PROJECT_ENV=dev -n demo
conda env config vars list -n demo
conda env config vars unset MY_PROJECT_ENV -n demo
```

设置后需要重新激活环境。也可以在 `environment.yml` 中声明非敏感变量：

```yaml
variables:
  MY_PROJECT_ENV: dev
```

环境变量会出现在环境导出文件中，因此不要把 Token、密码或私钥写入共享 YAML；敏感值应由 CI Secret、密钥管理器或运行时注入。

## 6. Conda 与 pip 混用

通过普通 `python -m pip` 安装时，Conda 和 pip 可以共存，但两者维护的包元数据相互独立：

- Conda 求解器不会把 pip 安装的包当成受 Conda 管理的依赖。
- 后续 Conda 操作可能覆盖或删除与 pip 包同名的文件。
- 同一个发行包不要同时交给 Conda 和 pip 管理。

推荐原则：

1. 先查看框架官方推荐的安装方式和 Channel。
2. 同一环境中的同一个包只选择一个主要安装来源。
3. 在专用项目环境中混用，不要污染 `base`。
4. 需要 pip 时使用当前环境的解释器执行 `python -m pip`。
5. 将 pip 依赖写入 `requirements.txt` 或 `environment.yml` 的 `pip:` 区域。
6. 怀疑依赖状态不一致时，优先重建环境，而不是继续覆盖安装。

```bash
conda activate demo
python -m pip install requests
python -m pip check
conda list
```

Conda 官方建议尽量先使用 Conda 安装可用包，再用 pip 补足其余软件；但 PyTorch 等项目经常把官方 wheel 作为首选方案，因此“所有底层包都必须使用 Conda”并不是通用规则。

官方 latest 文档中的 [conda-pypi](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/install-packages-from-pypi.html) 工作流标记为 Conda 26.9+，但在本文章基线日期（2026-09-25）该版本尚未正式发布，因此应视为前瞻信息，不要在当前版本上直接照抄。它要求 Rattler solver；正式发布后，配置流程应包括：

```bash
conda install --name base "conda>=26.9" "conda-rattler-solver>=0.1.1"
conda list | grep rattler
conda config --set solver rattler
conda config --append channels conda-pypi
```

该能力仅覆盖受支持的纯 Python wheel，客户端限定为 Conda，并且安装时仍需连接 PyPI；它不是普通 pip 工作流的完全替代品。

上面的 `solver: rattler` 是用户级配置，会影响该用户后续创建或更新的环境；使用前应确认其他项目是否依赖 libmamba。`conda-pypi` 被追加到 Channel 列表末尾，是为了保持较低优先级。它只提供纯 Python wheel，没有编译二进制，因此与 `defaults`、`conda-forge` 混用的 ABI 风险不同。启用或撤销后都应检查：

```bash
conda config --show solver channels
```

不要使用：

```bash
python -m pip install --user some-package
```

`--user` 不适合声明项目依赖。venv 通常会拒绝该选项，但普通 Conda 环境不一定被 pip 识别为 venv，可能允许它把包安装到用户目录（例如 Linux/macOS 的 `~/.local`），从而绕过项目环境；在 `base` 或 Conda 环境之外使用时尤其危险。

### 6.1 使用 uv 管理 Python 依赖

一种可行的组合是让 Conda 管理 Python、编译库和原生依赖，让 uv 管理纯 Python 包及其锁文件。应显式把 uv 指向当前 Conda 环境的解释器：

```bash
conda create -n app python=3.12
conda activate app
uv pip install --python "$(python -c 'import sys; print(sys.executable)')" -r requirements.txt
```

PowerShell 可以使用：

```powershell
conda create -n app python=3.12
conda activate app
$python = python -c "import sys; print(sys.executable)"
uv pip install --python $python -r requirements.txt
```

如果需要可重复安装的 Python 依赖，可把输入和锁定文件分开：

```bash
uv pip compile --python "$(python -c 'import sys; print(sys.executable)')" \
  requirements.in -o requirements.txt
uv pip sync --python "$(python -c 'import sys; print(sys.executable)')" \
  -r requirements.txt
```

uv 可以根据已激活 Conda 环境的 `CONDA_PREFIX` 自动发现目标，但显式传入 `--python` 更容易审计和复现。安装后应通过 `python -c "import sys; print(sys.executable)"` 和 `uv pip list --python <path>` 核对目标。相关命令见 [uv 的 pip environments 文档](https://docs.astral.sh/uv/pip/environments/)。

## 7. Mamba、libmamba 与 Micromamba

Mamba 是与 Conda 软件包和环境格式兼容的客户端，使用更快的依赖求解实现。Miniforge 默认同时提供 `conda` 和 `mamba`。

需要注意：

- 截至已发布的 Conda 26.7.x，通常默认使用 libmamba 求解器；先执行 `conda config --show solver` 检查，不必为了性能额外安装 Mamba。官方后续文档可能调整默认求解器，仍应以本机配置为准。
- Mamba 不是另一套 Channel 体系，也不会自动消除 Channel 混用造成的依赖冲突。
- Mambaforge 已停止维护，新安装应使用 Miniforge。
- Micromamba 是独立、无需 `base` 的轻量可执行文件，更适合 CI、Docker 和自动化环境。

如果当前 Conda 安装确实需要补充 Mamba，应确保 Channel 策略与整个安装保持一致，避免在 `base` 中无规划地混入不兼容构建：

```bash
conda install -n base --override-channels -c conda-forge mamba
mamba --version
```

常规使用；环境激活继续使用已经初始化的 Conda Shell 即可：

```bash
mamba create -n demo python=3.11 numpy
conda activate demo
mamba install scipy
```

官方资料：

- [Mamba 安装说明](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html)
- [Micromamba 用户指南](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html)

## 8. GPU 与 CUDA（可选）

先区分三个概念：

- **NVIDIA Driver**：让操作系统与 GPU 通信；没有兼容驱动，CUDA 程序无法使用 GPU。
- **CUDA Runtime**：供程序运行 CUDA API，不必包含完整开发工具。
- **CUDA Toolkit**：包含 `nvcc`、头文件、调试和开发工具；编译自定义 CUDA 扩展时通常需要。

检查驱动和 GPU：

```bash
nvidia-smi
```

`nvidia-smi` 显示的 CUDA Version 通常表示当前驱动最高支持的 CUDA 版本，不等于系统中安装了对应版本的完整 Toolkit。

下面的命令**只创建 Python 环境，没有安装 CUDA**：

```bash
conda create -n torch python=3.11
conda activate torch
```

安装 PyTorch 时，应从 [PyTorch 官方安装页面](https://pytorch.org/get-started/locally/)选择操作系统、Python、CUDA 或 CPU 构建，并复制页面生成的命令。不同 PyTorch 版本支持的 CUDA 版本不同，不宜在长期文档中固定 `pytorch-cuda=12.x`。

安装后验证：

```bash
python -c "import torch; print('torch:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA runtime:', torch.version.cuda)"
```

预编译 Conda 包或 wheel 通常可以携带所需 CUDA Runtime，因此不一定需要单独安装系统级 CUDA Toolkit；但编译扩展或开发 CUDA 程序时，通常仍需要兼容的 Toolkit、编译器和 `nvcc`。

## 9. Shell 初始化

`conda activate` 和 `conda deactivate` 依赖 Shell 初始化。常见 Shell 的初始化命令为：

```text
conda init bash
conda init zsh
conda init fish
conda init powershell
```

### 9.1 初始化和运行方式

初始化后重新打开终端。查看将要修改哪些文件：

```bash
conda init --dry-run bash
```

撤销最近一次 Bash 初始化：

```bash
conda init --reverse bash
```

如果只是非交互式脚本，不一定需要修改 Shell 配置。可以在当前 Bash 中加载 Hook：

```bash
eval "$(conda shell.bash hook)"
conda activate demo
```

或者直接使用 `conda run`：

```bash
conda run -n demo python script.py
```

如果只希望让 `conda` 可执行而不加载 Shell 函数，可以使用侵入性更小的方式（Conda 25.5+）：

```bash
conda init --condabin bash
```

### 9.2 base 环境自动激活

Conda 25.5 及之后的配置名是 `auto_activate`：

```bash
conda config --set auto_activate false
conda config --show auto_activate
```

Conda 25.5 以前的版本使用 `auto_activate_base`；它在 25.5 被弃用，并已在 26.3 移除。可以检查本机接受的配置项和来源：

```bash
conda config --describe auto_activate
conda config --show-sources
```

如果只希望 `conda` 命令可用，但不希望其环境中的 Python 覆盖系统 Python，关闭自动激活通常比直接把安装目录永久加入 `PATH` 更安全。

### 9.3 PowerShell 初始化被阻止

如果 `conda init powershell` 后出现“禁止运行脚本”，先查看组织策略和当前用户策略：

```powershell
Get-ExecutionPolicy -List
```

如果这是个人机器，且组织策略允许，可以在知情后为当前用户设置：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后重新打开 PowerShell。管理设备应遵循组织安全策略，不要为了 Conda 盲目使用 `Unrestricted` 或 `Bypass`。

## 10. 配置国内镜像（按需）

镜像是否可用、同步范围和支持平台可能变化。配置前应打开镜像站帮助页确认，不要长期复制已经失效的临时命令。

以清华 TUNA 为例：

- [Anaconda 镜像](https://mirrors.tuna.tsinghua.edu.cn/anaconda/)
- [Anaconda 配置帮助](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/)

### 10.1 镜像 Anaconda 官方仓库

如果镜像站提供 `main`、`r` 和 `msys2`，可以在用户级 `.condarc` 中配置 `default_channels`。下面的 `custom_channels` 只展示常见配置方式，不是镜像站支持的完整 Channel 列表；实际配置应完整参考镜像站当前帮助页：

```yaml
channels:
  - defaults
show_channel_urls: true
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```

Conda 26.1 及之后也可以用 `custom_multichannels` 定义 `defaults`，但 `default_channels` 仍受支持；应以本机版本的 `conda config --describe` 和镜像站说明为准。

### 10.2 只镜像社区 Channel

如果不希望访问 `defaults`：

```yaml
channels:
  - conda-forge
  - nodefaults
show_channel_urls: true
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```

Mamba 还可以按镜像站当前说明使用 `mirrored_channels`，例如：

```yaml
mirrored_channels:
  conda-forge:
    - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge
```

上面的 10.1“官方仓库镜像”和 10.2“仅社区 Channel”是两种基础配置，不应把 `defaults` 镜像与 `nodefaults` 方案直接拼在一起。`custom_channels` 供 Conda 使用，而 `mirrored_channels` 供 Mamba 使用；它们不是彼此替代的配置，是否同时出现取决于实际客户端和镜像需求。

修改后检查配置并刷新索引：

```bash
conda config --show channels
conda config --show-sources
conda clean --index-cache
```

`conda clean --all` 主要用于清理包缓存、索引缓存、Tarball 和日志，不会修复一般的依赖冲突；不要把它当成 UnsatisfiableError 的通用解决方案。

## 11. IDE 与 Jupyter 集成

### 11.1 PyCharm

PyCharm 可以创建或选择已有的 Conda 环境：

1. 打开 **Settings/Preferences**，进入 **Python Interpreter**。
2. 点击 **Add Interpreter**。
3. 选择 **Add Local Interpreter**，再选择 **Conda**。
4. 新建环境时选择 Python 版本并填写环境名称；已有环境时，从列表中选择目标环境。
5. 如果 PyCharm 没有自动找到 Conda，可手动指定 `conda` 可执行文件。
6. 保存后，在 Python Interpreter 选择器中确认项目使用的解释器。

先在终端确认环境和解释器路径：

```bash
conda env list
conda run -n demo python -c "import sys; print(sys.executable)"
```

### 11.2 VS Code

1. 安装或启用 Microsoft Python 扩展。
2. 打开命令面板，运行 **Python: Select Interpreter**。
3. 选择现有 Conda 环境，或直接选择 `./.conda-env/bin/python`（Windows 为 `./.conda-env/python.exe`）。
4. 在新终端中确认 VS Code 使用的解释器与项目环境一致：

```bash
python -c "import sys; print(sys.executable); print(sys.prefix)"
```

### 11.3 Jupyter

把 Conda 环境注册为 Jupyter Kernel：

```bash
conda install -n demo ipykernel
conda run -n demo python -m ipykernel install --user \
  --name demo \
  --display-name "Python (demo)"
conda run -n demo jupyter kernelspec list
```

`kernelspec list` 读取的是用户级 Kernel 目录，只要运行环境安装了 Jupyter 即可查看，不要求 Kernel 恰好安装在同一个 Conda 环境中。

这里 `ipykernel install --user` 的 `--user` 表示把 Kernel 配置安装到当前用户的数据目录，不是执行 `pip install --user`，因此不会把 Python 包绕过 Conda 环境安装。

相关文档：

- [PyCharm：配置 Python 解释器](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html)
- [PyCharm：创建 Conda 环境](https://www.jetbrains.com/help/pycharm/conda-support-creating-conda-virtual-environment.html)
- [VS Code Python environments](https://code.visualstudio.com/docs/python/environments)
- [Jupyter kernels](https://jupyter-client.readthedocs.io/en/stable/kernels.html)

## 12. 项目、服务器和 CI 实践

### 12.1 项目结构与 CI

推荐把声明式环境文件放在项目根目录：

```text
project/
├── environment.yml
├── requirements.txt
├── docker/
│   └── entrypoint.sh
├── src/
└── README.md
```

部署或持续集成时创建独立环境，不修改 `base`。Conda 26.3 及之后可以显式覆盖文件中的名称，并跳过交互确认：

```bash
conda create --yes --name demo --file environment.yml
conda run --no-capture-output -n demo python -m pytest
```

`--no-capture-output` 会让 stdout/stderr 实时显示，适合 CI 日志；Conda 26.1+ 也可以使用简写 `-s`。旧版 Conda 应改用 `conda env create -f environment.yml -y`。

实践建议：

- 将 `environment.yml` 提交到版本库，但不要提交 `.conda-env` 等实际环境目录。
- 在一个干净环境中测试创建流程。
- 重要发布使用显式规格或锁文件，而不是只写宽松的包名。
- CI 按操作系统和架构分别创建与求解环境，不用 `CONDA_SUBDIR` 长期强制错误的平台。
- CI 中缓存下载包或固定的环境前缀前，确认缓存与平台、Channel 权限和密钥匹配。
- 容器中只需要执行一条命令时，优先使用 `conda run`；自动化环境可考虑 Micromamba。
- 不要在 `base` 中维护每个项目的业务依赖。
- 不要把 Token、镜像凭据或机器专属绝对路径写入共享环境文件。

### 12.2 Docker 示例

使用 Miniforge 官方镜像，并在构建阶段创建项目环境。下面使用入口脚本激活环境后 `exec` 用户命令，使容器能够正确转发停止信号：

```dockerfile
FROM condaforge/miniforge3:latest

ARG ENV_NAME=demo
ENV ENV_NAME=${ENV_NAME}

COPY environment.yml .
RUN conda create --yes --name "${ENV_NAME}" --file environment.yml \
    && conda clean --yes --all

COPY src ./src
COPY docker/entrypoint.sh /usr/local/bin/conda-entrypoint
RUN chmod +x /usr/local/bin/conda-entrypoint

ENTRYPOINT ["/usr/local/bin/conda-entrypoint"]
CMD ["python", "app.py"]
```

`docker/entrypoint.sh`：

```bash
#!/usr/bin/env bash
set -euo pipefail
source /opt/conda/etc/profile.d/conda.sh
conda activate "${ENV_NAME}"
exec "$@"
```

上面的 `CMD` 假设入口文件是 `src/app.py`，需要按项目结构调整。运行容器时可加 `--init` 处理 PID 1 的信号和僵尸进程：

```bash
docker run --init -p 8000:8000 my-image
```

生产环境应固定基础镜像版本或 digest，并优先使用锁文件创建环境；不要在容器里修改 `base`。如果使用 Micromamba 或自定义镜像，入口脚本中的 Conda 安装路径也要相应调整。示例中的 `conda create --file` 需要基础镜像包含 Conda 26.3+；更早的镜像应改用 `conda env create -f environment.yml --yes`。

参考：[Miniforge 容器镜像](https://github.com/conda-forge/miniforge3)。

## 13. 常见排查

### 13.1 通用检查

```bash
conda --version
conda info
conda config --show
conda config --show-sources
conda env list
conda list
conda doctor
```

如果本机支持 `conda doctor --fix`（Conda 26.1+），修复前先预览：

```bash
conda doctor --fix --dry-run
```

### 13.2 平台或架构不匹配

先确认当前平台：

```bash
conda info
```

Apple Silicon、Intel、Linux x86_64 和 Linux ARM 使用不同的 Conda 子目录。可以通过 `--platform` 为一次创建操作指定目标平台：

```bash
conda create --platform osx-arm64 --name native-arm python=3.11
CONDA_SUBDIR=osx-arm64 conda create --name native-arm-env python=3.11
```

`CONDA_SUBDIR` 只应在明确需要时临时设置；不要让错误值长期留在 Shell 或 CI 配置中。强制跨操作系统创建环境通常不可行。

### 13.3 虚拟包与系统能力

Conda 会把主机能力表示成“虚拟包”，供求解器判断包是否可安装。例如：

- `__cuda`：检测到的 NVIDIA 驱动 CUDA 能力
- `__glibc`、`__linux`、`__unix`、`__osx`、`__win`：系统 ABI 和操作系统
- `__archspec`：CPU 架构能力
- 还可能包括 `__conda`；在 musl 系统上，Linux 虚拟包可能表现为 `__musl` 而不是 `__glibc`

查看当前检测结果：

```bash
conda info
```

虚拟包不是 Conda 安装的软件，而是对当前系统的描述。如果求解器提示 `package requires __cuda >= 12`，应先检查 NVIDIA 驱动、当前 Conda 平台以及包实际支持的构建，不应直接伪造版本。

仅在为目标平台执行 `--dry-run` 等求解操作、且确实缺少对应主机信息时，才考虑临时覆盖：

```bash
CONDA_OVERRIDE_CUDA=12.4 conda create --dry-run some-package
```

跨操作系统求解时，官方文档还建议根据目标系统补充相应变量，例如：

```bash
CONDA_OVERRIDE_LINUX=1 CONDA_OVERRIDE_GLIBC=2.17 \
  conda create --dry-run --platform linux-64 some-package
```

可用 `conda config --describe override_virtual_packages` 查看当前版本支持的覆盖配置。覆盖值必须与真实执行环境一致，否则求解成功也不代表环境能够运行。

### 13.4 `PackagesNotFoundError`

常见原因：

- Channel 中没有该包或该版本。
- 当前 Python 版本、操作系统或架构不匹配。
- 镜像没有同步目标子目录。
- 旧 Channel 元数据仍被缓存。

排查：

```bash
conda search -c conda-forge --override-channels package-name
conda clean --index-cache
```

如果指定包名确实存在，再检查它支持的 Python 版本和平台构建。

### 13.5 `UnsatisfiableError` 或依赖冲突

`conda clean --all` 不能解决一般的版本冲突。应优先：

1. 阅读错误末尾列出的冲突包。
2. 使用 `conda search <package> --info` 查看依赖。
3. 检查是否混用了不兼容的 `defaults` 与 `conda-forge` 构建。
4. 放宽或修正 Python、框架和 CUDA 的版本约束。
5. 在新环境中按声明式文件重新安装。

只有确认索引缓存损坏时，才优先执行：

```bash
conda clean --index-cache
```

### 13.6 `conda activate` 不可用

先区分两种情况：

```bash
conda --version
type conda
```

PowerShell 可以使用：

```powershell
Get-Command conda
Get-ExecutionPolicy -List
```

- 如果 `conda` 命令本身都找不到，说明安装目录不在 `PATH`，可先使用 Conda 可执行文件的完整路径。
- 如果 `conda` 可用但没有 `activate` Shell 函数，运行 `conda init <shell>` 并重新打开终端，或在当前脚本中加载 Hook。
- 非交互式脚本优先使用 `conda run -n <env> <command>`。

### 13.7 激活了错误环境或 Python

```bash
conda env list
conda info --envs
which python
python -c "import sys; print(sys.executable); print(sys.prefix)"
```

Windows 可以使用：

```powershell
where.exe python
```

### 13.8 Conda 与 pip 状态不一致

```bash
conda list
python -m pip check
```

如果同一个包同时出现 Conda 和 pip 记录，或 Conda 操作后行为异常，最稳妥的恢复方式通常是：保存必要规格，创建新环境，然后按顺序重新安装。

## 14. 最佳实践清单

- 开始前检查 Conda 版本；版本敏感命令以本机 `--help` 为准。
- 为每个项目创建独立环境，保持 `base` 精简。
- 使用项目本地 `--prefix` 环境时，将环境目录加入 `.gitignore`。
- 明确选择 `defaults` 或 `conda-forge` 作为默认 Channel，避免长期无规划混用。
- 确实需要混用时启用 `channel_priority: strict`，并理解它可能使环境无解。
- 一个包只由 Conda 或 pip 中的一个来源管理。
- `--from-history` 导出后人工检查，删除 `prefix:`，并单独保留普通 pip 依赖。
- 优先遵循框架官方安装说明，尤其是 PyTorch、CUDA 和编译型包。
- 提交声明式环境文件，同时按需保留显式规格或锁文件。
- 把“日常可维护的 YAML”和“发布时精确的锁文件”分开管理。
- 环境变量只保存非敏感值，Token 和密码由外部注入。
- Shell 中使用 `conda activate`，脚本和 CI 中优先使用 `conda run --no-capture-output`。
- 在 Apple Silicon、Linux ARM 和 x86_64 上分别验证平台构建。
- 遇到 `__cuda`、`__glibc` 等虚拟包问题时，先核对真实系统能力，不伪造版本。
- 根据协作、同平台复现和生产锁定场景选择不同环境文件。
- 使用 uv 等工具时显式指定当前 Conda 环境的解释器。
- 镜像变更后检查配置来源、平台支持和索引缓存。
- 更新 `base` 或批量更新环境前，先准备修订历史、导出文件或重建方案。

## 15. 参考资料

- [Conda 官方文档](https://docs.conda.io/projects/conda/en/latest/)
- [Conda Channels](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/channels.html)
- [Channel 配置最佳实践](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-channels.html#channel-best-practices)
- [Conda 命令参考](https://docs.conda.io/projects/conda/en/latest/commands/)
- [Conda 配置参考](https://docs.conda.io/projects/conda/en/latest/user-guide/configuration/settings.html)
- [Conda 环境管理](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
- [Conda 软件包管理](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html)
- [`conda doctor`](https://docs.conda.io/projects/conda/en/latest/commands/doctor.html)
- [Conda 25.5.0 Release](https://github.com/conda/conda/releases/tag/25.5.0)
- [Conda 25.7.0 Release](https://github.com/conda/conda/releases/tag/25.7.0)
- [Conda 26.1.0 Release](https://github.com/conda/conda/releases/tag/26.1.0)
- [Conda 26.3.0 Release](https://github.com/conda/conda/releases/tag/26.3.0)
- [Conda 26.5.0 Release](https://github.com/conda/conda/releases/tag/26.5.0)
- [Miniforge](https://conda-forge.org/download/)
- [Mamba 文档](https://mamba.readthedocs.io/en/latest/)
- [PyTorch 安装页面](https://pytorch.org/get-started/locally/)
- [NVIDIA CUDA Installation Guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)
- [Anaconda 服务条款](https://www.anaconda.com/legal/terms-of-service)

---

## AI 修改声明

本文由 LLM 依据 `ref/anacoda-introduce.md` 整理，并参考上述官方文档补充和核对内容。最近修改时间：2026-09-25 23:55（UTC+08:00）。
