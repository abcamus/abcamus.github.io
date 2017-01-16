---
layout: post
title:  "printascii详解"
date:   2016-12-13 21:22:37 +0800
categories: 嵌入式开发
tags: Linux uboot printascii 调试
excerpt: uboot下的printascii函数可以用来在串口打印信息，实现代码调试。这个函数实际上就是通过配置硬件相关的参数，通过uart完成打印。
---

* menu
{:toc}

uboot下的printascii函数可以用来在串口打印信息，实现代码调试。这个函数实际上就是通过配置硬件相关的参数，通过uart完成打印。

代码位于`arch/arm/lib/debug.S`

```c
#if !defined(CONFIG_DEBUG_SEMIHOSTING)
#include CONFIG_DEBUG_LL_INCLUDE		//debug/8250.S
#endif

ENTRY(printascii)
		/* 获取uart地址,定义在arch/arm/include/debug/8250.S,通过宏CONFIG_DEBUG_LL_INCLUDE包含进来,r3保存uart物理基地址，r1保存虚拟基地址
		*/
		addruart_current r3, r1, r2
		b	2f
1:		waituart r2, r3
		senduart r1, r3
		busyuart r2, r3
		teq	r1, #'\n'
		moveq	r1, #'\r'
		beq	1b
		/*
		 * 判断字符串是否为NULL，如果不是，跳转到1,r1包含读到的字符
		 */
2:		teq	r0, #0
		ldrneb	r1, [r0], #1
		teqne	r1, #0
		bne	1b
		mov	pc, lr
ENDPROC(printascii)

/* debug/8250.S*/
.macro	addruart, rp, rv, tmp
		ldr	\rp, =CONFIG_DEBUG_UART_PHYS
		ldr	\rv, =CONFIG_DEBUG_UART_VIRT
.endm
```

在调试exynos4412 uart的时候，我把它改成了

```c
.macro	waituart,rd,rx
#ifdef CONFIG_DEBUG_UART_8250_FLOW_CONTROL
#define UART_MSR		0x4
#define UART_MSR_CTS	0x2
1001:		load	\rd, [\rx, #UART_MSR << UART_SHIFT]
		tst	\rd, #UART_MSR_CTS
		beq	1001b
#endif
.endm

ENTRY(printascii)
		addruart_current r3, r1, r2
		b	2f
1:		waituart r2, r3
		senduart r1, r3
		//busyuart r2, r3
		teq	r1, #'\n'
		moveq	r1, #'\r'
		beq	1b
2:		teq	r0, #0
		ldrneb	r1, [r0], #1
		teqne	r1, #0
		bne	1b
		mov	pc, lr
ENDPROC(printascii)
```

然后用`printascii("debug info");`就能输出调试信息了。

