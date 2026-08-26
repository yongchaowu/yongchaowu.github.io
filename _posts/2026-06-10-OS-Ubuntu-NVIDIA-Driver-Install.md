---
layout: post
title: "OS-Ubuntu-NVIDIA Driver Install"
date: 2026-06-10 20:34:00
categories: ["OS"]
tags: ["Nvidia", "OS"]
---

## 安装前置准备

<!--more-->
### 查看系统内核与硬件

```shell
uname -r                # 内核：6.8.0-124-generic
lspci | grep -i nvidia  # 显卡：xxx
```

### 禁用开源 nouveau 驱动

`sudo nano /etc/modprobe.d/blacklist-nouveau.conf`

写入：

```shell
blacklist nouveau
options nouveau modeset=0
```

保存退出（Ctrl+O→回车→Ctrl+X），然后：

```shell
sudo update-initramfs -u
sudo reboot
```

重启后验证（无输出即成功）：

`lsmod | grep nouveau`


### 关闭安全启动（Secure Boot）

- 重启电脑，进 BIOS/UEFI
- 找到 Secure Boot → 设置为 Disabled
- 保存退出

### 安装编译依赖

```shell
sudo apt update
sudo apt install -y build-essential gcc make dkms linux-headers-$(uname -r)
```

---

## 安装驱动

### 使用apt官方源安装

```shell
sudo apt update
sudo apt install -y nvidia-driver-xx
sudo reboot
```

### 使用 `NVIDIA-Linux-x86_64-<版本号>.run` 安装包

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
# --no-cc-version-check --no-dkms 强制跳过版本检查

# 4. 恢复图形
sudo systemctl set-default graphical.target
sudo reboot

# 5. 验证
nvidia-smi

```

- 遇到 `Install 32-bit compatibility libraries?` 选 `No`
- 遇到 `Would you like to run the nvidia-xconfig utility?` 选 `Yes`