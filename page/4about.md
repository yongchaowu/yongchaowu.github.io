---
layout: default
title: About
display_title: 'About / 关于'
description: "About Yc.W — C++ backend engineer working across AI agents, LLM applications, and reliable systems."
permalink: /about/
icon: user
type: page
---

<main class="page about-page" id="main-content" tabindex="-1">
    <header class="about-header">
        <div>
            <span class="section-kicker">The person behind the notebook</span>
            <h1>About Yc.W</h1>
            <p>软件工程师，关注 C++ 后端、AI Agent / LLM 应用，以及让复杂系统保持可维护的工程实践。</p>
        </div>
        <div class="about-mark">YC</div>
    </header>

    <div class="about-grid">
        <section class="about-main">
            <h2>Current focus</h2>
            <p>我目前将工作分成三条相互连接的主线：</p>
            <div class="about-focus-grid">
                <article><span>01</span><h3>C++ Backend</h3><p>工业数据采集、仿真系统、行为模型、跨平台应用和后端服务。</p></article>
                <article><span>02</span><h3>AI Agent / LLM</h3><p>模型调用、RAG、Agent 工作流、推理服务、工具权限和生产化部署。</p></article>
                <article><span>03</span><h3>Reliable Delivery</h3><p>Linux、Docker、Git/GitLab、数据库、测试、诊断和可回滚发布。</p></article>
            </div>

            <h2>Experience</h2>
            <div class="about-timeline">
                <article><time>2023 — 2025</time><div><h3>C++ Backend · Simulation & Behavior Systems</h3><p>参与仿真框架、行为模型、Behavior Tree、C++11 / CMake / Linux、MySQL / SQLite、Docker 和 PyBind11 集成。</p></div></article>
                <article><time>2017 — 2021</time><div><h3>C++ Backend · Industrial Systems</h3><p>参与传感器、PLC、控制器通信、工业协议解析、IO 服务和跨平台数据采集软件。</p></div></article>
            </div>

            <h2>About this site</h2>
            <p>这是一个持续生长的工程笔记本。精选文章负责把历史资料重新组织成今天可读的路径；历史文章则保留当时的语境、来源和链接。涉及旧版本、驱动、部署和安全操作时，页面会尽量明确标注来源状态和风险。</p>
            <div class="about-links"><a class="button button--primary" href="{{ '/start-here/' | relative_url }}">Start reading</a><a class="button button--quiet" href="https://github.com/yongchaowu" target="_blank" rel="noopener">GitHub ↗</a></div>
        </section>
        <aside class="about-side">
            <div class="side"><div>Currently using</div><ul class="content-ul"><li>Linux · CMake · Docker</li><li>Python · vLLM · Ray</li><li>Git / GitLab · MySQL / SQLite</li><li>BehaviorTree · C++</li></ul></div>
            <div class="side"><div>Elsewhere</div><ul class="content-ul"><li><a href="https://github.com/yongchaowu" target="_blank" rel="noopener">GitHub ↗</a></li><li><a href="https://www.cnblogs.com/yongchao" target="_blank" rel="noopener">博客园 ↗</a></li><li><a href="mailto:{{ site.email }}">Email ↗</a></li></ul></div>
        </aside>
    </div>
</main>
<script src="{{ '/js/pageContent.js' | relative_url }}" charset="utf-8"></script>
