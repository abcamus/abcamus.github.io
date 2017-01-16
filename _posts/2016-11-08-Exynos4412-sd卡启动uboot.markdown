---
layout: post
title:  "Exynos4412 sd卡启动uboot"
date:   2016-11-08 21:22:37 +0800
categories: 嵌入式开发
tags: exynos4412 sdboot uboot
excerpt: 本文介绍裸机环境下如何编译烧写exynos 4412开发板的uboot
---

* menu
{:toc}

## Exynos4412 uboot烧写

本文介绍裸机环境下如何编译烧写exynos 4412开发板的uboot

### 1. uboot源代码

下载讯为提供的源码压缩包，文件名为iTop4412_uboot_scp_20141224.tar.gz，解压后得到iTop4412_uboot_scp文件夹即可。

### 2. CodeSign4SecureBoot

下载samsung官方提供的CodeSign4SecureBoot压缩包。和iTop4412_uboot_scp文件夹放于同一个目录。

### 3. 制作bl2
 
 在iTop4412_uboot_scp文件中执行
 
 ```shell
 $ make itop_4412_android_config
 $ make
 ```
生成u-boot.bin，然后执行
```sh
$ ./mkbl2 u-boot.bin bl2.bin 14336
```
生成bl2.bin，将生成的bl2.bin拷贝到../CodeSign4SecureBoot中

### 4. 拷贝bl1

将iTop4412_uboot_scp目录下的E4412_N.bl1.bin拷贝到../CodeSign4SecureBoot中，重命名为E4412_N.bl1.SCP2G.bin

### 5. 生成uboot

在iTop4412_uboot_scp目录下执行
```sh
$./create_uboot.sh
```
得到u-boot-iTop-4412.bin

### 6. 烧录到sd卡中

执行
```sh
$sudo ./mkuboot /dev/sdc
```
就得到了可以启动的sd卡

### 7. 从sd卡启动exynos-4412

把sd卡插入开发板卡槽中，启动拨码开关选择10,上电后就从sd卡启动了，顺利打印出log。

![这里写图片描述](http://img.blog.csdn.net/20161108174744527)
