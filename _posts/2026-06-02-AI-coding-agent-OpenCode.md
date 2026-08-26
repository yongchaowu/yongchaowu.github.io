---
layout: post
title: "AI coding agent-OpenCode"
date: 2026-06-02 07:27:00
categories: ["AI coding agent"]
tags: ["AI coding agent", "Agent", "OpenCode"]
---

- [OpenCode Documentation](https://open-code.ai/en)

<!--more-->
OpenCode is an open-source AI coding assistant that provides intelligent code completion, code generation, and conversational programming experience.

- [repository](https://github.com/opencode-ai/opencode)
- [crush repository](https://github.com/charmbracelet/crush)

A powerful AI coding agent. Built for the terminal. 

OpenCode is a Go-based CLI application that brings AI assistance to your terminal. It provides a TUI (Terminal User Interface) for interacting with various AI models to help with coding tasks, debugging, and more.

---

## Install

- install script: `curl -fsSL https://opencode.ai/install | bash`
- install command
```shell
# Using Homebrew (macOS/Linux)
brew install opencode-ai/tap/opencode
 
# Using npm
npm install -g opencode
 
# Using Go
go install github.com/opencode-ai/opencode@latest
```
- offline install(wget)
    `https://github.com/anomalyco/opencode/releases`

## Start
```shell
cd <project>  # Open directory
opencode      # Run command
```

## Docs

- [opencode docs]( https://opencode.ai/docs)


## Custom Provider 

Config opencode.json to set opencode default model with openai format.

```json
#~/.config/opencode/opencode.json
# "model": "vllm/deepseek-v4-flash" set default model

{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "vllm": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "vLLM本地模型",
      "options": {
        "baseURL": "https://api.deepseek.com/v1",
        "apiKey": "sk-dummpy"
      },
      "models": {
        "deepseek-v4-flash": {
          "name": "deepseek-v4-flash"
        }
      }
    }
  },
  "model": "vllm/deepseek-v4-flash"
}

```
