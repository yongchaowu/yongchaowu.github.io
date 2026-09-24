---

layout: post
title: 'Linux USB 连接与挂载日志清理脚本：从风险审计到安全重构'
summary: '一次针对 USB 连接与挂载日志维护脚本的安全审计与重构记录，重点讨论 USB 设备识别、日志备份、压缩日志处理、根盘保护、journal 清理与验证机制。'
lang: zh-CN
date: 2026-09-10 10:48:00
categories:
- Systems
tags:
- Linux
- Bash
- USB
- systemd
- 日志
- 运维
---
在 Linux 系统中，USB 设备的插拔、块设备识别、挂载和卸载，可能分别出现在 `dmesg`、传统 syslog、`auditd`、systemd journal 以及 `/proc/mounts` 等位置。

如果只是为了实验环境维护、测试机复位或管理员主动清理历史日志，一个简单的 Bash 脚本就能完成很多工作。但一旦脚本以 `root` 权限运行，事情就不再只是“删几行日志”这么简单：路径安全、设备误判、压缩日志损坏、根盘误卸载、备份失效以及日志服务 inode 等问题，都可能造成严重后果。

本文记录一次 `clean_usb_logs.sh` 的完整审计与安全重构过程，并给出最终的 `v2.2` 设计思路。

> 本文讨论的脚本用于合法的系统管理、实验环境维护和测试用途。删除系统日志可能影响审计、故障排查和取证能力，请确认符合所在环境的管理制度后再使用。

---

<!--more-->

## v2.1 更新：扫描进度、输入队列隔离与单遍日志分析

v2.0 在功能上已经能够完成查看和清理，但真实机器上的轮转日志可能很多。程序进入 `USB 设备使用记录查看` 后，会先分析 `kern.log`、`syslog`、`dmesg` 等历史日志；如果其中包含多个大型 `.gz/.xz/.zst` 文件，这一阶段可能持续一段时间。

旧界面在扫描结束前几乎没有输出，因此容易让人误以为脚本已经卡死。用户在这段时间按下的 `Enter`、方向键或其他字符还可能留在终端 TTY 输入队列中，等脚本随后执行 `read` 时被立即消费。典型表现就是：

```text
USB 设备使用记录查看
...长时间没有新输出...

清理模式? (1=精准过滤 2=统一清空) [默认 1]:
执行清理? (y/N):   已退出
```

这并不是脚本设置了超时时间，而通常是扫描期间缓存的换行被两个后续提示连续读取。由于第二个提示默认是 `N`，这种情况会安全退出，但交互体验并不理想。

v2.1 做了三项针对性调整：

1. **扫描进度可见。** 在分析历史日志时显示当前文件序号和文件名，不再出现长时间完全空白的“假死”状态。
2. **所有确认提示隔离旧输入。** 每次真正显示交互提示之前，先丢弃此前已经滞留在 TTY 输入队列中的字符；提示本身没有输入超时，必须在提示出现以后重新输入。
3. **历史日志改成单遍读取。** 每个日志文件只解压/读取一次，从同一份临时文本中提取 USB/UAS 直接设备、USB SCSI host 和 `host -> sdX` 映射，避免同一个大型压缩日志被重复解压。

新的查看阶段会更接近：

```text
USB 设备使用记录查看

[●] 收集白名单日志文件... ✓ (30 个)
[●] 分析当前/历史 USB 与 SCSI 关联（日志较多时会逐文件显示进度）
[●] 分析历史日志 (12/30): syslog.4.gz
...
✓ USB 关联分析完成：设备 1 个，SCSI host 3 个

① 当前 USB 设备
...
```

需要特别说明：用于检查“当前是否还有缓存字符”的极短 `read -t 0.01` 只存在于输入队列清理函数中，它**不是用户确认提示的超时**。真正的 `清理模式?`、`执行清理?`、`确认执行?` 和 USB 卸载确认都仍然会一直等待用户输入。

---

## v2.2 更新：Ctrl+Z、SIGTSTP 与 flock 生命周期

v2.1 解决了“扫描期间误按 Enter 被后续 `read` 消费”的问题，但实际使用又暴露出另一个终端行为问题：**`Ctrl+Z` 并不是退出。**

在普通 Linux 终端中，`Ctrl+Z` 通常由 TTY line discipline 转换为 `SIGTSTP`，发送给前台进程组。对于：

```bash
sudo bash clean_usb_logs_v2.1.sh
```

这样的启动方式，前台进程组中不仅有 Bash 脚本，还可能包含 `sudo`。按下 `Ctrl+Z` 后，程序可能进入 `Stopped` 状态，而不是退出。暂停进程仍然存在，打开的文件描述符不会自动消失，因此脚本持有的 `flock` 仍然有效。

再次运行时就可能看到：

```text
✗ 另一个 clean_usb_logs 实例正在运行
```

其真实链路通常是：

```text
Ctrl+Z
  ↓
前台进程组收到 SIGTSTP
  ↓
旧 sudo/bash 进入 Stopped
  ↓
FD 9 仍然打开
  ↓
flock 仍被旧进程持有
  ↓
新实例获取锁失败
```

### 为什么不能只写 `trap ... TSTP`

仅在 Bash 中加入：

```bash
trap '...' TSTP
```

并不足以覆盖 `sudo bash ...` 的全部场景，因为键盘 `Ctrl+Z` 是由终端驱动作用于整个前台进程组，`sudo` 本身也可能被暂停。

因此 v2.2 使用两层保护：

1. **TTY 层：运行期间禁用 VSUSP。**
2. **Shell 层：仍捕获外部发送的 SIGTSTP。**

启动后先保存原始 TTY 状态：

```bash
TTY_ORIG_STATE=$(stty -g < /dev/tty)
```

然后：

```bash
stty susp undef < /dev/tty
```

这样脚本运行期间按 `Ctrl+Z` 不再触发终端 suspend，也就不会留下继续占用 `flock` 的暂停进程。

退出时恢复：

```bash
stty "$TTY_ORIG_STATE" < /dev/tty
```

### 统一退出与资源释放

v2.2 将这些信号统一纳入退出路径：

```text
SIGINT   Ctrl+C
SIGTERM
SIGHUP
SIGTSTP  外部显式发送
```

清理顺序为：

```text
清除进度显示
    ↓
恢复原始 TTY
    ↓
删除 WORK_DIR
    ↓
flock -u 9
    ↓
关闭 FD 9
    ↓
退出
```

运行期间推荐：

```text
Ctrl+C  -> 安全中止
Ctrl+Z  -> 挂起功能被禁用
```

脚本启动后会显示：

```text
运行期间 Ctrl+Z 挂起已禁用；如需中止请使用 Ctrl+C。
```

### 已经存在的 v2.1 暂停实例怎么处理

v2.2 不能自动释放一个在启动它之前就已经存在的 v2.1 `Stopped` 进程所持有的锁。

先检查：

```bash
jobs -l
```

如果看到旧任务处于 `Stopped`，可以：

```bash
fg %1
```

再按：

```text
Ctrl+C
```

也可以检查锁持有者：

```bash
sudo fuser -v /run/lock/clean_usb_logs.lock
```

不建议把：

```bash
rm /run/lock/clean_usb_logs.lock
```

当成首选方案。`flock` 的锁与打开的文件描述符/inode 生命周期有关；正确处理方式是终止或恢复真正的锁持有进程。

---

## 1. 需求目标

原始需求主要包括两部分：

1. 查看 USB 设备及相关记录；
2. 在管理员确认后，对 USB 连接、块设备、挂载相关日志进行清理。

脚本同时保留两种模式：

### 精准过滤模式

只过滤已识别的 USB 相关内容，例如：

- USB / UAS 事件；
- USB 块设备名；
- 与 USB 关联的 SCSI host；
- USB mount / umount 信息；
- `/media/`、`/mnt/` 中具有明确挂载语义的记录。

### 统一清空模式

针对明确的日志白名单：

- 普通活动日志截断为空；
- 轮转压缩日志删除；
- `dmesg` 整体清理；
- systemd journal 通过官方接口 rotate + vacuum。

统一清空模式破坏性明显更高，因此默认仍然使用精准过滤模式。

---

## 2. 第一版存在的主要问题

第一版脚本已经具备一些不错的安全意识，例如：

- 限定 `/var/log` 白名单；
- `readlink -f` 检查真实路径；
- 清理前备份；
- `flock` 防止并发执行；
- 根盘保护；
- `.gz` 完整性检测；
- 清理后再次验证。

但进一步审查后，仍然发现了一些会影响真实生产环境安全性的实现问题。

---

## 2.1 使用 `removable=1` 判断 USB 设备并不可靠

很多人会把：

```text
/sys/block/sdX/removable
```

理解为“是不是 USB 盘”。

实际上：

```text
removable=1
```

表达的是设备自身是否属于可移除介质，并不等价于：

```text
transport = USB
```

USB 移动硬盘、USB SSD、硬盘盒等设备完全可能表现为：

```text
TRAN=usb
RM=0
```

如果只依赖 `removable=1`，就可能漏掉真实的 USB 存储设备。

### v2 的处理方式

新版改成多来源判断：

```bash
sysfs_is_usb
udev_is_usb
lsblk_is_usb
```

依次参考：

- sysfs block device 的 USB ancestry；
- `udevadm` 中的 `ID_BUS=usb`；
- `lsblk` 中的 `TRAN=usb`。

核心原则变成：

> 判断设备连接总线，而不是判断设备是否标记为 removable。

---

## 3. 不再使用裸 `SCSI` 关键词

旧实现中最危险的匹配之一，是把：

```text
SCSI
```

直接作为 USB 日志关键词。

Linux 中很多非 USB 存储同样位于 SCSI 子系统，例如：

- SATA/SAS 设备；
- iSCSI；
- virtio-scsi；
- 某些虚拟磁盘；
- 普通 SCSI 控制器。

因此：

```regex
USB|removable|SCSI
```

这样的过滤规则范围过大。

