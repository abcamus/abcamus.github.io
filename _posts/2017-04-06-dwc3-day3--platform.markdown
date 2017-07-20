---
layout: post
title:  "dwc3 day3--platform"
author: Kai Qiu
date:   2017-04-06 22:22:37 +0800
categories: 嵌入式开发
tags: usb3.0
topics: usb3.0开发指南
excerpt: 介绍如何把验证套件移植到具体的平台上
---

* menu
{:toc}

> 浪费时间是一桩大罪过。 —— 卢梭

这篇文章介绍如何将dwc3验证套件应用到自己的平台上，基本上算是使用手册吧。

## 一、构建usb验证项目

把整个dwc3_portable项目拷贝到自己的验证环境中，在自己的Makefile中指定编译目标，比如

```shell
DWC3_DIR := dwc3_portable
DWC3_SRC += $(DWC3_DIR)/usb.c \
	$(DWC3_DIR)/host/xhci.c \
	$(DWC3_DIR)/host/xhci-dwc3.c \
	$(DWC3_DIR)/host/xhci-mem.c \
	$(DWC3_DIR)/host/xhci-ring.c \
	(补全)
OBJS += $(DWC3_SRC:%.c=%.o)
```

执行make后进行编译，排查编译错误，一般都是配置的问题。根据自己的平台修改根目录下的dwc3portconfig.h文件。

## 二、平台调试

根据自己的平台交互接口，修改debug等函数实现。

## 三、执行流程

在usb.c中根据是否是`LOCAL_SIM`定义了不同的入口，如果是嵌入式平台，则入口是`start_usb`（代码中暂时还都是main，是为了本地编译测试的时候不报warning）。

### 3.1 初始化和设备识别

`usb_init`: 进行usb3.0控制器的初始化。
   |--`usb_lowlevel_init`: 映射寄存器地址，reset控制器，以及一些关键数据结构分配。
   |--`usb_new_device`: 枚举设备（控制传输测试）。

### 3.2 传输测试

参见usb.c相关接口，细节还有待实现，在下一次介绍。

## 四、后续工作

1. 几种传输方式的测试接口
2. gadget和otg模式测试
