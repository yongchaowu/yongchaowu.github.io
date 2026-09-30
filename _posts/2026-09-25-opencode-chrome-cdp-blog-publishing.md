---
layout: post
title: "OpenCode 如何用 CDP 驱动已登录的 Chrome 更新博客园文章？"
display_title: "OpenCode 如何用 CDP 驱动已登录的 Chrome 更新博客园文章？"
summary: "用 Chrome DevTools Protocol 让 OpenCode 接管一台已登录的 Chrome：本地 Markdown 比对 → MCP 封装 CDP → 已登录浏览器执行编辑 → 打开公开页核验。拆解五个组件各自的职责边界、复用登录态的前提、CDP 连接配置、一次更新的完整步骤，以及这套自动化真正的风险边界。"
lang: zh-CN
date: 2026-09-25 10:00:00
categories:
  - Developer Tools
  - AI & LLM
tags:
  - "OpenCode"
  - "CDP"
  - "Chrome"
  - "MCP"
  - "自动化"
  - "博客园"
  - "AI Coding Agent"
---

<!--more-->

> **修改时间：** 2026-09-25  
> **内容说明：** 本文由 AI 辅助整理，发布前请作者人工复核。

**CDP（Chrome DevTools Protocol，Chrome DevTools 协议）** 是 Chrome 提供的一套调试与自动化协议。借助 Chrome DevTools MCP 或其他 CDP 适配器，OpenCode 可以控制一个已经登录的 Chrome，像人工一样打开博客园后台、填写编辑器、点击保存，再打开公开页面核验结果。

这套方案不依赖博客园未公开的接口，其核心流程如下：

```text
本地 Markdown
      │ 读取与比较
      ▼
   OpenCode
      │ 编排浏览器操作
      ▼
Chrome DevTools MCP
      │ Chrome DevTools Protocol
      ▼
  已登录的 Chrome
      ├── 博客园后台
      └── 文章公开页面
```

其中，CDP 负责控制浏览器，OpenCode 负责安排操作步骤，Chrome 提供登录状态，本地文件工具负责读取和保存 Markdown。几者职责不同，任何一个都不能替代其余部分。

---

## 一、各个组件分别做什么

| 组件 | 主要职责 |
| --- | --- |
| Chrome | 保留登录会话，并承载博客园后台与公开页面 |
| CDP | 提供页面导航、内容读取、脚本执行、鼠标键盘输入等底层能力 |
| Chrome DevTools MCP | 将 CDP 封装为 OpenCode 可以调用的浏览器工具 |
| OpenCode | 理解任务、比较内容、安排操作并决定何时验证结果 |
| 本地文件工具 | 读取 Markdown、记录元数据或更新备份；这部分不属于 CDP |

常见 MCP 工具包括：

```text
list_pages       列出浏览器页面
navigate_page    打开或刷新页面
take_snapshot    读取页面结构和可交互元素
fill_form        填写多个表单控件
click            点击按钮或链接
wait_for         等待指定内容出现
evaluate_script  在页面上下文中读取或检查数据
```

工具名称可能因客户端或命名空间而不同，但基本模式都是：**先观察页面，再根据最新快照执行操作。**

---

## 二、为什么能复用已登录状态

CDP 本身不会自动登录网站，也不会绕过认证。它只是控制 Chrome。

当用户在某个 Chrome 用户资料中登录博客园后，登录状态会保存在该浏览器资料对应的站点会话中。只要自动化工具连接到这个 Chrome 实例，页面操作就会复用它已有的登录状态：

1. 用户先在 Chrome 中完成登录；
2. OpenCode 通过 MCP 连接该 Chrome；
3. 自动化操作使用当前浏览器已有的会话。

因此，这不是“自动登录”，也不是“绕过登录”。但这也意味着，一旦 Agent 连接到已登录的浏览器，就可能读取该资料中的其他页面，并以当前用户权限执行网页操作，所以应当使用专用浏览器资料并限制无关标签页。

---

## 三、配置 OpenCode 连接 Chrome

### 3.1 默认方式

