---
layout: post
title:  "python实现org到markdown格式转换"
date:   2016-12-19 21:22:37 +0800
categories: 工具
tags: python emacs markdown
excerpt: 摘要
---

* menu
{:toc}

我喜欢org mode的简洁，特别是和emacs的完美兼容，用她写文档那叫一个爽，再加上macbook下emacs操作手感极好，有点恋恋不舍。但是写博客啥的基本都是用markdown，于是就写了个python程序，用来把org mode文档转成markdown。以后就可以在本地写好org文档，要发博客的时候用程序转一下拷贝到博客编辑页面就可以了，哦yeah....

---------------------------------------
程序很简单，就实现了两个功能，用来兼容csdn markdown：

1. 支持标题转换
2. 支持源代码转换

因为这是我最常用的两个功能了，而且列表`-`啥的两者都是兼容的，所以直接拷贝就可以了。

#### python实现

```python
import re


TitleList = ['#', '##', '###', '####']

def GenTitle(line):
    LevelNum = -1
    for each in line:
        if each == '*':
            LevelNum = LevelNum+1
        else:
            break
    if LevelNum >= 0:
        line = TitleList[LevelNum] + line.lstrip('*')
    return line


def parser(fnamein, fnameout):
    fin = open(fnamein, 'r')
    fout = open(fnameout, 'w')

    print "Start parsing..."

    for eachline in fin:
        if eachline[0] == '*':
            eachline = GenTitle(eachline)
        elif re.match("#\+BEGIN_SRC|#\+END_SRC", eachline) is not None:
            eachline = "```\n"
        fout.write(eachline)
    print "Transfer finished"
    fin.close()
    fout.close()
        

if __name__ == "__main__":
    print "Please enter Input File Name (name.org): "
    filenameIn = raw_input()+".org"
    filenameOut = "output.md"
    
    print "============================="
    print "Input Filename: " + filenameIn
    print "Output Filename:" + filenameOut
    parser(filenameIn, filenameOut)
    print "============================="
```
