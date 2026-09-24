---

layout: post
title: 'C++ Performance Analysis Guide / C++ 性能分析指南'
summary: 'Survey of C++ performance analysis and optimization tools, from time and perf to VTune, valgrind, sanitizers, and CPU pinning, with practical usage examples.'
lang: en
date: 2026-09-05 01:41:00
categories:
- C & C++
tags:
- C++
- Tool
- Debug
---
> A comprehensive guide for profiling and optimizing C++ applications.
> 一份全面的 C++ 应用程序性能分析与优化指南。

---

<!--more-->

## Quick Overview / 快速概览

| Tool / 工具 | Use Case / 用途 | Overhead / 开销 |
|-------------|-----------------|-----------------|
| `time` | Quick timing / 快速计时 | Minimal / 极低 |
| `perf` | CPU profiling / CPU 分析 | Low / 低 |
| `VTune` | Hardware analysis / 硬件分析 | Medium / 中等 |
| `valgrind` | Memory/Cache / 内存/缓存 | High / 高 |
| Sanitizers | Memory/Thread errors / 内存/线程错误 | Medium-High / 中高 |
| `taskset` | CPU pinning / 绑核 | None / 无 |

---

## 1. time - 基础计时工具

> `time` is the simplest profiling tool. It measures wall clock time, user CPU time, and system CPU time.
> `time` 是最简单的性能分析工具，用于测量实际时间、用户态 CPU 时间和内核态 CPU 时间。

### Basic Usage / 基本用法

```bash
# Simple timing / 简单计时
time ./my_program

# Detailed output (Linux) / 详细输出
/usr/bin/time -v ./my_program
```

### Understanding the Output / 理解输出

```bash
# Example output:
# real    0m1.234s    # Wall clock time (实际经过的时间)
# user    0m1.100s    # CPU time in user mode (用户态 CPU 时间)
# sys     0m0.100s    # CPU time in kernel mode (内核态 CPU 时间)

# Key insights / 关键分析:
# - If sys >> 0: too many system calls (系统调用过多)
# - If user < real: program is I/O bound or sleeping (程序 I/O 密集或在等待)
# - If user ≈ real: program is CPU bound (程序 CPU 密集)
```

### Shell-specific Syntax / 不同 Shell 的语法

```bash
# Bash - custom format / 自定义格式
TIMEFORMAT='%R seconds (real), %U seconds (user), %S seconds (sys)'
time ./my_program

# Zsh - detailed output by default / 默认详细输出
time ./my_program
```

### Benchmarking Script / 性能测试脚本

```bash
#!/bin/bash
# Benchmark script with multiple runs / 多次运行的基准测试脚本

RUNS=10
TOTAL=0

echo "Benchmarking: $1"
echo "Running $RUNS times..."

for i in $(seq 1 $RUNS); do
    start=$(date +%s%N)
    $1
    end=$(date +%s%N)
    elapsed=$(( (end - start) / 1000000 ))
    TOTAL=$((TOTAL + elapsed))
    echo "Run $i: ${elapsed}ms"
done

AVG=$((TOTAL / RUNS))
echo "Average: ${AVG}ms"
```

---

## 2. perf - Linux 性能分析工具

> `perf` is a powerful profiling tool built into the Linux kernel. It can track CPU events, cache misses, branch predictions, and more.
> `perf` 是 Linux 内核内置的强大性能分析工具，可追踪 CPU 事件、缓存未命中、分支预测等。

### Installation / 安装

```bash
# Ubuntu/Debian
sudo apt install linux-tools-common linux-tools-$(uname -r)

# CentOS/RHEL
sudo yum install perf
```

### Basic Usage / 基本用法

```bash
# Quick performance statistics / 快速性能统计
perf stat ./my_program

# Record profiling data with call stacks / 记录性能数据（含调用栈）
perf record -g ./my_program

# View the report / 查看报告
perf report

# Interactive mode / 交互模式
perf report --stdio
```

### Understanding perf stat / 理解 perf stat 输出

```bash
# Example output:
# 1,234,567,890  cpu-cycles         # 3.456 GHz
#   234,567,890  instructions       # 0.19  insn per cycle  <-- IPC (每周期指令数)
#     1,234,567  cache-references   # 345.678 MiB/s
#       123,456  cache-misses       # 10.00% of all cache refs  <-- 缓存未命中率
#      12,345,678 branches          # 3456.789 M/sec
#         123,456 branch-misses     # 1.00% of all branches  <-- 分支预测失败率

# Key metrics to watch / 需要关注的关键指标:
# - IPC > 1 is good (IPC > 1 表示性能良好)
# - cache-misses < 5% is good (缓存未命中率 < 5% 为佳)
# - branch-misses < 2% is good (分支预测失败率 < 2% 为佳)
```

### Useful Events / 常用事件

```bash
# List all available events / 列出所有可用事件
perf list

# Common useful events / 常用事件:
# cpu-cycles        - CPU 周期数
# instructions      - 指令数
# cache-references  - 缓存访问次数
# cache-misses      - 缓存未命中次数
# branch-instructions - 分支指令数
# branch-misses     - 分支预测失败次数
# context-switches  - 上下文切换次数
# page-faults       - 页面错误次数

# Profile specific events / 分析特定事件
perf stat -e cache-misses,cache-references,branches,branch-misses ./my_program

# More detailed hardware counters / 更详细的硬件计数器
perf stat -d ./my_program
```

### Flame Graphs / 火焰图

> Flame graphs visualize where time is spent. Each block represents a function; wider blocks = more time.
> 火焰图可视化时间花费的位置。每个块代表一个函数，越宽表示耗时越多。

