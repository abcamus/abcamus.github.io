---
layout: post
title:  "Linux内核移植：eMMC驱动"
author: Kai Qiu
date:   2017-02-29 00:50:37 +0800
categories: 嵌入式开发
tags: 标签
excerpt: 移植Exynos 4412 eMMC驱动
---

* menu
{:toc}

> 单个的人是软弱无力的，就像漂流的鲁滨孙一样，只有同别人在一起，他才能完成许多事业。 —— 叔本华

内核版本：4.1
硬件平台：迅为exynos 4412开发板

移植eMMC驱动很快就结束了，从exynos4412-trats2.dts中拷贝配置，直接就能工作（删除vmmc-supply属性）。

```shell
mmc@12550000 {
		num-slots = <1>;
		broken-cd;
		non-removable;
		card-detect-delay = <200>;
		vmmc-supply = <&ldo22_reg>;
		clock-frequency = <400000000>;
		samsung,dw-mshc-ciu-div = <0>;
		samsung,dw-mshc-sdr-timing = <2 3>;
		samsung,dw-mshc-ddr-timing = <1 2>;
		pinctrl-0 = <&sd4_clk &sd4_cmd &sd4_bus4 &sd4_bus8>;
		pinctrl-names = "default";
		status = "okay";
		bus-width = <8>;
		cap-mmc-highspeed;
	};
```

### 编译选项

![exynos emmc编译开关](https://ooo.0o0.ooo/2017/03/01/58b5aaed79470.png)

### 启动日志

```shell
[    0.813637] dwmmc_exynos 12550000.mmc: 1 slots initialized
[    0.818063] Registering SWP/SWPB emulation handler
[    0.823968] hctosys: unable to open rtc device (rtc0)
[    0.843223] Warning: unable to open an initial console.
[    0.849600] Freeing unused kernel memory: 3544K (c047a000 - c07f0000)
[    0.886254] mmc1: MAN_BKOPS_EN bit is not set
[    0.890402] mmc_host mmc1: Bus speed (slot 0) = 50000000Hz (slot req 52000000Hz, actual 50000000HZ div = 0)
[    0.899076] mmc_host mmc1: Bus speed (slot 0) = 100000000Hz (slot req 52000000Hz, actual 50000000HZ div = 1)
[    0.908801] mmc1: new DDR MMC card at address 0001
[    0.913998] mmcblk1: mmc1:0001 4YMD3R 3.64 GiB 
[    0.918052] mmcblk1boot0: mmc1:0001 4YMD3R partition 1 4.00 MiB
[    0.923997] mmcblk1boot1: mmc1:0001 4YMD3R partition 2 4.00 MiB
[    0.929893] mmcblk1rpmb: mmc1:0001 4YMD3R partition 3 512 KiB
```
