---
layout: post
title:  "实现Graham扫描算法"
author: Kai Qiu
date:   2017-10-20 21:22:37 +0800
categories: 读书随笔
tags: haskell
excerpt: Haskell练习，实现Graham扫描算法
---

* menu
{:toc}

作为Haskell方面第一次上手练习，尽量不用到库里面的函数，然后通过一步一步实现Graham扫描算法，来熟悉haskell函数运行机制，了解调试过程，最重要的是要对函数的型态了然于胸。

参考书籍选自《Real World Haskell》和《Haskell趣学指南》。

### 一、问题描述

- 利用Graham扫描算法求N个点的凸包（http://wiki.mbalib.com/wiki/%E5%87%B8%E5%8C%85）。
- 凸包的定义：给定平面上的一个(有限)点集(即一组点)，这个点集的凸包就是包含点集中所有点的最小面积的凸多边形。

### 二、通过Haskell实现Graham算法

本次练习构造了如下几个函数用来辅助计算，最高层次为grahamHull，通过该函数获得最终结果。函数列举如下：

- 从一个二维坐标点构成的集合中取出最小的点，最小的点定义为具有最小y值的点，如果多个点具有最小y值，那么在y最小的点中取x最小的点。

```
getMinDot :: (Num a, Ord a) => [(a,a)] -> (a,a)
getMinDot ((x,y):pairs) =
  if pairs == []
  then (x,y)
  else if or [y<snd (getMinDot pairs), and [y==snd (getMinDot pairs), x<fst (getMinDot pairs)]]
  then (x,y)
  else getMinDot pairs
```

- 把二维坐标点构成的集合以列表形式排列，并把最小的点放到开头。

```
getNewList :: (Num a, Ord a) => [(a,a)] -> [(a,a)]
getNewList l = getMinDot l : [(x,y)| (x,y)<-l, (x,y) /= getMinDot l]
```

- 判断任意三个点方位走向

```
data Direction = DirLeft | DirRight | DirStraight deriving (Show, Eq)

getDir :: (Num a, Ord a) => (a,a) -> (a,a) -> (a,a) -> Direction
getDir (x1,y1) (x2,y2) (x3,y3) = let (xa,ya) = (x2-x1,y2-y1)
                                     (xb,yb) = (x3-x1,y3-y1) in
                                   if xa*yb-xb*ya > 0
                                   then DirLeft
                                   else if xa*yb-xb*ya < 0
                                   then DirRight
                                   else DirStraight
```

- 判断三个以上点连成的线段的方位走向

```
getDirList :: (Num a, Ord a) => [(a,a)] -> [Direction]
getDirList ((x1,y1):(x2,y2):(x3,y3):dotlist) =
  if dotlist == []
  then getDir (x1,y1) (x2,y2) (x3,y3):[]
  else getDir (x1,y1) (x2,y2) (x3,y3) : getDirList ((x2,y2):(x3,y3):dotlist)
```

- 根据每个点的极角大小进行排序（fast sort）

```
sortByAngle :: (Num a, Ord a) => [(a,a)] -> [(a,a)]
sortByAngle l = let newList = getNewList l in
                     case newList of
                       ((origX,origY):(x0,y0):dotlist) -> (origX,origY):mySort ((origX,origY):(x0,y0):dotlist)
                         where mySort ((srcX,srcY):(x0,y0):dotlist) =
                                 if dotlist == []
                                 then [(x0,y0)]
                                 else mySort ((srcX,srcY):[(x,y)|(x,y)<-dotlist, or [getDir (srcX,srcY) (x0,y0) (x,y) == DirRight, getDir (srcX,srcY) (x0,y0) (x,y) == DirStraight]])++[(x0,y0)]++mySort ((srcX,srcY):[(x,y)|(x,y)<-dotlist, getDir (srcX,srcY) (x0,y0) (x,y) == DirLeft])
                               mySort [(x,y)] = []
```

- Graham扫描法寻找凸包

```
grahamHull :: (Num a, Ord a) => [(a,a)] -> [(a,a)]
grahamHull l = let sortedList = sortByAngle l in
                 doGrahamHull sortedList
                 where doGrahamHull l = case l of
                         [(x1,y1),(x2,y2),(x3,y3)] -> [(x1,y1),(x2,y2),(x3,y3)]
                         ((x1,y1):(x2,y2):(x3,y3):(x4,y4):list) ->
                           if getDir (x2,y2) (x3,y3) (x4,y4) == DirRight
                           then doGrahamHull ((x1,y1):(x2,y2):(x4,y4):list)
                           else (x1,y1):doGrahamHull ((x2,y2):(x3,y3):(x4,y4):list)
```

- 运算结果：

```
*Main> grahamHull [(-1,0),(0,0),(1,0),(1,1),(2,1),(0,2)]
[(-1,0),(1,0),(2,1),(0,2)]
```

### 三、总结

这次练习有两点特别值得注意：一是在开头提到过的类型系统，注意函数的类型，对一些函数如果不确定型态可以在ghci中键入`:t func_name`进行查询。二是模式匹配和层次抽象，这和代数其实是能对应起来的。

> 版权声明：本文为博主原创文章，未经博主允许不得转载。