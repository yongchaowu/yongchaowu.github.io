---
layout: post
title: "Tool-Gitlab-CICD-jobs-删除或清空"
date: 2024-07-20 16:31:00
categories: ["Tool"]
tags: ["GitLab", "Tool"]
---

清空GitLab项目中所有的CI/CD Jobs列表或者说是清除Pipeline的历史记录，可以通过GitLab的Web界面或者API来实现。
注意：会删除Pipeline的记录和相关联的Job日志、Artifacts等信息，操作前请确保已经做好相应数据的备份。

<!--more-->
## 通过Web界面清空

1. 登录到GitLab。
2. 导航到项目。
3. 点击左侧菜单栏的“CI/CD” > “Pipelines”。
4. 在Pipelines页面，可以看到所有历史Pipeline的列表。GitLab目前没有直接提供一键清空所有Pipelines的选项，但可以手动逐个删除Pipeline。每个Pipeline右侧会有个垃圾桶图标，点击它即可删除相应的Pipeline及其包含的所有Jobs。如果Pipeline数量非常多，这个方法可能会比较耗时。

## 通过API清空

GitLab提供了API来管理Pipeline，包括删除Pipeline。以下是一个使用`cURL`命令通过API删除所有Pipeline的例子：

```bash
GITLAB_TOKEN="your_access_token"
PROJECT_ID="your_project_id"

# 获取所有Pipeline的ID
pipelines=$(curl --silent --header "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://gitlab.example.com/api/v4/projects/$PROJECT_ID/pipelines" | jq -r '.[].id')

# 遍历并删除每个Pipeline
for pipeline_id in $pipelines; do
 curl --request DELETE --silent --header "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://gitlab.example.com/api/v4/projects/$PROJECT_ID/pipelines/$pipeline_id"
done
```

**注意**：
- 替换`your_access_token`和`your_project_id`为实际的值。
- 上述脚本使用了`jq`工具来解析JSON输出，确保系统中安装了`jq`。
- 执行删除操作前请三思，因为删除的数据无法恢复。
- 如果GitLab实例使用的是自定义域名，请将`gitlab.example.com`替换为实际的域名。

使用API批量删除是更高效的方式，但同时也需要更加小心，以免误删重要数据。