```bash
# Install FlameGraph tool / 安装 FlameGraph 工具
git clone https://github.com/brendangregg/FlameGraph.git
export PATH=$PATH:$(pwd)/FlameGraph

# Record with perf / 使用 perf 记录
perf record -F 99 -g ./my_program

# Generate flame graph / 生成火焰图
perf script | stackcollapse-perf.pl | flamegraph.pl > flamegraph.svg

# Open in browser / 在浏览器中打开
# flamegraph.svg
```

### Practical Examples / 实际示例

```bash
# Find cache miss hotspots / 查找缓存未命中热点
perf record -e cache-misses ./my_program
perf report

# Compare two versions / 比较两个版本
perf stat -o perf1.txt ./my_program_v1
perf stat -o perf2.txt ./my_program_v2
perf diff perf1.txt perf2.txt

# Trace a running process / 追踪运行中的进程
perf record -p <pid> -g -- sleep 10

# Top-like real-time view / 类似 top 的实时视图
perf top
```

---

## 3. Intel VTune - 深度硬件分析

> VTune provides deep hardware-level analysis including CPU microarchitecture, memory access patterns, and threading issues.
> VTune 提供深度硬件级分析，包括 CPU 微架构、内存访问模式和线程问题。

### Installation / 安装

```bash
# Intel oneAPI Toolkit includes VTune
# 下载地址: https://www.intel.com/content/www/us/en/developer/tools/oneapi/vtune-profiler.html

# Source environment / 加载环境变量
source /opt/intel/oneapi/vtune/latest/env/vars.sh
```

### Basic Usage / 基本用法

```bash
# Hotspots analysis (find CPU bottlenecks) / 热点分析（查找 CPU 瓶颈）
vtune -collect hotspots ./my_program

# Memory analysis (find memory issues) / 内存分析（查找内存问题）
vtune -collect memory ./my_program

# Threading analysis (find synchronization issues) / 线程分析（查找同步问题）
vtune -collect threading ./my_program

# Generate summary report / 生成摘要报告
vtune -report summary -result-dir ./rslt
```

### Common Collect Modes / 常见收集模式

```bash
# Hotspots - CPU bound issues / 热点分析 - CPU 密集型问题
vtune -collect hotspots -duration 30 ./my_program

# Memory - bandwidth, NUMA issues / 内存分析 - 带宽、NUMA 问题
vtune -collect memory -knob analyze-mem-objects=true ./my_program

# Threading - synchronization issues / 线程分析 - 同步问题
vtune -collect threading ./my_program

# I/O analysis / I/O 分析
vtune -collect io ./my_program
```

### GUI Analysis / 图形界面分析

```bash
# Open results in GUI / 在图形界面中打开结果
vtune-gui ./rslt
```

---

## 4. CPU Pinning / 绑核

> Binding processes to specific CPU cores reduces context switches and improves cache locality.
> 将进程绑定到特定 CPU 核心可以减少上下文切换并提高缓存局部性。

### taskset

```bash
# Run on cores 0-15 / 在核心 0-15 上运行
taskset -c 0-15 ./my_program

# Run on specific core / 在特定核心上运行
taskset -c 0 ./my_program

# Get current affinity / 获取当前亲和性
taskset -p <pid>

# Modify running process / 修改运行中的进程
taskset -pc 2-3 <pid>

# Combine with other tools / 与其他工具结合使用
taskset -c 0-3 perf record -g ./my_program
```

### numactl

```bash
# Bind to NUMA node 0 / 绑定到 NUMA 节点 0
numactl --cpunodebind=0 ./my_program

# Bind to specific CPUs / 绑定到特定 CPU
numactl --cpubind=0,1 ./my_program

# Memory on same NUMA node / 内存在同一 NUMA 节点
numactl --cpunodebind=0 --membind=0 ./my_program

# Check NUMA topology / 检查 NUMA 拓扑
numactl --hardware
lscpu
```

### cgroups (Container-level) / cgroups（容器级别）

```bash
# Create cpuset cgroup (cgroups v2) / 创建 cpuset cgroup（cgroups v2）
sudo mkdir /sys/fs/cgroup/myapp
echo "0-3" | sudo tee /sys/fs/cgroup/myapp/cpuset.cpus
echo "<pid>" | sudo tee /sys/fs/cgroup/myapp/cgroup.procs
```

---

## 5. Sanitizers - 代码消毒器

> Sanitizers detect memory errors, data races, and undefined behavior at runtime.
> 消毒器在运行时检测内存错误、数据竞争和未定义行为。

### AddressSanitizer (ASan) - 内存错误检测

> Detects: buffer overflows, use-after-free, stack overflow, etc.
> 检测：缓冲区溢出、释放后使用、栈溢出等。

```bash
# Compile / 编译
g++ -fsanitize=address -fno-omit-frame-pointer -g my_code.cpp -o my_program

# Run (no special flags needed) / 运行（无需特殊标志）
./my_program

# With leak detection / 启用内存泄漏检测
ASAN_OPTIONS=detect_leaks=1 ./my_program

# With additional checks / 启用额外检查
ASAN_OPTIONS=detect_stack_use_after_return=1 ./my_program
```

### ThreadSanitizer (TSan) - 线程错误检测

> Detects: data races between threads.
> 检测：线程间的数据竞争。

```bash
# Compile / 编译
g++ -fsanitize=thread -g my_code.cpp -o my_program

# Run / 运行
./my_program

# With options / 带选项
TSAN_OPTIONS=history_size=7 ./my_program
```

### UndefinedBehaviorSanitizer (UBSan) - 未定义行为检测

