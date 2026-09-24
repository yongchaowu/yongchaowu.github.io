# wyclswq.top 全站审查与修改计划

> Review date: 2026-09-25
> Scope: Jekyll 站点壳层、导航、首页/路径页/主题/标签/归档/搜索/文章页/404、响应式显示、键盘与辅助技术、链接和发布验证。
> Method: 产品信息架构审查 + QA 路由/交互审查 + 生成站点静态检查。历史文章保持原 URL、日期和技术正文；必要的渲染安全修复单独登记 blob。

## 1. 当前基线

| 项目 | 基线 |
| --- | ---: |
| 已发布文章 | 350 |
| 历史文章 | 331 |
| 精选/深挖文章 | 19 |
| 主题入口 | 11 |
| 标签 | 243 个名称 / 241 个 canonical slug |
| 公共入口 | `/` `/pageN/` `/start-here/` `/curated/` `/category/` `/topics/*/` `/tag/` `/tag/*/` `/archive/` `/search/` `/about/` `/404.html` |

本次不把历史文章批量重写、删除、重命名或移动。新增内容通过 curated layer、来源关系和 sidecar 元数据进入阅读路径。

## 2. 全站产品审查结论

### 已确认的高优先级问题

| 优先级 | 问题 | 影响 | 处理 |
| --- | --- | --- | --- |
| P1 | 移动端 `.right` 侧栏被 `display:none` 覆盖 | 文章目录、页面目录无法打开 | 恢复 post/page drawer，增加 `aria-controls`、`aria-expanded`、Escape 关闭；topic 关系在正文提供移动端入口 |
| P1 | 搜索索引保留 HTML entity | `std::vector<int>`、`<`、`&` 等精确代码搜索失败 | 构建时解码常见 entity，客户端再次防御性解码；加入 smoke 回归 |
| P1 | dark mode inline code 对比度不足 | 代码标识符几乎不可读 | inline code 改用主题变量，block code 保持独立高亮样式 |
| P1 | 导航和主题控件在移动/无 JS 场景退化 | 菜单可能不可发现、主题无法切换 | 1024px 响应式菜单、JS 状态同步、no-JS 导航回退、移动端主题按钮、Escape 关闭 |
| P1 | Copy code 只在 hover 时显示且无剪贴板 fallback | 键盘/触屏/非 HTTPS 场景不可用 | 始终可见、键盘 focus、非安全上下文使用 selection fallback、状态 aria-label |
| P1 | 文章侧栏组件 CSS 依赖不存在的 `[post]` 选择器 | 来源、测试、系列和相关文章退化 | post layout 输出 `post` 标记，并补齐 v3 主题下的链接样式 |
| P1 | 搜索页面初始就下载大型全文索引 | 移动端首屏成本高 | 首次输入/筛选时 lazy-load，预计算 lowercase searchable fields |
| P2 | 标签索引 243 个标签没有过滤/排序 | 发现特定标签成本高 | 增加客户端过滤和“Most used / Name A–Z”排序，保留 canonical 链接 |
| P2 | Archive 年份链接可能落在折叠列表 | 点击后内容不可见 | 为每个年份增加 `aria-controls`，统一处理 click/hashchange |
| P2 | 首页分页第 2 页以后没有 h1 | 页面大纲和可访问性上下文不足 | 增加“Latest notes · Page N of M”标题 |
| P2 | 文章页 header 多个菜单同时标记 current | 屏幕阅读器语义混乱 | `aria-current="page"` 只保留给精确页面，上下文只使用 active 样式 |
| P2 | 小字号 metadata 过多、muted 色对比度偏低 | 长时间阅读和低视力用户体验差 | muted token 调整，小标签提升到 11px，过滤控件达到 36px 触控高度 |
| P2 | 搜索筛选没有 `note` / `unknown` 选项 | 历史文章和未知证据状态无法选择 | 补齐选项并与索引 vocabulary 同步 |
| P1 | BehaviorTree 历史文章的 list/fence 边界和外部 URL 未安全渲染 | 代码可能进入正文、产生重复 ID/空 anchor 或带空格的 URL | 最小 code-fence/URL 修复，登记新的 `format_fixes.yml` blob；其余历史样例进入 allowlist 警告 |
| P1 | 代码/表格在 390px 文章页撑大布局 | 移动端横向滚动，文章导航触发器可能被推出视口 | code block/table 设定最大宽度与换行/内部滚动策略，移动端重新测量 |
| P1 | Archive/Tag/About 在 1025px 仍是固定宽页面 | 平板出现横向页面滚动 | tablet 媒体规则加入三类页面并统一 92% 宽度 |
| P1 | GitLab root 密码重置历史页缺少安全状态 | 直接 landing 看不到授权、备份和锁回边界 | 增加 `not-tested`、`caution` sidecar 与可见风险提示，不改历史命令正文 |
| P2 | Header theme toggle 的旧高度/对齐规则与新 shell 冲突 | 图标可能偏离 64px header | `#top` 作用域 + flex 居中覆盖，并用 headless 浏览器 probe 验证主题切换 |
| P2 | “On this page”在短文章中显示空卡片 | 侧栏有无意义空白 | TOC 少于两个标题时隐藏整张侧栏卡片 |

