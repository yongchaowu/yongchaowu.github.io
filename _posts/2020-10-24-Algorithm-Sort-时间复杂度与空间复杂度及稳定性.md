---
layout: post
title: "Algorithm-Sort-时间复杂度与空间复杂度及稳定性"
date: 2020-10-24 20:47:00
categories: ["Algorithm"]
tags: ["Algorithm"]
---

<!--more-->

<table class="table table-bordered table-striped table-condensed">
   <tr>
      <th rowspan="2">类别</th>
      <th rowspan="2">排序方法</th>
      <th colspan="3">时间复杂度</th>
      <th>空间复杂度</th>
      <th rowspan="2">稳定性</th>
   </tr>
   <tr>
      <td>平均情况</td>
      <td>最好情况</td>
      <td>最坏情况</td>
      <td>辅助存储</td>
   </tr>
   <tr>
      <th rowspan="2">插入排序</th>
      <td>直接插入排序</td>
      <td>O(n2)</td>
      <td>O(n)</td>
      <td>O(n2)</td>
      <td>O(1)</td>
      <td>稳定</td>
   </tr>
   <tr>
      <td>希尔排序(shell sort)/缩小增量排序</td>
      <td>O(n1.3)</td>
      <td>O(n)</td>
      <td>O(n2)</td>
      <td>O(1)</td>
      <td>不稳定</td>
   </tr>
   <tr>
      <th rowspan="2">选择排序</th>
      <td>直接选择排序/简单选择排序</td>
      <td>O(n2)</td>
      <td>O(n2)</td>
      <td>O(n2)</td>
      <td>O(1)</td>
      <td>不稳定</td>
   </tr>
   <tr>
      <td>堆排序</td>
      <td>O(n*log2n)</td>
      <td>O(n*log2n)</td>
      <td>O(n*log2n)</td>
      <td>O(1)</td>
      <td>不稳定</td>
   </tr>
   <tr>
      <th rowspan="2">交换排序</th>
      <td>冒泡排序</td>
      <td>O(n2)</td>
      <td>O(n)</td>
      <td>O(n2)</td>
      <td>O(1)</td>
      <td>稳定</td>
   </tr>
   <tr>
      <td>快速排序</td>
      <td>O(n*log2n)</td>
      <td>O(n*log2n)</td>
      <td>O(n2)</td>
      <td>O(n*log2n)</td>
      <td>不稳定</td>
   </tr>
   <tr>
      <th>归并排序</th>
      <td></td>
      <td>O(n*log2n)</td>
      <td>O(n*log2n)</td>
      <td>O(n*log2n)</td>
      <td>O(n)</td>
      <td>稳定</td>
   </tr>
   <tr>
      <th>基数排序</th>
      <td>r:关键字的基数<br>
      d:长度<br>
      n:关键字个数</td>
      <td>O(d(r+n))</td>
      <td>O(d(n+rd))</td>
      <td>O(d(r+n))</td>
      <td>O(rd+n)</td>
      <td>稳定</td>
   </tr>
</table>