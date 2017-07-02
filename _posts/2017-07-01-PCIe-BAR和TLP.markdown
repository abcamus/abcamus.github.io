---
layout: post
title:  "PCIe BAR空间和TLP"
author: Kai Qiu
date:   2017-07-01 21:22:37 +0800
categories: 嵌入式开发
topics: 大话PCIe
tags: PCIe
excerpt: 上一篇文章中写到每个PCIe的function都有自己的configuration space，其实就是配置寄存器了（这个当然是要有的了，不然软件要怎么玩？只不过PCIe的配置寄存器要通过tlp才能去访问）。其实PCIe设备是有自己独立的一套内部空间，不仅仅是配置空间，包括每个设备提供哪些I/O地址，memory地址。而BAR（Base Address Register）就是用来表征这些地址空间的，通过BAR寄存器，我们首先知道这个基址对应的空间属性，然后给这段空间分配一个基址（这个基址只是用来路由寻址用的，不能和存储器空间的地址搞混，很多软件实现上会把两个地址设置成一样，但是本质上没有任何关系，只是tlp寻址的时候用的！）。
---

* menu
{:toc}

上一篇文章中写到每个PCIe的function都有自己的configuration space，其实就是配置寄存器了（这个当然是要有的了，不然软件要怎么玩？只不过PCIe的配置寄存器要通过tlp才能去访问）。其实PCIe设备是有自己独立的一套内部空间，不仅仅是配置空间，包括每个设备提供哪些I/O地址，memory地址。而BAR（Base Address Register）就是用来表征这些地址空间的。

## 一、BAR寄存器和PCIe内部空间

关于地址相关的问题，搞清楚这三个地址之间的关系就可以了：

1. 存储器地址，就是CPU，DMA等设备直接读写的地址。
2. TLP中的地址。
3. BAR空间地址。

如果两两组合的话，能够形成三种关系，但是事实上，这三者之间的关系其实就两部分：

1. 存储器地址和TLP地址字段的关系。
2. TLP地址字段和BAR空间地址的关系。

解决这两个问题，地址相关的问题就应该都清楚了。

### 1.1 BAR寄存器

首先要知道BAR有什么用？通过BAR寄存器，我们首先知道这个基址对应的空间属性，然后给这段空间分配一个基址（这个基址只是用来路由寻址用的，不能和存储器空间的地址搞混，很多软件实现上会把两个地址设置成一样，但是本质上没有任何关系，只是TLP寻址的时候用的！）。这样的话，TLP就能根据地址被路由到对应设备的BAR空间中去。比如说现在有一个mem read request，如果路由地址（地址信息包含在TLP中）是0x71000000，而有一个设备func0的mem空间范围是0x70000000~0x80000000，那么这个TLP就会被这个func处理。从func0的0x71000000对应的地址读取相应数据。

这就是TLP中的地址字段和BAR空间的地址之间的关系。还有一个问题是关于存储器地址和TLP地址字段的关系，有个硬件单元非常重要，那就是ATU，见第二节。这里详细介绍一下BAR的配置问题。

BAR位置：

对于EP来讲，配置空间的映射是这样的：

![2017-07-02 19-33-12屏幕截图.png](https://ooo.0o0.ooo/2017/07/02/5958da40cf7ca.png)

从上图中看到，BAR是从配置空间0x10到0x24的连续6个32位寄存器。关于BAR每个字段的解释可以参考`DWC_pcie_reference`<sup>[1]</sup>

BAR配置过程：

1. 通过cfg write request向BAR地址写入全1。
2. 通过cfg read request读取BAR。
3. 根据读取的BAR值进行如下判断：

从高位开始读取连续的1，说明这些比特位是可写的，表征该space的size，譬如读到的BAR为0x11100000，那么这个space的size为0x100000 bytes，同时由于第0位为0,表示memory BAR，否则为I/O BAR。bits[2:1]和bits[3]的含义如下图所示

![2017-07-02 19-46-10屏幕截图.png](https://ooo.0o0.ooo/2017/07/02/5958dd1eac263.png)


### 1.2 ATU(Address Translation Unit)

TLP中的地址哪里来？ATU转换过来的。这个问题就是这么的简单。ATU是什么？是一个地址转换单元，负责将一段存储器域的地址转换到PCIe总线域地址，除了地址转换外，还能提供访问类型等信息，这些信息都是ATU根据总线上的信号自己做的，数据都打包到TLP中，不用软件参与。软件需要做的是配置ATU，所以如果ATU配置完成，并且能正常工作，那么CPU访问PCIe空间就和访问本地存储器空间方法是一样的，只要读写即可。

这就解释了存储器地址和TLP地址字段的关系了。至此，地址相关的问题就解决了。

ATU配置举例：以kernel 4.4中designware PCIe host驱动为例

``` 
static void dw_pcie_prog_outbound_atu(struct pcie_port *pp, int index,
		int type, u64 cpu_addr, u64 pci_addr, u32 size)
{
    // 使用哪个ATU
	dw_pcie_writel_rc(pp, PCIE_ATU_REGION_OUTBOUND | index,
			  PCIE_ATU_VIEWPORT);
    // source地址（存储器域）的低32位
	dw_pcie_writel_rc(pp, lower_32_bits(cpu_addr), PCIE_ATU_LOWER_BASE);
	dw_pcie_writel_rc(pp, upper_32_bits(cpu_addr), PCIE_ATU_UPPER_BASE);
    // space size
	dw_pcie_writel_rc(pp, lower_32_bits(cpu_addr + size - 1),
			  PCIE_ATU_LIMIT);
    // 目标地址空间（PCIe总线地址）
	dw_pcie_writel_rc(pp, lower_32_bits(pci_addr), PCIE_ATU_LOWER_TARGET);
	dw_pcie_writel_rc(pp, upper_32_bits(pci_addr), PCIE_ATU_UPPER_TARGET);
    // 空间类型（mem or IO）
	dw_pcie_writel_rc(pp, type, PCIE_ATU_CR1);
    // 使能ATU
	dw_pcie_writel_rc(pp, PCIE_ATU_ENABLE, PCIE_ATU_CR2);
}
```

## 二、TLP

TLP(Transaction Layer Packet)应该算是PCIe中最重要的概念了。可以说TLP是用户程序和PCIe设备交互的唯一渠道（edma和MSI本质上还是通过TLP）。TLP的构成如下图所示，具体每个字段的含义参见`PCI_Express_Base_Specification_Revision_4.0.Ver.0.3`第2.2节

![2017-07-02 20-04-35屏幕截图.png](https://ooo.0o0.ooo/2017/07/02/5958e16f23933.png)

因为软件不需要显示的配置TLP，所以这里就没有TLP的配置了，取而代之的是相关硬件的配置（譬如ATU）。这里有个了解就行，等到调试的时候就需要仔细的了解了。

这篇文章总结了PCIe设备地址空间的知识，搞明白了这个之后应该能上手开始写PCIe驱动了，至少能枚举了。下篇就详细介绍PCIe设备枚举过程，也是对这些知识的一个应用。

> 下篇预告： PCIe设备枚举


参考文献：

[1] DWC_pcie_reference
[2] PCI_Express_Base_Specification_Revision_4.0.Ver.0.3