它可能把完全与 USB 无关的磁盘日志一并删除。

---

## 3.1 v2：只识别与 USB 上下文关联的 SCSI host

新版采取两阶段关联。

首先只从包含：

```text
USB
UAS
```

上下文的日志中提取：

```text
host6
host7
...
```

然后才根据已确认的 host 去关联：

```text
sd 6:0:0:0: [sdb]
```

这样：

```text
USB -> SCSI host -> sdX
```

形成一条明确的设备关联链。

而普通的：

```text
scsi 2:0:0:0
```

如果没有 USB/UAS 上下文，则不会自动被认为属于 USB。

这也是 v2 中非常重要的一次收敛。

---

## 4. USB 设备识别采用多重来源

新版当前设备识别核心逻辑可以概括为：

```bash
is_current_usb_disk() {
    local n="$1"
    sysfs_is_usb "$n" || udev_is_usb "$n" || lsblk_is_usb "$n"
}
```

三个来源互为补充。

---

## 4.1 sysfs

通过：

```text
/sys/class/block/<device>/device
```

解析真实 sysfs 路径。

如果设备 ancestry 中存在 USB bus，则认为它属于当前 USB 设备。

sysfs 的优点是：

- 不依赖日志；
- 不依赖设备是否 removable；
- 可以直接反映当前内核设备拓扑。

---

## 4.2 udev

如果系统存在：

```bash
udevadm
```

则读取：

```text
ID_BUS=usb
```

这比简单读取 `removable` 更符合我们的实际判断目标。

---

## 4.3 lsblk

最后还可以读取：

```bash
lsblk -ndo TRAN /dev/sdX
```

如果返回：

```text
usb
```

也可以认为设备通过 USB transport 连接。

---

## 5. 历史设备与当前设备必须区分

日志中可能记录：

```text
sdb
```

过去曾经是 USB 盘。

但今天重新启动以后：

```text
sdb
```

可能已经被分配给另一块内部磁盘。

因此不能仅根据历史日志看到 `sdb`，就永久把当前 `/dev/sdb` 当成 USB。

新版加入了这一规则：

> 如果历史设备名当前仍然存在，则必须重新验证当前设备确实仍属于 USB；否则拒绝采信历史名称。

这样可以降低 Linux 动态块设备命名带来的误判风险。

---

## 6. 根盘保护改成 fail-closed

一个拥有：

```bash
umount
```

能力的 root 脚本，最危险的错误之一就是误卸载系统盘。

旧版本如果根盘识别失败，会继续运行，只是失去保护。

v2 改成：

```text
无法建立可靠根盘保护
        ↓
禁止所有自动 USB 卸载
```

也就是典型的：

```text
fail-closed
```

而不是：

```text
fail-open
```

---

## 6.1 根盘解析

新版依赖：

```bash
findmnt
lsblk
```

从：

```text
/
/boot
/boot/efi
```

向上解析物理块设备。

这些磁盘都会加入：

```text
PROTECTED_DISKS
```

列表。

无论如何，下列挂载点不会进入自动卸载候选：

```text
/
/boot
/boot/efi
```

如果根盘无法可靠解析，则：

```text
ROOT_PROTECTION_OK=0
```

后续 USB 自动卸载直接跳过。

---

## 7. USB 挂载仍然需要二次人工确认

即使系统已经识别出 USB 设备，新版也不会直接执行卸载。

流程是：

```text
识别 USB
    ↓
读取 /proc/mounts
    ↓
排除受保护磁盘
    ↓
显示挂载点
    ↓
再次询问管理员
    ↓
用户输入 y 才卸载
```

同时会按挂载路径深度排序：

```text
深层挂载点
    ↓
父挂载点
```

避免先卸载父路径导致子挂载状态异常。

---

## 8. 备份目录改用 `mktemp`

旧版本采用类似：

```bash
/tmp/usb_logs_backup_20260910_093700
```

这样的时间戳目录。

虽然方便阅读，但 root 脚本不应该依赖可预测的 `/tmp` 路径。

新版改为：

```bash
mktemp -d /var/tmp/usb_logs_backup.XXXXXXXX
```

同时设置：

```bash
umask 077
chmod 700
```

这样能够显著降低：

- 目录预创建；
- symlink；
- 其他用户读取敏感日志备份；

等风险。

---

## 9. 每个日志文件必须独立通过备份 gate

这是新版一个比较重要的设计变化。

旧版本的逻辑大致是：

```text
只要至少一个日志备份成功
        ↓
继续修改其他日志
```

这意味着可能出现：

```text
syslog        backup OK
kern.log      backup OK
audit.log     backup FAIL
```

但之后仍然修改：

```text
audit.log
```

这与“先备份后修改”的设计目标不一致。

---

## 9.1 v2：Per-file backup gate

新版使用关联数组记录：

```bash
declare -A BACKUP_OK
declare -A BACKUP_PATH
```

每个文件都有自己的备份状态。

清理阶段会再次检查：

```text
BACKUP_OK[file] == 1
```

只有成功备份的文件才允许被修改。

因此：

```text
backup failed
      ↓
skip clean
```

而不是：

```text
backup failed
      ↓
continue anyway
```

---

## 10. dmesg 也必须先备份

`dmesg` 和普通日志文件不同。

内核 ring buffer 没有一个安全、通用的“只删除其中某几行”的接口。

因此如果管理员确实选择清理，只能整体处理。

新版规则是：

```text
dmesg 导出成功
       ↓
允许 dmesg -C

dmesg 导出失败
       ↓
禁止清理
```

也就是说：

> destructive action 前必须先取得 snapshot。

这和普通日志的 per-file backup gate 保持一致。

---

## 11. journal 不再直接 `rm`

直接删除：

```text
/var/log/journal/*
/run/log/journal/*
```

看似简单，但 journald 可能仍然持有活动 journal 文件的文件描述符。

因此直接：

```bash
rm
```

并不是最稳妥的方式。

新版使用 systemd 提供的管理接口：

```bash
journalctl --sync
journalctl --rotate
journalctl --vacuum-time=1s
journalctl --vacuum-size=1K
```

整体思想是：

```text
sync
 ↓
rotate active journal
 ↓
active 变 archived
 ↓
vacuum archived journal
```

避免直接删除 journald 当前正在使用的 active inode。

同时：

```text
journal backup failed
        ↓
skip journal cleanup
```

---

## 12. 精准模式不再使用 `sed -i`

对于活动日志：

```bash
sed -i
```

可能产生一个新文件，然后通过 rename 替换原文件。

结果就是 inode 发生变化。

日志 daemon 如果仍持有旧 inode，就可能继续向：

```text
deleted inode
```

写数据。

这种情况下：

```text
你看到的新 syslog 已经干净
```

并不代表：

```text
rsyslog 正在往你看到的文件写
```

---

## 12.1 v2 的处理策略

新版先在安全临时目录生成过滤后的内容：

```text
original
   ↓
decode
   ↓
filter
   ↓
encode
   ↓
temporary result
```

验证临时结果后，再把内容覆写到原文件。

这样尽可能：

```text
保持原 inode
```

而不是通过 `sed -i` 替换整个路径对象。

完成后再对：

```text
rsyslog
auditd
```

执行 best-effort reload/restart。

---

## 13. 支持更多轮转压缩格式

真实 Linux 发行版不一定只使用：

```text
.gz
```

日志轮转还可能使用：

```text
.xz
.bz2
.zst
.zstd
```

旧脚本如果只识别 gzip，却又通过通配符收集其他扩展名，就可能把压缩文件当文本交给 `sed`。

新版明确区分：

```text
plain
gzip
xz
bzip2
zstd
unsupported
```

支持：

```text
.gz
.xz
.bz2
.zst
.zstd
```

明确不支持的：

```text
.lz4
.zip
.7z
```

直接跳过，而不是尝试修改。

---

## 14. 修改压缩日志前先做完整性验证

不同格式分别执行：

```bash
gzip -t
xz -t
bzip2 -t
zstd -t
```

只有输入文件本身完整时，才允许进入修改过程。

生成新的压缩文件后，还会再次验证输出。

整个过程遵循：

```text
validate input
     ↓
generate temp
     ↓
validate output
     ↓
overwrite original
```

任何一个阶段失败，原日志都不应该被直接破坏。

---

## 15. 日志路径继续执行白名单保护

`root` 脚本不能随便接受一个路径然后修改。

新版仍然坚持：

```text
LOG_DIR
```

作为根白名单。

默认：

```text
/var/log
```

测试时可以通过：

```bash
USB_LOG_DIR=/tmp/test-logs
```

覆盖。

对于每个日志文件，会：

1. `readlink -f`；
2. 获取真实路径；
3. 检查真实路径仍位于 `LOG_DIR`；
4. 不满足条件则跳过。

因此即使日志目录中存在符号链接，也不会因为符号链接指向其他系统路径而越界修改。

---

## 16. 默认日志白名单

当前版本关注：

```text
kern.log
syslog
auth.log
daemon.log
boot.log
messages
audit/audit.log
dmesg
```

并同时扫描相应的轮转文件。

相比扫描整个：

```text
/var/log/**
```

白名单策略更加可控。

它的原则是：

> 宁可漏掉未知日志，也不要对所有日志进行不可控批量修改。

---

## 17. 匹配规则进一步收窄

基础 USB 匹配不再包含：

```text
SCSI
removable
```

而是更明确地使用：

```text
USB
UAS
ID_BUS=usb
TRAN=usb
```

随后动态追加：

```text
已确认 USB 设备名
已确认 USB SCSI host
mount(/dev/sdX...)
```

挂载路径也不是简单看到：

```text
/media/
/mnt/
```

就删除。

只有在：

```text
mount
unmount
automount
mounted
unmounted
```

等语义上下文中才匹配这些路径。

这样可以减少：

```text
普通应用日志刚好提到 /mnt/foo
```

却被误删的情况。

---

## 18. 查看模式

运行：

```bash
sudo bash clean_usb_logs_v2.2.sh
```

正式询问是否清理前，会先给出一份状态报告。

