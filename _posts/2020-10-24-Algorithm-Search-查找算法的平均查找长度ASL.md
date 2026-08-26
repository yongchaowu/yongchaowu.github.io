---
layout: post
title: "Algorithm-Search-查找算法的平均查找长度ASL"
date: 2020-10-24 23:38:00
categories: ["Algorithm"]
tags: ["Algorithm"]
---

<table class="table table-bordered table-striped table-condensed">
   <tr>
	  <th colspan="2">查找方法</th>
      <th>平均查找长度ASL</th>
	  <th>备注</th>
   </tr>
   <tr>
      <th colspan="2">顺序查找</th>
      <td>(x+1)/2</td>
   </tr>
   <tr>
      <th colspan="2">二分查找</th>
      <td>(x+1)/2</td>
	  <td>有序序列</td>
   </tr>
   <tr>
      <th rowspan="2">分块查找</th>
      <td>二分查找确定块</td>
      <td>log2(n/s +1)+s/2</td>
	  <td rowspan="2">s:块内元素个数</td>
   </tr>
   <tr>
      <td>顺序查找确定块</td>
      <td>(s2+2s+n)/2s</td>
   </tr>
</table>