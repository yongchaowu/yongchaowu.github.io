---
layout: post
title: "批量关掉 fork 的 Actions：6 个 API 机制，外加\"为什么 fork 本来就在跑 CI\""
display_title: "批量关掉 fork 的 Actions：6 个 API 机制，外加\"为什么 fork 本来就在跑 CI\""
summary: "用一条 gh api 关掉单个仓库的 Actions 很容易，批量关掉全部 fork 却有 6 个坑：-f 发字符串会 422、成功返回 204 空 body 不能 jq、漏掉 --paginate 会静默截断、网络 EOF 会打断循环、204 不带状态必须回读、/users 端点漏掉全部私有库。本文还回答一个更根本的问题：为什么 fork 的公有仓库本来就在跑 workflow，以及关掉之后为什么还会收到失败邮件、到底谁在吃 Actions 额度。"
lang: zh-CN
date: 2026-09-27 09:00:00
categories:
  - DevOps & Infrastructure
  - Developer Tools
tags:
  - "GitHub"
  - "gh-cli"
  - "GitHub Actions"
  - "REST API"
  - "Shell"
  - "Bash"
  - "运维"
  - "踩坑"
  - "成本"
---

<!--more-->

GitHub 仓库设置里有个 "Actions" 开关，关掉它就不跑 CI 了。对应的 REST 接口是
[Set GitHub Actions permissions for a repository](https://docs.github.com/rest/actions/permissions)，
用 `gh` 一行就能调：

```bash
gh api --method PUT /repos/OWNER/REPO/actions/permissions -F enabled=false
```

单仓库一条命令，本来没什么可写的。但一个做技术笔记的账号很容易攒下**几十个 fork**
（本文的实测样本是 85 个 fork / 99 个自营仓库），一个个敲就是 85 次手动劳动，
于是问题变成：**怎么用一条命令把它们全关掉。**

看起来只需要一个循环，但真正坑人的地方有 6 个，其中一个会让你**以为成功了、其实一个仓库都没关**。
而在你动手之前，还有一个更根本的问题没被回答：**这些 fork 凭什么在跑 CI？**

本文分三部分：先把批量关闭的 6 个机制讲透，再回答"为什么 fork 本来就在跑 workflow"，
最后说清"关掉之后还会发生什么"和"谁在吃 Actions 额度"。

> 本文所有数字来自一个已匿名的真实账号的实测（样本规模：99 个自营仓库 / 85 个 fork，
> 账单周期内 276 次运行）。仓库名、账号名一律用 `OWNER` / `REPO` 代指，
> 结论本身与具体项目无关。

---

## 第一部分：批量关闭的 6 个机制

### 一、先说结论：原始命令里的 `-f` 是错的

如果你照直觉写成小写 `-f`：

```bash
gh api --method PUT /repos/OWNER/REPO/actions/permissions -f enabled=false
```

它会返回 422：

```
gh: Invalid request.

For 'properties/enabled', "false" is not a boolean. (HTTP 422)
```

原因是 `gh` 的两个字段开关语义完全不同，这是第一个机制。

### 机制 1：`-f` 发字符串，`-F` 才做类型转换

| 开关 | 全称 | 行为 | `false` 发出去是什么 |
|---|---|---|---|
| `-f` | `--raw-field` | 原样加一个**字符串**参数 | `"false"` —— JSON 字符串 |
| `-F` | `--field` | 自动推断类型后加参数 | `false` —— JSON 布尔值 |

`-F` 的类型推断规则是：`true` / `false` → 布尔值，纯数字 → 数字，数组/对象按 JSON 解析，
`null` → 空值，其余按字符串。

而这个接口的 OpenAPI 定义要求 `enabled` 是 `boolean`，所以字符串 `"false"` 直接被
JSON Schema 校验挡下来。**注意这个 422 是"类型校验"错误，不是"参数缺失"错误**——
参数名和值都"对"，只是类型不对，所以报错信息看着很像"你写错了"，
实际上把 `-f` 换成 `-F` 就好了。

> 这个坑很隐蔽：如果你用浏览器控制台，或者 `curl -X PUT -d '{"enabled":false}'`，
> 是不会有问题的——只有 `gh` 的小写 `-f` 会踩到。

### 二、成功的时候，stdout 是**空的**

`-F` 跑通了，但如果你想确认结果，会发现第二个问题。

### 机制 2：成功是 `204 No Content`，响应体 0 字节

实测：

```console
$ out=$(gh api --method PUT /repos/OWNER/REPO/actions/permissions -F enabled=false 2>&1)
$ echo "exit=$? stdout_bytes=${#out}"
exit=0 stdout_bytes=0
```

`gh` 帮你在 stdout 上加了 `204` 状态行，但 **body 本身是空的**——这个接口不回传
`{"enabled": false}`。

所以下面这些确认写法全部无效：

```bash
# ✗ 什么都不输出，jq 收到空输入
gh api --method PUT ... -F enabled=false | jq .enabled

# ✗ 条件永远为假，脚本判定"失败"
[[ "$(gh api --method PUT ... -F enabled=false | jq -r .enabled)" == "false" ]]

# ✗ jq 报 parse error，退出码非 0
gh api --method PUT ... -F enabled=false | jq .enabled
```

想读状态只能再发一个 `GET`：

```bash
$ gh api /repos/OWNER/REPO/actions/permissions
{"enabled":false,"sha_pinning_required":false}
```

> 一个容易被误传开的说法是"gh 出错时退出码是 0"。**实测不是**：HTTP 错误时
> 422 和 404 的退出码都是 **1**，所以脚本里 `if gh api ...; then` 是可靠的判断方式，
> 不必去 grep 错误消息。真正让这个 bug 藏得深的是另一件事——**错误信息走 stderr**，
> 只捕获 stdout 的管道会完全看不到它。
>
> 但 204 空 body 仍然要求你额外做一次 `GET`：退出码只能告诉你"没报错"，
> 告诉不了你"状态已经变成你要的样子"。

### 三、最危险的一个：漏掉 `--paginate`

批量操作的第一个动作是"列出所有 fork"，这里有个静默截断。

### 机制 3：没有 `--paginate` 就只返回一页，且**不报错**

实测（账号共 99 个自营仓库、85 个 fork）：

| 调用 | 拿到的条数 |
|---|---|
| `per_page=100`，不带 `--paginate` | 99 ✅ 刚好装下 |
| `per_page=30`，不带 `--paginate` | **30** ❌ 静默少了 69 |
| `per_page=30`，带 `--paginate` | 90（第 4 页时撞上网络 EOF，见机制 4）|

`per_page=100` 那行能拿到 99 纯属**运气**——这个账号仓库数刚好 < 100。
换个人、或者过几个月再跑，仓库数一过 100 就会开始**静默丢仓库**：
API 不返回错误，只是少给你一页，然后你的循环就只处理了前 N 个。

配套还有一个误读，而且它有两种形态，都要小心：

```bash
# ✗ 形态一：length 拿到的是"每一页"的长度，不是总数
#         换 per_page 就变成 30，不能当总数用
gh api --paginate "/user/repos?per_page=100" --jq 'length'

# ✗ 形态二：更隐蔽——响应是个对象 {total_count, workflow_runs}，
#         对"对象"取 length 得到的是**键的个数**（= 2），不是数组长度。
#         这个坑会让你以为"还有 2 个任务在跑"，实际上一个都没有。
gh api "/repos/OWNER/REPO/actions/runs?status=in_progress" --jq 'length'
```

**判断数量一律用 `.total_count`，不要用 `length`：**

```bash
# ✅ 计数
gh api "/repos/OWNER/REPO/actions/runs?status=in_progress" --jq '.total_count'

# ✅ 摊平后自己数
gh api --paginate "/user/repos?per_page=100&affiliation=owner" \
  --jq '.[].full_name' | wc -l      # 99
```

### 四、网络会突然 EOF

### 机制 4：单次请求可能报 `unexpected EOF`，需要重试

批量跑 85 次请求，中间偶发断连是常态。本次实测就撞到两次：

```
Get "https://api.github.com/repos/OWNER/REPO/actions/permissions": EOF
Get "https://api.github.com/user/repos?per_page=30&affiliation=owner&page=4": unexpected EOF
```

危险的地方在于：假设循环跑到第 23 个仓库时来一次 EOF，而脚本没做重试也没记录，
那么你会得到一个**改了一半**的账号——前 22 个已关、62 个照旧跑，
而如果没有校验输出，这个半成品状态会被直接误当成"跑完了"。

所以批量写操作必须：**(a) 重试**，**(b) 记录哪些失败了**，**(c) 结束后独立回读校验**。

### 五、正确的完整流程

把上面 4 点合起来，加上"批量写必须回读校验"这条通用原则，得到最终脚本：

```bash
#!/usr/bin/env bash
# disable_actions.sh —— 关掉 $1 名下所有 fork 的 GitHub Actions
OWNER="${1:-$(gh api user --jq .login)}"
ok=0; fail=0; failed_list=()

# 机制 3：--paginate 必须带，否则超过 per_page 就静默截断
# 机制 6：枚举"当前账号"用 /user/repos（含私有库）；
#         换成 /users/<owner>/repos 会漏掉全部私有库，见下文
mapfile -t repos < <(
  gh api --paginate "/user/repos?per_page=100&affiliation=owner" \
    --jq '.[] | select(.fork == true) | .full_name'
)

echo "owner=$OWNER  forks=${#repos[@]}"
(( ${#repos[@]} == 0 )) && { echo "没有找到 fork，检查登录状态"; exit 1; }

for r in "${repos[@]}"; do
  done_ok=0
  # 机制 4：EOF / 临时故障重试 3 次，退避 2s / 4s / 6s
  for attempt in 1 2 3; do
    # 机制 1：-F（大写）才发布尔值；-f 发字符串会 422
    # 机制 2：成功是 204 + 空 body，jq 读不到状态，必须再 GET 一次
    if err=$(gh api --method PUT "/repos/$r/actions/permissions" -F enabled=false 2>&1); then
      state=$(gh api "/repos/$r/actions/permissions" --jq '.enabled' 2>/dev/null)
      if [[ "$state" == "false" ]]; then
        done_ok=1; break
      fi
      err="PUT 返回 204 但回读得到 enabled=$state"
    fi
    sleep $((attempt * 2))
  done

  if [[ $done_ok -eq 1 ]]; then
    ok=$((ok+1)); printf 'ok    %-55s enabled=false\n' "$r"
  else
    fail=$((fail+1)); failed_list+=("$r")
    printf 'ERR   %-55s -> %s\n' "$r" "$(printf '%s' "$err" | head -1)"
  fi
done

echo "----"
echo "disabled_ok=$ok  failed=$fail"
(( ${#failed_list[@]} )) && printf 'failed: %s\n' "${failed_list[@]}"

# 机制 5：脚本自报成功不算数，跑完后独立再全量回读一遍
echo "==== 独立复核 ===="
still_on=0
for r in "${repos[@]}"; do
  if [[ "$(gh api "/repos/$r/actions/permissions" --jq '.enabled' 2>/dev/null)" != "false" ]]; then
    printf 'STILL-ON  %s\n' "$r"; still_on=$((still_on+1))
  fi
done
echo "still_enabled=$still_on / ${#repos[@]}"
```

### 机制 5：写操作的成功要靠**独立回读**确认，不靠脚本自己说

批量脚本里 `ok=85` 是脚本**自认为**成功。中间可能出现过"PUT 报错了但被重试吞掉"、
"枚举列表不完整所以压根没轮到这个仓库"、"回读那次请求本身又 EOF 了导致 `state` 为空"——
这些都会让计数好看但状态不对。

所以最后必须**另起一轮、不依赖写入逻辑的纯读**再核对一遍：

```bash
# 独立复核：完全不走上面的写入逻辑，纯 GET
while read -r r; do
  gh api "/repos/$r/actions/permissions" --jq '"enabled=\(.enabled)"' | sed "s|^|$r |"
done < forks.txt > perms_after.txt

awk '{print $2}' perms_after.txt | sort | uniq -c    # 期望：全 enabled=false
grep -v 'enabled=false' perms_after.txt             # 期望：无输出
```

**只信 GET，不信 PUT。**

### 六、枚举端点选错，会漏掉全部私有库

还有一个在写文档时容易被想当然的坑：想"指定用户名"，很自然会写成
`/users/<owner>/repos`。实测这个端点**不返回该用户的任何私有库**：

```console
$ gh api --paginate "/user/repos?per_page=100&affiliation=owner"  --jq '.[].full_name' | sort -u | wc -l
99          # ← 激活账号名下全部仓库
$ gh api --paginate "/users/OWNER/repos?per_page=100"            --jq '.[].full_name' | sort -u | wc -l
93          # ← 少 6 个
$ gh api "/users/OWNER/repos?per_page=100" --jq '[.[] | select(.private==true)] | length'
0           # ← 该端点从不返回私有库
```

少的 6 个逐个查都是 `private=true`。而且**加参数也救不回来**——
`type=owner` / `type=all` / `visibility=all` 三个都试过，一律还是 93。

所以正确的分工是：

| 需求 | 用哪个端点 | 私有库 |
|---|---|---|
| 枚举**当前登录账号**的仓库（绝大多数场景） | `/user/repos?affiliation=owner` | ✅ 包含 |
| 枚举**别人**的仓库 | `/users/<owner>/repos` | ❌ 一律不含 |

想让脚本的 `$OWNER` 参数既真实生效、又不丢私有库，就用
`OWNER="${1:-$(gh api user --jq .login)}"` 把登录名取出来**仅用于打印和校验**，
查询仍然走 `/user/repos`。

> 本次侥幸没出事，是因为这 85 个 fork **恰好全是 public**（实测私有 fork 数量 = 0），
> 两个端点给出的 fork 集合完全一致。但这是运气，不是设计——一旦 fork 里有私有仓库，
> 用 `/users/` 端点就会静默漏掉它们。

---

## 第二部分：为什么 fork 的公有仓库本来就在跑 workflow

批量关只是手段。真正该问的是：**这些 fork 凭什么在消耗 runner？**
答案分四层，而且官方文档里都写着，只是很少有人把它和"我 fork 了一个仓库"联系起来。

### 七、fork 是一个完整独立的仓库，不是只读镜像

GitHub 官方文档在
[Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
里的原话是：

> Workflows don't run in forked repositories **by default**. You must enable GitHub Actions
> in the Actions tab of the forked repository.

以及
[Disabling and enabling a workflow](https://docs.github.com/actions/managing-workflow-runs/disabling-and-enabling-a-workflow)：

> When a public repository is forked, **scheduled workflows are disabled by default**.

注意这两句里的 **by default**。这是 fork 那一刻的**一次性初始状态**，不是一条持续生效的规则。
一旦 Actions 在这个 fork 上被启用过，它就变成了一个普通的、完整的仓库：

- 有自己的默认分支；
- 有自己的 `.github/workflows/`；
- 有自己的 Actions 开关、runner 配额、失败邮件。

**`fork` 字段记录的只是"代码从哪来"这条血缘，它不是一个"只读 / 不许跑 CI"的标记。**

### 关键点：`schedule:` 是**文件属性**，不是上游属性

这是整件事的根源。fork 会把上游的 `.github/workflows/*.yml` **连同里面的
`schedule: - cron: ...` 一起复制过来**，而这些 YAML 文件里**没有任何字段**
标注"这条 cron 属于上游，只在 upstream 跑"。

于是 GitHub 的调度器照常在**你的 fork 的默认分支上**执行这些 cron——
它既不知道、也不关心这份配置是谁写的。实测样本里：

| 统计项（账单周期内） | 数量 |
|---|---|
| 有运行记录的 fork | 30 |
| 其中含 `schedule`（cron）触发的 | **16** |
| 典型 fork 的运行构成 | `push=13, schedule=28`（cron 占多数）|
| 纯 cron、一次 push 都没有的 fork | 至少 1 个（`schedule=11, push=0`）|

所以一个你只是"存下来备查"的 fork，和一个你真正在参与开发的仓库，
在 GitHub 眼里**没有任何区别**——它的 cron 照跑不误。

### 八、GitHub 的 60 天自动禁用，被你自己的 push 抵掉了

看到"scheduled workflows are disabled by default"之后，很自然会以为：
过一阵子它们自己就停了。**并不会。** 同一份文档接着说：

> In a public repository, scheduled workflows are **automatically disabled when no
> repository activity has occurred in 60 days**.

这是 GitHub 为避免"无人维护的 fork 白烧 runner"加的兜底开关。但它有个关键前提：
**"repository activity" 指的是 commit / push，不包含 cron 自己跑起来。**

也就是说，如果一个仓库的"心跳"只有 cron 自己，60 天后必然被自动禁用。
**而只要你还在往 fork 里推代码，这个 60 天计时器就会被反复重置，cron 于是可以无限期活着。**

实测样本恰好命中了这个最坏组合——30 个有运行记录的 fork，
`pushed_at` **全部落在最近两天内**：

```
某 C 库 fork      push=2026-09-25   push=13, schedule=28
某编译器项目 fork push=2026-09-26   push=16, schedule=27
某前端框架 fork   push=2026-09-26   push=8,  schedule=28
某 CI 桌面应用    push=2026-09-26   schedule=11  (push=0)
```

结论：**GitHub 那个 60 天保护机制，恰恰是被"我定期同步上游"这个正常习惯给废掉的。**
它拦得住"躺了 60 天的僵尸 fork"，拦不住"活跃但从不为 CI 付账"的 fork。

> 顺带一提，社区里常见的"保活"做法（定期自动提交一个空 commit / 调一次 API
> 刷新活动时间）正是拿这个计时器做文章——它对**想让 cron 活下去**的人有用，
> 对你恰恰是反效果。

### 九、公有仓库的分钟数是免费的，所以没有任何信号

这是"为什么一直没人发现"的原因。**GitHub 托管 runner 对公有仓库不计费**，
所以这些 fork 烧的是 GitHub 自己的免费额度。实测账单周期内的消耗：

| 仓库类型 | 运行次数 | 原始 job 分钟 | 计费 |
|---|---|---|---|
| 公有 fork（重 CI 那种） | 41 | ~1,191 | **0** |
| 公有 fork（前端/工具类） | 38 | ~176 | **0** |
| 公有 fork（编译器那种） | 43 | ~43 | **0** |

**一分钱没花。** 没有账单、没有预算告警、没有超额邮件。
唯一的副作用就是**失败邮件**——所以"邮箱里堆满 fork 的 CI 失败通知"是这件事
唯一可见的症状，很容易被当成噪音直接归档掉。

### 但这不是安全问题

fork 场景下 GitHub 有两道隔离，需要说清楚以免过度担心：

- **secrets 不会传给 runner**——除了 `GITHUB_TOKEN`，fork 中的 workflow 拿不到任何 secret；
- **fork PR 里的 `GITHUB_TOKEN` 是只读的**——推不了东西、也改不了设置。

所以这些 cron 唯一的后果是**烧公共 runner 和发邮件**，不会泄露你的凭据。
需要担心的不是安全，是**信噪比**：真正重要的那个私有仓库的失败邮件，
被 85 个 fork 的噪音埋掉了。

---

## 第三部分：关掉之后

### 十、Actions 关闭**不会**中止已经在跑的 run

这是最容易产生"我明明关了，怎么还在跑"困惑的地方，也是本文唯一一个
**顺序敏感**的坑。

上面那个 204 空 body 的接口，只阻止**新的** workflow 运行。
**已经在排队或执行中的 run 完全不受影响**，它会一直跑到自己结束。

实测撞到的实例：

| 时刻 | 事件 |
|---|---|
| 16:26:17 | 某个密码学库 fork 的 `valgrind` 定时任务被 cron 触发，开始排队 |
| 16:26:25 | job 真正开始执行，配置、编译（`make`）全部成功 |
| 16:30:32 | 进入 `make test`（该库的全量测试套件） |
| **~17:51** | **本脚本把这个 fork 的 Actions 关掉了，并回读确认 `enabled=false`** |
| 17:50:58 | `make test` 失败（跑了 **84 分钟**） |
| 17:51:01 | run 报告 `failure`，GitHub 发出失败邮件 |

**测试在关闭动作之前就已经失败了**，邮件与关闭动作几乎同时到达纯属巧合。
但顺序关系值得记住：**关闭 Actions ≠ 停机，要停机得显式 cancel。**

### 正确的"彻底停"是两件事

```bash
# 1) 先看有没有在跑的（用 .total_count，不要用 length，见机制 3）
gh api "/repos/OWNER/REPO/actions/runs?status=in_progress" --jq '.total_count'
gh api "/repos/OWNER/REPO/actions/runs?status=queued"       --jq '.total_count'

# 2) 有就逐个取消
gh api "/repos/OWNER/REPO/actions/runs?status=in_progress" --jq '.workflow_runs[].id' \
  | xargs -r -I{} gh api --method POST /repos/OWNER/REPO/actions/runs/{}/cancel

# 3) 再关开关，阻止后续 cron
gh api --method PUT /repos/OWNER/REPO/actions/permissions -F enabled=false
```

**顺序建议先 cancel 再关开关**：先关开关的话，cancel 之前可能又冒出新的排队 run。
两个数都是 0 时 cancel 是空操作，不用担心误伤。
（本文样本在收尾时全量扫过 `in_progress / queued / waiting / requested / pending`，均为 0。）

### 这些"跑很久的失败"通常不是 Actions 的问题

顺便说清那个 84 分钟的失败：它的每一个 job 步骤都有明确结论——
`checkout` 成功、`install valgrind` 成功、`configure` 成功、`make` 成功，
**只有 `make test` 失败**。也就是说 fork 里的代码/测试本身有问题，
和权限开关毫无关系。同一天另一个 `run-checker` 类任务里的一个 `*_debug` 矩阵 job
也是挂在 `make test` 这一步。

**判断"是不是我关 Actions 关出来的"，看失败落在哪一步**：
如果卡在 `Set up job` / `checkout` 之类的前置步骤，才可能和权限或配额有关；
如果前面全绿、挂在测试步骤，那就是仓库自己的问题。

### 十一、那到底是谁在吃额度

既然公有 fork 免费，那"免费额度耗尽"必然来自**私有仓库**。
实测样本的私有仓库消耗（账单周期内）：

| 仓库 | 可见性 | Linux (×1) | Windows (×2) | macOS (×10) | 计费合计 |
|---|---|---|---|---|---|
| 私有库 A | private | 1,042 | 193 → 386 | 33s | **1,428** |
| 私有库 B | private | 21 | — | — | **21** |
| 其余 4 个私有库 | private | 0 | — | — | 0 |

### 三个必须知道的计费规则

1. **只有私有仓库计费**，公有仓库（含公有 fork）分钟数免费。
2. **runner 有倍率**，同一个 job 跑在不同 OS 上 costs 不一样：
   **Linux ×1、Windows ×2、macOS ×10**。一个"跑 1 分钟的 macOS 构建"等于 10 分钟 Linux。
3. **倍率只在私有仓库上有意义**——公有仓库直接免费，不进倍率计算。

第 2 条是最容易踩的：上面那个私有库 A 的 CI 里有个 macOS 构建 job，
这次只跑了 33 秒所以几乎没进账单，**但它是一颗定时炸弹**——
哪天 macOS 构建慢 1 分钟，账单就 +10。

### 按倍率算账，别用原始 job 分钟

想知道真实账单，必须按 OS 加权。用 `jq` 算很容易出错（`fromdateiso8601`
的差值 + `add` 的优先级组合很容易写歪，量级能差几十倍），
**建议直接用 Python，并且拿手算抽查一两个 run 对一下**：

```python
import json, subprocess, datetime as dt

def gh(*a):
    r = subprocess.run(["gh", "api", *a], capture_output=True, text=True)
    return json.loads(r.stdout) if r.returncode == 0 else None

def ts(s): return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

MULT = {"Linux": 1, "Windows": 2, "macOS": 10}

def which(labels):
    # runner labels 形如 ubuntu-latest / windows-latest / macos-latest
    for x in labels or []:
        x = x.lower()
        if x.startswith("macos"):   return "macOS"
        if x.startswith("windows"): return "Windows"
        if x.startswith(("ubuntu", "linux")): return "Linux"
    return "Linux"

repo, since = "OWNER/REPO", "2026-09-01"
runs = gh(f"/repos/{repo}/actions/runs?created=%3E={since}&per_page=100") or {}
raw, by_os, weighted = 0, {}, {}
for wr in runs.get("workflow_runs", []):
    jobs = gh(f"/repos/{repo}/actions/runs/{wr['id']}/jobs?per_page=100") or {}
    for j in jobs.get("jobs", []):
        if not (j.get("started_at") and j.get("completed_at")):
            continue
        m = int((ts(j["completed_at"]) - ts(j["started_at"])).total_seconds() // 60)
        os_ = which(j.get("labels"))
        raw += m
        by_os[os_] = by_os.get(os_, 0) + m
        weighted[os_] = weighted.get(os_, 0) + m * MULT[os_]

print(f"raw={raw}  billed={sum(weighted.values())}")
for o in sorted(by_os):
    print(f"  {o:<8}{by_os[o]:>8} min  x{MULT[o]:<3} -> {weighted[o]}")
```

> 注意 `labels` 字段给的是 `ubuntu-latest` / `windows-latest` / `macos-latest`，
> **不是** `Linux` / `Windows` / `macOS`。直接拿 `Linux` 去匹配会全部落空、
> 静默按 ×1 计算——macOS 的 10 倍就这么被漏掉了。

### 想看官方账单，token 需要额外 scope

账户级 Actions 账单接口是：

```bash
gh api "/users/OWNER/settings/billing/actions"
```

但它**需要 `user` scope**，普通 `repo` / `workflow` scope 的 token 会拿到：

```
This API operation needs the "user" scope.
To request it, run:  gh auth refresh -h github.com -s user
```

`gh auth refresh` 会触发浏览器重新授权，属于改动本地凭据的动作，
**应该由你自己决定要不要做**，不适合被脚本悄悄执行。拿不到账单时，
上面的加权统计是最好的替代。

### 十二、一份排查清单

遇到"fork 在跑 CI / 额度好像用得比想象快"时，按这个顺序查：

```bash
# 1. 现在有没有在跑的？（用 total_count）
for s in in_progress queued waiting; do
  echo -n "$s: "
  gh api "/repos/OWNER/REPO/actions/runs?status=$s" --jq '.total_count'
done

# 2. 这个 fork 到底是被什么触发的？（看 event 分布，schedule=cron）
gh api "/repos/OWNER/REPO/actions/runs?created=%3E=2026-09-01&per_page=100" \
  --jq '[.workflow_runs[].event] | sort | group_by(.) | map({e: .[0], n: length})'

# 3. 最近一次 push 是什么时候？（决定 60 天计时器有没有被重置）
gh api "/repos/OWNER/REPO" --jq '.pushed_at'

# 4. Actions 开关状态
gh api "/repos/OWNER/REPO/actions/permissions"
```

几条经验：

- **event 是 `schedule` 就跟你的代码无关**，那是上游的 cron，跟 fork 血缘一起搬过来的；
- **`pushed_at` 很新 = 60 天保护已失效**，cron 会一直跑；
- **额度问题只可能出在私有仓库**，公有 fork 不计费；
- **关 Actions 不停机**，要停得先 `cancel`；
- **`length` 不可信**，计数一律用 `.total_count`。

---

### 总结

**第一部分（怎么关）**，批量关 85 个 fork 的成本在 6 个机制上：

1. **`-f` 发字符串、`-F` 才转类型** —— `-f` 一律 422，而错误信息说"不是布尔值"，
   很容易让人以为是参数写错而不是大小写选错；
2. **成功返回 204 + 空 body** —— 任何试图从 PUT 响应里读状态的写法都会失败，
   只能回落到一次 `GET`（注意 `gh` 出错时退出码是 1，错误信息走 stderr）；
3. **漏掉 `--paginate` 会静默截断** —— 不报错，只是少给一页；`per_page=100` 时能用纯属
   仓库数恰好 < 100 的运气。而 `length` 无论对数组还是对对象都不可信，计数用 `.total_count`；
4. **网络会中途 EOF** —— 一次断连就把账号改成"改了一半"的状态，
   批量写必须重试 + 记失败 + 收尾复核；
5. **成功与否要靠独立回读判定** —— 脚本自己数出来的 `ok=85` 不可信，
   最后要另起一轮纯 `GET` 核对 `still_enabled=0`；
6. **枚举端点选错会丢全部私有库** —— `/users/<owner>/repos` 恒不返回私有库，
   枚举自己名下要用 `/user/repos`，且这个坑在"全是 public fork"的账号上完全看不出来。

**第二部分（为什么它们在跑）**，一句话是**`schedule:` 属于 workflow 文件，不属于上游仓库**：

7. fork 是完整独立的仓库，Actions 的"默认关闭"只在 fork 那一刻生效一次；
8. 上游的 cron 表达式随文件一起复制过来，YAML 里没有任何标记说它属于上游；
9. GitHub 那个"公有仓库 60 天无活动自动禁用 cron"的兜底，被你**自己的 push 反复重置**，
   于是 cron 可以无限期活着；
10. 公有仓库分钟数免费，所以既不花钱也没告警，唯一症状就是失败邮件；
    好在 fork 里不传 secret、`GITHUB_TOKEN` 只读，**不构成安全风险**。

**第三部分（关完之后）**：

11. 关闭 Actions **不中止已在运行的 run**——实测一条定时任务在关闭后又跑了 84 分钟才失败，
    要停机必须显式 `cancel`，且建议先 cancel 再关开关；
12. 额度只可能烧在**私有仓库**上，且 runner 有 **Linux ×1 / Windows ×2 / macOS ×10** 倍率，
    对账要按 OS 加权、并注意 `labels` 给的是 `ubuntu-latest` 这类值而非 `Linux`。

**总的一句话**：`schedule` 跟着文件走、不跟着血缘走；公有 fork 烧的是 GitHub 的钱所以没人拦你；
而真正要盯的账单在私有仓库里，且关开关不等于停机——
**先 cancel，再关开关，最后回读确认。**
