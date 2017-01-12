---
layout:	post
title:	"Micropython移植前戏：ARM裸机执行代码"
date:	2017-01-09
categories:	micropython
tags: micropython
excerpt: 以led灯裸机程序为例，介绍如何在exynos 4412开发板上运行裸机程序，然后以此为基础修改micropython的脚本，最后对micropython镜像进行测试。
---

## 一. exynos 4412裸机执行led灯程序

开门见山，先提供源代码。
{% highlight c %}
/*
 * led.c
 */
 #define GPL2CON     (*(volatile unsigned long *) 0x11000100)
#define GPL2DAT     (*(volatile unsigned long *) 0x11000104)

#define GPK1CON 	(*(volatile unsigned long *) 0x11000060)
#define GPK1DAT		(*(volatile unsigned long *) 0x11000064)

//GPL2_0, GPK1_1

void delay(int r0)
{
    volatile int count = r0;
    while (count--)
        ;
}

void led_blink()
{
	GPL2CON = 0x00000001;
	GPK1CON = 0x00000010;
	
	while(1)							
	{
		GPL2DAT = 1;
		GPK1DAT = 0;
		delay(0x80000);
		GPL2DAT = 0;
		GPK1DAT = 0x2;
		delay(0x80000);
	}
}

// start.S
//#define CONFIG_SYS_ICACHE_OFF  

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
	ldr	sp, =0x02050000

	bl	led_blink

halt:
	b halt
{% endhighlight %}

{% highlight makefile %}
led.bin: start.o led.o
	arm-none-linux-gnueabi-ld -Ttext 0x0 -o led.elf $^
	arm-none-linux-gnueabi-objcopy -O binary led.elf led.bin
	arm-none-linux-gnueabi-objdump -D led.elf > led_elf.dis


%.o : %.S
	arm-none-linux-gnueabi-gcc -o $@ $< -c -nostdlib

%.o : %.c
	arm-none-linux-gnueabi-gcc -o $@ $< -c -nostdlib

clean:
	rm *.o *.elf *.bin *.dis  -f
{% endhighlight %}

### 启动文件start.S
micropython中的bare-arm编译的时候没有启动文件，通过反汇编也可以看到并没有isr_vectors段，所以需要给他添加一个。

启动文件的任务： 配置arm

### 主体文件
就是.c文件，实现我们想要的功能。

## 二. 这一步要做的事情
添加start.S文件，确保启动入口正确

## 三. uboot下进行测试


[链接]

>引用：运行jekyll new myblog的时候说找不到gem jekyll，原因是GEM_HOME没有配置

Table： 表格，注意空行

项目 | 内容
---|---
item1 | 第一个项目内容

[链接]: http://jekyll.com.cn/docs/installation/
