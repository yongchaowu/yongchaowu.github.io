---

layout: post
title: 'VitePress 完全指南 / Complete VitePress Guide'
summary: 'Complete VitePress guide covering concepts, quick start, configuration, Markdown extensions, custom themes, deployment, and a practical blog example.'
lang: zh-CN
date: 2026-09-05 01:30:00
categories:
- Developer Tools
tags:
- Tool
- Web
- Front-End
- Markdown
---
{% raw %}
> Vite & Vue Powered Static Site Generator / Vite 与 Vue 驱动的静态站点生成器

---

<!--more-->

## 目录 / Table of Contents

- [什么是 VitePress / What is VitePress](#什么是-vitepress--what-is-vitepress)
- [为什么选择 VitePress / Why VitePress](#为什么选择-vitepress--why-vitepress)
- [VitePress vs 其他方案 / VitePress vs Alternatives](#vitepress-vs-其他方案--vitepress-vs-alternatives)
- [快速开始 / Getting Started](#快速开始--getting-started)
- [文件结构 / File Structure](#文件结构--file-structure)
- [常用命令 / Commands](#常用命令--commands)
- [配置详解 / Configuration](#配置详解--configuration)
- [Markdown 扩展 / Markdown Extensions](#markdown-扩展--markdown-extensions)
- [在 Markdown 中使用 Vue / Using Vue in Markdown](#在-markdown-中使用-vue--using-vue-in-markdown)
- [自定义主题 / Custom Theme](#自定义主题--custom-theme)
- [部署 / Deployment](#部署--deployment)
- [常见问题 / FAQ](#常见问题--faq)
- [实战示例 / Practical Example](#实战示例构建博客--practical-example-build-a-blog)
- [资源链接 / Resources](#资源链接--resources)

---

## 什么是 VitePress / What is VitePress

### English

VitePress is a **Static Site Generator (SSG)** designed for building fast, content-centric websites. It takes your Markdown content, applies a theme, and generates static HTML pages that can be deployed anywhere.

Key characteristics:
- Built on **Vite** for instant server start and hot module replacement
- Built on **Vue 3** for reactive components and modern JavaScript
- **Markdown-first** approach - write content in Markdown, get a beautiful website
- **File-based routing** - each `.md` file becomes a corresponding `.html` page

### 中文

VitePress 是一个**静态站点生成器 (SSG)**，专为构建快速、以内容为中心的网站而设计。它将你的 Markdown 内容应用主题，生成可以部署到任何地方的静态 HTML 页面。

核心特点：
- 基于 **Vite** 构建，实现即时服务器启动和热模块替换
- 基于 **Vue 3** 构建，支持响应式组件和现代 JavaScript
- **Markdown 优先**的方式 - 用 Markdown 编写内容，获得精美的网站
- **基于文件的路由** - 每个 `.md` 文件对应生成一个 `.html` 页面

---

## 为什么选择 VitePress / Why VitePress

### 优势 / Advantages

#### 1. 极快的开发体验 / Blazing Fast DX

| 特性 / Feature | 说明 / Description |
|---|---|
| 即时启动 / Instant Start | 基于 Vite，开发服务器毫秒级启动 / Based on Vite, dev server starts in milliseconds |
| 热更新 / HMR | 编辑 Markdown 立即预览，无需刷新 / Edit Markdown and see changes instantly |
| 增量构建 / Incremental Build | 只重新构建修改的页面 / Only rebuild changed pages |

#### 2. 卓越的性能 / Excellent Performance

| 指标 / Metric | 表现 / Result |
|---|---|
| 初始加载 / Initial Load | 静态 HTML，极快加载 / Static HTML, lightning fast |
| 页面导航 / Navigation | SPA 模式，无整页刷新 / SPA mode, no full page reload |
| 代码分割 / Code Splitting | 自动按需加载 / Automatic code splitting |
| SEO 友好 / SEO Friendly | 完整的静态 HTML 输出 / Full static HTML output |

#### 3. 丰富的功能 / Rich Features

- **内置主题 / Built-in Theme**: 专为文档设计的默认主题
- **暗黑模式 / Dark Mode**: 一键切换明暗主题
- **全文搜索 / Full-text Search**: 内置搜索功能
- **国际化 / i18n**: 多语言支持
- **自定义容器 / Custom Containers**: 提示框、警告框、详情框等
- **代码高亮 / Syntax Highlighting**: 基于 Shiki 的代码高亮
- **数学公式 / Math Equations**: 支持 LaTeX 数学公式
- **图表支持 / Diagrams**: 支持 Mermaid 图表

#### 4. 简单易用 / Simple & Easy

```
写 Markdown → 自动生成网站
Write Markdown → Auto-generate website
```

#### 5. 部署灵活 / Flexible Deployment

支持部署到：
- GitHub Pages
- GitLab Pages
- Netlify
- Vercel
- Cloudflare Pages
- AWS Amplify
- 任何静态托管服务 / Any static hosting

---

## VitePress vs 其他方案 / VitePress vs Alternatives

| 特性 / Feature | VitePress | VuePress | Docusaurus | Hexo |
|---|---|---|---|---|
| 构建工具 / Bundler | Vite | Webpack | Webpack | Webpack |
| 框架 / Framework | Vue 3 | Vue 2 | React | 无/Underscore |
| 启动速度 / Start Speed | 极快/Fast | 较慢/Slow | 较慢/Slow | 慢/Slow |
| 热更新 / HMR | 毫秒/Milliseconds | 秒/Seconds | 秒/Seconds | 秒/Seconds |
| 包大小 / Bundle Size | 小/Small | 中/Medium | 大/Large | 中/Medium |
| Markdown 扩展 / MD Extensions | 丰富/Rich | 丰富/Rich | 中等/Medium | 丰富/Rich |
| Vue 组件支持 / Vue Components | ✅ | ✅ | ❌ | ❌ |
| 维护状态 / Maintenance | 活跃/Active | 社区维护 | 活跃/Active | 活跃/Active |

### VitePress 2.x 新特性 / VitePress 2.x New Features

> ⚠️ VitePress 2.x 目前处于 alpha 阶段 / Currently in alpha stage
> 查看更新日志 / See [Changelog](https://github.com/vuejs/vitepress/blob/main/CHANGELOG.md)

| 特性 / Feature | 说明 / Description |
|---|---|
| MPA 模式 / MPA Mode | 零 JS 输出，适合纯静态内容 / Zero JS output, great for static content |
| 站点地图 / Sitemap | 自动生成站点地图 / Auto-generate sitemap |
| 目录级配置 / Directory Config | 每个目录可有独立配置 / Per-directory config overrides |
| 图标支持 / Icon Support | 内置 Iconify 图标 / Built-in Iconify icons |

---

## 快速开始 / Getting Started

### 环境要求 / Prerequisites

- **Node.js** 22 或更高版本 / version 22 or higher
- 终端 / Terminal
- 支持 Markdown 的文本编辑器 / Text editor with Markdown support

### 安装 / Installation

#### 方式一：全新项目 / Fresh Project

```bash
# 使用 npm
npm add -D vitepress@next

# 使用 pnpm (推荐 / Recommended)
pnpm add -D vitepress@next

# 使用 yarn
yarn add -D vitepress vue

# 使用 bun
bun add -D vitepress@next
```

#### 运行初始化向导 / Run Setup Wizard

```bash
# npm
npx vitepress init

# pnpm
pnpm vitepress init

# yarn
yarn vitepress init
```

初始化向导会问你几个问题 / The setup wizard will ask you:

```
┌  Welcome to VitePress!
│
◇  Where should VitePress initialize the config?
│  ./docs
│
◇  Where should VitePress look for your markdown files?
│  ./docs
│
◇  Site title:
│  My Awesome Project
│
◇  Site description:
│  A VitePress Site
│
◇  Theme:
│  Default Theme
│
◇  Use TypeScript for config and theme files?
│  Yes
│
◇  Add VitePress npm scripts to package.json?
│  Yes
│
◇  Add a prefix for VitePress npm scripts?
│  Yes
│
◇  Prefix for VitePress npm scripts:
│  docs
│
└  Done! Now run pnpm run docs:dev and start writing.
```

#### 方式二：已有项目 / Existing Project

```bash
# 在项目根目录创建 docs 文件夹
mkdir docs

# 在 docs 目录下初始化 VitePress
cd docs
npm init -y
npm add -D vitepress@next
```

### 首次启动 / First Run

```bash
# npm
npm run docs:dev

# pnpm
pnpm run docs:dev

# 或直接运行 / or run directly
npx vitepress dev docs
```

**结果 / Result:**

```
  VitePress  v2.0.0-alpha.20

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

打开浏览器访问 `http://localhost:5173/` 即可看到你的站点！

---

## 文件结构 / File Structure

```
.
├── docs
│   ├── .vitepress
│   │   ├── config.js          # 配置文件 / Configuration file
│   │   ├── cache/             # 开发缓存 / Dev cache (add to .gitignore)
│   │   └── dist/              # 构建输出 / Build output (add to .gitignore)
│   ├── public/                # 静态资源 / Static assets
│   │   └── favicon.ico
│   ├── index.md               # 首页 / Homepage
│   ├── guide
│   │   ├── index.md           # /guide/
│   │   └── getting-started.md # /guide/getting-started.html
│   └── api
│       └── index.md           # /api/
└── package.json
```

**注意 / Note:** `.vitepress/cache` 和 `.vitepress/dist` 应添加到 `.gitignore`:
```gitignore
.vitepress/cache
.vitepress/dist
```

### 路由规则 / Routing Rules

| 源文件 / Source File | 生成页面 / Generated Page | 访问路径 / URL |
|---|---|---|
| `index.md` | `index.html` | `/` |
| `guide/index.md` | `guide/index.html` | `/guide/` |
| `guide/about.md` | `guide/about.html` | `/guide/about` |
| `blog/hello.md` | `blog/hello.html` | `/blog/hello` |

---

## 常用命令 / Commands

### 开发命令 / Development Commands

```bash
# 启动开发服务器 / Start dev server
npm run docs:dev
# 结果: http://localhost:5173/

# 指定端口启动 / Start on specific port
npx vitepress dev docs --port 3000
# 结果: http://localhost:3000/

# 允许外部访问 / Allow external access
npx vitepress dev docs --host 0.0.0.0
```

### 构建命令 / Build Commands

```bash
# 构建生产版本 / Build for production
npm run docs:build
# 结果: 生成 .vitepress/dist 目录

# 指定 base 路径构建 / Build with base path
npx vitepress build docs --base /blog/

# 构建并预览 / Build and preview
npm run docs:build && npm run docs:preview
```

### 预览命令 / Preview Commands

```bash
# 预览构建结果 / Preview build output
npm run docs:preview
# 结果: http://localhost:4173/

# 指定端口预览 / Preview on specific port
npx vitepress preview docs --port 8080
```

### 完整 package.json 示例 / Complete package.json Example

```json
{
  "name": "my-docs",
  "scripts": {
    "docs:dev": "vitepress dev docs",
    "docs:build": "vitepress build docs",
    "docs:preview": "vitepress preview docs"
  },
  "devDependencies": {
    "vitepress": "^2.0.0-alpha.20"
  }
}
```

---

## 配置详解 / Configuration

### 基础配置 / Basic Configuration

`.vitepress/config.js`:

```js
import { defineConfig } from 'vitepress'

export default defineConfig({
  // 站点标题 / Site title
  title: 'My Documentation',

  // 站点描述 / Site description
  description: 'A VitePress site',

  // 语言 / Language
  lang: 'en-US',

  // 基础路径 / Base URL
  base: '/',

  // 最后更新时间 / Last updated
  lastUpdated: true,

  // 主题配置 / Theme configuration
  themeConfig: {
    // 导航栏 / Navigation bar
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/' },
      { text: 'API', link: '/api/' }
    ],

    // 侧边栏 / Sidebar
    sidebar: [
      {
        text: 'Guide',
        items: [
          { text: 'Introduction', link: '/guide/' },
          { text: 'Getting Started', link: '/guide/getting-started' }
        ]
      }
    ],

    // 社交链接 / Social links
    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ],

    // 页脚 / Footer
    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2026'
    },

    // 搜索 / Search
    search: {
      provider: 'local'
    },

    // 暗黑模式 / Dark mode
    appearance: true
  }
})
```

### 高级配置 / Advanced Configuration

```js
import { defineConfig } from 'vitepress'

export default defineConfig({
  // Markdown 配置 / Markdown config
  markdown: {
    lineNumbers: true,        // 显示行号 / Show line numbers
    math: true,               // 数学公式 / Math equations
    image: {
      lazyLoading: true       // 图片懒加载 / Image lazy loading
    }
  },

  // Vite 配置 / Vite config
  vite: {
    // 可以添加 Vite 插件 / Add Vite plugins
  },

  // Vue 配置 / Vue config
  vue: {
    // @vitejs/plugin-vue 选项 / @vitejs/plugin-vue options
  },

  // 清理 URLs / Clean URLs
  cleanUrls: true,

  // 忽略死链 / Ignore dead links
  ignoreDeadLinks: true,

  // Head 标签 / Head tags
  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }]
  ]
})
```

### TypeScript 配置 / TypeScript Config

`.vitepress/config.ts`:

```ts
import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'My Docs',
  description: 'TypeScript powered VitePress site',
  themeConfig: {
    // TypeScript 智能提示 / TypeScript intellisense
    nav: [
      { text: 'Home', link: '/' }
    ]
  }
})
```

---

## Markdown 扩展 / Markdown Extensions

### 自定义容器 / Custom Containers

```markdown
::: info
This is an info box.
:::

::: tip
This is a tip.
:::

::: warning
This is a warning.
:::

::: danger
This is a dangerous warning.
:::

::: details Click to expand
This is a details block.
:::
```

**结果 / Result:**

> **INFO**: This is an info box.

> **TIP**: This is a tip.

> **WARNING**: This is a warning.

> **DANGER**: This is a dangerous warning.

### GitHub 风格 Alerts / GitHub-flavored Alerts

```markdown
> [!NOTE]
> Highlights information users should know.

> [!TIP]
> Optional information to help users.

> [!IMPORTANT]
> Crucial information for success.

> [!WARNING]
> Critical content requiring attention.

> [!CAUTION]
> Negative consequences of an action.
```

### 代码块增强 / Code Block Enhancements

#### 语法高亮 / Syntax Highlighting

````markdown
```js
export default {
  name: 'MyComponent'
}
```
````

#### 行高亮 / Line Highlighting

````markdown
```js{4}
export default {
  data() {
    return {
      msg: 'Highlighted!'  // 这行会被高亮
    }
  }
}
```
````

#### 代码差异 / Code Diff

````markdown
```js
const msg = 'Old value' // [!code --]
const msg = 'New value' // [!code ++]
```
````

#### 代码聚焦 / Code Focus

````markdown
```js
export default {
  data() {
    return {
      msg: 'Focused!' // [!code focus]
    }
  }
}
```
````

#### 行号 / Line Numbers

````markdown
```ts:line-numbers
const line1 = 'This is line 1'
const line2 = 'This is line 2'
const line3 = 'This is line 3'
```
````

### 代码组 / Code Groups

````markdown
::: code-group

```js [config.js]
export default {
  // JS config
}
```

```ts [config.ts]
export default {
  // TS config
}
```

:::
````

### 表格 / Tables

```markdown
| Feature | Support |
| --- | --- |
| Tables | ✅ |
| Code Blocks | ✅ |
| Custom Containers | ✅ |
```

**结果 / Result:**

| Feature | Support |
| --- | --- |
| Tables | ✅ |
| Code Blocks | ✅ |
| Custom Containers | ✅ |

### 任务列表 / Task Lists

```markdown
- [x] Completed task
- [ ] Pending task
- [ ] Another task
```

**结果 / Result:**

- [x] Completed task
- [ ] Pending task
- [ ] Another task

### 目录 / Table of Contents

```markdown
[[toc]]
```

自动生成当前页面的目录。

### 数学公式 / Math Equations

需要安装 `markdown-it-mathjax3`:

```bash
npm add -D markdown-it-mathjax3@^4
```

配置:

```js
export default {
  markdown: {
    math: true
  }
}
```

使用:

```markdown
当 $a \ne 0$ 时，方程 $ax^2 + bx + c = 0$ 的解为：

$$ x = {-b \pm \sqrt{b^2-4ac} \over 2a} $$
```

### 导入代码片段 / Import Code Snippets

```markdown
<<< @/snippets/example.js
```

支持高亮指定行:

```markdown
<<< @/snippets/example.js{2,3}
```

### Markdown 文件包含 / Markdown File Inclusion

```markdown
<!--@include: ./parts/basics.md-->
```

支持选择行范围:

```markdown
<!--@include: ./parts/basics.md{3,}-->
```

### Frontmatter

```yaml
---
title: My Page
description: Page description
lang: zh-CN
layout: doc
---
```

---

## 在 Markdown 中使用 Vue / Using Vue in Markdown

每个 Markdown 文件都是一个 Vue 单文件组件 (SFC)。

### 模板语法 / Template Syntax

```markdown
# {{ message }}

<count-component />

<script setup>
import { ref } from 'vue'
const message = ref('Hello VitePress!')
</script>
```

### 使用自定义组件 / Using Custom Components

```markdown
<script setup>
import MyComponent from './components/MyComponent.vue'
</script>

<MyComponent :data="someData" />
```

### 访问页面数据 / Accessing Page Data

```markdown
<script setup>
import { useData } from 'vitepress'

const { page, frontmatter, title } = useData()
</script>

# {{ title }}

当前页面: {{ page.relativePath }}
```

---

## 自定义主题 / Custom Theme

### 创建自定义主题 / Create Custom Theme

`.vitepress/theme/index.js`:

```js
import DefaultTheme from 'vitepress/theme'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    // 注册全局组件 / Register global components
  }
}
```

### 自定义样式 / Custom Styles

`.vitepress/theme/custom.css`:

```css
:root {
  --vp-c-brand-1: #3451b2;
  --vp-c-brand-2: #3a5ccc;
  --vp-c-brand-3: #5078f6;
  --vp-c-brand-soft: rgba(100, 108, 255, 0.14);
}

.dark {
  --vp-c-brand-1: #5c73e7;
  --vp-c-brand-2: #6582f7;
  --vp-c-brand-3: #749bff;
}
```

### 使用自定义主题 / Use Custom Theme

```js
// .vitepress/config.js
import { defineConfigWithTheme } from 'vitepress'

export default defineConfigWithTheme({
  themeConfig: {
    // 你的自定义配置 / Your custom config
  }
})
```

---

## 部署 / Deployment

### 构建项目 / Build Project

```bash
npm run docs:build
```

结果生成 `.vitepress/dist` 目录。

### 部署到 GitHub Pages / Deploy to GitHub Pages

1. 在 `.github/workflows` 创建 `deploy.yml`:

```yaml
name: Deploy VitePress site to Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v6
        with:
          node-version: 24
          cache: npm
      - run: npm ci
      - run: npm run docs:build
      - uses: actions/upload-pages-artifact@v3
        with:
          path: docs/.vitepress/dist

  deploy:
    environment:
      name: github-pages
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/deploy-pages@v4
```

2. 在 GitHub 仓库设置中选择 "GitHub Actions" 作为 Source

### 部署到 Netlify / Deploy to Netlify

构建设置:
- **Build Command:** `npm run docs:build`
- **Output Directory:** `docs/.vitepress/dist`
- **Node Version:** `22`

### 部署到 Vercel / Deploy to Vercel

```bash
# 安装 Vercel CLI / Install Vercel CLI
npm i -g vercel

# 部署 / Deploy
vercel
```

### 部署到 Cloudflare Pages / Deploy to Cloudflare Pages

1. 连接 Git 仓库 / Connect Git repository
2. 构建设置 / Build settings:
   - **Build command:** `npm run docs:build`
   - **Build output directory:** `docs/.vitepress/dist`

### 本地预览构建结果 / Preview Build Locally

```bash
npm run docs:preview
# 结果: http://localhost:4173/
```

---

## 常见问题 / FAQ

### Q: VitePress 适合什么场景？

**English:**
VitePress is ideal for:
- Technical documentation
- API documentation
- Blog sites
- Portfolio sites
- Project documentation
- Knowledge bases

**中文:**
VitePress 适合：
- 技术文档
- API 文档
- 博客站点
- 作品集网站
- 项目文档
- 知识库

### Q: 如何启用暗黑模式？

在配置中设置:

```js
export default {
  appearance: true  // 默认启用 / enabled by default
}
```

### Q: 如何添加搜索功能？

```js
export default {
  themeConfig: {
    search: {
      provider: 'local'
    }
  }
}
```

### Q: 如何配置多语言？

```js
export default {
  locales: {
    root: {
      label: 'English',
      lang: 'en'
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN'
    }
  }
}
```

### Q: 如何使用自定义域名？

设置 `base` 为 `/`:

```js
export default {
  base: '/'
}
```

---

## 实战示例：构建博客 / Practical Example: Build a Blog

### 步骤 1：初始化项目 / Step 1: Initialize Project

```bash
mkdir my-blog && cd my-blog
npm init -y
npm add -D vitepress@next
npx vitepress init
```

### 步骤 2：创建文章 / Step 2: Create Posts

创建 `docs/posts/hello-world.md`:

```markdown
---
title: Hello World
date: 2026-09-05
tags: [blog, vitepress]
---

# Hello World

这是我的第一篇博客文章！

## 为什么选择 VitePress

VitePress 非常适合构建博客，因为：
- 写 Markdown 即可
- 自带漂亮的主题
- 部署简单
```

### 步骤 3：配置导航 / Step 3: Configure Navigation

`.vitepress/config.js`:

```js
export default {
  title: 'My Blog',
  description: 'A VitePress Blog',
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Posts', link: '/posts/' }
    ],
    sidebar: {
      '/posts/': [
        {
          text: 'Blog Posts',
          items: [
            { text: 'Hello World', link: '/posts/hello-world' }
          ]
        }
      ]
    }
  }
}
```

### 步骤 4：启动开发 / Step 4: Start Development

```bash
npm run docs:dev
# 访问 http://localhost:5173/posts/hello-world
```

### 步骤 5：构建部署 / Step 5: Build & Deploy

```bash
npm run docs:build
# 部署 docs/.vitepress/dist 目录
```

---

## 资源链接 / Resources

- [VitePress 官方文档 / Official Docs](https://vitepress.dev/)
- [VitePress GitHub](https://github.com/vuejs/vitepress)
- [Vite 官方文档 / Vite Docs](https://vite.dev/)
- [Vue.js 官方文档 / Vue Docs](https://vuejs.org/)

---

## 总结 / Summary

VitePress 是一个现代化的静态站点生成器，它结合了:

- ✅ **Vite** 的极速开发体验
- ✅ **Vue 3** 的强大组件系统
- ✅ **Markdown** 的简洁写作方式
- ✅ **SSG** 的优秀性能和 SEO

无论你是想构建技术文档、博客还是项目文档，VitePress 都是一个值得考虑的选择。

---

*最后更新 / Last updated: 2026-09-05 (Updated for VitePress 2.x)*
{% endraw %}