> Detects: signed integer overflow, null pointer dereference, etc.
> 检测：有符号整数溢出、空指针解引用等。

```bash
# Compile / 编译
g++ -fsanitize=undefined -g my_code.cpp -o my_program

# Run with stack trace / 运行并输出堆栈跟踪
UBSAN_OPTIONS=print_stacktrace=1 ./my_program
```

### Combined Usage / 组合使用

```bash
# Note: TSan + ASan cannot be combined
# 注意：TSan 和 ASan 不能同时使用

# ASan + UBSan / 组合使用
g++ -fsanitize=address,undefined -fno-omit-frame-pointer -g my_code.cpp -o my_program

# TSan + UBSan / 组合使用
g++ -fsanitize=thread,undefined -g my_code.cpp -o my_program
```

---

## 6. Valgrind - 内存调试工具

> Valgrind instruments your program to detect memory errors, cache behavior, and threading issues.
> Valgrind 通过插桩检测程序的内存错误、缓存行为和线程问题。

### Memcheck (Memory Errors) - 内存错误检测

> The default tool. Detects memory leaks, invalid reads/writes, use of uninitialized memory.
> 默认工具，检测内存泄漏、无效读写、使用未初始化内存。

```bash
# Basic memory check / 基本内存检查
valgrind --leak-check=full ./my_program

# With log file / 输出到日志文件
valgrind --leak-check=full --log-file=valgrind.log ./my_program

# Track file descriptors / 追踪文件描述符
valgrind --track-fds=yes ./my_program

# Show reachable memory / 显示可访问内存
valgrind --leak-check=full --show-reachable=yes ./my_program
```

### Callgrind (Profiling) - 性能分析

> Records function call information. Use with KCachegrind for visualization.
> 记录函数调用信息，配合 KCachegrind 可视化。

```bash
# Profile with callgrind / 使用 callgrind 分析
valgrind --tool=callgrind ./my_program

# Analyze results / 分析结果
callgrind_annotate callgrind.out.<pid>

# Visualize with KCachegrind / 使用 KCachegrind 可视化
kcachegrind callgrind.out.<pid>
```

### Cachegrind (Cache Simulation) - 缓存模拟

> Simulates CPU cache behavior to find cache misses.
> 模拟 CPU 缓存行为，找出缓存未命中。

```bash
# Cache simulation / 缓存模拟
valgrind --tool=cachegrind ./my_program

# Analyze / 分析
cg_annotate cachegrind.out.<pid>

# With specific cache sizes / 指定缓存大小
# L1 instruction cache: 32KB, 8-way, 64B line
# L1 data cache: 32KB, 8-way, 64B line
# Last level cache: 8MB, 16-way, 64B line
valgrind --tool=cachegrind \
    --I1=32768,8,64 \
    --D1=32768,8,64 \
    --LL=8388608,16,64 \
    ./my_program
```

### Helgrind (Thread Errors) - 线程错误检测

> Detects synchronization errors: data races, lock ordering violations.
> 检测同步错误：数据竞争、锁顺序违规。

```bash
# Detect threading errors / 检测线程错误
valgrind --tool=helgrind ./my_program

# DRD (alternative, faster) / DRD（替代工具，更快）
valgrind --tool=drd ./my_program
```

### Massif (Heap Profiling) - 堆内存分析

> Tracks heap memory usage over time.
> 追踪堆内存使用情况。

```bash
# Heap profiling / 堆内存分析
valgrind --tool=massif ./my_program

# Visualize / 可视化
ms_print massif.out.<pid>

# With time sampling / 按时间采样
valgrind --tool=massif --time-unit=ms ./my_program
```

---

## 7. Other Useful Tools / 其他实用工具

### gdb (Debugging) - 调试器

```bash
# Compile with debug info / 编译时包含调试信息
g++ -g my_code.cpp -o my_program

# Run in gdb / 在 gdb 中运行
gdb ./my_program

# Useful commands / 常用命令:
# (gdb) break main        # Set breakpoint / 设置断点
# (gdb) run               # Start program / 启动程序
# (gdb) next              # Step over / 单步跳过
# (gdb) step              # Step into / 单步进入
# (gdb) print variable    # Print variable / 打印变量
# (gdb) backtrace         # Show call stack / 显示调用栈
# (gdb) info threads      # Show threads / 显示线程
# (gdb) thread <id>       # Switch thread / 切换线程
```

### ltrace / strace - 系统调用追踪

```bash
# Library call tracing / 追踪库函数调用
ltrace ./my_program

# System call tracing / 追踪系统调用
strace ./my_program

# With timing information / 带时间信息
strace -T ./my_program

# Count syscalls / 统计系统调用
strace -c ./my_program

# Filter specific syscalls / 过滤特定系统调用
strace -e trace=open,read,write ./my_program
```

### pmap (Memory Map) - 内存映射

```bash
# Show memory layout / 显示内存布局
pmap -x <pid>

# Detailed output / 详细输出
pmap -XX <pid>
```

### /proc filesystem - /proc 文件系统

```bash
# CPU info / CPU 信息
cat /proc/cpuinfo

# Memory info / 内存信息
cat /proc/meminfo

# Process status / 进程状态
cat /proc/<pid>/status

# Process maps / 进程内存映射
cat /proc/<pid>/maps

# Limits / 进程限制
cat /proc/<pid>/limits
```

### gprof (GNU Profiler) - GNU 性能分析器

```bash
# Compile with profiling / 编译时启用性能分析
g++ -pg my_code.cpp -o my_program

# Run (creates gmon.out) / 运行（生成 gmon.out）
./my_program

# Analyze / 分析
gprof ./my_program gmon.out > analysis.txt
```

