---
layout: post
title:  "Linux loop设备"
date:   2016-09-20 21:22:37 +0800
categories: 嵌入式开发
tags: Linux
excerpt: 摘要
---

* menu
{:toc}

## loop设备介绍
Linux中，loop设备是一种伪设备，和真正的文件绑定后就像真正的设备一样工作。譬如，我们在安装iso镜像的软件时，常设置为loop设备，然后再把loop设备挂载到文件系统内。

Linux系统中的loop设备如下所示：

```sh
host > ls /dev/loop*
/dev/loop0  /dev/loop2  /dev/loop4  /dev/loop6  /dev/loop-control
/dev/loop1  /dev/loop3  /dev/loop5  /dev/loop7
```

## 使用loop设备

```sh
host > dd if=/dev/zero of=system.img bs=1M count=100
host > mke2fs system.img
host > sudo losetup /dev/loop0 system.img
host > mount /dev/loop0 mount_dir
```

这时在mount_dir目录下就可以访问system.img镜像了。
