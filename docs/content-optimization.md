# Blog content optimization / 博客内容优化说明

> 更新：2026-09-24
> 范围：当前 Jekyll 博客仓库的全部已发布文章

## 1. 当前基线

| 指标 | 数量 |
| --- | ---: |
| 已发布文章总数 | 347 |
| 原有历史文章 | 331 |
| 本次新增的重组文章 | 16 |
| 重组文章引用的历史来源 | 167 |
| 主题数 | 11 |
| 当前标签数 | 以构建后的 `/tag/` 页面为准 |

原有 331 篇 Markdown 文件没有被批量重写、删除、重命名或移动。它们的历史 URL、发布日期和正文保持不变；本次新增内容作为新的入口层发布。

### 主题覆盖

| 主题 | 原有文章 | 新增精选/深挖文章 |
| --- | ---: | ---: |
| AI & LLM | 17 | 3 |
| C & C++ | 48 | 2 |
| Systems | 51 | 2 |
| DevOps & Infrastructure | 13 | 1 |
| Developer Tools | 69 | 2 |
| Programming | 42 | 0 |
| Computer Science | 50 | 2 |
| Security & Networking | 21 | 1 |
| Database | 6 | 1 |
| Photography | 5 | 1 |
| Personal | 9 | 1 |

Programming 类文章目前通过 C++、系统、工具和 AI 入口交叉覆盖；暂不另建一篇泛化的 Programming 总览，避免与已有主题文章重复。

## 2. 已完成的优化

### 2.1 新增精选重组层

新增 `/curated/` 页面，按主题展示新的阅读入口。每篇重组文章都包含：

- 面向当前读者的问题、概念关系和实践路径；
- `curated: true` 与 `content_origin: curated` 元数据；
- `source_posts` 来源文件列表；
- 自动生成的“资料来源”链接；
- 对版本、命令和安全边界的明确提醒。

首批重组文章覆盖：

1. C++ 后端工程、构建、调试与性能；
2. Linux/Windows 系统化故障排查；
3. 数据结构与算法复习路线；
4. 设计模式实践指南；
5. AI Agent 工程化学习地图；
6. LLM 推理服务上线清单；
7. Git、GitLab、Docker 与交付运维；
8. 网络与安全实验室学习指南；
9. VS Code、CMake 与开发者工具工作流；
10. 数据库与工业协议笔记；
11. 摄影学习路径；
12. 旧文章不改的内容维护策略；
13. 现代 CMake 工程化：Targets、依赖发现、安装与 CPack；
14. Linux ELF 动态链接与 C++ 部署排障；
15. 现代 C++ 并发与生命周期；
16. Agent 沙箱与工具权限安全 Runbook。

### 2.2 保留原文并增加可追溯性

- 新文章通过仓库路径引用原文，避免依赖易变的手写 URL；
- 文章底部显示来源标题、日期和链接；
- 原始文章继续出现在 Archive、Topics、Tags 和 Search 中；
- 新文章不声称替代旧文章，也不抹去历史语境。

### 2.3 工程质量改进

- 新增 `scripts/validate-curation.rb`，检查来源路径、主题、摘要和重组标记；
- 更新 `scripts/smoke-test.rb`，不再硬编码文章总数；
- 修复标签页面对 `site.tags` 直接排序导致的 Jekyll `Array with Array` 构建错误，改为直接遍历标签映射；
- 修复标签生成器对数字标签和带符号标签的处理，并显式登记新标签 slug；
- 统一 Liquid 与 Python 的标签 slug 解析规则，修复 `C++`、`CI/CD`、下划线标签等历史链接不一致；
- 统一 `/tag/` 的页面归属，避免 `page/2tags.html` 与生成的 `tag/index.md` 产生目标冲突；
- 搜索元数据增加 `curated` 和 `content_origin` 字段，并提供精选筛选；
- GitHub Pages 构建后自动执行来源校验和 smoke test。

## 3. 对原文的处理建议

### 推荐：原文保留，按价值渐进重组

这是当前采用的处理方式：

1. **高价值技术簇**：新增主题综述或实践指南，原文作为证据和历史细节；
2. **高风险或过时内容**：在新文章中加版本、授权和安全提示，不直接改写旧文；
3. **短笔记**：先通过主题地图聚合，达到独立阅读价值后再写成新文章；
4. **个人记录**：保留原貌，只改善主题、标签和发现入口；
5. **重复或低信息文章**：暂不删除，先观察搜索和读者反馈。

### 暂不建议的事情

- 不要批量替换旧文中的命令、链接或代码；
- 不要为了统一分类而移动旧文件，这会改变 URL 和外部引用；
- 不要把 AI 辅助生成内容直接标成“已验证”；
- 不要删除历史文章来“清理首页”，应通过精选层和归档页解决信息密度问题。

## 4. 已知待处理项

以下是审计发现，不是本次对原文的强制修改：

| 项目 | 现状 | 建议 |
| --- | --- | --- |
| 分类可疑项 | 27 篇标题与当前一级主题不完全一致 | 先通过新文章和多标签改善发现入口，逐篇确认后再改 frontmatter |
| `display_title` | 约 240 篇历史文章没有单独设置 | 现有模板会回退到 `title`，暂不批量添加 |
| 标签变体 | `JavaScript/javascript`、`Performance/performance` 等 | 后续在 `_data/tag_slugs.yml` 和新内容中统一，旧标签保持兼容 |
| 外部链接/版本 | 旧文章中有历史下载页、版本和外部站点 | 逐簇复核；新文章只引用稳定入口并加复核提示 |
| 构建警告 | 少数旧文章含 `<!--more-->` 与 Liquid 样式文本警告 | 单独开“原文技术修复”变更，避免和内容重组混在一起 |
| `/tag/` 输出 | 已统一由 `page/2tags.html` 提供，生成器不再写重复的 `tag/index.md` | 保持单一 canonical 页面；新增标签后重新运行生成器 |

### 需要优先人工复核的历史簇

以下内容不建议直接复制为生产操作手册；新文章已经加了版本、授权或安全边界提示：

- 多节点 vLLM/Ray/Docker：防火墙、Swap、NFS、`--privileged`、host network、可变镜像和 GPU 利用率；
- GitLab：shell runner、宽权限 sudo、数据库删除/更新、重置账户、清理 jobs 和卸载服务；
- Agent/模型服务：离线部署中的远程 Provider、dummy key、沙箱隔离强度和未经验证的模型/性能数字；
- USB/SSD/文件系统：`rm`、日志清理、`ntfsfix`、`chkdsk /f|/r` 等操作必须先确认设备、备份和授权；
- 逆向/破解课程：保留为授权实验室学习材料，不重新发布绕过验证、修改版权或网络验证的操作步骤。

## 5. 后续工作顺序

1. 先观察 `/curated/` 的阅读路径和搜索点击；
2. 为高价值旧文补充来源关系，而不是直接改正文；
3. 对安全、网络、驱动和数据库文章做人工技术复核；
4. 统一标签 slug 和历史分类，但保留旧 URL；
5. 最后处理构建警告和原文格式问题。

## 6. 本地验证

```bash
python3 scripts/generate_tag_pages.py
ruby scripts/validate-curation.rb
bundle exec jekyll build
ruby scripts/smoke-test.rb
node --check js/search.js
node --check js/pageContent.js
```

提交前建议同时检查：重组文章的来源链接、构建后的 `/curated/` 页面、搜索 JSON 条目数和原文文件差异。
