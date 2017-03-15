---
layout: post
title:  "Linux USB Host 驱动开发入门 "
date:   2016-10-21 21:22:37 +0800
categories: 嵌入式开发
tags: USB Linux
topics: Linux内核移植
excerpt: 摘要
---

* menu
{:toc}


## 1. 目录结构
下面以当前内核4.1.34为例，介绍usb驱动在内核源码树中的组织方式，不保证各个内核版本都适用，但是基本上每个版本都是一样的。
内核源码中涉及usb驱动的目录：

1. drivers/usb/
该目录为主要的usb驱动目录，所有和usb硬件相关的代码都在这里，还包括部分类协议代码，有对mass storage设备的支持，串口设备的支持。也就是说内核默认支持u盘这类mass storage设备。

2. drivers/media/usb/
该目录代码提供对usb视频设备的支持，uvc驱动位于同名子目录。

3. drivers/net/
这个目录下有提供对usb wireless设备的支持

4. sound/usb/
提供对usb音频设备的支持，实现uac协议

5. 小结
以上目录结构也反映出当前usb接口的主流设备：存储设备，音视频设备和无线设备。拿到新的设备后，就应该知道去哪里找对应的代码了。

## 2. 驱动范例讲解
下面以usb-skeleton.c为例来介绍usb驱动基本实现，注意这里讲的是设备驱动，区别hcd和udc driver，详见第一讲。
在拿到一个usb设备时，如果没有相关驱动可以参考，可以借鉴这个框架实现，文件路径：$KERNEL_ROOT/drivers/usb/usb_skeleton.c
这是第一次涉及代码的讲解，所以讲的比较细一点，进而对一般的驱动也能有个大致的了解，其实驱动本质上都是类似的。

### 2.1 驱动注册
usb驱动注册符合一般设备驱动注册流程，但又有些特殊的地方。这个驱动入口位于

`module_usb_driver(skel_driver) [<linux/usb.h>]`

最终它会调用

`usb_register_driver(&skel_driver, THIS_MODULE, KBUILD_MODNAME)[drivers/usb/core/driver.c]`

这里先分析到 usb/core/ 目录下的相关接口，做一些必要的介绍，暂时忽略usb core内部实现以及内核关于设备注册的细节，到第三讲对usb core里面的代码进行分析，第四讲对内核相关代码进行分析^_^。

usb_register_driver()这个函数做了什么事情呢？初始化和device_driver注册。

首先对skel_driver结构完成初始化，skel_driver中内嵌了一个struct usbdrv_wrap，在struct usbdrv_wrap中又内嵌了一个struct device_driver，最终就是初始化这个device_driver

|type |struct usb_driver |struct usbdrv_wrap | struct device_driver |
:--:|:--:|:--:|:--:
|var |skel_driver |drvwrap  |driver  |

然后调用driver_register()函数进行一系列内核活动，兜了一圈后回到usb/core，调用函数
`usb_probe_interface(struct device *dev)   [drivers/usb/core/driver.c]`
注意函数体里面有这么几句 

``` c
...
struct usb_interface *intf = to_usb_interface(dev);
...
const struct usb_device_id *id;
...
id = usb_match_dynamic_id(intf, driver);
if (!id)
id = usb_match_id(intf, driver->id_table);
if (!id)
return error;
dev_dbg(dev, "%s - got id\n", __func__);
...
error = driver->probe(intf, id);
if (error)
goto err;
...

```

先根据intf变量去id_table中匹配设备id，如果匹配上了，就调用driver->probe(intf, id)，这里就是调用skel_driver->probe，也就是
```c
[usb-skeleton.c]
static int skel_probe(struct usb_interface *interface, const struct usb_device_id *id)
```
这里有个问题：既然通过intf来匹配id，那么intf里面的内容又是从哪里来的呢？_ 这就是usb驱动注册所特有的东西了。相关内容位于第三讲关于usb core的分析中。从这里也可以看出来，对于usb驱动而言，每一个interface对应一个驱动，这就和usb协议对应上了，因为一个interface代表一个function，bingo! Let's move on.
至此，我们可以大胆假设我们的驱动已经和设备id匹配上了，现在位于skel_probe函数中，那接下来做什么工作呢？
首先：初始化一个结构体struct usb_skel *dev
这里要注意一个看代码的习惯，一定要重视内嵌的结构体，比如struct usb_skel中的struct usb_anchor

| struct usb_skel | struct usb_anchor |
:--:|:--:
| dev             | submitted         |

接下来从接口描述符中获取端点描述符,分配端点buffer
然后分配urb
```c
[drivers/usb/core/urb.c]

usb_alloc_urb() 
```

最后注册进文件系统。

```c
usb_register_dev() [drivers/usb/core/file.c]
```

至此设备驱动就注册完成了。细节到第三讲和第四讲再细述。
说明：默认的usb-skeleton驱动只支持同时拥有bulk-in和bulk-out端点的设备

### 2.1 设备操作
在上一步已经把和设备id匹配的驱动注册进了内核，现在就可以通过linux系统调用来操作设备了。
来看看都提供了哪些操作接口：
驱动注册的时候和设备文件绑定了一个操作对象 struct file_operations，至于怎么绑定的，和设备号相关，这里不是重点，暂不细说了。

``` c
static const struct file_operations skel_fops = {
.owner =        THIS_MODULE,
.read =         skel_read,
.write =        skel_write,
.open =         skel_open,
.release =      skel_release,
.flush =        skel_flush,
.llseek =       noop_llseek,
};
```

在应用层触发open系统调用[1]，就会执行到和设备文件对应的open操作，对于skel设备就是skel_open了。其他几个函数也是类似的，skel_read对应read系统调用，skel_write对应write系统调用，skel_release对应close系统调用等等。详情可以参考《UNIX环境高级编程》[2]。
再来看skel_open函数，它有两个参数：(struct inode *inode, struct file *file)
这两个参数是open系统调用最终传递给skel_open的，涉及到文件系统sysfs相关内容，暂且不管。
首先调用接口usb_find_interface(&skel_driver, subminor)                         [drivers/usb/core/usb.c]
找到和skel_driver绑定的次设备号为subminor的设备，这里的设备是指usb interface，前文已有描述。然后从interface中拿到绑定的设备(usb_skel,被保存到file对象中， file->private_data = dev，以后就可以从file中获取usb_skel了)，再调用usb_autopm_get_interface。这个接口和usb interface的管理有关，暂时不细述。
打开，关闭操作一般都是做一些初始化工作，在read，write，ioctl这些接口完成设备功能，下面来看skel_read调用。

```c
static ssize_t skel_read(struct file *file, char *buffer, size_t count, loff_t *ppos)
```

获取设备dev = file->private_data， 关键的地方在于


```c
rv =wait_event_interruptible(dev->bulk_in_wait(!dev->ongoing_read));
```

等待进程被唤醒，然后我们去找哪里会唤醒bulk_in_wait
god!在skel_read_bulk_callback(struct urb *urb)中，这个函数是urb中的一个回调函数，当一次transfer完成时调用，通过
skel_do_read_io->usb_fill_bulk_urb来绑定

## 3 实战演练 

### Footnotes

[1] 系统调用是操作系统提供给应用程序使得进程能够进入到内核环境做一些必要的操作，对应用来讲，有用的其实就只是这些系统调用而已，至于操作系统怎么管理内存，如何调度进程，人家是不关心的。从操作系统的角度来讲，系统调用就是其功能的扩展。它提供这样一种机制，使得在使用者看来具有某些类型的功能。

[2] 《UNIX环境高级编程》