主要包括：

```text
① 当前 USB 设备
② 当前 USB 块设备
③ 历史 USB 连接
④ 已关联 USB 的 SCSI host
⑤ 当前 USB 挂载
⑥ 日志文件残留扫描
⑦ systemd journal
⑧ 根盘卸载保护
```

因此第一次使用时完全可以：

```text
只查看
不执行清理
```

确认设备识别是否符合预期以后再决定。

---

## 19. 两种使用模式

## 19.1 默认精准模式

```bash
sudo bash clean_usb_logs_v2.2.sh
```

启动后选择：

```text
1 = 精准过滤
```

主要用于只处理匹配的 USB / mount 相关日志。

---

## 19.2 统一清空模式

也可以通过：

```bash
sudo bash clean_usb_logs_v2.2.sh --all
```

预选：

```text
2 = 统一清空
```

该模式会对日志白名单执行整体清理，明显更加激进。

除非是在：

- 一次性测试机；
- 实验环境；
- 可恢复虚拟机；
- 已确认备份完整的维护环境；

否则不建议使用。

---

## 20. 测试环境

脚本提供：

```bash
USB_LOG_DIR
```

用于重定向日志根目录。

例如：

```bash
sudo USB_LOG_DIR=/tmp/test-logs \
    bash clean_usb_logs_v2.2.sh
```

这样可以构造：

```text
/tmp/test-logs/syslog
/tmp/test-logs/kern.log
/tmp/test-logs/syslog.1.gz
...
```

在不直接操作真实 `/var/log` 的情况下验证：

- 日志收集；
- 压缩文件识别；
- USB pattern；
- 清理结果；
- backup gate。

对于任何 root 级日志维护脚本，我都更推荐先通过这种方式构造测试目录。

## 20.1 交互输入为什么不会再被扫描阶段的按键影响

v2.1 将所有破坏性流程中的交互读取统一封装为安全提示函数。其逻辑可以简化为：

```bash
flush_pending_input
read -r -p "当前提示..." value
```

`flush_pending_input` 只在标准输入确实是 TTY 时工作，并最多丢弃有限数量的当前可用字符。这样即使管理员在前面的日志扫描或备份阶段误按了几次 Enter，这些字符也不会自动回答后面的确认问题。

这种设计还有一个有意的副作用：不要在提示显示之前“抢先输入”下一步答案。提前键入的内容会被认为是旧输入并被丢弃。对于 root 级破坏性脚本，这是更安全的取舍。

---

## 21. 依赖工具

基础环境需要：

```text
bash >= 4
coreutils
grep
sed
awk
findmnt
lsblk
flock
```

增强 USB 判断可能使用：

```text
udevadm
lsusb
```

压缩格式则按实际文件决定是否需要：

```text
gzip
xz
bzip2
zstd
```

如果某种压缩日志存在，但对应工具不存在，新版会跳过该日志，而不是尝试把它当成普通文本处理。

---

## 22. 安全流程总结

整个 v2.2 的清理链路可以概括成：

```text
               ┌──────────────┐
               │ root / lock  │
               └──────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │ 收集日志白名单 │
              └───────┬───────┘
                      │
                      ▼
             ┌────────────────┐
             │ 识别 USB / host │
             └────────┬───────┘
                      │
                      ▼
            ┌──────────────────┐
            │ 建立根盘保护链路 │
            └─────────┬────────┘
                      │
                      ▼
              ┌───────────────┐
              │ 创建安全备份   │
              └───────┬───────┘
                      │
              ┌───────▼────────┐
              │ backup gate OK? │
              └─────┬──────┬───┘
                    │Yes   │No
                    │      └──────► skip
                    ▼
            ┌──────────────────┐
            │ 人工确认 USB 卸载 │
            └────────┬─────────┘
                     │
                     ▼
           ┌────────────────────┐
           │ 精准过滤 / 全量清理 │
           └─────────┬──────────┘
                     │
                     ▼
             ┌──────────────┐
             │ 清理后再验证   │
             └──────────────┘
```

这比单纯：

```text
grep -> sed -i -> rm
```

多了不少步骤，但对于一个：

```text
以 root 身份修改系统日志
```

的脚本来说，这些保护是必要的。

---

## 23. 静态检查

当前 `v2.2` 已通过：

```bash
bash -n clean_usb_logs_v2.2.sh
```

并且：

```bash
bash clean_usb_logs_v2.2.sh --help
```

可以正常输出参数说明。v2.2 还额外对 USB/SCSI 解析辅助函数做了样例回归检查，确认能够从 USB/UAS 上下文抽取 USB host，并保留独立的非 USB SCSI host 映射，不再依赖裸 `SCSI` 关键词。

`--help` 当前内容为：

```text
用法: sudo bash clean_usb_logs_v2.2.sh [--all] [--help]

  --all, -a   预选“统一清空”模式
  --help, -h  显示帮助

环境变量:
  USB_LOG_DIR=/path       覆盖日志根目录（测试时可用）
  USB_LOG_LOCK_FILE=path  覆盖 flock 锁文件

默认不带参数为精准过滤模式。
```

需要注意：

> `bash -n` 只能说明 Bash 语法合法，并不能证明脚本已经覆盖所有 Linux 发行版、文件系统、日志系统和块设备拓扑。

如果要进一步用于长期生产环境，仍然应该针对目标发行版建立自动化测试。

---

## 24. 后续还可以继续增强什么

如果继续迭代，我会优先考虑以下几个方向。

### dry-run

加入：

```bash
--dry-run
```

只显示：

```text
哪些文件会变化
哪些行会匹配
哪些 USB 会被认为可卸载
```

完全不产生破坏性修改。

### non-interactive

加入：

```bash
--yes
```

但只建议在明确的 CI / 测试环境使用。

### structured report

支持：

```bash
--report-json
```

输出：

```json
{
  "usb_devices": [],
  "matched_logs": {},
  "protected_disks": [],
  "backup_dir": "",
  "result": ""
}
```

方便自动化审计。

### distribution test matrix

至少覆盖：

```text
Ubuntu / Debian
Rocky / AlmaLinux
RHEL
openSUSE
Kylin
```

因为各发行版在：

- rsyslog；
- journald；
- auditd；
- logrotate；
- 压缩工具；

方面存在实际差异。

---

## 25. 最终结论

这次重构最重要的变化，并不是“让日志删得更彻底”，而是：

> 把一个拥有 root 权限的破坏性脚本，从“尽量能完成任务”改成“无法确认安全时尽量不做”。

核心原则可以总结为：

```text
设备不能确认        -> 不认作 USB
根盘不能确认        -> 不卸载
日志不能备份        -> 不修改
压缩格式不能确认    -> 不处理
临时结果不能验证    -> 不覆盖
journal 不能备份    -> 不 vacuum
用户没有明确确认    -> 不执行
```

对于系统管理脚本而言，这种：

```text
fail-closed
```

的设计通常比“尽可能执行成功”更重要。

最终脚本文件：

```text
clean_usb_logs_v2.2.sh
```

建议第一次使用时先只运行查看流程，并在测试日志目录或虚拟机中完成验证，再决定是否应用到真实系统。

---

## 附：文件说明

项目可以保持下面这种结构：

```text
usb-log-cleaner/
├── clean_usb_logs_v2.2.sh
└── README.md
```

如果作为博客仓库，则可以：

```text
content/
└── linux-usb-log-cleaner.md

scripts/
└── clean_usb_logs_v2.2.sh
```

本文 Markdown 即可直接作为：

```text
linux-usb-log-cleaner.md
```

发布到支持 Markdown 的博客系统中，例如 Hugo、Hexo、VuePress、VitePress 或普通静态站点。

---

## 26. 完整脚本：clean_usb_logs_v2.2.sh

为了便于 Blog 发布、单文件归档和版本管理，下面直接嵌入当前 **v2.2 完整脚本**。

该代码块与独立文件 `clean_usb_logs_v2.2.sh` 由同一份脚本文本生成，因此 Blog 中的完整代码与下载脚本保持一致。

