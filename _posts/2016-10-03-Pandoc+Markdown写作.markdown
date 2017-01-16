---
layout: post
title:  "Pandoc+Markdown写作 "
date:   2016-10-03 21:22:37 +0800
categories: 工具
tags: pandoc markdown
excerpt: 之前写文章渐渐习惯了markdown，但是在交付或者打印的时候还是要通过pdf，所以就想能不能通过什么工具直接从markdown转到pdf，于是在网上搜索方法，找了几篇文章，感觉最终的结果还不错，就把应用的过程记在这里。
---

* menu
{:toc}

之前写文章渐渐习惯了markdown，但是在交付或者打印的时候还是要通过pdf，所以就想能不能通过什么工具直接从markdown转到pdf，于是在网上搜索方法，找了几篇文章，感觉最终的结果还不错，就把应用的过程记在这里。

## 1 安装pandoc和Miktex
我的是Windows平台，所以直接在pandoc官方网站下载了安装包安装即可。
http://www.pandoc.org/installing.html
上面有Miktex链接，一起下载下来安装。

## 2 中文支持
### 2.1 中文编译不通过
添加编译选项 --latex-engine=xelatex

### 2.2 中文不能显示
添加编译选项 -M CJKmainfont:SimSun
再添加-M mainfont:"Times New Roman" -M monofont:Monaco个人觉得好看一点。

### 2.3 不能自动换行
修改tex模板，先导出模板pandoc -D latex > template.tex
然后在
$if(mathfont)$
    \setmathfont(Digits,Latin,Greek)[$for(mathfontoptions)\$$mathfontoptions\$$sep$,$endfor$]{$mathfont$}
$endif$之后添加
\XeTeXlinebreaklocale "zh"

## 3. 排版
### 3.1 修改边距
在导言栏添加
\usepackage[tmargin=0.5in,bmargin=1in,lmargin=0.75in,rmargin=1.25in]{geometry}


### 3.2  代码配色
通过

 ```{.c .numberLines} code```


## 4. emacs markdown mode

下载markdown-mode.el  http://jblevins.org/projects/markdown-mode/


.emacs中添加如下配置

```ruby
(autoload 'markdown-mode "markdown-mode"
   "Major mode for editing Markdown files" t)
(add-to-list 'auto-mode-alist '("\\.markdown\\'" . markdown-mode))
(add-to-list 'auto-mode-alist '("\\.md\\'" . markdown-mode))

(autoload 'gfm-mode "gfm-mode"
   "Major mode for editing GitHub Flavored Markdown files" t)
(add-to-list 'auto-mode-alist '("README\\.md\\'" . gfm-mode))
```


## 5. 其他配置

可以通过查看template.tex文件中的if语句，然后在命令行里添加相应的参数。


## 6. 参考文献：

http://www.cnblogs.com/baiyangcao/p/5574483.html

http://www.bagualu.net/wordpress/archives/5396#pandoc%E4%B8%AD%E7%9A%84%E4%B8%AD%E6%96%87%E6%8D%A2%E8%A1%8C%E9%97%AE%E9%A2%98

生成文档命令：
pandoc test.md -o test.pdf --template=template.tex --latex-engine=xelatex -M CJKmainfont:SimSun -M mainfont:"Times New Roman" -M monofont:Monaco
