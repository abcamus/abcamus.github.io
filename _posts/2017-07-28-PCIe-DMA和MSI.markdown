---
layout: post
title:  "DMA和MSI机制"
author: Kai Qiu
date:   2017-07-28 21:22:37 +0800
categories: 嵌入式开发
topics: 大话PCIe
tags: PCIe MSI
excerpt: 摘要
---

* menu
{:toc}

## 一、PCIe DMA机制

PCIe控制器也提供DMA(Direct Memory access)功能，用来批量地异步数据传输。

### 1.1 DMA读写的发起和结束

假设现在RC要从EP mem space读1MB数据，可以有这么两种方式：RC发起DMA读；EP发起DMA写。这两种方式结果是等效的，对最后完成中断的方式会不一样，前者通过local interrupt表示自己DMA读完了，后者需要EP发送一笔IMWr来表示DMA读完成了。

### 1.2 DMA配置

![这里写图片描述](http://img.blog.csdn.net/20170728004106267?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvYWJjYW11cw==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

如图表示本地控制器发起一笔1MB写操作

#### 1.2.1 SAR和DST

SAR表示DMA传输的数据源地址，如果RC发起从EP读操作，那么SAR必定是EP中某个BAR range内。目标地址DAR就是系统ddr中的地址。反之，如上图所示的写操作，DAR就是EP中mem space。

#### 1.2.2 Max_Payload_Size
DMA读写本质上还是通过拆分成TLP来进行的，每次传输的size就是通过tlp header中的length来确定的，而length由控制器的Max_Payload_Size决定，这个值取EP和RC的capability中相应参数的最小值。

### 1.3、Linked List

对于大批量数据的传输，通常都会有所谓的Linked List Mode。试想一下，在Linux运行时要进行大批量数据传输的时候是很难分配到大块连续的物理地址的，那么势必需要重复发起DMA传输，这样的话DMA的异步传输功能岂不是被变相衰弱了。所以**在硬件上要有这样一种机制来避免这个问题，这就是LL DMA**。

这种机制广泛存在于各种高速设备中，USB3.0传输的时候内部通过链接trb实现的就是Linked List DMA。

![这里写图片描述](http://img.blog.csdn.net/20170728084932701?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvYWJjYW11cw==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

如上图所示，Linked List中每个配置块称作element，每个element中的内容就是前面DMA传输时候的配置，硬件在发起DMA传输的时候把这块payload加载到指定的寄存器中。LL mode的结束通过CB来标志，toggle一下即表示到了LL的末尾。

## 二、PCIe MSI机制

PCIe采用data path才传递interrupt，这就是Message Signal Interrupt。假如RC收到一笔对应的写操作，那么在硬件实现上就会自动转换成中断信号给中断控制器，这笔写请求并不会到任何ram区域。

### 2.1 硬件支持

#### 2.1.1 Generic Interrupt Controller

https://developer.arm.com/products/system-ip/system-controllers/interrupt-controllers

从CoreLink GIC-500开始支持MSI/MSI-X。CoreLink GIC-400不支持，所以就算PCIe设备支持也无法实现MSI(-X)机制。

#### 2.1.2 PCIe设备支持

每一个具有MSI capability的device都有一组对应的寄存器来表示MSI能力。

MSI Control Register中的multiple message capable（三个比特，假设值为x，x属于[0, 5]）表示MSI可产生多少message，计算方法为2的x次方。另外有三个比特multiple message enable，和message capable对应，表示实际使能了多少message。还有一个MSI data寄存器和MSI address寄存器，要结合中断控制器配置，表示具体的message编码和message的目标地址。

到这篇文章为止涉及的知识已经能够让PCIe工作起来了，接下来开始写些Linux PCIe驱动相关的文章。