直接配置 `chrome-devtools-mcp` 时，它默认会启动一个使用专用资料目录的 Chrome。用户可以第一次手动登录，后续运行继续复用这个专用会话：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "chrome-devtools": {
        "type": "local",
        "command": [
          "npx",
          "-y",
          "chrome-devtools-mcp@latest"
        ]
      }
    }
  }
}
```

这种方式环境隔离较好。如果目标是让手动操作与 Agent 操作共享同一个已登录的 Chrome，可以选择下面的连接方式。

### 3.2 自动连接正在运行的 Chrome

Chrome 144 及以上版本可以先在 `chrome://inspect/#remote-debugging` 中启用远程调试，再让 MCP 使用 `--autoConnect`：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "chrome-devtools": {
        "type": "local",
        "command": [
          "npx",
          "-y",
          "chrome-devtools-mcp@latest",
          "--autoConnect"
        ]
      }
    }
  }
}
```

Chrome 必须已经启动。首次连接时，Chrome 会显示调试授权提示，只有用户明确允许后，MCP 才能访问该浏览器资料。

### 3.3 通过本地调试端口连接

不支持自动连接时，可以先使用独立的用户资料目录启动 Chrome：

```bash
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=/path/to/dedicated-chrome-profile
```

再将 MCP 指向本地调试端点：

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "chrome-devtools": {
        "type": "local",
        "command": [
          "npx",
          "-y",
          "chrome-devtools-mcp@latest",
          "--browser-url=http://127.0.0.1:9222"
        ]
      }
    }
  }
}
```

不要把远程调试端口暴露到公网。启用该端口后，能访问它的程序可能控制整个浏览器会话。

配置完成后，可以检查连接状态：

```bash
opencode mcp list
```

---

## 四、更新一篇文章的完整流程

下面使用抽象文件与 URL 作为示例，不依赖某一篇特定文章：

```text
本地文件：article.md
后台编辑页：https://www.cnblogs.com/<user>/admin/post/EditPosts/<postId>
公开页面：https://www.cnblogs.com/<user>/p/<postId>.html
```

### 1. 读取并检查本地内容

先读取 Markdown，确认标题、正文、链接、代码块和需要保留的 HTML。已有文章应尽量做局部修改，不要为了格式统一而整体重写。

### 2. 确认浏览器和登录状态

列出页面，确认目标 Chrome 已经登录博客园。如果会话过期或需要验证码，应停止并请用户手动处理，不要尝试读取密码、Cookie 或其他认证数据。

### 3. 打开编辑页并读取快照

进入目标文章的编辑页，读取最新页面快照，定位：

- 标题输入框；
- 正文编辑器；
- 分类、标签等控件；
- 保存或发布按钮；
- 当前发布状态。

页面快照中的元素标识可能随导航或页面更新而失效，因此不要长期复用旧标识。

### 4. 比较差异并等待确认

在修改前，向用户说明：

```text
目标文章：<公开页面 URL>
拟修改内容：<具体段落或差异>
保持不变：标题、分类、标签及其他元数据
验证方式：重新打开编辑页和公开页面
```

保存、发布、删除等会改变线上状态的操作，应在获得明确确认后执行。

### 5. 填写并保存

根据编辑器当前使用的格式填写标题和正文，并保留原有分类、标签及其他设置。博客园编辑器可能是普通文本框、`contenteditable`、富文本组件或 iframe，不能只依赖一个长期不变的 CSS 选择器。

填写完成后点击保存，并等待页面完成异步请求。不要仅凭一条“保存成功”提示就认定线上内容已经更新。

### 6. 回读并核验

保存后依次检查：

1. 重新打开编辑页，确认标题、正文和元数据；
2. 打开公开页面，确认关键段落和代码块；
3. 必要时调用 `navigate_page` 并设置 `ignoreCache: true`，排除浏览器缓存影响。

只有公开页面显示预期内容，才能把远程更新标记为完成。

### 7. 更新本地记录

如果工作流还需要维护本地备份，应在远程验证成功后，再由 OpenCode 的文件工具单独保存 Markdown、文章 ID、分类、标签、更新时间和公开 URL。

