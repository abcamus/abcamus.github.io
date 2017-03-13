---
layout: post
title:  "Linux内核移植：wifi驱动"
author: Kai Qiu
date:   2017-03-06 21:22:37 +0800
categories: 嵌入式开发
tags: Linux内核 wifi
excerpt: 移植Linux wifi驱动
---

* menu
{:toc}

> 人是生而自由的，但却无往不在枷锁之中。自以为是其他一切的主人的人，反而比其他一切更是奴隶。 —— 卢梭

卢梭的这句话让我想起了《人类简史》中的一段描述，大意是这样的：人类自以为驯服了水稻小麦，春耕秋种，粮食丰收，却因此不得不忍受面朝黄土背朝天的辛劳，到底是谁驯服了谁呢？ 和卢梭的这个观点简直异曲同工。

这次真的是最后一次了，以后相关的东西统统结束，告一段落。照例，最小化理论叙述，直接上手。

## 一 硬件信息

平台依旧采用itop Exynos4412核心板，wifi模块为mt6620，sdio接口，该芯片集802.11n Wi-Fi，bluetooth4.0+HS，GPS和FM收发器于一身。

相关知识：在[移植sdmmc驱动]()一文中已经调通了sdio驱动，这里要根据实际情况做平台相关配置（主要就是管脚配置），[gpio驱动]()我们也已经调试过了。所以工作在于整合wifi驱动，管脚配置，框架兼容。


## 附：源代码列表

