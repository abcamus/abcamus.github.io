---
layout: post
title:  "Linux pinctrl和gpio驱动"
author: Kai Qiu
date:   2017-03-05 23:51:37 +0800
categories: 嵌入式开发
tags: Linux内核 gpio
topics: Linux内核移植
excerpt: exynos 4412平台有很多模块穿插了gpio的控制，譬如usb phy需要gpio来控制提供bus，sdmmc的所有管脚都和gpio复用。gpio作为管脚的一种，现在融合到了pinctrl驱动中，篇文章就介绍一下Linux 4.1版本内核是如何管理gpio的。
---

* menu
{:toc}

> 世上最快乐的事，莫过于为理想而奋斗。 —— 苏格拉底

谨以这句格言送给自己和所有在路上的朋友。

exynos 4412平台有很多模块穿插了gpio的控制，譬如usb phy需要gpio来控制提供vbus，sdmmc的所有管脚都和gpio复用。gpio作为管脚的一种，现在融合到了pinctrl驱动中，这篇文章就介绍一下Linux 4.1版本内核是如何管理gpio的。

## 一 设备树和平台编码的配合

设备树负责组织gpio，但是关于每个bank有多少个gpio口，每个口的地址偏移是多少，内核把这些信息硬编码进了内核（我觉得后面可能还会调整）。
	
### 1.1 pinctrl框架

平台对应的驱动位于drivers/pinctrl/samsung文件夹中，配置都在pinctrl-exynos.c中。

```c
const struct samsung_pin_ctrl exynos4x12_pin_ctrl[] __initconst = {
	{
		/* pin-controller instance 0 data */
		.pin_banks	= exynos4x12_pin_banks0,
		.nr_banks	= ARRAY_SIZE(exynos4x12_pin_banks0),
		.eint_gpio_init = exynos_eint_gpio_init,
		.suspend	= exynos_pinctrl_suspend,
		.resume		= exynos_pinctrl_resume,
	}, {
		/* pin-controller instance 1 data */
		.pin_banks	= exynos4x12_pin_banks1,
		.nr_banks	= ARRAY_SIZE(exynos4x12_pin_banks1),
		.eint_gpio_init = exynos_eint_gpio_init,
		.eint_wkup_init = exynos_eint_wkup_init,
		.suspend	= exynos_pinctrl_suspend,
		.resume		= exynos_pinctrl_resume,
	}, {
		/* pin-controller instance 2 data */
		.pin_banks	= exynos4x12_pin_banks2,
		.nr_banks	= ARRAY_SIZE(exynos4x12_pin_banks2),
		.eint_gpio_init = exynos_eint_gpio_init,
		.suspend	= exynos_pinctrl_suspend,
		.resume		= exynos_pinctrl_resume,
	}, {
		/* pin-controller instance 3 data */
		.pin_banks	= exynos4x12_pin_banks3,
		.nr_banks	= ARRAY_SIZE(exynos4x12_pin_banks3),
		.eint_gpio_init = exynos_eint_gpio_init,
		.suspend	= exynos_pinctrl_suspend,
		.resume		= exynos_pinctrl_resume,
	},
};
```

匹配的id号定义在pinctrl-samsung.c中。

```c
static const struct of_device_id samsung_pinctrl_dt_match[] = {
#ifdef CONFIG_PINCTRL_EXYNOS
	{ .compatible = "samsung,exynos3250-pinctrl",
		.data = (void *)exynos3250_pin_ctrl },
	{ .compatible = "samsung,exynos4210-pinctrl",
		.data = (void *)exynos4210_pin_ctrl },
	{ .compatible = "samsung,exynos4x12-pinctrl",
		.data = (void *)exynos4x12_pin_ctrl },
	{ .compatible = "samsung,exynos4415-pinctrl",
		.data = (void *)exynos4415_pin_ctrl },
	{ .compatible = "samsung,exynos5250-pinctrl",
		.data = (void *)exynos5250_pin_ctrl },
	{ .compatible = "samsung,exynos5260-pinctrl",
		.data = (void *)exynos5260_pin_ctrl },
	{ .compatible = "samsung,exynos5420-pinctrl",
		.data = (void *)exynos5420_pin_ctrl },
	{ .compatible = "samsung,exynos5433-pinctrl",
		.data = (void *)exynos5433_pin_ctrl },
	{ .compatible = "samsung,s5pv210-pinctrl",
		.data = (void *)s5pv210_pin_ctrl },
	{ .compatible = "samsung,exynos7-pinctrl",
		.data = (void *)exynos7_pin_ctrl },
#endif
#ifdef CONFIG_PINCTRL_S3C64XX
	{ .compatible = "samsung,s3c64xx-pinctrl",
		.data = s3c64xx_pin_ctrl },
#endif
#ifdef CONFIG_PINCTRL_S3C24XX
	{ .compatible = "samsung,s3c2412-pinctrl",
		.data = s3c2412_pin_ctrl },
	{ .compatible = "samsung,s3c2416-pinctrl",
		.data = s3c2416_pin_ctrl },
	{ .compatible = "samsung,s3c2440-pinctrl",
		.data = s3c2440_pin_ctrl },
	{ .compatible = "samsung,s3c2450-pinctrl",
		.data = s3c2450_pin_ctrl },
#endif
	{},
};
MODULE_DEVICE_TABLE(of, samsung_pinctrl_dt_match);
```