MCP 可以把部分工具结果写入文件，但“更新线上文章”和“维护本地备份”仍是两个独立动作。两者都成功，才算完整流程结束。

---

## 五、CDP 底层做了什么

一次浏览器操作通常包含以下过程：

1. 发现并连接 Chrome 页面目标；
2. 附加 CDP 会话并启用所需 Domain；
3. 发送导航、读取或输入命令；
4. 接收命令结果和异步事件；
5. 等待页面达到预期状态。

常见 CDP 命令包括：

```text
Page.navigate                 导航页面
DOM.getDocument                获取 DOM 文档
Runtime.evaluate              执行页面 JavaScript
Input.dispatchMouseEvent       派发鼠标事件
Input.dispatchKeyEvent         派发键盘事件
Network.enable                 观察网络请求
```

Chrome DevTools MCP 会把这些底层能力包装成更适合 Agent 调用的工具，并处理页面快照、等待和错误反馈。对于常见的博客园更新任务，通常不需要自行实现完整的 CDP 客户端；只有开发专用插件或批处理服务时，才有必要直接处理 WebSocket、Domain 和事件。

---

## 六、安全与可靠性

### 6.1 安全边界

- 优先使用专用 Chrome 用户资料，不连接包含邮箱、网银等敏感页面的日常资料；
- 不读取、输出或记录 Cookie、密码、验证码、`localStorage` 和访问令牌；
- 不公开远程调试端口及 `webSocketDebuggerUrl`；
- 在保存、发布、删除和批量操作前取得明确授权；
- 只在目标站点和指定文章范围内操作。

### 6.2 常见失败原因

- **登录过期**：停止操作，交由用户重新登录；
- **页面结构变化**：重新获取快照，而不是继续使用旧选择器；
- **异步保存延迟**：等待请求完成，并重新读取页面；
- **缓存未刷新**：使用无缓存刷新后再判断结果；
- **验证不完整**：后台保存成功不等于公开页面已经更新。

---

## 七、可复用的任务提示词

```text
请使用 OpenCode 的 Chrome DevTools MCP 处理以下文章：

本地文件：<Markdown 文件路径>
目标公开页面：<文章公开 URL>
目标编辑页面：<博客园编辑页 URL>

执行要求：

1. 确认正在控制正确的 Chrome，并检查博客园登录状态。
2. 读取本地文件，导航到目标编辑页并读取最新页面快照。
3. 比较本地内容与线上内容，列出拟修改和保持不变的字段。
4. 在保存、发布或提交前停止，等待我的明确确认。
5. 确认后填写编辑器并保存，等待页面完成异步操作。
6. 重新打开编辑页和公开页面，核验标题、正文、分类、标签及关键代码块。
7. 公开页面验证成功后，再单独更新本地 Markdown 和元数据。
8. 任一步骤验证失败时立即停止，不要继续处理其他文章。

禁止读取、输出或保存密码、Cookie、验证码、localStorage 和访问令牌。
```

---

## 总结

OpenCode 并未直接修改博客园数据库，而是在已登录的 Chrome 中执行后台页面原本就允许的操作：

> **Chrome 提供登录上下文，CDP 控制页面，MCP 适配工具，OpenCode 编排流程，公开页面负责验收，本地文件工具负责备份。**

只要登录会话有效、页面控件可以识别、保存动作经过授权，并且保存后能够从公开页面读回新内容，这套自动化流程就可以可靠运行。

---

## 参考资料

- [OpenCode V2：MCP servers](https://opencode.ai/v2/docs/mcp-servers)
- [Chrome DevTools for agents：Get started](https://developer.chrome.com/docs/devtools/agents/get-started)
- [Chrome DevTools MCP：配置](https://developer.chrome.com/docs/devtools/agents/get-started/configuration)
- [Chrome DevTools MCP：官方仓库](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Chrome DevTools MCP：工具参考](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/tool-reference.md)
- [Chrome DevTools MCP：Advanced usage](https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/advanced-usage.md)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
