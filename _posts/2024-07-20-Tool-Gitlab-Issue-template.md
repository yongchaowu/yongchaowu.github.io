---
layout: post
title: Gitlab-Issue-template
date: 2024-07-20 16:32:00
categories:
- Developer Tools
tags:
- GitLab
- Tool
---
创建一个高效的Bug报告Issue模板。
- `.gitlab/issue_templates/bug.md`
---
以下是一个推荐的GitLab Bug Report Issue模板示例。可以根据项目的具体需求调整这个模板：

```markdown
---
title: "[BUG] 简短描述问题"
labels: bug
assignees:

<!--more-->

---

### 描述
请详细描述遇到的错误情况，包括你正在执行的操作、期望的结果与实际发生的结果之间的差异。

### 复现步骤
1. 步骤1
2. 步骤2
3. ...
4. 错误发生

### 期望行为
请清晰地说明你期望系统在上述操作下应如何表现。

### 实际行为
描述实际发生的错误情况或系统反应。

### 系统信息
- **操作系统**: [e.g., Windows 10, macOS Big Sur, Ubuntu 20.04]
- **浏览器版本**(如果适用): [e.g., Chrome 92, Firefox 89]
- **GitLab版本**(如果是在本地部署): [e.g., 14.5.2]
- **其他相关环境信息**: [如Node.js版本、数据库类型和版本等]

### 日志或报错信息
如果有的话，请提供完整的错误消息或相关的日志信息。可以使用代码块(```)包裹以保持格式。

    ```
    错误信息示例
    ```

### 附加信息
- 任何可能有助于解决问题的额外信息、截图或视频。
- 是否有已知的临时解决方案。

### 可能的解决方案建议(可选)
如果你有想法，可以在这里提出可能的解决步骤或根本原因猜测。

---

请确保在提交前检查以上所有信息的完整性，这将极大地帮助团队快速定位并解决问题。感谢你的贡献！
```

将此模板添加到GitLab项目的`.gitlab/issue_templates`目录下，并命名为例如`Bug_report.md`，这样当团队成员或贡献者创建新的Issue时，他们就可以选择并使用该模板来提交详细的Bug报告了。

本文修订依据：GitLab 官方 [Trademark Guidelines](https://handbook.gitlab.com/handbook/marketing/brand-experience/trademark-guidelines/)（政策文本最后修订于 2024-07-03；页面源 commit `4469685d7b8ac40a08f48eb793b75f8143ed690e`，2026-08-27）。本文仅将标题中的 `Gitlab` 更正为官方产品名 `GitLab`，文件名及 Issue 模板内容均保持不变。

> **AI 修改声明：** 本文由 LLM 协助修订，最近修改时间：2026-09-25 15:43（UTC+08:00）。修订仅纠正标题中的 GitLab 品牌大小写。