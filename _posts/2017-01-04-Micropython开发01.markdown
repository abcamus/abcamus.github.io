---
layout:	post
title:	"Micropython开发（1）: 认识Micro Python"
date:	2017-01-04
categories:	Micropython
tags: Micropython
excerpt: 介绍micropython, 包括以下几个方面：1. Micro Python的发展情况，语法特点，代码结构，支持的硬件。2. 介绍了本项目的开发平台： 基于exynos-4412 SoC的开发板。3. 最后初步实验，完成Linux平台下的测试，然后解决交叉编译过程中出现的问题。
---
* titles
{:toc}

micropython是Damien George发明的运行在MCU之上的python，从[项目主页]可以下载。

本文对micropython做了简单介绍，然后在Linux平台下编译通过。

### 一、Micro Python语法特点:

完整支持Python 3.4 语法
1. 完整的Python词法分析器, 解析器,编译器，虚拟机和运行时。
2. 包含命令行接口，可离线运行。
3. Python 字节码由内置虚拟机编译运行.
4. 有效的内部存储算法，能带来高效的内存利用率。整数变量存储在内存堆中，而不是栈中。
5. 使用Python decorators特性,函数可以被编译成原生机器码，虽然这一特性会带来大约2倍的内存消耗，但也使python有更快的执行速度。
6. 函数编译可设置使用底层整数代替python内建对象作为数字使用。有些代码的运行效率可以媲美c的效率，并且可以被python直接调用，适合做时间紧迫性，运算复杂度高的应用。
7. 通过内联汇编功能，应用可以完全接入底层运行时，内联汇编器也可以像普通的python函数一样调用。
8. 基于简单和快速标记的内存垃圾回收算法，运行周期少于4ms，许多函数都可以避免使用栈内存段，因此也不需要垃圾回收功能。

### 二、代码结构：

Major components in this repository:

- py/ -- the core Python implementation, including compiler, runtime, and core library.
- unix/ -- a version of MicroPython that runs on Unix.
- stmhal/ -- a version of MicroPython that runs on the PyBoard and similar STM32 boards (using ST's Cube HAL drivers).
- minimal/ -- a minimal MicroPython port. Start with this if you want to port MicroPython to another microcontroller.
- tests/ -- test framework and test scripts.
- docs/ -- user documentation in Sphinx reStructuredText format.

Additional components:

- bare-arm/ -- a bare minimum version of MicroPython for ARM MCUs. Used mostly to control code size.
- teensy/ -- a version of MicroPython that runs on the Teensy 3.1 (preliminary but functional).
- pic16bit/ -- a version of MicroPython for 16-bit PIC microcontrollers.
- cc3200/ -- a version of MicroPython that runs on the CC3200 from TI.
- esp8266/ -- an experimental port for ESP8266 WiFi modules.
- tools/ -- various tools, including the pyboard.py module.
- examples/ -- a few example Python scripts.

### 三、硬件平台
讯为itop exynos4412核心板（SCP）。

#### 3.1 核心板工艺
工艺 八层盲埋孔设计，沉金工艺

#### 3.2 基本参数

部件 | 参数
--|--
CPU | 三星Exynos4412,四核Cortex-A9，主频为1.6GHz
内存 |2GB 双通道 DDR3
存储 |16GB    ［独家支持］
PMIC | 选用三星自家电源管理芯片，高效节能！具有9路DC/DC和28路LDO输出电源 经千百万部手机实践检验，与三星4412处理器匹配最佳
USB HOST | 板载USB3503，引出高性能HSIC，实现3路USB HOST输出
扩展 | 引出脚多达320个，满足用户各类扩展需求

#### 3.3 运行温度

名字 | 条件
---|---
温度 | 在-20℃到70℃范围的高低温运行测试中运行良好

#### 3.4 其它

项目 | 功能
---|---
视频编解码 | 支持MPEG-4/MPEG2、H.264/H263、VC-1、DivX的视频编解码1080p@30fps
图形加速 |支持2D，3D图形加速ARM Mali-400 MP Core
存储 |支持SD/MMC/SDIO接口存储卡，最高支持32GB
硬件编解码 |支持JPEG硬件编解码，最大支持8192×8192分辨率
电磁屏蔽罩接口 |预留电磁屏蔽罩接口以及四个加固螺孔
供电 |支持5V电压供电
特点 |该核心板已经把4412处理器最难实现部分全部承担，可帮助用户轻松实现高端四核产品级设计！

#### 3.5 应用范围

名字 | 举例
---|---
应用范围	| 家居控制平台、智能家居平台、健身器械操作平台、美容器械操作平台、医疗器械操作平台、智能仪表、仪器、触摸屏控制器、导航设备、车载DVD；智能广告控制终端、排队系统、广告机、楼宇对机、分机以及管理机等


### 四、在Linux平台上编译使用
进入minimal/，执行

{% highlight shell %}
$ make
$ make run
Use make V=1 or set BUILD_VERBOSE in your environment to increase build verbosity.
stty raw opost -echo
build/firmware.elf
MicroPython v1.8.6-156-gadf3cb5-dirty on 2016-12-23; minimal with exynos4412
Type "help()" for more information.
>>> 
{% endhighlight %}

### 五、交叉编译
新建项目exynos，执行
{% highlight shell %}
$ make CROSS=1
/home/camus/arm-2014.05/arm-none-linux-gnueabi/libc/usr/include/gnu/stubs.h:10:29: fatal error: gnu/stubs-hard.h: No such file or directory
 # include <gnu/stubs-hard.h>
 {% endhighlight %}

看这个文件名，是浮点计算的问题，估计是编译选项不对。参照uboot的编译开关： http://blog.csdn.net/abcamus/article/details/54023051

最终Makefile中添加

{% highlight makefile %}
LIB_PATH = -L /home/camus/arm-2014.05/bin/../lib/gcc/arm-none-linux-gnueabi/4.8.3/ -lgcc
CFLAGS_CORTEX_V7 = -mthumb -march=armv7-a -mabi=aapcs-linux -msoft-float
CFLAGS = $(INC) -Wall -Werror -ansi -std=gnu99 $(CFLAGS_CORTEX_V7) $(COPT)
{% endhighlight %}

然后在main.c中添加了raise函数（参照uboot）
{% highlight c %}
int raise(int signum)
{
	printf("raise: Signal # %d caught\n", signum);
	return 0;
}
{% endhighlight %}
再执行
{% highlight shell %}
$ make CROSS=1
{% endhighlight %}
顺利生成bin文件，接着就可以上板子测试了。

[项目主页]: https://github.com/micropython/micropython