### Compiler Optimizations / 编译器优化报告

```bash
# Check optimization reports / 查看优化报告
g++ -O2 -fopt-info my_code.cpp
g++ -O2 -fopt-info-optimized my_code.cpp

# Profile-guided optimization (PGO) / 基于配置文件的优化
g++ -fprofile-generate -O2 my_code.cpp -o my_program
./my_program                    # Generates profile data / 生成配置数据
g++ -fprofile-use -O2 my_code.cpp -o my_program_optimized
```

---

## 8. Benchmarking / 基准测试

### Google Benchmark - 谷歌基准测试框架

```cpp
#include <benchmark/benchmark.h>

// Simple benchmark / 简单基准测试
static void BM_StringCreation(benchmark::State& state) {
    for (auto _ : state) {
        std::string empty_string;
    }
}
BENCHMARK(BM_StringCreation);

// Benchmark with arguments / 带参数的基准测试
static void BM_VectorPushBack(benchmark::State& state) {
    for (auto _ : state) {
        std::vector<int> v;
        for (int i = 0; i < state.range(0); i++) {
            v.push_back(i);
        }
    }
}
BENCHMARK(BM_VectorPushBack)->Range(8, 1 << 18);

BENCHMARK_MAIN();
```

```bash
# Compile / 编译 (replace <benchmark_include> with actual path, e.g. /usr/include)
g++ -O2 -isystem <benchmark_include> my_bench.cpp -lbenchmark -lpthread -o my_bench

# Run / 运行
./my_bench

# Filter tests / 过滤测试
./my_bench --benchmark_filter="BM_StringCreation"

# Output format / 输出格式
./my_bench --benchmark_format=json
```

### Quick Micro-benchmark / 快速微基准测试

```cpp
#include <chrono>
#include <iostream>
#include <vector>

int main() {
    const int SIZE = 1000000;

    // Start timing / 开始计时
    auto start = std::chrono::high_resolution_clock::now();

    // Code to measure / 要测量的代码
    std::vector<int> v(SIZE);
    for (int i = 0; i < SIZE; i++) {
        v[i] = i * 2;
    }

    // End timing / 结束计时
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

    std::cout << "Time: " << duration.count() << " us" << std::endl;
    std::cout << "Throughput: " << SIZE / (duration.count() / 1e6) / 1e6 << " M ops/sec" << std::endl;

    return 0;
}
```

---

## 9. Performance Tips / 性能优化技巧

### Compiler Flags / 编译器优化选项

```bash
# Optimization levels / 优化级别
-O0    # No optimization (for debugging) / 无优化（用于调试）
-O1    # Basic optimization / 基本优化
-O2    # Standard optimization (recommended) / 标准优化（推荐）
-O3    # Aggressive optimization / 激进优化
-Os    # Size optimization / 体积优化
-Ofast # Fastest (may break standards) / 最快（可能不符合标准）

# Architecture-specific / 架构特定优化
-march=native     # Optimize for current CPU / 针对当前 CPU 优化
-mtune=native     # Tune for current CPU / 调优当前 CPU
-mavx2            # Enable AVX2 instructions / 启用 AVX2 指令集
-msse4.2          # Enable SSE4.2 / 启用 SSE4.2

# Profile-guided optimization / 基于配置文件的优化
-fprofile-generate  # First pass / 第一遍
-fprofile-use       # Second pass / 第二遍

# Link-time optimization / 链接时优化
-flto
```

### Common Pitfalls / 常见陷阱

```cpp
// BAD: Unnecessary copies / 错误：不必要的拷贝
void process(std::vector<int> data);  // Copies entire vector / 拷贝整个 vector

// GOOD: Pass by reference / 正确：引用传递
void process(const std::vector<int>& data);

// GOOD: Move semantics / 正确：移动语义
void process(std::vector<int>&& data);

// BAD: Cache misses in nested loops / 错误：嵌套循环中的缓存未命中
for (int i = 0; i < N; i++)
    for (int j = 0; j < M; j++)
        sum += matrix[j][i];  // Column-major access (bad for C++) / 列优先访问（对 C++ 不友好）

// GOOD: Row-major access / 正确：行优先访问
for (int i = 0; i < N; i++)
    for (int j = 0; j < M; j++)
        sum += matrix[i][j];  // Row-major access (good for C++) / 行优先访问（对 C++ 友好）

// BAD: Branch prediction failure / 错误：分支预测失败
for (int i = 0; i < SIZE; i++) {
    if (data[i] > threshold)  // Unpredictable branch / 不可预测的分支
        sum += data[i];
}

// GOOD: Branchless / 正确：无分支写法
for (int i = 0; i < SIZE; i++) {
    sum += (data[i] > threshold) ? data[i] : 0;  // Compiler can optimize / 编译器可以优化
}
```

### Checklist / 检查清单

```markdown
- [ ] Compile with `-O2` or `-O3` (使用 -O2 或 -O3 编译)
- [ ] Use `-march=native` for target-specific optimizations (使用 -march=native)
- [ ] Profile before optimizing (优化前先分析)
- [ ] Check for cache misses with `perf stat` (用 perf stat 检查缓存未命中)
- [ ] Use `valgrind` for memory issues (用 valgrind 检查内存问题)
- [ ] Consider data structure layout (AoS vs SoA) (考虑数据结构布局)
- [ ] Minimize branch mispredictions (最小化分支预测失败)
- [ ] Use move semantics for large objects (对大对象使用移动语义)
- [ ] Avoid unnecessary allocations in hot paths (避免热路径中的不必要分配)
- [ ] Use reserve() for vectors when size is known (已知大小时使用 reserve())
```

