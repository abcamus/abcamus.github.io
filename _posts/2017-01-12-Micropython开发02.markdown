---
layout:	post
title:	"Micropython开发（2）：解释器移植"
author: Kai Qiu
date:	2017-01-12
categories:	Micropython
tags: Micropython
excerpt: 经过了几天的努力，Micropython repl终于跑起来了，很是兴奋，把过程记在这里，很多文章还在csdn上，后续会搬迁过来。
---

* 目录
{:toc}

## 一 概述
[micropython:介绍与编译] 一文介绍了Micropython的语法特点，当前的应用平台以及在linux下的试用。这篇文章接着介绍如何将Micropython解释器移植到exynos 4412平台下，运行repl。

### 1-1 知识储备

1. [arm gcc编译器相关的知识]
2. [链接脚本相关的知识]
3. Makefile相关的知识，参考《GNU make中文手册》
4. Exynos 4412 硬件特别是uart和mem映射相关，可以参考：[Exynos4412时钟模块以及UART时钟配置]以及芯片手册。
5. boot相关的知识：[Exynos 4412 u-boot 调试]以及[Exynos4412 sd卡启动uboot]
6. Micropython的代码结构：[micropython：介绍与编译]

### 1-2 成果展示

最终的运行的repl界面如下

{% highlight shell %}
LANDROVER # mmc read 40000000 1800 400

MMC read: dev # 0, block # 6144, count 1024 ... 1024 blocks read: OK
LANDROVER # go 40000000
## Starting application at 0x40000000 ...
Hello, Micropython,
MicroPython v1.8.6 on 2017-01-11; minimal with exynos4412
Type "help()" for more information.
>>> A=["hello", 1, -10]
took 0 ms
qstr:
  n_pool=1
  n_qstr=2
  n_str_data_bytes=12
  n_total_bytes=60
GC: total: 1984, used: 368, free: 1616
 No. of 1-blocks: 4, 2-blocks: 4, max blk sz: 8, max free sz: 55
GC: total: 1984, used: 368, free: 1616
 No. of 1-blocks: 4, 2-blocks: 4, max blk sz: 8, max free sz: 55
>>> A[0]
'hello'
{% endhighlight %}

## 二 移植过程

### 2-1 代码选型
选择mininal作为开发的样例代码，原来考虑过bare-arm，但是由于bare-arm即没有串口支持，也没有malloc机制，根本无法使用，所以考虑到工作量，用minimal作为初次尝试比较好。

### 2-2 启动代码实现
在minimal中的main.c文件实现了_start函数，用来对stm32硬件做初始化，为了节省硬件相关的调试时间，我们直接利用了uboot，因为uboot启动后已经初始化好了exynos 4412的时钟，dram控制器等重要部分。启动代码最终实现为

```c
.global _start

_start:
	//disable watch dog
	ldr	r0, =0x10060000
    mov	r1, #0
    str	r1, [r0]

	//turn on icache
	mrc	p15, 0, r0, c1, c0, 0
	//bic	r0, r0, #0x00002300	/* clear bits 13, 9:8 (--V- --RS) */
	//bic	r0, r0, #0x00000087	/* clear bits 7, 2:0 (B--- -CAM) */
	//orr	r0, r0, #0x00000002	/* set bit 2 (A) Align */
	//orr	r0, r0, #0x00001000	/* set bit 12 (I) I-Cache */
	
#ifdef CONFIG_SYS_ICACHE_OFF
    	// clear bit 12 (I) I-cache
    	bic	r0, r0, #0x00001000
#else
    	// set bit 12 (I) I-cache
    	orr	r0, r0, #0x00001000
#endif
       	mcr	p15, 0, r0, c1, c0, 0
	//mcr p15, 0, r0, c7, c5, 0	@ invalidate icache

	//set stack
	ldr	sp, =0x41000000

	bl	main
loop:
	bl loop

halt:
	b halt
```

