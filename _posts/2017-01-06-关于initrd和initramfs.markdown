---
layout: post
title:  "关于initrd和initramfs"
date:   2017-01-06 21:22:37 +0800
categories: 嵌入式开发
tags: initrd initramfs 文件系统
topics: Linux内核移植
excerpt: ram disk中的file system叫做initrd，全名叫做initial ramdisk。如何创建initial ramisk? 如何配置以及如何使用呢？这篇文章讲的就是这些
---
* titles
{:toc}

## 一、initrd
ram disk中的file system叫做initrd，全名叫做initial ramdisk。

>注意: 当下用initrams多

### 如何创建initial ramisk

```shell
host > dd if=/dev/zero of=/dev/ram0 bs=1k count=<count>
host > mke2fs -vm0 /dev/ram0 <count>
host > tune2fs -c 0 /dev/ram0
host > dd if=/dev/ram0 bs=1k count=<count> | gzip -v9 > ramdisk.gz
```

这段代码就创建了大小为count的ramdisk

### 创建完之后还要添加哪些东西
还要添加一些必要的文件让他工作，可能是库，应用程序等。例如busybox。

```shell
host $ mkdir mnt
host $ gunzip ramdisk.gz
host $ mount -o loop ramdisk mnt/
host $ ... copy stuff you want to have in ramdisk to mnt...
host $ umount mnt
host $ gzip -v9 ramdisk
```

### 内核如何支持initial ramdisk

```shell
#
# General setup
#
...
CONFIG_BLK_DEV_INITRD=y
CONFIG_INITRAMFS_SOURCE=""
...

#
# UBI - Unsorted block images
#
...
CONFIG_BLK_DEV_RAM=y
CONFIG_BLK_DEV_RAM_COUNT=1
CONFIG_BLK_DEV_RAM_SIZE=8192
CONFIG_BLK_DEV_RAM_BLOCKSIZE=1024
...
```

### 告诉uboot怎么找到她

```shell
UBOOT # tftp 0x87000000 ramdisk.gz
UBOOT # erase 0x2200000 +0x<filesize>
UBOOT # cp.b 0x87000000 0x2200000 0x<filesize>

UBOOT # setenv bootargs ... root=/dev/ram0 rw initrd=0x87000000,8M
UBOOT # setenv bootcmd cp.b 0x2200000 0x87000000 0x<filesize>; bootm
UBOOT # saveenv
```

>注意： ramdisk 中要有ram0节点

```shell
brw-rw---- 1 root disk 1, 0 Sep 11 1999 /dev/ram0
```

### 最后启动内核

## 二、initramfs
initramfs相当于把initrd放进了内核，通过cpio（这是一个文件处理工具）实现。

### 如何创建
比initrd简单多了

```shell
host > mkdir target_fs
host > ... copy stuff you want to have in initramfs to target_fs...
```

>注意： 
>1. initramfs中的cpio系统不能处理hard link，用soft link
>2. 顶层必须有个init程序，这是kernel要用的，可以这么做

```shell
/init -> /bin/busybox
```

接着

```shell
host > cd target_fs
host > find . | cpio -H newc -o > ../target_fs.cpio
```

### 内核支持

```shell
#
# General setup
#
...
CONFIG_BLK_DEV_INITRD=y
CONFIG_INITRAMFS_SOURCE="<path_to>/target_fs>"
...

#
# UBI - Unsorted block images
#
...
CONFIG_BLK_DEV_RAM=y
CONFIG_BLK_DEV_RAM_COUNT=1
CONFIG_BLK_DEV_RAM_SIZE=8192
CONFIG_BLK_DEV_RAM_BLOCKSIZE=1024
```

然后执行make uImage的时候就被包含到kernel中了。

### uboot支持

因为已经在kernel中了，不需要像initrd一样通过参数 root=/xxx rw initrd=xxx来告诉uboot了

## 三、比较

1. initrd方式中kernel和initial file system为独立的部分，互不影响，下载的时候镜像也小。
2. 创建修改initramfs比initrd容易。
3. 在烧写的时候，显然一个镜像更容易管理。

#### 参考文献
[Initrd Wiki]

[Initrd Wiki]: http://processors.wiki.ti.com/index.php/Initrd