关键数据结构就是这两个了。下面说明一下gpio信息是如何硬编码进内核的。

### 1.2 gpio编码

gpio的编码信息都保存在这样的结构中。从Exynos4412用户手册中可以看到所有的gpio分为四个部分，每个部分目前就对应这样一个结构。

```c
/* pin banks of exynos4x12 pin-controller 0 */
static const struct samsung_pin_bank_data exynos4x12_pin_banks0[] __initconst = {
	// 该组gpio管脚数量+该组gpio偏移地址+名字+相对于eint配置寄存器(0x700)的偏移
	EXYNOS_PIN_BANK_EINTG(8, 0x000, "gpa0", 0x00),
	EXYNOS_PIN_BANK_EINTG(6, 0x020, "gpa1", 0x04),
	EXYNOS_PIN_BANK_EINTG(8, 0x040, "gpb", 0x08),
	EXYNOS_PIN_BANK_EINTG(5, 0x060, "gpc0", 0x0c),
	EXYNOS_PIN_BANK_EINTG(5, 0x080, "gpc1", 0x10),
	EXYNOS_PIN_BANK_EINTG(4, 0x0A0, "gpd0", 0x14),
	EXYNOS_PIN_BANK_EINTG(4, 0x0C0, "gpd1", 0x18),
	EXYNOS_PIN_BANK_EINTG(8, 0x180, "gpf0", 0x30),
	EXYNOS_PIN_BANK_EINTG(8, 0x1A0, "gpf1", 0x34),
	EXYNOS_PIN_BANK_EINTG(8, 0x1C0, "gpf2", 0x38),
	EXYNOS_PIN_BANK_EINTG(6, 0x1E0, "gpf3", 0x3c),
	EXYNOS_PIN_BANK_EINTG(8, 0x240, "gpj0", 0x40),
	EXYNOS_PIN_BANK_EINTG(5, 0x260, "gpj1", 0x44),
};
```

至于gpio的操作等都很简单，查看一下手册立马就知道了。如果刚更新到新版内核，可能要稍微琢磨一下上面这些结构体是怎么编码的。所以就在这里记录一下吧。希望看到的人能尽快上手。

## 二 gpio调试

关于gpio的知识应该是所有模块最简单的了，基本上熟悉了内核中的驱动框架之后就不会有什么难点了，遇到具体问题去翻一下手册就很容易解决。这里再记录一下内核中调试gpio的几种方法。

- debugfs
  驱动中把gpio相关信息注册进了debugfs，所以我们可以通过挂载debugfs来查看gpio配置。
  
  内核配置：
  ![debugfs.png](https://ooo.0o0.ooo/2017/03/06/58bcc5d95f352.png)
  
  然后mount debugfs，就可以查看管脚映射了。
  
  ```shell
  host # mount -t debugfs none home/debugfs
  host # ls home/debugfs/gpio
106e0000.pinctrl  11400000.pinctrl  pinctrl-devices   pinctrl-maps
11000000.pinctrl  3860000.pinctrl   pinctrl-handles
  ```
  
- sysfs
  也可以sysfs查看gpio配置，首先也要配置内核。
  
  ![sysfs_gpio.png](https://ooo.0o0.ooo/2017/03/06/58bcc7fdc756c.png)
  
  然后就可以在/sys/class/gpio/目录下看到相关信息了。
  
  ```shell
  host # ls /sys/class/gpio
  export       gpiochip14   gpiochip188  gpiochip244  gpiochip36   gpiochip83
gpiochip0    gpiochip143  gpiochip196  gpiochip251  gpiochip40   gpiochip90
gpiochip104  gpiochip148  gpiochip204  gpiochip259  gpiochip48   gpiochip97
gpiochip111  gpiochip156  gpiochip212  gpiochip267  gpiochip56   unexport
gpiochip118  gpiochip164  gpiochip22   gpiochip27   gpiochip64
gpiochip120  gpiochip170  gpiochip220  gpiochip275  gpiochip70
gpiochip128  gpiochip174  gpiochip228  gpiochip283  gpiochip78
gpiochip136  gpiochip180  gpiochip236  gpiochip32   gpiochip8
  ```
  
  现在我们想要点个灯看一下效果，可以这样操作，查看itop Exynos4412硬件原理图可以知道，GPL2[0]对应LED2。GPL[2]在内核中对应gpiochip120(可以通过搜索字符串gpl2或者直接查看源代码知道)。
  
  ```shell
  host # echo 120 > export
  host # echo "out" > gpio120/direction 
  host # echo 1 > gpio120/value
  ```
  
  可以看到LED2亮了。可以通过
  
  ```shell
  host # echo 120 > unexport
  ```
  
  取消映射。

## 三 总结

gpio可以说是最简单的硬件了，如果要对代码进行良好的抽象，保证实用性和可扩展性，却不见得是个简单的东西。总之，有现成的框架，遇到问题多看看手册自然就能迎刃而解。
