---
layout: post
title:  "利用emacs+graphviz绘制流程图"
date:   2016-10-20 21:22:37 +0800
categories: 工具
tags: emacs graphviz 流程图绘制
excerpt: 摘要
---

* menu
{:toc}

写文章除了插入代码以外，总是免不了需要流程图来介绍，显得直观易懂。以前在学校的时候用过graphviz来产生有向图数据，来测试算法。同样的工具也可以用来绘制精美的流程图，下面就Linux Mint环境下如何配置和使用graphviz做简单介绍。

## 1. 安装emacs graphviz-dot-mode
从[这里graphviz-dot-mode](http://users.skynet.be/ppareit/projects/graphviz-dot-mode/graphviz-dot-mode.html)下载graph-dot-mode.el，然后在.emacs中添加如下配置语句

```lisp
(load-file "graphviz-dot-mode.el路径")
```

这里还是遇到了配置slime时候一样的问题，打开dot文件后，会报

```lisp
Error in post-command-hook (autopair-global-mode-check-buffers): (wrong-type-argument characterp nil)
```

于是又加了一条

```lisp
(set-default 'autopair-dont-activate #'(lambda()(eq major-mode 'graphviz-dot-mode)))
```

就把graphviz-dot-mode下的自动补全给禁止了。

## 2. 安装graphviz并测试

```sh
$sudo apt-get install graphviz
```

在emacs中输入如下内容并保存

```sh
digraph G{
	size = "4, 4";//图片大小
	main[shape=box];/*形状*/
	main->parse;
	parse->execute;
	main->init[style = dotted];//虚线
	main->cleanup;
	execute->{make_string; printf}//连接两个
	init->make_string;
	edge[color = red]; // 连接线的颜色
	main->printf[style=bold, label="100 times"];//线的 label
	make_string[label = "make a\nstring"]// \n, 这个node的label，注意和上一行的区别
	node[shape = box, style = filled, color = ".7.3 1.0"];//一个node的属性
	execute->compare;
}
```

快捷键C-c c编译，C-c p显示，效果如下
![这里写图片描述](http://img.blog.csdn.net/20161020231819009)

http://users.skynet.be/ppareit/projects/graphviz-dot-mode/graphviz-dot-mode.html
