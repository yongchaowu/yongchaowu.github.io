---

layout: post
title: '深入解析 OpenCode CLI：从架构设计到实战构建'
summary: 'OpenCode 是一个开源的 AI 编程助手，运行在终端中。本文深入解析其 TUI 架构、声明式 UI 渲染、Client-Server 分离设计，并手把手教你用 Bun + SolidJS + OpenTUI 构建一个类似的 AI CLI 工具。'
lang: zh-CN
date: 2026-09-05 02:14:00
categories:
- AI & LLM
tags:
- OpenCode
- TUI
- SolidJS
- TypeScript
- CLI
- Terminal
- AI Agent
---
## 引言

如果你用过 Cursor、Windsurf 这类 AI IDE，一定会对它们的智能补全和对话式编程印象深刻。但有些开发者更喜欢待在终端里——不需要 GUI，不需要 Electron，只需要一个干净的命令行界面。

<!--more-->


**OpenCode**（[anomalyco/opencode](https://github.com/anomalyco/opencode)）就是为这类开发者设计的。它是一个开源的 AI 编程助手，运行在终端中，支持多模型、多 Agent、工具调用、文件搜索等功能。目前在 GitHub 上已经获得了超过 20 万颗星。

但 OpenCode 真正让我感兴趣的，不是它的功能列表，而是它的**架构设计**。当你打开 OpenCode，看到的那个流畅的 TUI 界面——输入框固定在底部、消息区域平滑滚动、工具调用可以折叠展开、Markdown 带语法高亮——这一切的背后，是一套精心设计的声明式 UI 系统。

这篇文章将带你深入了解：

- OpenCode 的整体架构和设计理念
- `@opentui/solid` 如何将 SolidJS 的响应式范式映射到终端
- Client-Server 分离架构带来的可能性
- 如何从零构建一个类似的 AI CLI 工具

---

## 一、架构全景：TUI 与 Server 的分离

### 1.1 整体架构

OpenCode 的架构可以用一张图概括：

```text
┌─────────────────────────────────────────────────────┐
│                    OpenCode CLI                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌────────────────────────────────────────────────┐  │
│  │              TUI Frontend                      │  │
│  │                                                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │  │
│  │  │ @opentui │  │ @opentui │  │ solid-js │    │  │
│  │  │  /core   │  │  /solid  │  │          │    │  │
│  │  └──────────┘  └──────────┘  └──────────┘    │  │
│  │                     │                          │  │
│  │              @opencode-ai/sdk                  │  │
│  └─────────────────────┬──────────────────────────┘  │
│                        │ HTTP / SSE                   │
│  ┌─────────────────────▼──────────────────────────┐  │
│  │              OpenCode Server                    │  │
│  │                                                │  │
│  │  ┌─────────┐ ┌─────┐ ┌──────┐ ┌──────┐      │  │
│  │  │ Session │ │ LLM │ │ Tools│ │ Files│ ...   │  │
│  │  └─────────┘ └─────┘ └──────┘ └──────┘      │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
└─────────────────────────────────────────────────────┘
```

关键点在于：**TUI 和 Server 是完全分离的**。TUI 通过 `@opencode-ai/sdk` 与 Server 通信，SDK 本质上是一个生成的 HTTP 客户端，封装了所有的 API 调用和 SSE 事件流。

### 1.2 为什么选择 TypeScript/Bun 而不是 Go？

早期的 OpenCode 使用 Go + Bubble Tea 实现。如果你在网上搜索，还能找到不少旧版的 README 提到这个技术栈。但主线已经完全转向了 TypeScript/Bun + SolidJS + OpenTUI。

这个转变有几个关键原因：

1. **声明式 UI 的表达力**：Bubble Tea 是基于 Elm 架构的命令式 UI 模型，而 OpenTUI 提供了类似 React/Solid 的声明式组件模型，更适合构建复杂的交互界面
2. **生态复用**：TypeScript 生态有 Vercel AI SDK、Effect、Zod 等成熟的工具链
3. **Monorepo 管理**：Bun + Turborepo 让多包管理变得简单
4. **前后端统一**：Server 可以用 Hono 框架，TUI 用 OpenTUI，共享同一套类型定义

### 1.3 Monorepo 包结构

OpenCode 的代码组织在一个精心设计的 Monorepo 中：

```text
packages/
├── opencode/       # 主服务端实现、旧 CLI、Worker 管理
├── cli/            # 新 CLI 入口（薄适配层）
├── tui/            # @opencode-ai/tui — 独立的 TUI 包
├── sdk/            # 生成的 JavaScript SDK（Promise + Effect）
├── client/         # HTTP 客户端库
├── core/           # 共享领域逻辑、标志位、全局状态
├── server/         # HTTP 服务器、API 处理、中间件
├── protocol/       # API Schema 定义、端点构造
├── schema/         # 共享 Schema 类型
├── llm/            # LLM 提供商集成
├── plugin/         # 插件加载和管理
├── desktop/        # 桌面应用封装
├── app/            # Web 应用
└── web/            # 文档站点
```

依赖流向非常清晰：

```text
Schema → Protocol → Server
              │
              ▼
           Client (Promise / Effect)
              │
              ▼
           SDK (组合 Client + Core + Server in-memory)
              │
              ▼
           TUI / CLI / Desktop
```

**核心原则：TUI 只依赖生成的 SDK，不导入任何后端实现模块。** 这意味着 Server 端的任何改动，只要 API 不变，TUI 就不需要修改。

---

## 二、@opentui/solid：终端的声明式 UI 引擎

### 2.1 从命令式到声明式

传统的终端 UI 编程是命令式的：你直接操作 ANSI 转义码来控制光标位置、颜色、清屏等。

```ts
// 传统方式：命令式
process.stdout.write("\x1b[2J")        // 清屏
process.stdout.write("\x1b[1;1H")      // 移动光标到左上角
process.stdout.write("Hello World")    // 输出文本
process.stdout.write("\x1b[0m")        // 重置颜色
```

OpenTUI 提供了完全不同的范式——**声明式**。你只需要描述 UI 应该是什么样子，框架负责计算差异并更新终端：

```tsx
// OpenTUI 方式：声明式
function App() {
  return (
    <box flexDirection="column">
      <text color="blue">Hello World</text>
      <box flexGrow={1}>
        <text>Content area</text>
      </box>
      <input placeholder="Type here..." />
    </box>
  )
}
```

你可以把它类比为：

```text
React / Solid  →  DOM / Browser
OpenTUI        →  Terminal Screen
```

### 2.2 渲染管线

OpenTUI 的渲染流程分为六个阶段：

```text
Component Tree (SolidJS 组件树)
       │
       ▼
Layout Engine (计算每个元素的位置和大小)
       │
       ▼
Terminal Cells (将内容映射到终端单元格)
       │
       ▼
Diff Algorithm (计算新旧帧的差异)
       │
       ▼
ANSI Escape Sequences (生成最小化的 ANSI 转义码)
       │
       ▼
Terminal (写入 stdout)
```

关键优化在于 **Diff** 阶段。OpenTUI 不会每次都清屏重绘，而是像前端的 Virtual DOM 一样，只更新发生变化的 terminal cells。这就是为什么 OpenCode 的流式输出看起来非常顺滑。

### 2.3 渲染器初始化

在 OpenCode 的 `app.tsx` 中，渲染器的创建使用了 Effect 的资源管理：

```ts
const renderer = yield* Effect.tryPromise({
  try: () =>
    createCliRenderer({
      externalOutputMode: "passthrough",
      targetFps: 60,           // 60fps 渲染循环
      gatherStats: false,
      exitOnCtrlC: false,
      useKittyKeyboard: {},    // 使用 Kitty 键盘协议
      autoFocus: false,
      openConsoleOnError: false,
      useMouse: !Flag.OPENCODE_DISABLE_MOUSE && input.config.mouse,
    }),
  catch: (error) => (error instanceof Error ? error : new Error(String(error))),
})
```

然后注册键位映射并启动渲染：

```ts
const defaultKeymap = createDefaultOpenTuiKeymap()
const opencodeKeymap = yield* OpencodeKeymap
keymap.register(defaultKeymap)
keymap.register(opencodeKeymap)

yield* render(() => <SolidJSTree />, renderer)
```

### 2.4 SolidJS 的响应式状态管理

OpenCode 使用 SolidJS 的 Signal 和 Store 来管理状态：

```ts
// 创建响应式状态
const [messages, setMessages] = createSignal([])
const [streaming, setStreaming] = createSignal(false)

// 状态更新触发精确的 UI 重渲染
setMessages([
  ...messages(),
  {
    role: "assistant",
    text: chunk
  }
])
```

与 React 不同，SolidJS 的响应式是**细粒度的**——当 `messages` 更新时，只有绑定了 `messages()` 的组件会重新执行，而不是整个组件树。这在终端 UI 中尤为重要，因为每一帧的渲染开销都需要最小化。

---

## 三、组件系统：拆解 TUI 的每一层

### 3.1 聊天界面布局

OpenCode 的聊天界面可以拆解为几个主要区域：

```text
┌──────────────────────────────────────────────────────┐
│ OpenCode                        model / agent / info  │  ← Header
├──────────────────────────────────────────────────────┤
│                                                      │
│  User                                                │
│  帮我看看这个函数                                     │  ← UserMessage
│                                                      │
│  Assistant                                           │
│  我先读取 src/main.ts...                              │  ← AssistantMessage
│                                                      │
│  ┌─ Read ─────────────────────────────────────────┐  │
│  │ src/main.ts                                    │  │  ← ToolCall
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  找到问题了...                                       │
│                                                      │
├──────────────────────────────────────────────────────┤
│ > Ask anything...                                    │  ← Prompt
├──────────────────────────────────────────────────────┤
│ model                     tokens       cwd            │  ← Status
└──────────────────────────────────────────────────────┘
```

### 3.2 组件树

每个区域对应一个 SolidJS 组件：

```text
App
 ├─ Header                  # 顶部栏：应用名、模型、Agent 信息
 ├─ SessionView             # 会话视图容器
 │    ├─ UserMessage        # 用户消息
 │    ├─ AssistantMessage   # 助手消息（支持 Markdown 渲染）
 │    ├─ ToolCall           # 工具调用展示
 │    │    ├─ BashTool      # Bash 命令输出
 │    │    ├─ ReadTool      # 文件读取内容
 │    │    ├─ EditTool      # 文件编辑差异
 │    │    └─ GlobTool      # 文件搜索结果
 │    └─ Reasoning          # 推理过程（Thinking）
 ├─ Prompt                  # 输入区域
 │    ├─ TextInput          # 文本输入框
 │    ├─ Autocomplete       # @ 文件自动补全
 │    └─ CommandPalette     # / 命令面板
 └─ Status                  # 底部状态栏
```

### 3.3 Provider 树：依赖注入

OpenCode 使用了深度嵌套的 SolidJS Context Provider 来管理依赖。这是一个精心设计的分层结构：

```text
ExitProvider
  └─ EpilogueProvider
       └─ ErrorBoundary
            └─ TuiPathsProvider           # 路径：cwd, home, state, worktree
                 └─ TuiTerminalEnvironmentProvider  # 平台、终端环境
                      └─ TuiStartupProvider         # 初始路由、加载状态
                           └─ ClipboardProvider      # 剪贴板
                                └─ OpencodeKeymapProvider  # 键位映射
                                     └─ ArgsProvider       # CLI 参数
                                          └─ KVProvider    # 键值持久化
                                               └─ ToastProvider
                                                    └─ RouteProvider  # 路由状态
                                                         └─ TuiConfigProvider
                                                              └─ PluginRuntimeProvider
                                                                   └─ SDKProvider  # SDK 客户端 + SSE 事件流
                                                                        └─ PermissionProvider
                                                                             └─ ProjectProvider
                                                                                  └─ SyncProvider  # 全局状态存储
                                                                                       └─ DataProvider
                                                                                            └─ ThemeProvider
                                                                                                 └─ LocalProvider
                                                                                                      └─ App  # 主组件
```

每一层 Provider 负责一个特定的关注点，通过 SolidJS 的 `createContext` 向下传递依赖。这种设计让组件可以按需获取依赖，而不需要通过 props 逐层传递。

### 3.4 输入模式：@、/、!

OpenCode 的输入框支持多种模式，通过 Prompt 组件的状态切换：

#### `@` 文件搜索

输入 `@src/` 会触发模糊文件搜索：

```ts
// Prompt 组件内部状态
const [query, setQuery] = createSignal("")
const [files, setFiles] = createSignal([])
const [selected, setSelected] = createSignal(0)
```

显示效果：

```text
> @src/ser

┌───────────────────────────────────┐
│ src/server/server.ts              │
│ src/server/routes.ts              │
│ src/service/session.ts            │
│ src/service/provider.ts           │
└───────────────────────────────────┘
```

官方文档确认 `@` 会对当前项目执行 fuzzy file search（使用 fuzzysort 库）。

#### `/` 命令面板

输入 `/` 会触发命令面板，支持斜杠命令：

- `/compact` — 压缩会话历史
- `/connect` — 连接 Provider
- `/export` — 导出会话
- `/help` — 帮助
- `/models` — 切换模型
- `/new` — 新建会话
- `/sessions` — 会话列表
- `/themes` — 切换主题

也可以通过 `Ctrl+P` 随时打开命令面板的对话框版本。

#### `!` Shell 命令

输入 `!ls -la` 会执行 shell 命令，输出作为工具结果添加到对话中。

这些都不是 Shell 自己实现的，而是 Prompt 组件根据输入状态切换不同的 overlay。

---

## 四、Client-Server 架构：分离的力量

### 4.1 为什么分离？

OpenCode 的一个核心设计决策是将 TUI 和 AI 后端完全分离。这意味着：

```bash
# 终端 1：启动后端服务
opencode web --port 4096

# 终端 2：TUI 连接到远程服务
opencode attach http://10.20.30.40:4096
```

这种分离带来了几个关键优势：

1. **多客户端支持**：同一个 Server 可以同时服务 Terminal TUI、Web 界面、Desktop 应用、甚至 Mobile 客户端
2. **远程开发**：Server 运行在远程服务器上，本地只需要一个轻量级 TUI
3. **嵌入式模式**：SDK 支持 in-process 运行，Server 和 TUI 在同一个进程中，通过内存传输通信，零网络开销

```text
Terminal ─┐
Web      ─┼──> same OpenCode server
Desktop  ─┤
Mobile   ─┘
```

### 4.2 SDK：唯一的领域边界

`@opencode-ai/sdk` 是 TUI 和 Server 之间的唯一桥梁。SDK 是**自动生成的**，基于 Protocol 包中定义的 API Schema。

SDK 提供两种客户端变体：

| 变体 | 用途 | 特点 |
|------|------|------|
| Promise 客户端 | 网络调用 | 零 Effect 依赖，同步构造 |
| Effect 客户端 | 内嵌模式 | 丰富的 Effect 原生值，运行时 Schema 解码 |

```ts
// Promise 客户端示例
const session = await client.session.create()
const message = await client.message.create({
  sessionID: session.id,
  parts: [{ type: "text", text: "Hello" }]
})

// Effect 客户端示例
const program = Effect.gen(function* () {
  const session = yield* client.session.create()
  return session
})
```

### 4.3 流式 Token 的完整路径

当 LLM 生成一个 token 时，它经历的完整路径是：

```text
LLM Provider (OpenAI/Anthropic/etc.)
    │
    │ token chunk
    ▼
OpenCode Server
    │
    │ SSE event: message.part.delta
    ▼
@opencode-ai/sdk (EventSource)
    │
    │ batched events (16ms window)
    ▼
Sync Store (SolidJS createStore)
    │
    │ fine-grained reactive update
    ▼
AssistantMessage Component
    │
    │ re-render only changed text
    ▼
OpenTUI Renderer (60fps)
    │
    │ diff + ANSI escape codes
    ▼
Terminal
```

#### SSE 事件批处理

为了避免过多的 UI 重渲染，OpenCode 实现了事件批处理：

```ts
const events = await sdk.global.event({
  signal: ctrl.signal,
  sseMaxRetryAttempts: 0,
})

for await (const event of events.stream) {
  handleEvent(event)
}
```

如果事件在 16ms 内到达，它们会被批处理到一个 SolidJS `batch()` 中，合并为一次 UI 更新。超过 16ms 的事件则立即处理。

#### Delta 增量更新

核心的 token 流式处理在 Sync Store 中：

```ts
// search 是一个在数组中查找元素的辅助函数
function search<T>(arr: T[], id: string, key: (item: T) => string) {
  const index = arr.findIndex((item) => key(item) === id)
  return { found: index !== -1, index }
}

case "message.part.delta": {
  const parts = store.part[event.properties.messageID]
  if (!parts) break
  const result = search(parts, event.properties.partID, (part) => part.id)
  if (!result.found) break
  setStore(
    "part",
    event.properties.messageID,
    produce((draft) => {
      const part = draft[result.index]
      const field = event.properties.field as keyof typeof part
      const existing = part[field] as string | undefined
      // 增量追加 delta 到现有文本
      ;(part[field] as string) = (existing ?? "") + event.properties.delta
    }),
  )
  break
}
```

每个 delta 事件包含：
- `messageID` — 消息 ID
- `partID` — 消息部件 ID
- `field` — 更新的字段（如 "text" 或 "reasoning"）
- `delta` — 新增的文本片段

SolidJS 的细粒度响应式确保只有受影响的 `<text>` 组件会重新渲染，而不是整个消息列表。

---

## 五、实战：构建你自己的 OpenCode 风格 CLI

### 5.1 技术栈选择

如果你想要构建一个类似的 AI CLI 工具，推荐的技术栈：

```text
Runtime:       Bun
Language:      TypeScript
UI Framework:  SolidJS
TUI Renderer:  @opentui/core + @opentui/solid
AI SDK:        Vercel AI SDK (ai)
Schema:        Zod 或 Effect Schema
Build:         Bun (或 Turborepo 管理 Monorepo)
```

### 5.2 项目结构

```text
my-ai-cli/
├── src/
│   ├── index.tsx              # 入口：创建渲染器、启动应用
│   ├── app.tsx                # 根组件：Provider 树、布局
│   ├── components/
│   │   ├── message.tsx        # 消息渲染（用户/助手/工具调用）
│   │   ├── prompt.tsx         # 输入框（支持 @ 自动补全）
│   │   ├── tool.tsx           # 工具调用展示（可折叠）
│   │   └── status.tsx         # 底部状态栏
│   ├── store/
│   │   └── session.ts         # 会话状态管理
│   ├── api/
│   │   └── llm.ts             # LLM 流式调用
│   └── util/
│       └── markdown.ts        # Markdown 终端渲染
├── package.json
├── tsconfig.json
└── bun.lockb
```

### 5.2.1 依赖配置

创建 `package.json`：

```json
{
  "name": "my-ai-cli",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "bun --watch src/index.tsx",
    "start": "bun src/index.tsx"
  },
  "dependencies": {
    "@opentui/core": "latest",
    "@opentui/solid": "latest",
    "@ai-sdk/openai": "latest",
    "ai": "latest",
    "solid-js": "^1.9.0",
    "glob": "^10.0.0"
  },
  "devDependencies": {
    "typescript": "^5.8.0",
    "@types/bun": "latest"
  }
}
```

### 5.3 核心实现

#### Step 1: 入口文件 `index.tsx`

```tsx
import { createCliRenderer } from "@opentui/core"
import { render } from "@opentui/solid"
import { App } from "./app"

async function main() {
  const renderer = await createCliRenderer({
    targetFps: 60,
    exitOnCtrlC: false,
  })

  await render(() => <App />, renderer)
}

main()
```

#### Step 2: 根组件 `app.tsx`

```tsx
import { createSignal, For } from "solid-js"
import { Message } from "./components/message"
import { Prompt } from "./components/prompt"
import { Status } from "./components/status"
import { streamChat } from "./api/llm"

interface Message {
  role: "user" | "assistant"
  content: string
}

export function App() {
  const [messages, setMessages] = createSignal<Message[]>([])
  const [streaming, setStreaming] = createSignal(false)

  const handleSend = async (text: string) => {
    // 添加用户消息
    setMessages((prev) => [...prev, { role: "user", content: text }])
    setStreaming(true)

    // 流式获取助手回复
    let assistantContent = ""
    for await (const chunk of streamChat(text)) {
      assistantContent += chunk
      // 更新最后一条消息或添加新消息
      setMessages((prev) => {
        const last = prev[prev.length - 1]
        if (last?.role === "assistant") {
          return [
            ...prev.slice(0, -1),
            { ...last, content: assistantContent },
          ]
        }
        return [...prev, { role: "assistant", content: assistantContent }]
      })
    }

    setStreaming(false)
  }

  return (
    <box flexDirection="column" width="100%" height="100%">
      {/* 消息区域 */}
      <box flexGrow={1} flexDirection="column" overflow="hidden">
        <For each={messages()}>
          {(msg) => <Message role={msg.role} content={msg.content} />}
        </For>
        {streaming() && <text color="gray">Thinking...</text>}
      </box>

      {/* 分隔线 */}
      <text color="gray">{"─".repeat(80)}</text>

      {/* 输入框 */}
      <Prompt onSend={handleSend} />

      {/* 状态栏 */}
      <Status model="gpt-4o" tokens={1234} />
    </box>
  )
}
```

#### Step 3: 消息组件 `components/message.tsx`

```tsx
import { createSignal } from "solid-js"

interface MessageProps {
  role: "user" | "assistant"
  content: string
}

export function Message(props: MessageProps) {
  const [expanded, setExpanded] = createSignal(true)

  const prefix = () => (props.role === "user" ? "You" : "AI")
  const color = () => (props.role === "user" ? "green" : "blue")

  return (
    <box flexDirection="column" marginTop={1}>
      {/* 角色标签 */}
      <text bold color={color()}>
        {prefix()}
      </text>

      {/* 消息内容 */}
      {expanded() && (
        <box marginLeft={2} marginRight={2}>
          <text wrap="wrap">{props.content}</text>
        </box>
      )}
    </box>
  )
}
```

#### Step 4: 输入框 `components/prompt.tsx`

```tsx
import { createSignal, createEffect, For } from "solid-js"

interface PromptProps {
  onSend: (text: string) => void
}

export function Prompt(props: PromptProps) {
  const [input, setInput] = createSignal("")
  const [files, setFiles] = createSignal<string[]>([])
  const [showAutocomplete, setShowAutocomplete] = createSignal(false)

  // 监听 @ 触发文件搜索
  createEffect(() => {
    const value = input()
    const atIndex = value.lastIndexOf("@")
    if (atIndex !== -1) {
      const query = value.slice(atIndex + 1)
      // 模糊搜索文件（实际项目中使用 fuzzysort 或类似库）
      searchFiles(query).then(setFiles)
      setShowAutocomplete(true)
    } else {
      setShowAutocomplete(false)
    }
  })

  // 模糊搜索文件的辅助函数（示例实现）
  async function searchFiles(query: string): Promise<string[]> {
    const { glob } = await import("glob")
    const files = await glob("**/*", { ignore: ["node_modules", ".git"] })
    return files
      .filter((f) => f.toLowerCase().includes(query.toLowerCase()))
      .slice(0, 10)
  }

  const handleSubmit = () => {
    const text = input().trim()
    if (text) {
      props.onSend(text)
      setInput("")
    }
  }

  return (
    <box flexDirection="column">
      {/* 自动补全列表 */}
      {showAutocomplete() && files().length > 0 && (
        <box border={true} borderColor="gray" flexDirection="column">
          <For each={files()}>
            {(file) => <text color="cyan">{file}</text>}
          </For>
        </box>
      )}

      {/* 输入框 */}
      <box>
        <text color="green">{"> "}</text>
        <input
          value={input()}
          onInput={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleSubmit()
          }}
          placeholder="Ask anything... (@ for files, / for commands)"
          width="100%"
        />
      </box>
    </box>
  )
}
```

#### Step 5: 流式 LLM 调用 `api/llm.ts`

```ts
import { createOpenAI } from "@ai-sdk/openai"
import { streamText } from "ai"

const openai = createOpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

export async function* streamChat(message: string) {
  const result = streamText({
    model: openai("gpt-4o"),
    messages: [{ role: "user", content: message }],
  })

  for await (const chunk of result.textStream) {
    yield chunk
  }
}
```

#### Step 6: 状态栏 `components/status.tsx`

```tsx
interface StatusProps {
  model: string
  tokens: number
}

export function Status(props: StatusProps) {
  return (
    <box
      flexDirection="row"
      justifyContent="space-between"
      border={true}
      borderTop={true}
      borderColor="gray"
      paddingX={1}
    >
      <text color="gray">Model: {props.model}</text>
      <text color="gray">Tokens: {props.tokens}</text>
      <text color="gray">CWD: {process.cwd()}</text>
    </box>
  )
}
```

### 5.4 运行效果

运行 `bun src/index.tsx`，你将看到一个基本的 AI CLI 界面：

```text
┌──────────────────────────────────────────────────────┐
│                                                      │
│  You                                                 │
│  What is the capital of France?                      │
│                                                      │
│  AI                                                  │
│  The capital of France is Paris.                     │
│                                                      │
│──────────────────────────────────────────────────────│
│ > What is the capital of France?                     │
├──────────────────────────────────────────────────────┤
│ Model: gpt-4o                  Tokens: 1234    ~/project │
└──────────────────────────────────────────────────────┘
```

### 5.5 进阶优化

要达到 OpenCode 的水平，你还需要：

1. **Markdown 渲染**：集成 Shiki 进行语法高亮，使用 `marked` 或 `markdown-it` 解析 Markdown
2. **工具调用**：实现 Bash、Read、Edit 等工具，并在 UI 中展示为可折叠面板
3. **Diff 展示**：使用 `diff` 库生成 unified diff，在终端中用颜色高亮
4. **会话持久化**：使用 SQLite 或 JSON 文件保存会话历史
5. **快捷键系统**：参考 `@opentui/keymap` 实现自定义键位映射
6. **插件系统**：设计 Plugin API，允许社区扩展功能

---

## 六、总结

OpenCode 的架构设计展示了现代终端应用的一种可能范式：

1. **声明式 UI 不是 Web 的专利**：OpenTUI 证明了声明式组件模型可以完美映射到终端，带来更好的开发体验和更流畅的用户交互
2. **Client-Server 分离是正确的抽象**：通过 SDK 作为唯一边界，TUI 和 Server 可以独立演进，支持多种客户端形态
3. **细粒度响应式是性能的关键**：SolidJS 的 Signal 机制让终端 UI 能够高效处理流式数据，避免不必要的重渲染
4. **Monorepo + 类型安全是工程的基础**：Effect Schema + 代码生成确保了从 API 定义到客户端调用的全链路类型安全

如果你正在构建自己的 AI CLI 工具，OpenCode 的架构值得深入研究。它不仅是一个优秀的开源项目，更是一本关于现代终端应用架构的教科书。

---

## 参考资料

- [OpenCode GitHub 仓库](https://github.com/anomalyco/opencode)
- [TUI Package 设计文档](https://github.com/anomalyco/opencode/blob/dev/specs/tui-package.md)
- [TUI 入口实现](https://github.com/anomalyco/opencode/blob/dev/packages/cli/src/tui.ts)
- [TUI 官方文档](https://github.com/anomalyco/opencode/blob/dev/packages/web/src/content/docs/tui.mdx)
- [CLI 文档](https://github.com/dthompsonfl/opencode.tools/blob/main/docs/opencode.official.docs/cli.mdx)
- [OpenTUI 仓库](https://github.com/opentui/opentui)
- [SolidJS 文档](https://www.solidjs.com/)
- [Vercel AI SDK](https://sdk.vercel.ai/)
