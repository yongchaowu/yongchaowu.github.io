---
layout: post
title: "数据库与工业协议笔记：从 SQL、嵌入式存储到数据采集"
display_title: "数据库与工业协议笔记：从 SQL、嵌入式存储到数据采集"
summary: "把 SQLite、MySQL、PostgreSQL、PL/SQL、Navicat 和 MTConnect 记录整理成数据存储与协议学习的选择框架。"
lang: zh-CN
date: 2026-09-24 10:30:00
categories:
  - Database
tags:
  - Database
  - SQL
  - SQLite
  - PostgreSQL
  - MySQL
  - MTConnect
curated: true
content_origin: curated
curation_level: reference
version: curated-v1
source_posts:
  - "_posts/2020-07-09-DB-PL-SQL.md"
  - "_posts/2020-07-09-SQLite.md"
  - "_posts/2024-04-23-Tool-Mysql-安装and卸载and运行.md"
  - "_posts/2024-08-09-Tool-Postgresql.md"
  - "_posts/2024-04-23-Tool-Navicat.md"
  - "_posts/2020-07-10-MTCOnnect_ANSI_MTC1_4-2018.md"
---

数据库文章最容易变成安装步骤和零散 SQL 的集合。更好的学习方式，是先根据数据规模、并发、事务、部署边界和协议语义选择模型，再学习具体产品的操作。

> 本文是数据库与工业协议历史笔记的重组。安装命令、默认端口、认证方式和协议版本可能变化，请优先参考当前官方文档。

> **技术交叉核对（2026-09-25）**：SQLite 的显式事务、savepoint 和错误回滚语义已对照 [SQLite Transaction Control Syntax](https://www.sqlite.org/lang_transaction.html)；其他数据库仍需查阅各自版本和引擎文档。

<!--more-->

## 先按工作负载选择

| 场景 | 优先了解 | 关键问题 |
| --- | --- | --- |
| 单机、嵌入式、边缘设备 | SQLite | 文件如何备份、事务和并发如何处理 |
| 通用服务型应用 | MySQL / PostgreSQL | 事务、索引、权限、复制和扩展 |
| Oracle 生态或过程化业务 | PL/SQL | 事务边界、游标、错误处理和迁移 |
| 工业设备数据采集 | MTConnect / 工业协议 | 时间语义、设备身份、断线和重连 |

这些选择不是互斥的。边缘设备可能使用 SQLite 缓存，再通过消息或批量方式同步到 PostgreSQL；工业采集服务也可能把实时流落到时序或关系数据库中。

## SQLite：从文件到可靠备份

[SQLite](#source-note-2) 适合嵌入式和只读/轻量写入场景，但“它是文件”不代表可以随意复制正在写入的数据库。备份时应考虑 WAL、锁、文件权限和一致性快照；恢复后用完整性检查和业务查询验证，而不是只看文件是否存在。

## 服务型数据库：把运维问题写进设计

[MySQL 安装与运行](#source-note-3) 和 [PostgreSQL](#source-note-4) 的历史记录可作为环境搭建入口。真正需要固定的是：字符集、时区、认证、连接池、备份、日志、监控和迁移策略。

[Navicat](#source-note-5) 适合可视化和人工检查，但生产变更不应只依赖图形客户端。保存 SQL、影响行数、执行时长和回滚方式，避免把一次误操作隐藏在鼠标点击里。

## SQL 学习重点

[PL/SQL 笔记](#source-note-1) 可以用来学习过程化逻辑，但建议先掌握基础的关系模型、索引、事务和集合操作，再进入游标、存储过程和批处理。每个过程都应有输入校验、异常处理、幂等策略和可观察日志。

```text
-- 伪代码：先做只读预检，再执行经过审核的写事务
-- 事务边界、DDL、savepoint 和回滚行为因数据库引擎而异
PRECHECK: explain / count / backup / permissions
BEGIN
  EXECUTE_REVIEWED_CHANGE
  VERIFY affected_rows_and_invariants
  ON_SUCCESS: COMMIT
  ON_FAILURE: ROLLBACK
```

## MTConnect：协议之外还有语义

[MTConnect ANSI MTC 1.4 资料](#source-note-6) 适合学习设备、资产、流和数据语义。阅读协议时不要只追踪 XML 字段，还要记录：

- 设备身份和 Agent 的关系；
- 数据项的单位、采样频率和时间范围；
- 连接、缓冲和断线后的行为；
- 错误响应的可诊断信息；
- 原始数据进入业务系统后的质量校验。

## 一个可复用的数据库变更模板

```text
变更目的：
影响表与数据量：
锁表/停机风险：
备份与校验：
灰度步骤：
回滚 SQL：
监控指标：
执行记录：
```

数据库优化的目标不是“让单条 SQL 看起来更复杂”，而是让数据生命周期、访问模式、故障恢复和协议语义都能被团队准确理解。
