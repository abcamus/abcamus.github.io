---
layout: post
title:  "Linux访问PCIe空间"
author: Kai Qiu
date:   2017-09-04 21:22:37 +0800
categories: 嵌入式开发
tags: PCIe
topics: 大话PCIe
excerpt: Linux访问PCIe设备的接口
---

* menu
{:toc}

Linux在枚举PCIe设备的过程由内核中的PCI框架负责，在EP配置完成之后，驱动通过以下接口访问PCIe空间，原理参考前文[《大话PCIe：设备枚举》](http://blog.csdn.net/abcamus/article/details/74853567)


## 一、访问配置空间

相关接口位于drivers/pci/access.c

### 1.1 读配置空间

- pci_read_config_byte(const struct pci_dev *dev, int where, u8 *val);
- pci_read_config_word(const struct pci_dev *dev, int where, u16 *val);
- pci_read_config_dword(const struct pci_dev *dev, int where, u32 *val);

### 1.2 写配置空间
- pci_write_config_byte(const struct pci_dev *dev, int where, u8 *val);
- pci_write_config_word(const struct pci_dev *dev, int where, u16 *val);
- pci_write_config_dword(const struct pci_dev *dev, int where, u32 *val);

## 二、访问BAR空间

在枚举过程中，PCI驱动已经分配了address给各个BAR，通过一些接口就可以访问到BAR Resource。

### 2.1 获取BAR Resource

位于include/linux/pci.h，以宏的形式提供。

- pci_resource_start(dev, bar)
- pci_resource_end(dev, bar)
- pci_resource_flags(dev, bar)
- pci_resource_len(dev, bar)

通过pci_resource_start宏取得bar值之后，Linux认为这个地址是IO地址，如果要访问的话可以通过ioremap映射到内核空间，然后通过readl/writel等IO接口进行操作。