---

## 10. Workflow Example / 工作流程示例

```bash
# Step 1: Quick check / 第一步：快速检查
time ./my_program

# Step 2: Find hotspots / 第二步：查找热点
perf stat ./my_program
perf record -g ./my_program
perf report

# Step 3: Check for memory issues / 第三步：检查内存问题
valgrind --leak-check=full ./my_program

# Step 4: Check for threading issues / 第四步：检查线程问题
g++ -fsanitize=thread -g my_code.cpp -o my_program
./my_program

# Step 5: Deep analysis / 第五步：深度分析
vtune -collect hotspots ./my_program

# Step 6: Fix issues and repeat / 第六步：修复问题并重复
```

---

## Example Outputs / 示例输出

> Real-world output examples for each tool, so you know what to expect.
> 每个工具的真实输出示例，让你知道会看到什么。

### time Output / time 输出示例

```bash
$ time ./matrix_multiply

real    0m2.345s      # 总耗时 2.345 秒
user    0m2.301s      # CPU 用户态耗时 2.301 秒
sys     0m0.028s      # CPU 内核态耗时 0.028 秒

# Analysis / 分析:
# user ≈ real, sys 很小 → CPU 密集型程序，性能良好
# 如果 user << real → 说明程序在等 I/O 或锁
# 如果 sys 很大 → 系统调用过多（如频繁 read/write）
```

```bash
$ /usr/bin/time -v ./matrix_multiply
    Command being timed: "./matrix_multiply"
    User time (seconds): 2.30        # 用户态时间
    System time (seconds): 0.02      # 内核态时间
    Percent of CPU this job got: 98% # CPU 利用率
    Elapsed (wall clock) time: 2.35  # 实际耗时
    Average shared text size (kbytes): 0
    Average unshared data size (kbytes): 0
    Average stack size (kbytes): 0
    Average total size (kbytes): 0
    Maximum resident set size (kbytes): 131072  # 峰值内存 128MB
    Average resident set size (kbytes): 0
    Major (requiring I/O) page faults: 0       # 主缺页（磁盘 I/O）
    Minor (reclaiming a frame) page faults: 32768  # 次缺页（内存回收）
    Voluntary context switches: 100            # 自愿上下文切换
    Involuntary context switches: 50           # 非自愿上下文切换
    Swaps: 0
    File system inputs: 0
    File system outputs: 0
    Socket messages sent: 0
    Socket messages received: 0
    Signals delivered: 0
    Page size (bytes): 4096
    Exit status: 0
```

### perf stat Output / perf stat 输出示例

```bash
$ perf stat ./matrix_multiply

 Performance counter stats for './matrix_multiply':

       2,345.67 msec  task-clock                #    0.989 CPUs utilized
             123      context-switches          #   52.438 /sec
              12      cpu-migrations            #    5.116 /sec
           8,192      page-faults               #    3.493 K/sec
   7,890,123,456      cycles                    #    3.364 GHz
  12,345,678,901      instructions              #    1.56  insn per cycle  ✅ IPC > 1
   1,234,567,890      branches                  #  526.248 M/sec
      12,345,678      branch-misses             #    1.00% of all branches  ✅ < 2%
     234,567,890      cache-references          #  100.003 M/sec
      12,345,678      cache-misses              #    5.26% of all cache references  ⚠️ 偏高

    2.371234567 seconds time elapsed
    2.301234567 seconds user
    0.068000000 seconds sys

# Summary / 总结:
# IPC = 1.56 → 每个周期执行 1.56 条指令，性能良好
# branch-misses = 1.00% → 分支预测很好
# cache-misses = 5.26% → 缓存未命中率偏高，需要优化数据访问模式
```

```bash
$ perf stat -d ./matrix_multiply    # 更详细的硬件计数器

 Performance counter stats for './matrix_multiply':

       2,345.67 msec  task-clock
    7,890,123,456      cycles
   12,345,678,901      instructions              #    1.56  insn per cycle
       1,234,567,890      branches
      12,345,678      branch-misses             #    1.00% of all branches

       234,567,890      L1-dcache-loads           #  100.003 M/sec
        12,345,678      L1-dcache-load-misses    #    5.26% of all L1-dcache hits  ⚠️
         1,234,567      LLC-loads                 #  526.248 K/sec
           123,456      LLC-load-misses           #   10.00% of all LLC hits  ⚠️

# Analysis / 分析:
# L1 cache miss = 5.26% → L1 缓存未命中率偏高
# LLC (Last Level Cache) miss = 10% → 最后一级缓存未命中率高
# 建议: 优化数据局部性，使用更紧凑的数据结构
```

### perf report Output / perf report 输出示例

```
$ perf report --stdio

# Overhead  Command       Shared Object      Symbol
# ........  ............  ..................  ..........................
    45.23%  matrix_multiply  matrix_multiply  [.] multiply_blocks
    23.11%  matrix_multiply  matrix_multiply  [.] transpose_matrix
    12.45%  matrix_multiply  libc.so.6         [.] __memcpy_avx2
     8.67%  matrix_multiply  matrix_multiply  [.] initialize_matrix
     5.34%  matrix_multiply  libc.so.6         [.] __memset_avx2
     3.20%  matrix_multiply  matrix_multiply  [.] main
     2.00%  matrix_multiply  [kernel]          [k] native_write_msr

# Analysis / 分析:
# multiply_blocks 占 45% → 这是热点函数
# transpose_matrix 占 23% → 矩阵转置也是瓶颈
# memcpy/memset 占 20% → 内存操作开销大
# 优化方向: 优化 multiply_blocks 算法，减少 transpose 开销
```

