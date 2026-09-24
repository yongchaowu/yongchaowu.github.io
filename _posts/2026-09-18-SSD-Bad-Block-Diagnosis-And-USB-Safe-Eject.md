---

layout: post
title: 'WD Blue SN570 坏块排查与 USB 安全弹出：Linux / Windows 全流程'
summary: '从 SMART 与全盘只读扫描判断 SSD 是否真有坏块，到 NTFS 逻辑损坏的修复（ntfsfix / chkdsk），并附一个按序列号定位磁盘、自动卸载断电的安全弹出脚本。'
lang: zh-CN
date: 2026-09-18 21:51:00
categories:
- Systems
tags:
- SSD
- NVMe
- SMART
- NTFS
- Linux
- Windows
- USB
- 数据安全
---
事情起因很简单：一块挂在 USB 硬盘盒里的 WD Blue SN570 1TB SSD，内核日志里出现了 `Buffer I/O error ... lost async page write`，文件系统被标成 dirty，回收站里还有几个文件怎么都删不掉（`Input/output error`）。

**它到底是"盘坏了（坏块）"，还是"文件系统坏了"？** 这篇文章把整套排查、判断与修复流程整理成可复用的方法，最后给出一个安全弹出脚本。

---

<!--more-->

## 目录

- [0. 环境与背景](#0-环境与背景)
- [1. 先分清：介质坏块 vs 文件系统损坏](#1-先分清介质坏块-vs-文件系统损坏)
- [2. Linux 侧诊断流程](#2-linux-侧诊断流程)
  - [2.1 确认设备与拓扑](#21-确认设备与拓扑)
  - [2.2 读 SMART：判断有没有介质错误](#22-读-smart判断有没有介质错误)
  - [2.3 全盘只读扫描：badblocks](#23-全盘只读扫描badblocks)
  - [2.4 内核日志取证](#24-内核日志取证)
- [3. 修复：软件层面能做什么](#3-修复软件层面能做什么)
  - [3.1 Linux：ntfsfix](#31-linuxntfsfix)
  - [3.2 Windows：chkdsk](#32-windowschkdsk)
  - [3.3 软件修复的边界](#33-软件修复的边界)
- [4. USB 安全弹出脚本 eject-sn570](#4-usb-安全弹出脚本-eject-sn570)
- [5. 命令速查表](#5-命令速查表)
- [6. 经验总结](#6-经验总结)

---

## 0. 环境与背景

| 项 | 值 |
|---|---|
| 硬盘 | WD Blue SN570 1TB SSD（NVMe） |
| 硬盘盒 | Ugreen / ASMedia ASM2362（USB 3.2 Gen2，NVMe→USB 桥） |
| 系统 | Ubuntu 22.04（内核 6.8） |
| 文件系统 | NTFS（单分区，`/dev/sdb1`） |
| 现象 | 内核写 I/O 错误、NTFS dirty、回收站文件删不掉 |

关键点：**这块 NVMe 盘不在原生 M.2 槽，而是通过 USB 桥接芯片以 SCSI 设备（`/dev/sdb`）暴露出来。** 这带来两个后果：

1. SMART / NVMe 命令需要桥接芯片转发，老工具读不到；
2. TRIM（discard）通常不透传，`discard_max_bytes` 为 0。

---

## 1. 先分清：介质坏块 vs 文件系统损坏

排查 SSD"坏没坏"，最容易混淆的就是这两类问题：

| 维度 | 介质坏块（硬件） | 文件系统损坏（逻辑） |
|---|---|---|
| 典型现象 | 读写固定 LBA 报 `medium error` | `lost async page write`、dirty、删不掉文件 |
| SMART | `Media and Data Integrity Errors > 0` | 全部正常 |
| 触发原因 | 闪存磨损、掉电、主控异常 | 掉电 / 非正常拔插 / 元数据写一半中断 |
| 修复方式 | **无法软件修复**，靠主控重映射或换盘 | `ntfsfix` / `chkdsk` 可修 |
| 可否继续用 | 错误增长则尽快备份换盘 | 修好后可继续用 |

**结论先行的经验法则：**

- SMART 干净 + 全盘只读扫描 0 错误 → 几乎没有介质坏块，问题在文件系统；
- SMART 出现 Media Errors / Reallocated / Pending 增长 → 硬件在退化，先备份。

本例最终结论：**无坏块，是掉电导致的 NTFS 逻辑损坏。**

---

## 2. Linux 侧诊断流程

### 2.1 确认设备与拓扑

```bash
lsblk -o NAME,SIZE,MODEL,SERIAL,MOUNTPOINT,FSTYPE
lsusb
lsusb -t          # 看 USB 拓扑与驱动（uas / usb-storage）
```

判断桥接芯片与是否支持 TRIM：

```bash
cat /sys/block/sdb/device/model
cat /sys/block/sdb/device/vendor
cat /sys/block/sdb/queue/discard_max_bytes   # 0 表示 TRIM 未透传
```

### 2.2 读 SMART：判断有没有介质错误

Ubuntu 22.04 自带的 `smartmontools 7.2` **不识别 ASM2362**，会报 `scsi error unsupported scsi opcode`。`sntasmedia`（ASMedia USB-NVMe 桥）支持是 **7.3+** 才加入的，因此需要自己编译新版：

```bash
sudo apt-get install -y gcc g++ make
cd /tmp
curl -sL -o smt.tar.gz \
  "https://sourceforge.net/projects/smartmontools/files/smartmontools/7.4/smartmontools-7.4.tar.gz/download"
tar xzf smt.tar.gz && cd smartmontools-7.4
./configure --without-systemd --without-selinux
make -j"$(nproc)" smartctl
sudo ./smartctl -i -d sntasmedia /dev/sdb
```

> 常见 device type：ASMedia 用 `-d sntasmedia`；JMicron 用 `-d sntjmicron`；Realtek 用 `-d sntrealtek`；实在不行加 `-T permissive` 或换原生 M.2 槽。

核心健康字段：

```bash
sudo ./smartctl -H -d sntasmedia /dev/sdb
sudo ./smartctl -A -d sntasmedia /dev/sdb
sudo ./smartctl -l error -d sntasmedia /dev/sdb
```

**重点看这几项：**

| 字段 | 健康值 | 含义 |
|---|---|---|
| SMART overall-health | PASSED | 综合自检 |
| Critical Warning | 0x00 | 无告警 |
| Available Spare | 100%（阈值 10%） | 备用块未消耗 |
| Percentage Used | 越低越好 | 寿命消耗 |
| **Media and Data Integrity Errors** | **0** | **无介质错误（最关键）** |
| Error Log Entries | 少 / 为 0 | 控制器错误日志 |
| UDMA_CRC / 接口错误 | 0 | 线材 / 接口问题 |

本例结果：全部正常，`Media and Data Integrity Errors = 0`。

> 部分桥接芯片不透传 NVMe self-test 命令（`NVMe admin command 0x14 not supported`），此时改用下面的 `badblocks` 做全盘只读扫描。

### 2.3 全盘只读扫描：badblocks

非破坏性、只读，挂载状态下也相对安全（强烈建议只读，别用 `-w`）：

```bash
sudo badblocks -sv -b 4096 /dev/sdb
```

- `-s` 显示进度，`-v` 详细，`-b 4096` 指定块大小加速；
- 1TB 通过 USB 5Gbps 约 1 小时；
- 结束时输出 `Pass completed, 0 bad blocks found.`

> 若盘上无重要数据，也可用 `f3`（f3write/f3read）做读写校验，但它是破坏性的。

### 2.4 内核日志取证

```bash
sudo journalctl -k --no-pager | grep -iE "I/O error|medium error|blk_update|ntfs|sdb"
```

区分关键：

- `Buffer I/O error ... lost async/sync page write` → 写回失败，多半是**掉电/拔插导致**；
- `critical medium error` / `medium error` → 指向**介质坏块**。

本例的写错误全部集中在同一秒（某次掉电时刻），并非分散在固定 LBA，因此判定为逻辑损坏。

---

## 3. 修复：软件层面能做什么

### 3.1 Linux：ntfsfix

先卸载，再清 dirty 位 + 基础修复，然后重挂：

```bash
sudo umount /dev/sdb1
sudo ntfsfix /dev/sdb1
udisksctl mount -b /dev/sdb1
```

`ntfsfix` 能做的：清除 dirty 标志、重放日志、检查 `$MFT`/`$MFTMirr` 与备份引导扇区。
**不能做的**：修复目录项 / MFT 记录级别的损坏（这正是"文件删不掉"的根因）。

### 3.2 Windows：chkdsk

MFT 记录损坏时，最可靠的是 Windows 的 `chkdsk`（管理员 CMD / PowerShell）：

```cmd
chkdsk E: /f
```

- `/f` 修复文件系统错误（多数情况够用，快）；
- `/r` 额外扫描坏扇区并恢复可读信息（**很慢**，1TB + USB 可能数小时）；
- `/b` 重新评估坏簇（针对新发现的坏块）。

完成后可正常清空回收站。若之前在 Linux 删不掉的文件，chkdsk 通常能修复其 MFT 记录，之后即可删除。

### 3.3 软件修复的边界

必须明确：**物理坏块无法用软件修复。**

- SSD 主控本就用**备用块 + 坏块重映射**管理闪存，操作系统看不到、也不需要"修"；
- 所谓"软修复"只是：写入该 LBA → 主控将其重映射到备用块；或文件系统层标记坏簇（NTFS 的 `chkdsk /r`）；
- **TRIM / 安全擦除**：USB 桥不透传时 `fstrim`/`blkdiscard` 无效，需插原生 M.2 槽；
- **固件更新**：用厂商工具（WD Dashboard，仅 Windows），最好在原生 M.2 槽操作；
- 判据：SMART 中 `Reallocated / Pending / Media Errors` 持续增长或 `Available Spare` 下降 = 硬件退化，**备份并换盘**。

---

## 4. USB 安全弹出脚本 eject-sn570

### 4.1 为什么需要脚本

USB 桥接盘（尤其 ASM2362）在写入缓存未刷完时被拔掉，就会出现：

- `Synchronize Cache(10) failed: Result: hostbyte=DID_ERROR`；
- NTFS 变 dirty；
- SMART 里 `Unsafe Shutdowns` 计数飙升（本例 76 次）。

手动"安全弹出"容易漏掉某个分区或忘记 `sync`。脚本做三件事：**按设备身份定位 → 卸载所有分区 → sync → 断电弹出**。

### 4.2 设计逻辑

1. **不写死 `/dev/sdX`**：按 `SERIAL`（序列号）定位，回退用 `MODEL` 匹配，重启换盘符也不怕；
2. **遍历所有分区**：从 `lsblk` 取子分区，逐个 `findmnt` 找挂载点并 `udisksctl unmount`；
3. **先 sync 再断电**：`sync` 刷缓存，`udisksctl power-off` 让桥接芯片断电，避免脏数据；
4. **失败即中止**：任一步失败就报错退出，禁止"假装成功"。

获取自己的序列号：

```bash
lsblk -dno NAME,MODEL,SERIAL
```

### 4.3 脚本内容

保存为 `~/.local/bin/eject-sn570` 并 `chmod +x`：

```bash
#!/usr/bin/env bash
set -euo pipefail

SERIAL="${SN570_SERIAL:-<YOUR_SERIAL>}"
MODEL="${SN570_MODEL:-SN570 1TB SSD}"

dev="$(lsblk -dno NAME,SERIAL | awk -v s="$SERIAL" '$2==s{print $1; exit}')"
if [[ -z "$dev" ]]; then
  dev="$(lsblk -dno NAME,MODEL | awk -v m="$MODEL" 'index($0,m){print $1; exit}')"
fi
if [[ -z "$dev" ]]; then
  echo "未找到设备: serial=$SERIAL model=$MODEL" >&2
  exit 1
fi

disk="/dev/$dev"
echo "目标磁盘: $disk ($(cat "/sys/block/$dev/device/model" 2>/dev/null || echo unknown))"

mapfile -t parts < <(lsblk -lno NAME "$disk" | tail -n +2)
for p in "${parts[@]}"; do
  [[ -z "$p" ]] && continue
  tgt="$(findmnt -no TARGET "/dev/$p" 2>/dev/null || true)"
  if [[ -n "$tgt" ]]; then
    echo "卸载 /dev/$p ($tgt)"
    udisksctl unmount -b "/dev/$p" || { echo "卸载失败: /dev/$p" >&2; exit 1; }
  fi
done

echo "同步缓存..."
sync

echo "断电弹出 $disk ..."
if udisksctl power-off -b "$disk"; then
  echo "已安全弹出，可以拔线。"
else
  echo "断电弹出失败，请不要直接拔线。" >&2
  exit 1
fi
```

### 4.4 使用

```bash
eject-sn570

# 或临时覆盖序列号
SN570_SERIAL=xxxx eject-sn570
```

脚本无需 `sudo`（`udisksctl` 走 polkit，对当前登录用户生效）。看到"已安全弹出，可以拔线"后再拔。

---

## 5. 命令速查表

| 目的 | Linux | Windows |
|---|---|---|
| 查看设备 | `lsblk -o NAME,SIZE,MODEL,SERIAL,MOUNTPOINT` | 磁盘管理 / `Get-Disk` |
| 读 SMART | `smartctl -A -d sntasmedia /dev/sdb` | `wmic diskdrive get status`（有限）/ 厂商工具 |
| 全盘只读扫坏块 | `badblocks -sv -b 4096 /dev/sdb` | `chkdsk X: /r`（读写式） |
| 看内核报错 | `journalctl -k \| grep -iE "I/O error\|medium error"` | 事件查看器 → 系统 |
| 清 dirty / 修 FS | `ntfsfix /dev/sdb1` | `chkdsk X: /f` |
| 深度修 FS | （有限） | `chkdsk X: /r` / `/b` |
| 刷缓存 | `sync` | 安全弹出 |
| 安全弹出 | `udisksctl power-off -b /dev/sdb` | 任务栏"安全删除硬件" |
| 固件升级 | 无官方工具，需 Windows | WD Dashboard |

---

## 6. 经验总结

1. **先定性再动手**：SMART 干净 + 只读扫描 0 错误，基本可排除介质坏块，别急着低格或换盘。
2. **老工具会骗你**：Ubuntu 22.04 的 `smartmontools 7.2` 读不到 ASM2362，升级到 7.3+ 才能看到 `sntasmedia`。
3. **掉电的锅别让盘背**：集中发生在某一时刻的 `lost async page write`，是拔插/掉电，不是坏块。
4. **逻辑损坏分级修**：`ntfsfix` 治标（清 dirty），MFT 记录级损坏交给 Windows `chkdsk /f`。
5. **物理坏块软件修不了**：靠主控重映射；错误计数增长就备份换盘。
6. **USB 盘一定要安全弹出**：用脚本把"卸载 → sync → 断电"固化，能显著减少 dirty 与 `Unsafe Shutdowns`。
7. **TRIM 与固件**：USB 桥多不透传 TRIM；固件升级和安全擦除请走原生 M.2 槽。

> 一句话：**SMART 判硬件，日志判诱因，文件系统工具做修复，安全弹出防复发。**
