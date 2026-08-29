---
layout: post
title: GitHub SSH
display_title: 'Generating and Configuring a GitHub SSH Key'
summary: >
  Quick reference for generating an ed25519 SSH key, adding it to the ssh-agent,
  and configuring it for GitHub authentication on a new machine.
lang: en
date: 2026-06-09 19:56:00
categories:
- Developer Tools
tags:
- Key
- Git
- OS
---

- [Generating a new SSH key and adding it to the ssh-agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

<!--more-->
## Shell Command
  - `ssh-keygen -t ed25519 -C "x@x.com"`

## File Folder
  - `~/.ssh/`
  - `~/.ssh/id_ed25519`
  - `~/.ssh/id_ed25519.pub` 