### 保留的低优先级/待人工复核项

- 286 篇历史文章没有显式 `lang`；需要按内容抽样建立语言 sidecar，不能未经抽样批量改动。
- 历史 BehaviorTree.CPP Manual Notes 的列表/内联 XML code fence 已做最小格式修复并登记 `format_fixes.yml`；其他历史代码样例仍需抽样，不批量改写。
- 12 篇历史 list/fence 渲染样例已列入 `site-review.py` 的显式 allowlist，只产生可追踪 warning；未新增静默忽略规则。
- 29 篇历史分类可疑项继续通过多标签和 curated 路径改善发现入口。
- 真实桌面浏览器/触屏/屏幕阅读器矩阵仍需人工执行；本轮已用 headless Chrome 完成可自动化的页面与交互 probe，并加入 `scripts/site-review.py` 作为静态门禁。

## 3. 已执行的内容修复

### 3.1 新增 curated guides

1. `2026-09-25-curated-behaviortree-cpp-engineering.md`
   - 执行生命周期、RUNNING/halt、异步唤醒、BT/FSM 混合边界；
   - 仿真更新顺序、线程/Blackboard 契约、性能测量和测试路径。
2. `2026-09-25-curated-ray-vllm-offline-runbook.md`
   - wheelhouse/hash、镜像 digest、GPU 可见性、Ray head/worker、并行策略、认证、私网、健康检查和回滚。
3. `2026-09-25-curated-gpu-docker-deployment.md`
   - GPU/驱动/CUDA/容器/模型兼容性矩阵、只读挂载、远程代码、功能验收和性能记录模板。

三篇新文章均保留历史来源路径、来源引用和 `review-required` / `version-sensitive` / `caution` 状态，并加入对应 topic、reading path 和 editorial sidecar。

### 3.2 信息架构

- `/start-here/` 增加六个高层 domain 入口：
  - C++ Systems
  - BehaviorTree / Simulation
  - AI Infrastructure
  - GPU / CUDA
  - Linux / DevOps
  - Archive
- canonical 11-topic 路由保持不变，六个 domain 是阅读层，不是破坏性分类迁移。
- 首页、About、footer 和 SEO 描述统一为 `Systems · C++ · AI Infrastructure` / `C++ systems` 方向。

## 4. 已执行的壳层与交互修复

- Header：将 legacy `header` 规则限定到 `#top`，避免 Search/Archive/Tag/About 等页面标题被错误压成 52px；修复高特异性黑色 active/hover 背景。1024px 响应式菜单、动态 `aria-label`/`aria-expanded`、Escape 关闭、resize 同步、主题按钮 aria 状态。
- Progressive enhancement：head 标记 `js/no-js`，无 JS 时导航仍可读。
- Search：lazy index、entity 精确搜索、预计算字段、note/unknown 筛选、无障碍输入属性、更多结果按钮语义；补上初始 query callback 回归测试，并修正结果 metadata/title 的网格布局。
- Tag index：过滤、排序、空状态。
- Archive：年份折叠按钮与 hash 同步。
- Base path：search/tags 的 `data-base-url` 统一输出规范化路径，smoke test 比较时忽略末尾 `/`。
- Article/page drawer：目录可访问控制、焦点返回、Escape 关闭。
- Copy code：可见按钮、键盘 focus、selection fallback、成功/失败状态。
- CSS：inline code dark-mode 对比度、muted 色、字号、触控高度、post component 样式、domain cards；legacy header 规则限定到 `#top`。
- Responsive/content safety：代码/表格内部滚动与换行、tablet 页面宽度、GitLab root 重置风险提示、短文空 TOC 隐藏、search 初始 filter active 状态。
- 历史渲染安全：修复 BehaviorTree.CPP Manual Notes 中列表/内联 XML code fence，已登记 `format_fixes.yml`；补上 Related Articles 的 `similar_posts` anchor，修正 curated 列表语义。
- QA：新增 `scripts/site-review.py` 和无依赖的 `scripts/search-interaction-test.js`，并在 Pages workflow 中执行。

### 4.1 本轮已执行的 headless Chrome 验证