```bash
#!/usr/bin/env bash
#=============================================================================#
#  USB 连接 & 挂载记录 查看/清理脚本 - 安全重构版 v2.2
#
#  目标
#   A. 查看当前/历史 USB 连接、USB 存储设备与挂载记录
#   B. 精准模式: 尽量只删除 USB/设备名/USB-SCSI host/挂载相关日志行
#   C. 全清模式: 清空白名单日志；压缩轮转文件删除
#   D. dmesg / systemd journal 无法可靠按单行删除，按组件整体清理
#
#  主要安全策略
#   - 必须 root 执行；flock 防并发
#   - 日志仅允许位于 LOG_DIR 白名单内，符号链接解析后仍须位于 LOG_DIR
#   - 备份目录使用 mktemp + umask 077，避免 /tmp 可预测目录问题
#   - 每个日志文件“备份成功后才允许修改”；备份失败的文件直接跳过
#   - dmesg 清空前先保存文本快照；journal 清理前先备份持久/内存 journal
#   - 支持 plain/.gz/.xz/.bz2/.zst；未知压缩格式不作为文本修改
#   - 精准清理使用临时文件生成新内容，再覆写原 inode，尽量避免 sed -i 换 inode
#   - USB 判定优先使用 sysfs USB ancestry / udev ID_BUS=usb / lsblk TRAN=usb
#   - 不再把裸 "SCSI" 当作 USB 关键词；仅使用已关联 USB 的 SCSI host
#   - 根盘保护 fail-closed：无法可靠识别根盘时，不自动卸载任何 USB 挂载
#   - /、/boot、/boot/efi 永不卸载；USB 挂载按最深路径优先卸载
#   - journal 使用 journalctl rotate + vacuum，避免直接删除活跃 journal inode
#   - v2.1: 耗时扫描显示逐文件进度；所有交互前清空此前缓存的 TTY 输入
#   - v2.1: 历史日志每个文件只解压/读取一次完成 USB/SCSI 关联分析
#   - v2.2: 运行期间禁用终端 Ctrl+Z 挂起字符，避免 sudo/bash 被暂停后继续占用 flock
#   - v2.2: 捕获 INT/TERM/HUP/TSTP，统一恢复 TTY、清理临时目录并释放 flock
#
#  用法
#     sudo bash clean_usb_logs_v2.2.sh
#     sudo bash clean_usb_logs_v2.2.sh --all
#     sudo USB_LOG_DIR=/tmp/test-logs bash clean_usb_logs_v2.2.sh
#
#  说明
#   - 本脚本用于管理员主动维护。清理日志可能影响审计、取证与故障排查能力。
#   - "精准"表示按已知模式过滤，不代表可数学证明地识别所有 USB 相关日志。
#=============================================================================#

set +e
set -o pipefail
export LC_ALL=C
umask 077

#----------------------------- 配置 -----------------------------------------

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

LOG_DIR="${USB_LOG_DIR:-/var/log}"
LOCK_FILE="${USB_LOG_LOCK_FILE:-/run/lock/clean_usb_logs.lock}"
[ -d /run/lock ] || LOCK_FILE="${USB_LOG_LOCK_FILE:-/var/lock/clean_usb_logs.lock}"

# 基础 USB 语义。故意不包含裸 SCSI/removable，避免把非 USB 存储误删。
BASE_PATTERN='[Uu][Ss][Bb]|[Uu][Aa][Ss]([[:space:]:]|$)|[Ii][Dd]_[Bb][Uu][Ss]=[Uu][Ss][Bb]|[Tt][Rr][Aa][Nn]=[Uu][Ss][Bb]'
EXT_PATTERN="$BASE_PATTERN"

LOG_BASES=()
LOG_FILES=()
USB_DEVS=()               # 当前或历史确认/关联为 USB 的整盘设备名，如 sdb
USB_SCSI_HOSTS=()         # 已与 USB/UAS 上下文关联的 SCSI host 编号
PROTECTED_DISKS=()        # 根/boot 链路中的物理盘
ROOT_PROTECTION_OK=0
CLEAN_MODE="lines"       # lines / all
BACKUP_DIR=""
WORK_DIR=""
JOURNAL_BACKUP_OK=0
DMESG_BACKUP_OK=0

# v2.2: TTY / signal / lock 生命周期状态
TTY_ORIG_STATE=""
TTY_SUSP_DISABLED=0
LOCK_ACQUIRED=0
CLEANUP_DONE=0

# Bash 4+ associative arrays
declare -A BACKUP_OK
declare -A BACKUP_PATH

#----------------------------- UI / 基础 ------------------------------------

ok()   { echo -e "  ${GREEN}✓${NC} $*"; }
info() { echo -e "  ${CYAN}$*${NC}"; }
warn() { echo -e "  ${YELLOW}$*${NC}"; }
fail() { echo -e "  ${RED}✗${NC} $*"; }

rule() {
    echo -e "${CYAN}───────────────────────────────────────────────────────────${NC}"
}

banner() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  ${BOLD}$*${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

have() { command -v "$1" >/dev/null 2>&1; }

# 丢弃耗时扫描/备份阶段中用户提前键入、仍滞留在 TTY 输入队列里的字符。
# 目的不是设置超时，而是确保每个确认提示只接受“提示出现之后”的输入。
flush_pending_input() {
    [ -t 0 ] || return 0

    local ch drained=0 n=0
    # read -n 1 会逐字符消费已经可用的终端输入；短超时仅用于判断“当前是否还有字符”，
    # 不作用于后续真正的用户提示。限制 4096 字节，避免异常输入源导致无限循环。
    while [ "$n" -lt 4096 ] && IFS= read -r -s -n 1 -t 0.01 ch; do
        drained=1
        n=$((n + 1))
    done

    if [ "$drained" -eq 1 ]; then
        warn "已丢弃此前缓存的键盘输入；请根据当前提示重新输入。"
    fi
}

# 所有交互确认统一通过这里读取：显示提示前先清空旧输入，不设置用户输入超时。
# v2.2 中 Ctrl+Z 的终端 suspend 功能被禁用；若 ^Z 作为普通控制字符进入输入，
# 则丢弃本次输入并重新提示，避免它被误当成确认内容。
safe_prompt_read() {
    local var_name="$1" prompt="$2" value=""

    while :; do
        flush_pending_input
        IFS= read -r -p "$prompt" value || value=""

        if [[ "$value" == *$'\032'* ]]; then
            echo ""
            warn "Ctrl+Z 挂起已禁用；如需退出请按 Ctrl+C。请根据当前提示重新输入。"
            value=""
            continue
        fi
        break
    done

    printf -v "$var_name" '%s' "$value"
}

# 扫描大量轮转/压缩日志时只刷新当前一行，避免终端看起来“假死”。
scan_progress() {
    [ -t 1 ] || return 0
    local phase="$1" current="$2" total="$3" name="$4"
    printf '\r\033[K  %b[●]%b %s (%d/%d): %s' "$YELLOW" "$NC" "$phase" "$current" "$total" "$name"
}

clear_scan_progress() {
    [ -t 1 ] && printf '\r\033[K'
    return 0
}

cleanup_tmp() {
    [ -n "$WORK_DIR" ] && [ -d "$WORK_DIR" ] && rm -rf -- "$WORK_DIR" 2>/dev/null
    return 0
}

# v2.2: 保存并修改终端设置。
# Ctrl+Z 通常由 TTY line discipline 转换为 SIGTSTP，并发送给整个前台进程组。
# 当脚本由 `sudo bash ...` 启动时，仅在 bash 内 trap TSTP 不足以保证 sudo 本身不被暂停。
# 因此运行期间直接禁用 TTY 的 VSUSP 字符；退出时无条件恢复原始 stty 状态。
setup_tty_safety() {
    [ -t 0 ] || return 0
    have stty || return 0
    [ -r /dev/tty ] && [ -w /dev/tty ] || return 0

    TTY_ORIG_STATE=$(stty -g < /dev/tty 2>/dev/null) || {
        TTY_ORIG_STATE=""
        return 0
    }

    if stty susp undef < /dev/tty 2>/dev/null; then
        TTY_SUSP_DISABLED=1
    fi
    return 0
}

restore_tty() {
    if [ "${TTY_SUSP_DISABLED:-0}" -eq 1 ] && [ -n "${TTY_ORIG_STATE:-}" ] \
       && [ -r /dev/tty ]; then
        stty "$TTY_ORIG_STATE" < /dev/tty 2>/dev/null || true
    fi
    TTY_SUSP_DISABLED=0
    return 0
}

release_lock() {
    if [ "${LOCK_ACQUIRED:-0}" -eq 1 ]; then
        if have flock; then
            flock -u 9 2>/dev/null || true
        fi
        exec 9>&- 2>/dev/null || true
        LOCK_ACQUIRED=0
    fi
    return 0
}

cleanup_all() {
    [ "${CLEANUP_DONE:-0}" -eq 1 ] && return 0
    CLEANUP_DONE=1

    clear_scan_progress
    restore_tty
    cleanup_tmp
    release_lock
    return 0
}

on_signal() {
    local sig="$1" code="$2"
    clear_scan_progress
    echo ""

    case "$sig" in
        INT)  warn "收到 Ctrl+C / SIGINT，正在安全退出..." ;;
        TSTP) warn "收到 SIGTSTP 挂起请求；为避免暂停进程继续占用锁，改为安全退出..." ;;
        TERM) warn "收到 SIGTERM，正在安全退出..." ;;
        HUP)  warn "收到 SIGHUP，正在安全退出..." ;;
        *)    warn "收到信号 $sig，正在安全退出..." ;;
    esac

    cleanup_all
    exit "$code"
}

trap cleanup_all EXIT
trap 'on_signal INT 130' INT
trap 'on_signal TERM 143' TERM
trap 'on_signal HUP 129' HUP
trap 'on_signal TSTP 148' TSTP

require_bash4() {
    if [ -z "${BASH_VERSION:-}" ] || [ "${BASH_VERSINFO[0]:-0}" -lt 4 ]; then
        fail "需要 Bash 4 或更高版本"
        exit 1
    fi
}

canonicalize_log_dir() {
    local real
    real=$(readlink -f -- "$LOG_DIR" 2>/dev/null)
    if [ -z "$real" ] || [ ! -d "$real" ]; then
        fail "日志目录不存在或无法解析: $LOG_DIR"
        exit 1
    fi
    LOG_DIR="$real"

    LOG_BASES=(
        "$LOG_DIR/kern.log"
        "$LOG_DIR/syslog"
        "$LOG_DIR/auth.log"
        "$LOG_DIR/daemon.log"
        "$LOG_DIR/boot.log"
        "$LOG_DIR/messages"
        "$LOG_DIR/audit/audit.log"
        "$LOG_DIR/dmesg"
    )
}

prepare_work_dir() {
    local root="/var/tmp"
    [ -d "$root" ] && [ -w "$root" ] || root="/tmp"
    WORK_DIR=$(mktemp -d "$root/clean_usb_logs.work.XXXXXXXX" 2>/dev/null)
    if [ -z "$WORK_DIR" ] || [ ! -d "$WORK_DIR" ]; then
        fail "无法创建安全临时目录"
        exit 1
    fi
    chmod 700 "$WORK_DIR" 2>/dev/null
}

#----------------------------- 路径与日志格式 -------------------------------

is_safe_path() {
    local p="$1" real
    [ -n "$p" ] || return 1
    real=$(readlink -f -- "$p" 2>/dev/null) || return 1
    case "$real" in
        "$LOG_DIR"/*) return 0 ;;
        *) return 1 ;;
    esac
}

log_format() {
    case "$1" in
        *.gz)              echo gz ;;
        *.xz)              echo xz ;;
        *.bz2)             echo bz2 ;;
        *.zst|*.zstd)      echo zst ;;
        *.lz4|*.zip|*.7z)  echo unsupported ;;
        *)                 echo plain ;;
    esac
}

format_tool_available() {
    case "$1" in
        plain) return 0 ;;
        gz)    have gzip ;;
        xz)    have xz ;;
        bz2)   have bzip2 ;;
        zst)   have zstd ;;
        *)     return 1 ;;
    esac
}

validate_log_file() {
    local f="$1" fmt
    fmt=$(log_format "$f")
    case "$fmt" in
        plain) [ -r "$f" ] ;;
        gz)    have gzip  && gzip -t -- "$f" >/dev/null 2>&1 ;;
        xz)    have xz    && xz -t -- "$f" >/dev/null 2>&1 ;;
        bz2)   have bzip2 && bzip2 -t -- "$f" >/dev/null 2>&1 ;;
        zst)   have zstd  && zstd -q -t -- "$f" >/dev/null 2>&1 ;;
        *)     return 1 ;;
    esac
}

read_log() {
    local f="$1" fmt
    fmt=$(log_format "$f")
    case "$fmt" in
        plain) cat -- "$f" 2>/dev/null ;;
        gz)    gzip -cd -- "$f" 2>/dev/null ;;
        xz)    xz -cd -- "$f" 2>/dev/null ;;
        bz2)   bzip2 -cd -- "$f" 2>/dev/null ;;
        zst)   zstd -q -dc -- "$f" 2>/dev/null ;;
        *)     return 2 ;;
    esac
}

collect_log_files() {
    LOG_FILES=()
    local base f real fmt

    shopt -s nullglob
    for base in "${LOG_BASES[@]}"; do
        for f in "$base" "$base".* "$base"-[0-9]*; do
            [ -f "$f" ] || continue
            is_safe_path "$f" || {
                warn "跳过不安全路径: $f"
                continue
            }
            real=$(readlink -f -- "$f" 2>/dev/null)
            [ -n "$real" ] && [ -f "$real" ] || continue

            fmt=$(log_format "$real")
            if [ "$fmt" = "unsupported" ]; then
                warn "跳过不支持的压缩格式: $real"
                continue
            fi
            if ! format_tool_available "$fmt"; then
                warn "跳过 $real：缺少 $fmt 解压工具"
                continue
            fi
            LOG_FILES+=("$real")
        done
    done
    shopt -u nullglob

    if [ ${#LOG_FILES[@]} -gt 0 ]; then
        mapfile -t LOG_FILES < <(printf '%s\n' "${LOG_FILES[@]}" | awk '!seen[$0]++')
    fi
}

#----------------------------- USB 设备识别 ---------------------------------

normalize_block_disk() {
    local n="$1" parent
    [ -n "$n" ] || return 1
    n=${n#/dev/}

    if [ -b "/dev/$n" ] && have lsblk; then
        parent=$(lsblk -ndo PKNAME "/dev/$n" 2>/dev/null | head -n1)
        if [ -n "$parent" ]; then
            printf '%s\n' "$parent"
            return 0
        fi
    fi

    # 常见 sdX 分区退化处理；USB 存储主要落在 sd*。
    if [[ "$n" =~ ^(sd[a-z]{1,2})[0-9]+$ ]]; then
        printf '%s\n' "${BASH_REMATCH[1]}"
    else
        printf '%s\n' "$n"
    fi
}

sysfs_is_usb() {
    local n="$1" p
    [ -e "/sys/class/block/$n" ] || return 1
    p=$(readlink -f "/sys/class/block/$n/device" 2>/dev/null)
    [ -n "$p" ] || return 1
    [[ "$p" == *"/usb"* || "$p" == *"/usb/"* || "$p" =~ /usb[0-9]+/ ]]
}

udev_is_usb() {
    local n="$1"
    have udevadm || return 1
    [ -b "/dev/$n" ] || return 1
    udevadm info --query=property --name="/dev/$n" 2>/dev/null | grep -q '^ID_BUS=usb$'
}

lsblk_is_usb() {
    local n="$1" tran
    have lsblk || return 1
    [ -b "/dev/$n" ] || return 1
    tran=$(lsblk -ndo TRAN "/dev/$n" 2>/dev/null | head -n1 | tr '[:upper:]' '[:lower:]')
    [ "$tran" = "usb" ]
}

is_current_usb_disk() {
    local n="$1"
    sysfs_is_usb "$n" || udev_is_usb "$n" || lsblk_is_usb "$n"
}

extract_usb_scsi_hosts_from_stream() {
    # 只从明确出现 usb/uas 的行中抽取 hostN，避免裸 SCSI 误判。
    grep -iE 'usb|uas' 2>/dev/null \
        | grep -oE 'host[0-9]+' 2>/dev/null \
        | sed 's/^host//' 2>/dev/null
}

extract_sd_from_usb_context_stream() {
    grep -iE 'usb|uas' 2>/dev/null \
        | grep -oE 'sd[a-z]{1,2}[0-9]*' 2>/dev/null \
        | sed -E 's/[0-9]+$//' 2>/dev/null
}

extract_scsi_host_sd_pairs_from_stream() {
    # 收集“host -> sdX”映射，但此时不判断 host 是否 USB。
    # 等所有日志扫描结束并得到 USB_SCSI_HOSTS 后，再进行交叉匹配。
    grep -E '(^|[[:space:]])(sd|scsi)[[:space:]]+[0-9]+:[0-9]+:[0-9]+:[0-9]+:.*\[sd[a-z]{1,2}\]' 2>/dev/null \
        | sed -nE 's/.*(sd|scsi)[[:space:]]+([0-9]+):[0-9]+:[0-9]+:[0-9]+:.*\[(sd[a-z]{1,2})\].*/\2 \3/p' 2>/dev/null
}

collect_usb_devices() {
    USB_DEVS=()
    USB_SCSI_HOSTS=()

    local verbose="${1:-0}"
    local raw_devs="" raw_hosts="" raw_pairs="" n d f hits pairs h stream_tmp
    local idx=0 total_files=${#LOG_FILES[@]}

    # 1) 当前块设备：不依赖 removable=1，判断真实 bus/transport。
    for d in /sys/block/*; do
        [ -e "$d" ] || continue
        n=$(basename "$d")
        case "$n" in
            loop*|ram*|zram*|dm-*|md*) continue ;;
        esac
        if is_current_usb_disk "$n"; then
            raw_devs="$raw_devs $n"
        fi
    done

    # 2) 历史日志单遍解压/读取：一次生成临时纯文本，再从同一份内容提取
    #    USB/UAS 直接设备、USB host，以及所有 SCSI host->sdX 映射。
    for f in "${LOG_FILES[@]}"; do
        idx=$((idx + 1))
        [ "$verbose" = "1" ] && scan_progress "分析历史日志" "$idx" "$total_files" "${f#"$LOG_DIR"/}"

        validate_log_file "$f" || continue
        stream_tmp="$WORK_DIR/usb-scan.$$.txt"
        if read_log "$f" > "$stream_tmp" 2>/dev/null; then
            hits=$(extract_sd_from_usb_context_stream < "$stream_tmp")
            [ -n "$hits" ] && raw_devs="$raw_devs $hits"

            hits=$(extract_usb_scsi_hosts_from_stream < "$stream_tmp")
            [ -n "$hits" ] && raw_hosts="$raw_hosts $hits"

            pairs=$(extract_scsi_host_sd_pairs_from_stream < "$stream_tmp")
            [ -n "$pairs" ] && raw_pairs="${raw_pairs}"$'\n'"$pairs"
        fi
        rm -f -- "$stream_tmp"
    done
    [ "$verbose" = "1" ] && clear_scan_progress

    # 当前 dmesg 也只读取一次并参与同样的三类关联。
    if have dmesg; then
        stream_tmp="$WORK_DIR/dmesg.usb-scan.$$.txt"
        if dmesg 2>/dev/null > "$stream_tmp"; then
            hits=$(extract_sd_from_usb_context_stream < "$stream_tmp")
            [ -n "$hits" ] && raw_devs="$raw_devs $hits"

            hits=$(extract_usb_scsi_hosts_from_stream < "$stream_tmp")
            [ -n "$hits" ] && raw_hosts="$raw_hosts $hits"

            pairs=$(extract_scsi_host_sd_pairs_from_stream < "$stream_tmp")
            [ -n "$pairs" ] && raw_pairs="${raw_pairs}"$'\n'"$pairs"
        fi
        rm -f -- "$stream_tmp"
    fi

    if [ -n "${raw_hosts//[[:space:]]/}" ]; then
        mapfile -t USB_SCSI_HOSTS < <(
            printf '%s\n' $raw_hosts 2>/dev/null | grep -E '^[0-9]+$' | sort -n -u
        )
    fi

    # 3) 只把“属于已确认 USB host”的 host->sdX 映射加入设备列表。
    if [ ${#USB_SCSI_HOSTS[@]} -gt 0 ] && [ -n "${raw_pairs//[[:space:]]/}" ]; then
        while read -r h n; do
            [ -n "$h" ] && [ -n "$n" ] || continue
            for d in "${USB_SCSI_HOSTS[@]}"; do
                if [ "$h" = "$d" ]; then
                    raw_devs="$raw_devs $n"
                    break
                fi
            done
        done <<< "$raw_pairs"
    fi

    # 4) 去重；若历史 sdX 名称当前被复用为非 USB 盘，则拒绝采信。
    if [ -n "${raw_devs//[[:space:]]/}" ]; then
        mapfile -t USB_DEVS < <(
            for n in $raw_devs; do
                n=$(normalize_block_disk "$n")
                [[ "$n" =~ ^sd[a-z]{1,2}$ ]] || continue
                if [ -e "/sys/block/$n" ] && ! is_current_usb_disk "$n"; then
                    continue
                fi
                printf '%s\n' "$n"
            done | sort -u
        )
    fi
}

build_pattern() {
    local d h
    EXT_PATTERN="$BASE_PATTERN"

    for d in "${USB_DEVS[@]}"; do
        # 使用显式边界，避免 sdb 匹配到字符串中间。
        EXT_PATTERN+="|(^|[^A-Za-z0-9_])$d[0-9]*([^A-Za-z0-9_]|$)"
        EXT_PATTERN+="|mount\\(/dev/$d[0-9]*"
    done

    for h in "${USB_SCSI_HOSTS[@]}"; do
        EXT_PATTERN+="|[Ss][Cc][Ss][Ii][[:space:]]+[Hh][Oo][Ss][Tt]$h([^0-9]|$)"
        EXT_PATTERN+="|[Ss][Dd][[:space:]]+$h:[0-9]+:[0-9]+:[0-9]+:"
        EXT_PATTERN+="|[Ss][Cc][Ss][Ii][[:space:]]+$h:[0-9]+:[0-9]+:[0-9]+:"
    done

    # 只在挂载语义上下文中匹配 /media 与 /mnt，避免删除任意包含路径的普通日志。
    EXT_PATTERN+='|([Mm]ount|[Uu]nmount|[Aa]utomount|[Mm]ounted|[Uu]nmounted)[^[:cntrl:]]*(/media/|/mnt/)'
    EXT_PATTERN+='|media-[^[:space:]]+\\.mount'
}

count_lines() {
    local f="$1" c
    validate_log_file "$f" || { echo 0; return 1; }
    c=$(read_log "$f" | grep -cE "$EXT_PATTERN" 2>/dev/null)
    echo "${c:-0}"
}

#----------------------------- 根盘 / 挂载保护 ------------------------------

collect_protected_disks() {
    PROTECTED_DISKS=()
    ROOT_PROTECTION_OK=0

    have findmnt || {
        warn "缺少 findmnt，无法建立可靠根盘保护；本次禁止自动卸载"
        return 1
    }
    have lsblk || {
        warn "缺少 lsblk，无法建立可靠根盘保护；本次禁止自动卸载"
        return 1
    }

    local target src name type found_root=0
    for target in / /boot /boot/efi; do
        [ -e "$target" ] || continue
        src=$(findmnt -nro SOURCE -T "$target" 2>/dev/null | head -n1)
        [ -n "$src" ] || continue

        # 对 block source 沿父链向上找 TYPE=disk。
        if [[ "$src" == /dev/* ]] && [ -e "$src" ]; then
            while read -r name type; do
                [ "$type" = "disk" ] || continue
                PROTECTED_DISKS+=("$name")
                [ "$target" = "/" ] && found_root=1
            done < <(lsblk -s -nro NAME,TYPE "$src" 2>/dev/null)
        fi
    done

    if [ ${#PROTECTED_DISKS[@]} -gt 0 ]; then
        mapfile -t PROTECTED_DISKS < <(printf '%s\n' "${PROTECTED_DISKS[@]}" | awk 'NF && !seen[$0]++')
    fi

    if [ "$found_root" -eq 1 ]; then
        ROOT_PROTECTION_OK=1
        return 0
    fi

    # overlay/tmpfs/zfs 等无法回溯物理 root disk 时采取 fail-closed。
    warn "无法可靠解析根文件系统对应的物理盘；本次禁止自动卸载 USB"
    return 1
}

is_protected_disk() {
    local d="$1" p
    for p in "${PROTECTED_DISKS[@]}"; do
        [ "$d" = "$p" ] && return 0
    done
    return 1
}

decode_mount_field() {
    local s="$1"
    s=${s//\\040/ }
    s=${s//\\011/$'\t'}
    s=${s//\\134/\\}
    printf '%s' "$s"
}

usb_mount_entries() {
    [ ${#USB_DEVS[@]} -gt 0 ] || return 0
    [ -r /proc/mounts ] || return 0

    local src mp rest base disk d
    while read -r src mp rest; do
        [[ "$src" == /dev/* ]] || continue
        base=${src#/dev/}
        disk=$(normalize_block_disk "$base")

        for d in "${USB_DEVS[@]}"; do
            [ "$disk" = "$d" ] || continue

            # 根/boot 物理盘永不进入卸载候选。
            is_protected_disk "$disk" && continue

            mp=$(decode_mount_field "$mp")
            case "$mp" in
                /|/boot|/boot/efi) continue ;;
            esac

            printf '%s\t%s\t%s\n' "$src" "$mp" "$disk"
            continue 2
        done
    done < /proc/mounts
}

umount_usb_devices() {
    if [ ${#USB_DEVS[@]} -eq 0 ]; then
        info "无已识别 USB 块设备，跳过卸载"
        return 0
    fi

    if [ "$ROOT_PROTECTION_OK" -ne 1 ]; then
        warn "根盘保护未建立：为避免误卸载系统盘，本次跳过所有自动卸载"
        return 0
    fi

    local entries
    entries=$(usb_mount_entries)
    if [ -z "$entries" ]; then
        info "当前没有可卸载的 USB 挂载"
        return 0
    fi

    echo ""
    echo -e "${CYAN}发现已挂载 USB 设备:${NC}"
    while IFS=$'\t' read -r src mp disk; do
        printf '  %-16s  %s\n' "$src" "$mp"
    done <<< "$entries"
    echo ""

    local ans
    safe_prompt_read ans "先卸载这些 USB 挂载? (y/N): "
    if [[ ! "$ans" =~ ^[Yy]$ ]]; then
        warn "保留当前挂载；仅清理已有日志"
        return 0
    fi

    # 深层挂载点优先，避免父挂载先卸载。
    local sorted src mp disk err
    sorted=$(printf '%s\n' "$entries" | awk -F '\t' '{print length($2) "\t" $0}' | sort -rn | cut -f2-)
    while IFS=$'\t' read -r src mp disk; do
        [ -n "$mp" ] || continue
        echo -ne "  卸载 $mp ... "
        if err=$(umount -- "$mp" 2>&1); then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}~ 跳过 (${err})${NC}"
        fi
    done <<< "$sorted"
}

#----------------------------- 安全备份 -------------------------------------

create_backup_dir() {
    local root="/var/tmp"
    [ -d "$root" ] && [ -w "$root" ] || root="/tmp"

    BACKUP_DIR=$(mktemp -d "$root/usb_logs_backup.XXXXXXXX" 2>/dev/null)
    if [ -z "$BACKUP_DIR" ] || [ ! -d "$BACKUP_DIR" ]; then
        fail "无法创建安全备份目录"
        return 1
    fi
    chmod 700 "$BACKUP_DIR" 2>/dev/null || return 1
    mkdir -p "$BACKUP_DIR/logs" "$BACKUP_DIR/meta" "$BACKUP_DIR/journal" 2>/dev/null || return 1
    ok "备份位置: $BACKUP_DIR"
    return 0
}

backup_one_log() {
    local f="$1" rel dst
    BACKUP_OK["$f"]=0
    BACKUP_PATH["$f"]=""

    is_safe_path "$f" || return 1
    rel=${f#"$LOG_DIR"/}
    [ "$rel" != "$f" ] || return 1
    dst="$BACKUP_DIR/logs/$rel"

    mkdir -p -- "$(dirname -- "$dst")" 2>/dev/null || return 1
    if cp -a -- "$f" "$dst" 2>/dev/null; then
        BACKUP_OK["$f"]=1
        BACKUP_PATH["$f"]="$dst"
        return 0
    fi
    return 1
}

backup_dmesg() {
    DMESG_BACKUP_OK=0
    have dmesg || return 1
    if dmesg > "$BACKUP_DIR/meta/dmesg.txt" 2>/dev/null; then
        chmod 600 "$BACKUP_DIR/meta/dmesg.txt" 2>/dev/null
        DMESG_BACKUP_OK=1
        return 0
    fi
    return 1
}

backup_mount_state() {
    cp -a /proc/mounts "$BACKUP_DIR/meta/proc_mounts.txt" 2>/dev/null || true
    have findmnt && findmnt -a > "$BACKUP_DIR/meta/findmnt.txt" 2>/dev/null || true
    have lsblk && lsblk -O > "$BACKUP_DIR/meta/lsblk.txt" 2>/dev/null || true
}

backup_journal_tree() {
    local src="$1" name="$2"
    [ -d "$src" ] || return 0
    mkdir -p "$BACKUP_DIR/journal/$name" 2>/dev/null || return 1
    cp -a -- "$src"/. "$BACKUP_DIR/journal/$name"/ 2>/dev/null
}

backup_journal() {
    JOURNAL_BACKUP_OK=0

    have journalctl && journalctl --sync >/dev/null 2>&1 || true

    local need=0 ok_all=1
    if [ -d "$LOG_DIR/journal" ]; then
        need=1
        backup_journal_tree "$LOG_DIR/journal" persistent || ok_all=0
    fi
    if [ -d /run/log/journal ]; then
        need=1
        backup_journal_tree /run/log/journal volatile || ok_all=0
    fi

    if [ "$need" -eq 0 ]; then
        # 没有 journal 文件树，也视为无需备份。
        JOURNAL_BACKUP_OK=1
        return 0
    fi

    if [ "$ok_all" -eq 1 ]; then
        JOURNAL_BACKUP_OK=1
        return 0
    fi
    return 1
}

backup_everything() {
    banner "创建安全备份"
    create_backup_dir || return 1

    local f success=0 failed=0
    for f in "${LOG_FILES[@]}"; do
        if backup_one_log "$f"; then
            ok "已备份: ${f#"$LOG_DIR"/}"
            success=$((success + 1))
        else
            fail "备份失败，后续将跳过: $f"
            failed=$((failed + 1))
        fi
    done

    if backup_dmesg; then
        ok "dmesg 快照已备份"
    else
        warn "无法读取/备份 dmesg；后续不会清空 dmesg"
    fi

    backup_mount_state

    if backup_journal; then
        ok "journal 已备份"
    else
        fail "journal 备份不完整；后续不会清理 journal"
    fi

    cat > "$BACKUP_DIR/meta/README.txt" <<META
clean_usb_logs_v2 backup
created: $(date -Is 2>/dev/null || date)
log_dir: $LOG_DIR
mode: $CLEAN_MODE
usb_devices: ${USB_DEVS[*]:-none}
usb_scsi_hosts: ${USB_SCSI_HOSTS[*]:-none}
protected_disks: ${PROTECTED_DISKS[*]:-unknown}
log_backups_ok: $success
log_backups_failed: $failed
dmesg_backup_ok: $DMESG_BACKUP_OK
journal_backup_ok: $JOURNAL_BACKUP_OK
META
    chmod 600 "$BACKUP_DIR/meta/README.txt" 2>/dev/null

    return 0
}

#----------------------------- 日志改写 -------------------------------------

sed_escaped_pattern() {
    # sed 地址 /.../ 中只需把 / 转义；EXT_PATTERN 其余 ERE 保持原样。
    printf '%s' "${EXT_PATTERN//\//\\/}"
}

filter_log_to_tmp() {
    local f="$1" tmp="$2" fmt pat
    fmt=$(log_format "$f")
    pat=$(sed_escaped_pattern)

    validate_log_file "$f" || return 1

    case "$fmt" in
        plain)
            sed -E "/${pat}/d" -- "$f" > "$tmp" 2>/dev/null
            ;;
        gz)
            gzip -cd -- "$f" 2>/dev/null | sed -E "/${pat}/d" | gzip -9c > "$tmp" 2>/dev/null
            ;;
        xz)
            xz -cd -- "$f" 2>/dev/null | sed -E "/${pat}/d" | xz -9c > "$tmp" 2>/dev/null
            ;;
        bz2)
            bzip2 -cd -- "$f" 2>/dev/null | sed -E "/${pat}/d" | bzip2 -9c > "$tmp" 2>/dev/null
            ;;
        zst)
            zstd -q -dc -- "$f" 2>/dev/null | sed -E "/${pat}/d" | zstd -q -c > "$tmp" 2>/dev/null
            ;;
        *)
            return 2
            ;;
    esac
}

validate_generated_file() {
    local tmp="$1" fmt="$2"
    [ -f "$tmp" ] || return 1
    case "$fmt" in
        plain) return 0 ;;
        gz)    gzip -t -- "$tmp" >/dev/null 2>&1 ;;
        xz)    xz -t -- "$tmp" >/dev/null 2>&1 ;;
        bz2)   bzip2 -t -- "$tmp" >/dev/null 2>&1 ;;
        zst)   zstd -q -t -- "$tmp" >/dev/null 2>&1 ;;
        *)     return 1 ;;
    esac
}

restore_from_backup() {
    local f="$1" b="${BACKUP_PATH[$1]:-}"
    [ -n "$b" ] && [ -f "$b" ] || return 1
    cat -- "$b" > "$f" 2>/dev/null
}

clean_log_file() {
    local f="$1" tmp fmt

    [ "${BACKUP_OK[$f]:-0}" -eq 1 ] || {
        echo -e " ${YELLOW}跳过${NC} (无成功备份)"
        return 1
    }

    fmt=$(log_format "$f")
    tmp="$WORK_DIR/filtered.$RANDOM.$$.${fmt}"

    if ! filter_log_to_tmp "$f" "$tmp"; then
        rm -f -- "$tmp"
        echo -e " ${RED}✗${NC} (读取/过滤失败，原文件未改动)"
        return 1
    fi

    if ! validate_generated_file "$tmp" "$fmt"; then
        rm -f -- "$tmp"
        echo -e " ${RED}✗${NC} (生成结果校验失败，原文件未改动)"
        return 1
    fi

    # 覆写内容而非 rename，保留原 inode/权限/属主/xattr。
    if cat -- "$tmp" > "$f" 2>/dev/null; then
        rm -f -- "$tmp"
        echo -e " ${GREEN}✓${NC}"
        return 0
    fi

    fail "写回失败，尝试从备份恢复: $f"
    restore_from_backup "$f" >/dev/null 2>&1 || fail "自动恢复失败，请使用 $BACKUP_DIR 手工恢复"
    rm -f -- "$tmp"
    echo -e " ${RED}✗${NC}"
    return 1
}

wipe_log_file() {
    local f="$1" fmt

    [ "${BACKUP_OK[$f]:-0}" -eq 1 ] || return 1
    fmt=$(log_format "$f")

    case "$fmt" in
        plain)
            : > "$f" 2>/dev/null || {
                restore_from_backup "$f" >/dev/null 2>&1
                return 1
            }
            ;;
        gz|xz|bz2|zst)
            rm -f -- "$f" 2>/dev/null || return 1
            ;;
        *)
            return 1
            ;;
    esac
    return 0
}

#----------------------------- journal / service ----------------------------

safe_reload_or_restart() {
    local svc="$1"
    have systemctl || return 1
    systemctl cat "$svc" >/dev/null 2>&1 || return 1
    systemctl is-active --quiet "$svc" >/dev/null 2>&1 || return 1

    systemctl reload "$svc" >/dev/null 2>&1 && return 0
    systemctl restart "$svc" >/dev/null 2>&1
}

clean_journal() {
    [ "$JOURNAL_BACKUP_OK" -eq 1 ] || {
        echo -e " ${YELLOW}跳过${NC} (journal 未完整备份)"
        return 1
    }
    have journalctl || {
        echo -e " ${YELLOW}跳过${NC} (journalctl 不可用)"
        return 1
    }

    # 官方接口：先把当前 active journal 旋转为 archived，再 vacuum archived。
    # vacuum 不删除当前 active 文件，因此避免直接 rm 活跃 inode。
    journalctl --sync >/dev/null 2>&1 || true
    if ! journalctl --rotate >/dev/null 2>&1; then
        echo -e " ${RED}✗${NC} (journal rotate 失败)"
        return 1
    fi

    # --vacuum-time=1s 删除绝大多数刚旋转前的历史；再用极小 size 清理剩余归档。
    # 两个操作都只针对 archived journal。
    journalctl --vacuum-time=1s >/dev/null 2>&1 || true
    journalctl --vacuum-size=1K >/dev/null 2>&1 || true

    echo -e " ${GREEN}✓${NC}"
    return 0
}

#----------------------------- 查看 -----------------------------------------

view_records() {
    banner "USB 设备使用记录查看"

    echo -ne "  ${YELLOW}[●]${NC} 收集白名单日志文件..."
    collect_log_files
    echo -e " ${GREEN}✓${NC} (${#LOG_FILES[@]} 个)"

    echo -e "  ${YELLOW}[●]${NC} 分析当前/历史 USB 与 SCSI 关联（日志较多时会逐文件显示进度）"
    collect_usb_devices 1
    build_pattern
    ok "USB 关联分析完成：设备 ${#USB_DEVS[@]} 个，SCSI host ${#USB_SCSI_HOSTS[@]} 个"
    echo ""

    echo -e "${CYAN}① 当前 USB 设备${NC}"; rule
    if have lsusb; then
        lsusb 2>/dev/null || echo "  无法读取 lsusb"
    else
        echo "  lsusb 未安装"
    fi
    echo ""

    echo -e "${CYAN}② 当前 USB 块设备${NC}"; rule
    if [ ${#USB_DEVS[@]} -gt 0 ]; then
        local d
        for d in "${USB_DEVS[@]}"; do
            if [ -e "/sys/block/$d" ]; then
                if have lsblk; then
                    lsblk -dn -o NAME,SIZE,MODEL,TRAN,RM "/dev/$d" 2>/dev/null | sed 's/^/  /'
                else
                    echo "  /dev/$d"
                fi
            fi
        done
    else
        echo "  无"
    fi
    echo ""

    echo -e "${CYAN}③ 历史 USB 连接 (dmesg)${NC}"; rule
    local dmesg_usb=""
    have dmesg && dmesg_usb=$(dmesg 2>/dev/null | grep -iE 'usb.*(new|disconnect|device|storage)|uas' | head -30)
    if [ -n "$dmesg_usb" ]; then
        sed 's/^/  /' <<< "$dmesg_usb"
    else
        echo "  无可见记录"
    fi
    echo ""

    echo -e "${CYAN}④ 已关联 USB 的 SCSI host${NC}"; rule
    if [ ${#USB_SCSI_HOSTS[@]} -gt 0 ]; then
        info "host: ${USB_SCSI_HOSTS[*]}"
    else
        echo "  无"
    fi
    echo ""

    echo -e "${CYAN}⑤ 当前 USB 挂载${NC}"; rule
    local mounts
    mounts=$(usb_mount_entries)
    if [ -n "$mounts" ]; then
        while IFS=$'\t' read -r src mp disk; do
            printf '  %-16s  %s\n' "$src" "$mp"
        done <<< "$mounts"
        warn "清理时会单独询问是否卸载"
    else
        echo "  无"
    fi
    echo ""

    echo -e "${CYAN}⑥ 日志文件残留扫描${NC}"; rule
    local total=0 found=0 f c
    [ ${#LOG_FILES[@]} -eq 0 ] && info "未发现白名单日志文件"
    for f in "${LOG_FILES[@]}"; do
        c=$(count_lines "$f"); c=${c:-0}
        if [ "$c" -gt 0 ] 2>/dev/null; then
            fail "${f#"$LOG_DIR"/} : $c 条"
            found=1
            total=$((total + c))
        else
            ok "${f#"$LOG_DIR"/} : 0 条"
        fi
    done
    [ "$found" -eq 1 ] && echo -e "\n  ${RED}文件日志合计残留: ${BOLD}${total} 条${NC}"
    echo ""

    echo -e "${CYAN}⑦ systemd journal${NC}"; rule
    if have journalctl; then
        local jk jt
        jk=$(journalctl -k --no-pager 2>/dev/null | grep -cE "$EXT_PATTERN"); jk=${jk:-0}
        jt=$(journalctl --no-pager 2>/dev/null | grep -cE "$EXT_PATTERN"); jt=${jt:-0}
        info "内核层 $jk 条，全量 journal $jt 条"
    else
        info "journalctl 不可用"
    fi
    echo ""

    echo -e "${CYAN}⑧ 根盘卸载保护${NC}"; rule
    if [ "$ROOT_PROTECTION_OK" -eq 1 ]; then
        ok "受保护物理盘: ${PROTECTED_DISKS[*]}"
    else
        warn "根盘无法可靠解析：自动卸载功能已 fail-closed"
    fi
}

#----------------------------- 清理主流程 -----------------------------------

clean_logs() {
    banner "USB 日志清理"

    local mode_desc
    if [ "$CLEAN_MODE" = "all" ]; then
        mode_desc="统一清空：白名单普通日志截断为空，压缩轮转删除；dmesg/journal 整体清理"
    else
        mode_desc="精准过滤：白名单日志仅删除 USB/设备/USB-SCSI host/挂载相关行；dmesg/journal 整体清理"
    fi

    echo -e "${RED}警告：该操作会删除系统日志内容，可能影响审计、取证与故障排查。${NC}"
    echo ""
    echo -e "模式: ${BOLD}$mode_desc${NC}"
    echo "保护策略:"
    echo "  - 每个文件必须先成功备份，否则该文件不会修改"
    echo "  - dmesg 必须先成功导出，否则不会清空"
    echo "  - journal 必须先完整备份，否则不会 vacuum"
    echo "  - 根盘识别失败时禁止自动卸载"
    echo "  - 当前 USB 挂载是否卸载会再次单独确认"
    echo ""

    local confirm
    safe_prompt_read confirm "确认执行? (输入 YES): "
    if [ "$confirm" != "YES" ]; then
        warn "已取消"
        return 0
    fi

    # 重新收集，避免 view 到 clean 之间设备状态变化。
    collect_log_files
    collect_usb_devices
    build_pattern
    collect_protected_disks >/dev/null 2>&1 || true

    info "USB 设备: ${BOLD}${USB_DEVS[*]:-无}${NC}"
    info "USB SCSI host: ${BOLD}${USB_SCSI_HOSTS[*]:-无}${NC}"

    # 先备份，再进行任何破坏性动作。
    backup_everything || {
        fail "无法建立安全备份目录，终止清理"
        return 1
    }

    banner "卸载 USB 挂载"
    umount_usb_devices

    # 卸载动作本身可能产生新的 mount/umount 日志；重新收集文件和模式。
    collect_log_files
    collect_usb_devices
    build_pattern

    banner "开始清理"

    echo -ne "${YELLOW}[●] 清空 dmesg...${NC}"
    if [ "$DMESG_BACKUP_OK" -eq 1 ]; then
        if dmesg -C 2>/dev/null; then
            echo -e " ${GREEN}✓${NC}"
        else
            echo -e " ${YELLOW}~${NC} (内核/CAP_SYSLOG 禁止清除)"
        fi
    else
        echo -e " ${YELLOW}跳过${NC} (无成功备份)"
    fi

    local f
    for f in "${LOG_FILES[@]}"; do
        echo -ne "${YELLOW}[●] ${f#"$LOG_DIR"/}...${NC}"

        # 文件可能是在卸载后新出现/轮转出来的；若之前没有备份，严格跳过。
        if [ "${BACKUP_OK[$f]:-0}" -ne 1 ]; then
            echo -e " ${YELLOW}跳过${NC} (该文件未在备份阶段成功备份)"
            continue
        fi

        if [ "$CLEAN_MODE" = "all" ]; then
            if wipe_log_file "$f"; then
                echo -e " ${GREEN}✓${NC} (已清空/删除轮转压缩文件)"
            else
                echo -e " ${RED}✗${NC}"
            fi
        else
            clean_log_file "$f"
        fi
    done

    echo -ne "${YELLOW}[●] 清理 journal...${NC}"
    clean_journal

    # 保留原 inode 时通常无需 reopen；这里仅做 best-effort reload，促使日志服务刷新状态。
    echo -ne "${YELLOW}[●] 刷新日志服务...${NC}"
    local changed=0 svc
    for svc in rsyslog auditd; do
        safe_reload_or_restart "$svc" && changed=1
    done
    if [ "$changed" -eq 1 ]; then
        echo -e " ${GREEN}✓${NC}"
    else
        echo -e " ${YELLOW}跳过${NC} (服务未运行/不允许 reload/restart)"
    fi

    banner "清理验证"
    local total=0 c
    for f in "${LOG_FILES[@]}"; do
        [ -e "$f" ] || {
            ok "${f#"$LOG_DIR"/} : 已不存在"
            continue
        }
        c=$(count_lines "$f"); c=${c:-0}
        if [ "$c" -gt 0 ] 2>/dev/null; then
            fail "${f#"$LOG_DIR"/} : 仍有 $c 条"
            total=$((total + c))
        else
            ok "${f#"$LOG_DIR"/} : 干净"
        fi
    done

    local dc=0 jc=0 live
    if have dmesg; then
        dc=$(dmesg 2>/dev/null | grep -cE "$EXT_PATTERN"); dc=${dc:-0}
        if [ "$dc" -gt 0 ] 2>/dev/null; then
            fail "dmesg: 仍有 $dc 条"
            total=$((total + dc))
        else
            ok "dmesg: 无匹配残留"
        fi
    fi

    if have journalctl; then
        jc=$(journalctl --no-pager 2>/dev/null | grep -cE "$EXT_PATTERN"); jc=${jc:-0}
        if [ "$jc" -gt 0 ] 2>/dev/null; then
            fail "journal: 仍有 $jc 条"
            total=$((total + jc))
        else
            ok "journal: 无匹配残留"
        fi
    fi

    live=$(usb_mount_entries)
    if [ -n "$live" ]; then
        fail "/proc/mounts 仍有 USB 挂载:"
        while IFS=$'\t' read -r src mp disk; do
            printf '    %-16s  %s\n' "$src" "$mp"
        done <<< "$live"
    else
        ok "/proc/mounts: 无可识别 USB 挂载"
    fi

    banner "完成"
    if [ "$total" -eq 0 ]; then
        echo -e "${GREEN}未发现匹配的 USB 连接/挂载日志残留。${NC}"
    else
        echo -e "${YELLOW}验证仍发现 $total 条匹配记录，请检查上方清单。${NC}"
    fi
    echo ""
    echo -e "备份目录: ${CYAN}$BACKUP_DIR${NC}"
    echo "确认系统正常后，可由管理员手工删除该备份目录。"
}

#----------------------------- 参数 / 主程序 --------------------------------

usage() {
    cat <<USAGE
用法: sudo bash $0 [--all] [--help]

  --all, -a   预选“统一清空”模式
  --help, -h  显示帮助

环境变量:
  USB_LOG_DIR=/path       覆盖日志根目录（测试时可用）
  USB_LOG_LOCK_FILE=path  覆盖 flock 锁文件

交互说明:
  Ctrl+C                  安全退出
  Ctrl+Z                  运行期间禁用挂起，避免暂停进程持续占用 flock

默认不带参数为精准过滤模式。
USAGE
}

parse_args() {
    local arg
    for arg in "$@"; do
        case "$arg" in
            -a|--all) CLEAN_MODE="all" ;;
            -h|--help) usage; exit 0 ;;
            *) fail "未知参数: $arg"; usage; exit 1 ;;
        esac
    done
}

acquire_lock() {
    have flock || {
        warn "flock 不可用，无法提供并发保护"
        return 0
    }

    local lock_dir
    lock_dir=$(dirname -- "$LOCK_FILE")
    [ -d "$lock_dir" ] || mkdir -p -- "$lock_dir" 2>/dev/null

    exec 9>"$LOCK_FILE" || {
        fail "无法打开锁文件: $LOCK_FILE"
        exit 1
    }
    chmod 600 "$LOCK_FILE" 2>/dev/null

    if ! flock -n 9; then
        fail "另一个 clean_usb_logs 实例正在运行"

        local holders=""
        if have fuser; then
            holders=$(fuser "$LOCK_FILE" 2>/dev/null | xargs 2>/dev/null)
            [ -n "$holders" ] && warn "当前锁持有 PID: $holders"
        fi

        warn "如果此前运行的是 v2.1 并按过 Ctrl+Z，可先执行: jobs -l"
        warn "必要时可检查: sudo fuser -v $LOCK_FILE"
        exec 9>&- 2>/dev/null || true
        exit 1
    fi

    LOCK_ACQUIRED=1
}

main() {
    require_bash4

    if [ "${EUID:-$(id -u)}" -ne 0 ]; then
        fail "请使用 root 运行: sudo bash $0"
        exit 1
    fi

    # 尽早禁用 Ctrl+Z 的 TTY suspend，避免扫描期间误按导致 sudo/bash 整组暂停。
    setup_tty_safety

    parse_args "$@"
    canonicalize_log_dir
    prepare_work_dir
    acquire_lock
    collect_protected_disks >/dev/null 2>&1 || true

    [ -t 1 ] && clear
    echo -e "${BOLD}${CYAN}"
    cat <<'TITLE'
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃   USB 连接 & 挂载记录 清理工具 v2.2   ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
TITLE
    echo -e "${NC}"

    if [ "$TTY_SUSP_DISABLED" -eq 1 ]; then
        info "运行期间 Ctrl+Z 挂起已禁用；如需中止请使用 Ctrl+C。"
        echo ""
    fi

    view_records

    echo ""
    local def m
    if [ "$CLEAN_MODE" = "all" ]; then def=2; else def=1; fi
    safe_prompt_read m "清理模式? (1=精准过滤 2=统一清空) [默认 $def]: "
    case "${m:-$def}" in
        2) CLEAN_MODE="all" ;;
        *) CLEAN_MODE="lines" ;;
    esac

    echo ""
    local choice
    safe_prompt_read choice "执行清理? (y/N): "
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        clean_logs
    else
        warn "已退出"
    fi
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
    main "$@"
fi
```

> 如果从本文复制脚本，请保存为 `clean_usb_logs_v2.2.sh`，先执行 `bash -n clean_usb_logs_v2.2.sh` 做语法检查。首次运行建议先查看扫描结果，再决定是否执行清理。