### 2-3 指令集兼容
Micropython使用的是thumb指令集，容易理解了，因为python最终编译成字节流。要做相应的编译器配置，包括uboot也要修改。参考知识储备中的第一条。

### 2.4 修改内存分布
调整链接脚本，因为我们没有用到flash，直接都映射到dram中，这里映射了起始的16MB。代码段示例如下：

```shell
OUTPUT_FORMAT("elf32-littlearm", "elf32-littlearm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(_start)

/* Specify the memory areas */
MEMORY
{
    RAM (xrw)       : ORIGIN = 0x40000000, LENGTH = 0x1000000 
}
 
/* top end of the stack */
_estack = ORIGIN(RAM) + LENGTH(RAM);

/* define output sections */
SECTIONS
{

	. = ORIGIN(RAM);
    .text :
    {
        . = ALIGN(4);
		build/start.o (.text*)
        KEEP(*(.isr_vector)) /* isr vector table */
        *(.text)           /* .text sections (code) */
        *(.text*)          /* .text* sections (code) */
        *(.rodata)         /* .rodata sections (constants, strings, etc.) */
        *(.rodata*)        /* .rodata* sections (constants, strings, etc.) */

        . = ALIGN(4);
        _etext = .;        /* define a global symbol at end of code */
        _sidata = _etext;  /* This is used by the startup in order to initialize the .data secion */
    } >RAM
    ...
}
```

### 2.5 交互界面
修改uart_core.c文件，做好寄存器兼容。同样的修改发送接收函数即可。

```c
#if MICROPY_MIN_USE_EXYNOS4412
/* baudrate rest value */
union br_rest {
	unsigned short	slot;		/* udivslot */
	unsigned char	value;		/* ufracval */
};

typedef struct {
	uint32_t ulcon;
	uint32_t ucon;
	uint32_t ufcon;
	uint32_t umcon;
	uint32_t utrstat;	// 0x10
	uint32_t uerstat;
	uint32_t ufstat;
	uint32_t umstat;
	uint8_t utxh;		// 0x20
	uint8_t res1[3];
	uint8_t urxh;
	uint8_t res2[3];
	uint32_t ubrdiv;		// 0x28
	union br_rest	rest;
	uint8_t res3[0xffd0];
} periph_uart_t;

#define SAMSUNG_UART2 ((periph_uart_t*)0x13820000)
#endif
```

## 三 总结与展望
这次开发经历了三天左右的时间，从周一到周三。相比于知识，思路才是最重要的，看最近alphogo又化身master连战60名中日韩围棋界高手，其实足以证明人的思考其实是很有限的。现在很多面试者会被问知道xxx，其实不知道也并无关系，关键看在不知道的情况下如何才能去发现并逐步解决未知的问题。这个才是最重要的。
近期又和朋友交流工作问题，我发表的观点是：其实人与人之间智力上的差距对工作的影响并没有那么大。真正影响的因素其实是受系统合理的训练的程度。很多表现优秀的人其实不管是有意的还是无意的都接受了较多系统性的训练，这才能在工作上有更出色的表现。而且我觉得现代社会其实是一个反智社会，就算只会抽烟喝酒打牌，也照样可以混出名堂，比如各种主播，健身达人等。
接下来希望能在此基础上实现更多自己的idea。准备好迎接更多的挑战。


[micropython:介绍与编译]: http://blog.csdn.net/abcamus/article/details/53842722
[arm gcc编译器相关的知识]: http://blog.csdn.net/abcamus/article/details/54023051
[链接脚本相关的知识]: http://blog.csdn.net/abcamus/article/details/53509720
[Exynos4412时钟模块以及UART时钟配置]: http://blog.csdn.net/abcamus/article/details/53224562
[Exynos 4412 u-boot 调试]: http://blog.csdn.net/abcamus/article/details/53424619
[Exynos4412 sd卡启动uboot]: http://blog.csdn.net/abcamus/article/details/53084947
[micropython：介绍与编译]: http://blog.csdn.net/abcamus/article/details/53842722