### Valgrind Memcheck Output / Valgrind 内存检查输出

```bash
$ valgrind --leak-check=full --show-leak-kinds=all ./my_program

==12345== Memcheck, a memory error detector
==12345== HEAP SUMMARY:
==12345==     in use at exit: 1,024 bytes in 4 blocks  # 退出时仍有 1024 字节未释放
==12345==   total heap usage: 150 allocs, 146 frees, 89,600 bytes allocated
==12345==
==12345== 128 bytes in 1 blocks are definitely lost in loss record 1 of 4  # 确定泄漏
==12345==    at 0x4C2FB0F: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==12345==    by 0x1086DB: create_buffer (buffer.c:15)    # 泄漏位置
==12345==    by 0x1087AB: main (main.c:10)
==12345==
==12345== 256 bytes in 1 blocks are definitely lost in loss record 2 of 4
==12345==    at 0x4C2FB0F: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==12345==    by 0x108812: load_data (data.c:42)
==12345==    by 0x1087C0: main (main.c:15)
==12345==
==12345== 640 bytes in 1 blocks are still reachable in loss record 3 of 4  # 仍可访问但未释放
==12345==    at 0x4C2FB0F: malloc (in /usr/lib/valgrind/vgpreload_memcheck-amd64-linux.so)
==12345==    by 0x109213: init_pool (pool.c:28)
==12345==    by 0x1087D5: main (main.c:20)
==12345==
==12345== LEAK SUMMARY:
==12345==    definitely lost: 384 bytes in 2 blocks   # 确定泄漏（必须修复）
==12345==    indirectly lost: 0 bytes in 0 blocks
==12345==      possibly lost: 0 bytes in 0 blocks     # 可能泄漏
==12345==    still reachable: 640 bytes in 2 blocks   # 仍可访问（可忽略）
==12345==         suppressed: 0 bytes in 0 blocks
==12345==
==12345== For lists of detected and suppressed errors, rerun with: -s
==12345== ERROR SUMMARY: 2 errors from 2 contexts (suppressed: 0 from 0)

# Analysis / 分析:
# definitely lost: 384 bytes → 必须修复的内存泄漏
# still reachable: 640 bytes → 程序退出时未释放，通常可忽略
# 查看 buffer.c:15 和 data.c:42 找到泄漏点并修复
```

### Valgrind Cachegrind Output / Valgrind 缓存模拟输出

```bash
$ valgrind --tool=cachegrind ./matrix_multiply
$ cg_annotate cachegrind.out.12345

I1 cache:         32768 B, 64 B, 64 sets, 8-way  # L1 指令缓存
D1 cache:         32768 B, 64 B, 64 sets, 8-way  # L1 数据缓存
LL cache:        8388608 B, 64 B, 131072 sets, 8-way  # 最后一级缓存

           I1       D1       LL
Ir     234,567,890
I1mr           12,345         # L1 指令缓存未命中
ILmr              123         # LL 指令缓存未命中

Dr   1,234,567,890
D1mr      12,345,678          # L1 数据缓存未命中  ⚠️
DLmr         123,456          # LL 数据缓存未命中  ⚠️

 DW     234,567,890

# 按函数分析 / Per-function analysis:
# (文件:行号)  函数名
#            Ir         Dr         Dw       I1mr      D1mr      ILmr      DLmr
#  100.00% 234,567,890 1,234,567,890 234,567,890  12,345  12,345,678     123    123,456  TOTAL
#   45.23% 106,123,456   558,456,789  106,123,456   5,678   6,789,012      56     56,789  multiply_blocks
#   23.11%  54,234,567   285,345,678   54,234,567   2,345   3,456,789      23     28,901  transpose_matrix
#   12.45%  29,234,567   153,678,901   29,234,567   1,567   1,234,567      12     18,012  initialize_matrix

# Analysis / 分析:
# D1mr = 12,345,678 → L1 数据缓存未命中 1200 万次
# multiply_blocks 和 transpose_matrix 是主要瓶颈
# 原因: 矩阵转置导致列优先访问，造成大量缓存未命中
```

### ASan Output / ASan 内存错误输出

```bash
$ ./my_program_asan

=================================================================
==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x602000000018 at pc 0x0000004a1234 bp 0x7ffd45678900 sp 0x7ffd456788f8
WRITE of size 4 at 0x602000000018 thread T0
    #0 0x4a1233 in process_data /home/user/code/main.cpp:25   # 错误位置
    #1 0x4a1456 in main /home/user/code/main.cpp:40
    #2 0x7f1234567830 in __libc_start_main
    #3 0x4011a9 in _start

0x602000000018 is located 0 bytes to the right of 24-byte region [0x602000000000,0x602000000018)
allocated by thread T0 here:
    #0 0x7f12345671a7 in malloc
    #1 0x4a1567 in main /home/user/code/main.cpp:35

SUMMARY: AddressSanitizer: heap-buffer-overflow /home/user/code/main.cpp:25

# Analysis / 分析:
# 堆缓冲区溢出: 在 main.cpp:25 写入了超出分配区域的数据
# 分配了 24 字节 (6 个 int)，但写入了第 7 个元素
# 修复: 检查数组边界，确保不越界访问
```

### TSan Output / TSan 线程错误输出

