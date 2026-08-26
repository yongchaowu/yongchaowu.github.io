---
layout: post
title: Markdown-表格嵌套
date: 2020-10-24 21:12:00
categories:
- Developer Tools
tags:
- Tool
- Markdown
---

October 24, 2020 8:48 PM

<!--more-->
Markdown的基本表格是没办法实现多层嵌套的，如合并的单元格显示问题。

## 简单形式 语法、效果及对齐
如下是简单形式：
| column1 | column2 |
|--------|--------|
|        |        |

效果：

| column1 | column2 |
|--------|--------|
|        |        |

此外":"可以设置对齐方式。

**以上的格式很难书写，可以用[TableConvert](https://tableconvert.com/) 格式化内容.**

## 解决方案 使用html的`<table>`实现
具体涉及：`<tr>`、`<td>`、`<th>`以及最重要的`<th rowspan="xxx"></th>`、`<th colspan="xxx"></th>`
辅助处理转换方法：[Excel到HTML的无格式表转换器](http://pressbin.com/tools/excel_to_html_table/index.html)
具体细节可参照: [Markdown之表格的处理](https://www.ituring.com.cn/article/3452)

以上设置 在`Algorithm-Sort-时间复杂度与空间复杂度及稳定性`中使用。

## 对于html的使用总结
**以下摘自https://www.ituring.com.cn/article/3452**
1.将第一个 `<table>`变成`<table class="table table-bordered table-striped table-condensed">`
给表格带上某种样式，如果没有的话，比较不好看：
table-bordered：带圆角边框和竖线
table-striped：奇偶行颜色不同
table-condensed：压缩行距
以上三个可以进行不同的组合，如果是很长的表格，建议只用后两个.

2.如果需要表头跟内容不一样，可以将`<td>表头内容</td>`换成`<th>表头内容</th>`.
3.如果表格内文需要换行，可以在要换行的内容后加入`<br>`，后面的内容就会跑到下一行.
4.如果内文中有代码，需要特别显示，可使用：`<code>代码</code>`.
5.如果表格中有需要设为斜体的内容，可使用：`<I>要设为斜体的内容</I>`.
6.如果有跨行或者跨列的单元格，可用`<th colspan="跨列数">内容</th>`,跨行则是用rowspan="跨行数".
7.如果要调整某一列的宽度，可使用：`<th width="宽度值或百分比">表头内容</th>`.
8.如果要调整整个表格的宽度，可以参考berlinix的这篇文章:http://www.ituring.com.cn/article/details/8367