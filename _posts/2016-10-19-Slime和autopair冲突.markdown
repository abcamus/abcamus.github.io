---
layout: post
title:  "Slime和autopair冲突 "
date:   2016-10-19 21:22:37 +0800
categories: 工具
tags: emacs slime autopair
excerpt: 在emacs中打开slime，如果slime中出错，就会一直报autopair-global-mode-check-buffers error
---

* menu
{:toc}

### 问题与解决
在emacs中打开slime，如果slime中出错，就会一直报

```lisp
autopair-global-mode-check-buffers error
```

而且很多功能都不能用，点击右上角x关闭也不行。

解决方法如下

```lisp
  (set-default 'autopair-dont-activate #'(lambda () (eq major-mode 'sldb-mode)))
```