```bash
$ ./my_program_tsan

==================
WARNING: ThreadSanitizer: data race (pid=12345)
  Read of size 4 at 0x7f1234567890 by thread T1:     # 线程 T1 读取
    #0 process_data /home/user/code/worker.cpp:42
    #1 worker_thread /home/user/code/worker.cpp:60

  Previous write of size 4 at 0x7f1234567890 by main thread (mutexes: write M0):  # 主线程写入
    #0 update_value /home/user/code/worker.cpp:30
    #1 main /home/user/code/main.cpp:55

  Location is stack block of size 40 at 0x7ffd12345678 allocated by main thread:
    #0 malloc
    #1 main /home/user/code/main.cpp:20

  Mutex M0 (0x7f1234567800) created at:
    #0 pthread_mutex_init
    #1 initialize /home/user/code/worker.cpp:15

SUMMARY: ThreadSanitizer: data race /home/user/code/worker.cpp:42 in process_data

# Analysis / 分析:
# 数据竞争: 主线程在写入 data[0] 的同时，T1 线程在读取
# 位置: worker.cpp:42 和 worker.cpp:30
# 修复: 使用 mutex 保护共享数据，或使用 atomic
```

### UBSan Output / UBSan 未定义行为输出

```bash
$ ./my_program_ubsan

main.cpp:25:20: runtime error: signed integer overflow
    0x7f1234567890 cannot be represented in type 'int'
    #0 0x4a1233 in compute /home/user/code/main.cpp:25
    #1 0x4a1456 in main /home/user/code/main.cpp:40

main.cpp:30:15: runtime error: null pointer passed as argument 1
    #0 0x7f1234567800 in memset
    #1 0x4a1567 in clear_buffer /home/user/code/main.cpp:30

# Analysis / 分析:
# 有符号整数溢出: int 最大值 + 1
# 空指针解引用: 传递了 nullptr 给 memset
# 修复: 使用 unsigned 类型，检查指针是否为 null
```

### strace Output / strace 系统调用输出

```bash
$ strace -c ./my_program

% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- --------
 45.23    0.123456          12     10000           write
 23.11    0.063456           6     10000           read
 12.45    0.034567           3     10000           close
  8.67    0.023456           2     10000           open
  5.34    0.014567           1     10000           mmap
  3.20    0.008789           1      5000           mprotect
  2.00    0.005432           1      5000           munmap
  0.00    0.000000           0        10           brk
------ ----------- ----------- --------- --------- --------
100.00    0.273717                 50010           total

# Analysis / 分析:
# write 占 45% → 程序大量写操作
# read 占 23% → 读操作也较多
# 总共 50010 次系统调用 → 可能需要缓冲 I/O
# 优化: 使用 buffered I/O 减少系统调用次数
```

### pmap Output / pmap 内存映射输出

```bash
$ pmap -x 12345

Address           Kbytes     RSS   Dirty Mode  Mapping
0000000000400000     512     480       0 r-x--  my_program      # 代码段
0000000000680000      32      32      32 r----  my_program      # 只读数据
0000000000688000      16      16      16 rw---  my_program      # 可写数据
0000000000690000      64      48      48 rw---  [heap]          # 堆内存
00007f1234000000    1024     980       0 r-x--  libc-2.31.so    # libc 代码
00007f1234200000      16      16      16 r----  libc-2.31.so    # libc 只读数据
00007f1234204000       8       8       8 rw---  libc-2.31.so    # libc 可写数据
00007f1234206000      20      16      16 rw---  [anon]          # 匿名映射
00007ffc12340000     132      20      20 rw---  [stack]         # 栈内存
00007ffc12350000      16       0       0 r-x--  [vdso]          # 内核虚拟动态共享对象
                      ----  ------  ------
total kB          1,840   1,616     152

# Analysis / 分析:
# 堆 (heap): 64KB, 48KB RSS → 堆内存使用情况
# 栈 (stack): 132KB, 20KB RSS → 栈内存使用情况
# libc: 1068KB → 库文件占用
# 总 RSS = 1616KB → 实际物理内存使用
```

### massif Output / massif 堆内存分析输出

```bash
$ valgrind --tool=massif ./my_program
$ ms_print massif.out.12345

    KB
70400^                                                                    $
     |                                                                   @$
64000^                                                                 @@@$
     |                                                                @@@@@$
57600^                                                               @@@@@@@$
     |                                                             @@@@@@@@@$
51200^                                                           @@@@@@@@@@@@
     |                                                         @@@@@@@@@@@@@$
44800^                                                       @@@@@@@@@@@@@@@@
     |                                                     @@@@@@@@@@@@@@@@@@
38400^                                                   @@@@@@@@@@@@@@@@@@@@
     |                                                 @@@@@@@@@@@@@@@@@@@@@@
32000^                                               @@@@@@@@@@@@@@@@@@@@@@@@
     |                                             @@@@@@@@@@@@@@@@@@@@@@@@@@
25600^                                           @@@@@@@@@@@@@@@@@@@@@@@@@@@@
     |                                         @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
19200^                                       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
     |                                     @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
12800^                                   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@$
     |                                 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
 6400^                               @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@$
     |                             @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
     0^@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
      0    250000  500000  750000  1000000 1250000 1500000 1750000 2000000
                                time (ms)

  n        time(i)         total(B)         useful-heap(B)       extra-heap(B)         stacks(B)
  0            0                64                   32                   32                    0
  1       500000            65536                65504                   32                    0
  2      1000000           131072               131040                   32                    0
  3      1500000           262144               262112                   32                    0
  4      2000000           524288               524256                   32                    0
  5      2000000           524288               524256                   32                    0

# Analysis / 分析:
# 内存随时间线性增长 → 程序可能存在内存泄漏
# 每次分配约 64KB → 可能是循环中不断分配内存
# 优化: 检查循环中的 malloc/new，确保正确释放
```

### Google Benchmark Output / Google Benchmark 输出示例