- 1440px：首页、Search、Start here、Archive、文章页和 Tag index 截图检查；修复了全局 `header` 规则压扁页面标题的问题。
- 390px：首页、Search、文章页、Tag index 截图检查；菜单默认关闭，文章 anchor 保持在视口内，BehaviorTree 长代码/表格不再产生文档级横向溢出。
- 交互 probe：搜索初始 `?q=CMake` 渲染结果；主题切换 `light → dark`；移动菜单打开/Escape；文章目录打开/Escape；Archive 年份折叠；均通过。
- 390px 代码页测量：`documentElement.scrollWidth <= innerWidth`；仍建议在真实触屏设备上复核滚动惯性、软键盘和屏幕阅读器。

## 5. 全站点击/显示测试矩阵

每个核心路由都应按以下顺序检查：页面加载 → 主导航 → footer → 页面内 CTA → 主题切换 → 搜索/筛选 → 文章工具 → 返回/滚动。

| 路由/组件 | 必测项目 | 验收标准 |
| --- | --- | --- |
| `/` | Start、Curated、路径卡、topic 卡、分页、Older/Newer | 所有链接可达；每页有 h1；分页上下文清楚 |
| `/start-here/` | domain map、4 条 reading path、topic cards | 入口不重复；每条路径能到达首篇和完整路径 |
| `/curated/` | 路径、source note、curated card、Archive CTA | source note 全部可达；状态标签可读 |
| `/category/` | 11 个 topic、Editor pick、Open topic | topic anchor 唯一；无重复 id |
| `/topics/*/` | featured、primary notes、related topics、侧栏/移动关系 | 桌面侧栏和移动正文关系均可达 |
| `/tag/` | Featured tags、过滤、排序、canonical tag | 过滤不改变链接语义；空状态清楚 |
| `/tag/*/` | alias note、文章列表、Search full archive | slug/别名不产生空页或重复计数 |
| `/search/` | 输入、topic/type/status/curated filters、Show more、URL 状态 | 首屏不必加载全文；`<`/`&` 代码可搜；刷新后状态保留 |
| `/archive/` | 年份导航、折叠/展开、hash、文章链接 | 点击年份后列表可见；aria 状态同步 |
| 文章页 | breadcrumb、tags、TOC drawer、copy、related、previous/next | 移动目录可打开；代码按钮可键盘操作；来源不断链 |
| `/about/` | focus cards、GitHub/博客园/email | 外链新窗口安全；联系入口清楚 |
| `/404.html` | 搜索框、Popular Topics、Recent Notes、返回按钮 | 搜索预填不覆盖用户输入；推荐内容可达 |
| 375/820/1024/1440px | header、卡片、表格、长标题、代码块 | 无水平溢出；触控目标至少约 36–44px；字体可读 |

## 6. 验证门禁

```bash
uv run --with-requirements scripts/requirements.txt scripts/generate_tag_pages.py --check
ruby scripts/audit-content.rb
ruby scripts/validate-curation.rb
ruby scripts/validate-tags.rb
bundle exec jekyll clean
TZ=UTC bundle exec jekyll build
ruby scripts/smoke-test.rb
python3 scripts/site-review.py
node scripts/search-interaction-test.js
node --check js/search.js
node --check js/pageContent.js
node --check js/tags.js
node --check js/toc.js
node --check js/main.js
node --check js/copy-code.js
ruby scripts/verify-post-history.rb
```

Pages CI 还会验证生成的标签页、构建产物、JSON 索引、历史 blob 和 rendered site review。

## 7. 后续任务

### P1（下一轮）

- 在真实桌面浏览器中执行 375/820/1440px 点击矩阵和截图回归。
- 为历史中文/英文文章建立非破坏性的语言识别 sidecar。
- 对 243 个标签做可发现性抽样，评估是否需要分组而不是继续增加标签。
- 用 Lighthouse/axe 对 light/dark 主题进行对比度和键盘回归。

### P2

- 为搜索建立 Worker 或分片索引，评估 2.5MB 索引的移动端首屏成本。
- 为 tag index 增加 A–Z 分组和更细的 featured/常用标签策略。
- 为历史文章补齐抽样后的 `display_title` 和多语言阅读提示。
- 为 GPU/驱动/vLLM 部署增加可复现的环境记录模板。

## 8. 变更边界

- 不修改历史文章正文、日期、文件路径或公开 URL；本轮仅对已登记的历史 code-fence 渲染安全修复改变 Markdown 排版，不改变技术结论。
- 新问题若需要历史技术勘误，必须登记 `_data/format_fixes.yml` 并绑定批准后的 blob。
- 不把 `reported-tested` 解释为独立复现。
- 不把版本、模型、GPU、CUDA 或性能数字写成跨环境保证。
