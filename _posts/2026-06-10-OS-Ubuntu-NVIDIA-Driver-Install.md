---
layout: post
title: Ubuntu NVIDIA Driver Install
summary: >
  Complete walkthrough for installing NVIDIA GPU drivers on Ubuntu, including
  kernel module removal, secure boot handling, and CUDA toolkit verification.
lang: en
version: "550.163.01"
tested:
  OS: "Ubuntu 24.04"
  Kernel: "6.8.0-124-generic"
  Driver: "550.163.01"
date: 2026-06-10 20:34:00
categories:
- Systems
tags:
- NVIDIA
- OS
---

## Quick Start

> Goal: 在 Ubuntu 上安装 NVIDIA 驱动并验证 GPU 可用。

<!--more-->

### Prerequisites

- Ubuntu 24.04（其他版本步骤类似）
- Root 或 sudo 权限
- Secure Boot 已在 BIOS 中关闭

### 1. 禁用 nouveau 驱动

```bash
sudo bash -c 'cat > /etc/modprobe.d/blacklist-nouveau.conf << EOF
blacklist nouveau
options nouveau modeset=0
EOF'
sudo update-initramfs -u
sudo reboot
```

重启后验证（无输出即成功）：

```bash
lsmod | grep nouveau
```

### 2. 安装编译依赖

```bash
sudo apt update
sudo apt install -y build-essential gcc make dkms linux-headers-$(uname -r)
```

### 3. 安装驱动

```bash
sudo apt update
sudo apt install -y nvidia-driver-550
sudo reboot
```

### Verify

```bash
nvidia-smi
```

应显示 GPU 信息、驱动版本和 CUDA 版本。

> 使用 `.run` 安装包或完整卸载流程见下方章节。

## 安装前置准备

### 查看系统内核与硬件

```shell
uname -r                # 内核：6.8.0-124-generic
lspci | grep -i nvidia  # 显卡型号
```

### 关闭安全启动（Secure Boot）

- 重启电脑，进 BIOS/UEFI
- 找到 Secure Boot → 设置为 Disabled
- 保存退出

## 安装驱动

### 使用 apt 官方源安装

```shell
sudo apt update
sudo apt install -y nvidia-driver-xx
sudo reboot
```

### 使用 .run 安装包

```shell
# 1. 先卸载 apt 版驱动（避免冲突）
sudo apt purge -y nvidia-driver-* nvidia-dkms-*
sudo apt autoremove -y

# 2. 关图形界面
sudo systemctl set-default multi-user.target
sudo reboot

# 3. tty 下安装（关键参数）
cd ~/Downloads
chmod +x NVIDIA-Linux-x86_64-550.163.01.run
sudo ./NVIDIA-Linux-x86_64-550.163.01.run \
  --no-x-check \
  --no-opengl-files \
  --dkms

# 4. 恢复图形
sudo systemctl set-default graphical.target
sudo reboot

# 5. 验证
nvidia-smi
```

遇到提示：

- `Install 32-bit compatibility libraries?` → 选 `No`
- `Would you like to run the nvidia-xconfig utility?` → 选 `Yes`

## Troubleshooting

### 驱动安装后 nvidia-smi 无输出

检查 nouveau 是否完全禁用：

```bash
lsmod | grep nouveau
```

如仍有输出，确认 `/etc/modprobe.d/blacklist-nouveau.conf` 内容正确并重新 `update-initramfs -u`。

### 安装后分辨率异常

通常是 `--no-opengl-files` 未使用或 X 配置错误：

```bash
sudo nvidia-xconfig
sudo reboot
```

### Secure Boot 导致驱动加载失败

最简方案：在 BIOS 中关闭 Secure Boot。如需保留 Secure Boot，需使用 MOK（Machine Owner Key）签名驱动。

## Reference

### 安装参数

| 参数 | 说明 |
|------|------|
| `--no-x-check` | 跳过 X server 检查 |
| `--no-opengl-files` | 不安装 OpenGL 文件（避免冲突） |
| `--dkms` | 注册 DKMS 模块（内核升级后自动重编译） |

### 关键路径

| 路径 | 说明 |
|------|------|
| `/etc/modprobe.d/blacklist-nouveau.conf` | nouveau 禁用配置 |
| `/var/log/nvidia-installer.log` | .run 安装日志 |

### 常用命令

```bash
nvidia-smi                          # 查看 GPU 和驱动状态
cat /proc/driver/nvidia/version     # 驱动版本
sudo apt purge nvidia-driver-*      # 卸载驱动
```

## Next Steps

After installing the driver, you can proceed to:

- [Python Ray Offline Installation Guide]({% post_url 2026-06-12-Python-Ray-Offline-Installation-Guide %}) — Set up Ray for distributed computing
- [Multi-Node LLM Serving: vLLM + Ray]({% post_url 2026-06-12-Multi-Node-LLM-Serving-vLLM+Ray(Docker) %}) — Deploy vLLM across multiple nodes