```bash
$ ./my_bench

Running ./my_bench
Run on (8 X 3400 MHz CPU s)
Load Average: 0.52, 0.48, 0.45
------------------------------------------------------------------------------------------------
Benchmark                                  Time             CPU   Iterations
------------------------------------------------------------------------------------------------
BM_StringCreation                       12.3 ns         12.2 ns     56789012   # 字符串创建性能
BM_VectorPushBack/8                     45.6 ns         45.5 ns     21876543   # vector push_back
BM_VectorPushBack/64                   312.4 ns        312.0 ns      3456789
BM_VectorPushBack/512                 2890.1 ns       2889.0 ns       456789
BM_VectorPushBack/4096               23456.7 ns      23450.0 ns        56789
BM_VectorPushBack/32768             198765.4 ns     198700.0 ns         6789
BM_SortRandom/1024                     8901.2 ns       8900.0 ns      123456   # 排序性能
BM_SortRandom/8192                    78901.2 ns      78900.0 ns       12345
BM_SortRandom/65536                  678901.2 ns     678900.0 ns        1234

# Analysis / 分析:
# Vector push_back 从 8 到 4096 元素性能很好
# 超过 4096 后性能急剧下降 → 触发了重新分配
# 排序 65536 元素需要 678μs → 可以考虑并行排序
```

### perf diff Output / perf diff 比较输出

```bash
$ perf diff perf1.txt perf2.txt

# Baseline       Delta  Shared Object      Symbol
# ...........    .....  ..................  ..........................
    45.23%    -12.34%  my_program         [.] multiply_blocks    # 优化后减少 12%
    23.11%     -8.56%  my_program         [.] transpose_matrix  # 优化后减少 8%
    12.45%     +5.67%  libc.so.6          [.] __memcpy_avx2     # memcpy 增加
     8.67%     -2.11%  my_program         [.] initialize_matrix # 初始化减少
     5.34%     +3.45%  libc.so.6          [.] __memset_avx2     # memset 增加
     3.20%    +13.89%  my_program         [.] main              # main 比例上升

# Analysis / 分析:
# multiply_blocks 减少 12% → 优化有效！
# transpose_matrix 减少 8% → 优化有效！
# memcpy/memset 增加 → 可能是因为优化后其他部分变快了
# 整体: v2 版本比 v1 版本快约 20%
```

### VTune Summary Output / VTune 摘要输出

```bash
$ vtune -report summary -result-dir ./rslt

VTune Profiler analysis results.
Enqueue this project for source analysis: vtune -cl-source-dir /home/user/project -result-dir ./rslt

If you see incomplete call stack data, try the -search-dir option to rebuild the symbol table.

ElapRealTime  CPU Time  Instruction Count  Retired Cycles  Cache Misses  Branch Misses  Total Loops  Total Functions
-----------  --------  -----------------  ---------------  ------------  -------------  -----------  ---------------
   2.345s     2.301s       12.34G               7.89G          12.3M         12.3M           45             128

Hotspots: 2 functions (68% of total time)
  1. multiply_blocks     - 45.23% (1.041s)
  2. transpose_matrix    - 23.11% (0.532s)

# Analysis / 分析:
# 总 CPU 时间 2.3s，两个热点函数占 68%
# 优化这两个函数可以显著提升性能
```

### Helgrind Output / Helgrind 线程错误输出

```bash
$ valgrind --tool=helgrind ./my_program

==12345== Helgrind, a thread error detector
==12345== Possible data race during read of size 4 at 0x7f1234567890
==12345==    at 0x4A1234: process_data (worker.cpp:42)
==12345==  Address 0x7f1234567890 is at offset 0 from 0x7f1234567880. Allocation context:
==12345==    at 0x4C2FB0F: malloc (in /usr/lib/valgrind/vgpreload_helgrind-amd64-linux.so)
==12345==    by 0x4A1567: main (main.cpp:20)
==12345==  Other location 'defined' by:
==12345==    at 0x4A1567: update_value (worker.cpp:30)
==12345==    by 0x4A1678: main (main.cpp:55)
==12345==
==12345== Conflicting load and store (size 4):
==12345==    at 0x4A1234: process_data (worker.cpp:42)
==12345==    by 0x4A1456: worker_thread (worker.cpp:60)
==12345==    by 0x4C3456: mythread (hg_intercepts.c:306)
==12345==  Other location 'defined' by:
==12345==    at 0x4A1567: update_value (worker.cpp:30)
==12345==    by 0x4A1678: main (main.cpp:55)
==12345==
==12345==  Lock acquired at:
==12345==    at 0x4C3456: pthread_mutex_init (hg_intercepts.c:869)
==12345==    by 0x4A1789: initialize (worker.cpp:15)

# Analysis / 分析:
# 数据竞争: worker.cpp:42 读取和 worker.cpp:30 写入冲突
# 没有使用 mutex 保护共享数据
# 修复: 在访问共享数据前加锁
```

---

## References / 参考资料

- [perf Wiki](https://perf.wiki.kernel.org/index.php/Main_Page) - Linux perf 官方文档
- [Intel VTune Documentation](https://software.intel.com/content/www/us/en/develop/documentation/vtune-help/top.html) - Intel VTune 官方文档
- [Valgrind Documentation](https://valgrind.org/docs/manual/manual.html) - Valgrind 官方文档
- [Google Benchmark](https://github.com/google/benchmark) - 谷歌基准测试框架
- [Flame Graphs](http://www.brendangregg.com/flamegraphs.html) - 火焰图详解
- [CppCon Performance Talks](https://www.youtube.com/cppcon) - CppCon 性能相关演讲
