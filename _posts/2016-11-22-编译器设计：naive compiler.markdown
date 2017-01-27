---
layout: post
title:  "编译器设计：naive compiler"
date:   2016-11-22 21:22:37 +0800
categories: 读书随笔
tags: 编译器
excerpt: 摘要
---

* menu
{:toc}

## Compiler Design

### 一 方法介绍

#### 1-1 Source Language
选择C语言作为源语言，从最简单的语句开始，一步一步完善语言支持。

#### 1-2 Implementation  Language
选择python作为实现语言，主要是可以方便测试，而且处理字符很方便。

#### 1-3 Implementation Platform
Intel X86，因为我的笔记本是这个，方便。

#### 1-4 测试case以及测试driver
测试case由样例程序以及它们的输出组成，通过测试driver读取测试case，然后在本地平台生成可运行程序，把运行结果和case进行比较，进而确定case通过与否。

### 二 最简实现，一个弱智的文本打印工具

根据文章 [MAC OSX 多文件编译链接](http://blog.csdn.net/abcamus/article/details/53288428) 提供的source.c和main.c，参考gcc汇编source.c的结果

```
$ gcc -S source.c -o source.s
```

得到source.s，代码如下

```
	.section	__TEXT,__text,regular,pure_instructions
	.macosx_version_min 10, 12
	.globl	_c_entry
	.align	4, 0x90
_c_entry:                               ## @c_entry
	.cfi_startproc
## BB#0:
	pushq	%rbp
Ltmp0:
	.cfi_def_cfa_offset 16
Ltmp1:
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
Ltmp2:
	.cfi_def_cfa_register %rbp
	movl	$12, %eax
	popq	%rbp
	retq
	.cfi_endproc


.subsections_via_symbols
```

```
import sys
entry_name = "_c_entry"

header = "\t.section\t__TEXT,__text,regular,pure_instructions\n\t.macosx_version_min 10, 12\n\t.globl "+entry_name+"\n\t.align 4, 0x90"

func_start = "\n\t"+entry_name+":"+"\n\t"+".cfi_startproc\n\tpushq\t%rbp\nLtmp0:\n\t.cfi_def_cfa_offset 16\nLtmp1:\n\t.cfi_offset %rbp, -16\n\tmovq\t%rsp, %rbp\nLtmp2:\n\t.cfi_def_cfa_register %rbp"

func_end = "\n\t.cfi_endproc\n\n.subsections_via_symbols"

def do_compile(fd):
    fd.write(func_start)
    fd.write("\n\tmovl\t$12, %eax")
    fd.write("\n\tpopq\t%rbp\n\tretq")
    fd.write(func_end)
    
    
def add_header(fd):
    fd.write(header)
    
if __name__ == "__main__":
    fin = open("source.c", 'r')
    fout = open("out.s", 'w')
    if fout is False:
        print "Cannot create OUTPUT file"
        exit
    add_header(fout)
    do_compile(fout)
    fin.close()
    fout.close()
```

### 三 生成可执行程序
根据  [MAC OSX 多文件编译链接](http://blog.csdn.net/abcamus/article/details/53288428) 生成test程序，执行打印出12

### 四 总结
其实这个程序并不能称为编译器，因为他并没有对源代码进行分析，而只是死板的生成了一个固定的汇编程序，但是这和编译器工作的结果是一样的，所以暂且叫他naive compiler吧。

#### 参考文献：
[1] An Incremental Approach to Compiler Construction. Abdulaziz Ghuloum