```shell
├── arch
│   └── arch_xxx
│       └── mach-xxx
│           └── include
│               └── mach
│                   └── mtk_wcn_cmb_stub.h
├── drivers
│   ├── mmc
│   │   ├── core
│   │   │   └── sdio.c
│   │   └── host
│   │       ├── sdhci.c
│   │       └── sdhci-s3c.c
│   └── mtk_wcn_combo
│       ├── common
│       │   ├── core
│       │   │   ├── btm_core.c
│       │   │   ├── include
│       │   │   │   ├── btm_core.h
│       │   │   │   ├── dbg_core.h
│       │   │   │   ├── psm_core.h
│       │   │   │   ├── stp_core.h
│       │   │   │   ├── stp_dbg.h
│       │   │   │   ├── stp_wmt.h
│       │   │   │   ├── wmt_conf.h
│       │   │   │   ├── wmt_core.h
│       │   │   │   ├── wmt_ctrl.h
│       │   │   │   ├── wmt_dbg.h
│       │   │   │   ├── wmt_func.h
│       │   │   │   ├── wmt_ic.h
│       │   │   │   └── wmt_lib.h
│       │   │   ├── psm_core.c
│       │   │   ├── stp_core.c
│       │   │   ├── stp_dbg.c
│       │   │   ├── wmt_conf.c
│       │   │   ├── wmt_core.c
│       │   │   ├── wmt_ctrl.c
│       │   │   ├── wmt_dbg.c
│       │   │   ├── wmt_func.c
│       │   │   ├── wmt_ic_6620.c
│       │   │   └── wmt_lib.c
│       │   ├── include
│       │   │   ├── core_exp.h
│       │   │   ├── mtk_wcn_cmb_hw.h
│       │   │   ├── osal.h
│       │   │   ├── stp_exp.h
│       │   │   ├── wmt_exp.h
│       │   │   ├── wmt.h
│       │   │   └── wmt_plat.h
│       │   ├── linux
│       │   │   ├── hif_sdio.c
│       │   │   ├── include
│       │   │   │   ├── hif_sdio.h
│       │   │   │   ├── mtk_wcn_cmb_stub.h
│       │   │   │   ├── osal_linux.h
│       │   │   │   ├── osal_typedef.h
│       │   │   │   └── wmt_dev.h
│       │   │   ├── osal.c
│       │   │   ├── stp_chrdev_bt.c
│       │   │   ├── stp_chrdev_gps.c
│       │   │   ├── stp_exp.c
│       │   │   ├── stp_uart.c
│       │   │   ├── wmt_chrdev_wifi.c
│       │   │   ├── wmt_dev.c
│       │   │   └── wmt_exp.c
│       │   ├── Makefile
│       │   └── platform
│       │       └── sample
│       │           ├── mtk_wcn_cmb_hw_6620.c
│       │           ├── mtk_wcn_cmb_stub_sample.c
│       │           └── wmt_plat_sample.c
│       ├── drv_bt
│       │   ├── include
│       │   │   ├── bt_conf.h
│       │   │   └── hci_stp.h
│       │   ├── linux
│       │   │   └── hci_stp.c
│       │   └── Makefile
│       ├── drv_fm
│       │   ├── include
│       │   │   └── fm.h
│       │   ├── Makefile
│       │   ├── private
│       │   │   ├── Makefile
│       │   │   ├── mtk_fm.c
│       │   │   └── mtk_fm.h
│       │   └── public
│       │       ├── Makefile
│       │       ├── mt6620_fm.c
│       │       ├── mt6620_fm.h
│       │       ├── mt6620_fm_lib.c
│       │       ├── mt6620_fm_lib.h
│       │       ├── mt6620_fm_reg.h
│       │       └── mt6620_rds.c
│       ├── drv_wlan
│       │   ├── Makefile
│       │   ├── p2p
│       │   │   ├── common
│       │   │   │   └── wlan_p2p.c
│       │   │   ├── include
│       │   │   │   ├── mgmt
│       │   │   │   │   ├── p2p_assoc.h
│       │   │   │   │   ├── p2p_bss.h
│       │   │   │   │   ├── p2p_fsm.h
│       │   │   │   │   ├── p2p_func.h
│       │   │   │   │   ├── p2p_ie.h
│       │   │   │   │   ├── p2p_rlm.h
│       │   │   │   │   ├── p2p_rlm_obss.h
│       │   │   │   │   ├── p2p_scan.h
│       │   │   │   │   └── p2p_state.h
│       │   │   │   ├── nic
│       │   │   │   │   ├── p2p_cmd_buf.h
│       │   │   │   │   ├── p2p.h
│       │   │   │   │   ├── p2p_mac.h
│       │   │   │   │   ├── p2p_nic_cmd_event.h
│       │   │   │   │   └── p2p_nic.h
│       │   │   │   ├── p2p_precomp.h
│       │   │   │   └── wlan_p2p.h
│       │   │   ├── Makefile
│       │   │   ├── mgmt
│       │   │   │   ├── p2p_assoc.c
│       │   │   │   ├── p2p_bss.c
│       │   │   │   ├── p2p_fsm.c
│       │   │   │   ├── p2p_func.c
│       │   │   │   ├── p2p_ie.c
│       │   │   │   ├── p2p_rlm.c
│       │   │   │   ├── p2p_rlm_obss.c
│       │   │   │   ├── p2p_scan.c
│       │   │   │   └── p2p_state.c
│       │   │   ├── nic
│       │   │   │   └── p2p_nic.c
│       │   │   └── os
│       │   │       └── linux
│       │   │           ├── gl_p2p.c
│       │   │           ├── gl_p2p_cfg80211.c
│       │   │           ├── gl_p2p_init.c
│       │   │           ├── gl_p2p_kal.c
│       │   │           └── include
│       │   │               ├── gl_p2p_ioctl.h
│       │   │               ├── gl_p2p_kal.h
│       │   │               └── gl_p2p_os.h
│       │   └── wlan
│       │       ├── common
│       │       │   ├── dump.c
│       │       │   ├── wlan_bow.c
│       │       │   ├── wlan_lib.c
│       │       │   └── wlan_oid.c
│       │       ├── include
│       │       │   ├── CFG_Wifi_File.h
│       │       │   ├── config.h
│       │       │   ├── debug.h
│       │       │   ├── link.h
│       │       │   ├── mgmt
│       │       │   │   ├── aa_fsm.h
│       │       │   │   ├── ais_fsm.h
│       │       │   │   ├── assoc.h
│       │       │   │   ├── auth.h
│       │       │   │   ├── bow_fsm.h
│       │       │   │   ├── bss.h
│       │       │   │   ├── cnm.h
│       │       │   │   ├── cnm_mem.h
│       │       │   │   ├── cnm_scan.h
│       │       │   │   ├── cnm_timer.h
│       │       │   │   ├── hem_mbox.h
│       │       │   │   ├── mib.h
│       │       │   │   ├── privacy.h
│       │       │   │   ├── rate.h
│       │       │   │   ├── rlm_domain.h
│       │       │   │   ├── rlm.h
│       │       │   │   ├── rlm_obss.h
│       │       │   │   ├── rlm_protection.h
│       │       │   │   ├── roaming_fsm.h
│       │       │   │   ├── rsn.h
│       │       │   │   ├── scan.h
│       │       │   │   ├── sec_fsm.h
│       │       │   │   ├── swcr.h
│       │       │   │   ├── wapi.h
│       │       │   │   └── wlan_typedef.h
│       │       │   ├── nic
│       │       │   │   ├── adapter.h
│       │       │   │   ├── bow.h
│       │       │   │   ├── cmd_buf.h
│       │       │   │   ├── hal.h
│       │       │   │   ├── hif_emu.h
│       │       │   │   ├── hif_rx.h
│       │       │   │   ├── hif_tx.h
│       │       │   │   ├── mac.h
│       │       │   │   ├── mt5931_reg.h
│       │       │   │   ├── mt6620_reg.h
│       │       │   │   ├── nic.h
│       │       │   │   ├── nic_rx.h
│       │       │   │   ├── nic_tx.h
│       │       │   │   ├── que_mgt.h
│       │       │   │   └── wlan_def.h
│       │       │   ├── nic_cmd_event.h
│       │       │   ├── nic_init_cmd_event.h
│       │       │   ├── p2p_typedef.h
│       │       │   ├── precomp.h
│       │       │   ├── pwr_mgt.h
│       │       │   ├── queue.h
│       │       │   ├── rftest.h
│       │       │   ├── typedef.h
│       │       │   ├── wlan_bow.h
│       │       │   ├── wlan_lib.h
│       │       │   └── wlan_oid.h
│       │       ├── Makefile
│       │       ├── mgmt
│       │       │   ├── aaa_fsm.c
│       │       │   ├── ais_fsm.c
│       │       │   ├── assoc.c
│       │       │   ├── auth.c
│       │       │   ├── bss.c
│       │       │   ├── cnm.c
│       │       │   ├── cnm_mem.c
│       │       │   ├── cnm_timer.c
│       │       │   ├── hem_mbox.c
│       │       │   ├── mib.c
│       │       │   ├── privacy.c
│       │       │   ├── rate.c
│       │       │   ├── rlm.c
│       │       │   ├── rlm_domain.c
│       │       │   ├── rlm_obss.c
│       │       │   ├── rlm_protection.c
│       │       │   ├── roaming_fsm.c
│       │       │   ├── rsn.c
│       │       │   ├── saa_fsm.c
│       │       │   ├── scan.c
│       │       │   ├── scan_fsm.c
│       │       │   ├── sec_fsm.c
│       │       │   ├── swcr.c
│       │       │   └── wapi.c
│       │       ├── nic
│       │       │   ├── cmd_buf.c
│       │       │   ├── nic.c
│       │       │   ├── nic_cmd_event.c
│       │       │   ├── nic_pwr_mgt.c
│       │       │   ├── nic_rx.c
│       │       │   ├── nic_tx.c
│       │       │   └── que_mgt.c
│       │       └── os
│       │           ├── linux
│       │           │   ├── gl_bow.c
│       │           │   ├── gl_init.c
│       │           │   ├── gl_kal.c
│       │           │   ├── gl_proc.c
│       │           │   ├── gl_rst.c
│       │           │   ├── gl_wext.c
│       │           │   ├── gl_wext_priv.c
│       │           │   ├── hif
│       │           │   │   └── sdio
│       │           │   │       ├── arm.c
│       │           │   │       ├── include
│       │           │   │       │   ├── hif.h
│       │           │   │       │   ├── hif_sdio.h
│       │           │   │       │   └── mtk_porting.h
│       │           │   │       ├── sdio.c
│       │           │   │       └── x86.c
│       │           │   ├── include
│       │           │   │   ├── gl_kal.h
│       │           │   │   ├── gl_os.h
│       │           │   │   ├── gl_rst.h
│       │           │   │   ├── gl_sec.h
│       │           │   │   ├── gl_typedef.h
│       │           │   │   ├── gl_wext.h
│       │           │   │   └── gl_wext_priv.h
│       │           │   └── platform.c
│       │           └── version.h
│       ├── gps
│       │   ├── gps.c
│       │   └── Makefile
│       ├── Kconfig
│       └── Makefile
├── include
│   ├── kernel_2.6.39
│   │   └── net
│   │       └── cfg80211.h
│   └── kernel_3.0.8
│       └── net
│           └── cfg80211.h
├── net
│   ├── bluetooth
│   │   ├── kernel_2.6.39
│   │   │   └── hci_core.c
│   │   └── kernel_3.0.8
│   │       └── hci_core.c
│   └── wireless
│       ├── kernel_2.6.39
│       │   ├── Kconfig
│       │   ├── mlme.c
│       │   ├── nl80211.c
│       │   └── nl80211.h
│       └── kernel_3.0.8
│           ├── Kconfig
│           └── nl80211.c
└── readme.txt
```
