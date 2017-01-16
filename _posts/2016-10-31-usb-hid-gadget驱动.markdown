---
layout: post
title:  "usb hid gadget驱动 "
date:   2016-10-31 21:22:37 +0800
categories: 嵌入式开发
tags: USB hid gadget Linux
excerpt: 因为usb gadget驱动在实际应用中比较少见，通常usb口主要就两个功能，一是供电；二是接外部设备。而且如果是开发usb设备的话，很多是通过usb设备芯片配合firmware来提供成熟的解决方案，所以写这篇文章，以hid gadget驱动为例，来记录usb gadget驱动的开发使用过程。
---

* menu
{:toc}

因为usb gadget驱动在实际应用中比较少见，通常usb口主要就两个功能，一是供电；二是接外部设备。而且如果是开发usb设备的话，很多是通过usb设备芯片配合firmware来提供成熟的解决方案，所以写这篇文章，以hid gadget驱动为例，来记录usb gadget驱动的开发使用过程。

## 一. usb gadget框架层次
*****************
usb gadget是通过驱动来使usb控制器扮演特定设备。为了方便，下面就把usb gadget简称为ugadget了。
ugadget分为三个层次，示例图如下：

![这里写图片描述](http://img.blog.csdn.net/20161031114156272)

对应的代码位于（以kernel 4.x为例）：

|层次		|位置|
--|--
驱动层		|usb/gadget/legacy/*
复合层		|usb/gadget下composite.c以及usb/gadget/function/*
控制器驱动	|usb/gadget/udc/*

### 1.1 驱动层

驱动层定义不同平台相关的驱动配置，然后负责和复合层进行交互，交互通过`struct usb_composite_driver`完成。

```cpp
include/linux/usb/composite.h

struct usb_composite_driver {
	const char				*name;
	const struct usb_device_descriptor	*dev;
	struct usb_gadget_strings		**strings;
	enum usb_device_speed			max_speed;
	unsigned		needs_serial:1;

	int			(*bind)(struct usb_composite_dev *cdev);
	int			(*unbind)(struct usb_composite_dev *);

	void			(*disconnect)(struct usb_composite_dev *);

	/* global suspend hooks */
	void			(*suspend)(struct usb_composite_dev *);
	void			(*resume)(struct usb_composite_dev *);
	struct usb_gadget_driver		gadget_driver;
};
```

### 1.2 复合层
复合层起到承上启下的作用，对上(驱动层)提供驱动接口，对下负责管理usb配置以及功能，所有function目录下的接口可以认为是供composite层调用的库。function目录汇集了很多功能层的接口代码，hid对应的文件为f_hid.c，其中必须实例化`struct usb_function`类型的结构体:

```cpp
struct usb_function {
	const char			*name;
	/*字符串描述符*/
	struct usb_gadget_strings	**strings;
	/*全速，高速，超速设备描述符*/
	struct usb_descriptor_header	**fs_descriptors;
	struct usb_descriptor_header	**hs_descriptors;
	struct usb_descriptor_header	**ss_descriptors;

	/*配置描述*/
	struct usb_configuration	*config;

	/*os相关描述*/
	struct usb_os_desc_table	*os_desc_table;
	unsigned			os_desc_n;

	/* REVISIT:  bind() functions can be marked __init, which
	 * makes trouble for section mismatch analysis.  See if
	 * we can't restructure things to avoid mismatching.
	 * Related:  unbind() may kfree() but bind() won't...
	 */

	/* configuration management:  bind/unbind */
	int			(*bind)(struct usb_configuration *,
					struct usb_function *);
	void			(*unbind)(struct usb_configuration *,
					struct usb_function *);
	void			(*free_func)(struct usb_function *f);
	struct module		*mod;

	/* runtime state management */
	int			(*set_alt)(struct usb_function *,
					unsigned interface, unsigned alt);
	int			(*get_alt)(struct usb_function *,
					unsigned interface);
	void			(*disable)(struct usb_function *);
	int			(*setup)(struct usb_function *,
					const struct usb_ctrlrequest *);
	bool			(*req_match)(struct usb_function *,
					const struct usb_ctrlrequest *);
	void			(*suspend)(struct usb_function *);
	void			(*resume)(struct usb_function *);

	/* USB 3.0 additions */
	int			(*get_status)(struct usb_function *);
	int			(*func_suspend)(struct usb_function *,
						u8 suspend_opt);
	/* private: */
	/* internals */
	struct list_head		list;
	DECLARE_BITMAP(endpoints, 32);
	const struct usb_function_instance *fi;

	unsigned int		bind_deactivated:1;
};
```

提供了字符设备相关的操作接口，定义在`struct file_operation`中，如下所示：

```cpp
static const struct file_operations f_hidg_fops = {
	.owner		= THIS_MODULE,
	.open		= f_hidg_open,
	.release	= f_hidg_release,
	.write		= f_hidg_write,
	.read		= f_hidg_read,
	.poll		= f_hidg_poll,
	.llseek		= noop_llseek,
};
```

### 1.3 控制器驱动层
核心代码位于usb/gadget/udc/udc-core.c，负责管理不同平台的gadget device，相关结构定义为

```cpp
include/linux/usb/gadget.h

struct usb_gadget {
	struct work_struct		work;
	struct usb_udc			*udc;
	/* readonly to gadget driver */
	const struct usb_gadget_ops	*ops;
	struct usb_ep			*ep0;
	struct list_head		ep_list;	/* of usb_ep */
	enum usb_device_speed		speed;
	enum usb_device_speed		max_speed;
	enum usb_device_state		state;
	const char			*name;
	struct device			dev;
	unsigned			out_epnum;
	unsigned			in_epnum;
	struct usb_otg_caps		*otg_caps;

	unsigned			sg_supported:1;
	unsigned			is_otg:1;
	unsigned			is_a_peripheral:1;
	unsigned			b_hnp_enable:1;
	unsigned			a_hnp_support:1;
	unsigned			a_alt_hnp_support:1;
	unsigned			quirk_ep_out_aligned_size:1;
	unsigned			quirk_altset_not_supp:1;
	unsigned			quirk_stall_not_supp:1;
	unsigned			quirk_zlp_not_supp:1;
	unsigned			is_selfpowered:1;
	unsigned			deactivated:1;
	unsigned			connected:1;
};
```

以Marvell USB Controller为例，udc初始化入口为

```cpp
usb/gadget/udc/mv_udc_core.c

/*mv_udc_probe*/
retval = usb_add_gadget_udc_release(&pdev->dev, &udc->gadget,
			gadget_release);
	if (retval)
		goto err_create_workqueue;
```
其他类似的管理接口还有
```cpp
void usb_gadget_udc_reset(struct usb_gadget *gadget,
		struct usb_gadget_driver *driver);
static inline int usb_gadget_udc_start(struct usb_udc *udc);
...
...
```

可以看到udc层实际上有两个任务

1. 用来管理不同平台的gadget device。
2. 通过绑定gadget driver实例来为复合层提供服务。

## 二. 初始化流程
----------------------

### 2.1 驱动层介绍
gadget驱动通过调用ugadget框架对应接口来进行初始化，所有的gadget驱动目前位于`usb/gadget/legacy`目录下。

legacy目录一览：

|文件				|实现功能|
:----:|:----:
webcam.c			|usb摄像头
hid.c				|hid设备
serial.c			|串口设备
ether.c				|网络设备
mass_storage.c		|存储设备
audio.c				|音频设备
printer.c			|打印机
zero.c				|一个假设备，主要用来参考

现在来看hid设备对应的驱动文件hid.c
### 2.2 hidg驱动初始化详解
初始化分为两部分：首先按照驱动层级从上至下的绑定相关结构体，然后再自下而上进行具体的结构体初始化。
#### 2.1 至上而下遍历：搜索绑定驱动和设备
驱动的入口为

```cpp
usb/gadget/legacy/hid.c

static struct usb_composite_driver hidg_driver = {
	.name		= "g_hid",
	.dev		= &device_desc,
	.strings	= dev_strings,
	.max_speed	= USB_SPEED_HIGH,
	.bind		= hid_bind,
	.unbind		= hid_unbind,
};

static int __init hidg_init(void)
{
	int status;

	/*定义平台相关设备，在hidg_plat_driver_probe中绑定hid类协议参数，包括绑定报告描述符*/
	status = platform_driver_probe(&hidg_plat_driver,
				hidg_plat_driver_probe);
	if (status < 0)
		return status;
	
	/*进入到复合设备层， hidg_driver为struct composite_driver类型*/
	status = usb_composite_probe(&hidg_driver);
	if (status < 0)
		platform_driver_unregister(&hidg_plat_driver);

	return status;
}
```

进入到usb_composite_probe之后，对composite_driver和gadget_driver进行绑定，然后通过usb_gadget_probe_driver进入udc层，来绑定udc和gadget driver

```cpp
usb/gadget/composite.c
	...
	/*这里的赋值是结构体赋值*/
	driver->gadget_driver = composite_driver_template;
	gadget_driver = &driver->gadget_driver;

	gadget_driver->function =  (char *) driver->name;
	gadget_driver->driver.name = driver->name;
	gadget_driver->max_speed = driver->max_speed;

	return usb_gadget_probe_driver(gadget_driver);
```

进入udc层后，首先根据驱动名字来匹配udc

```cpp
usb/gadget/udc/udc-core.c
...
mutex_lock(&udc_lock);
	if (driver->udc_name) {
		list_for_each_entry(udc, &udc_list, list) {
			ret = strcmp(driver->udc_name, dev_name(&udc->dev));
			if (!ret)
				break;
		}
		if (!ret && !udc->driver)
			goto found;
	} else {
		list_for_each_entry(udc, &udc_list, list) {
			/* For now we take the first one */
			if (!udc->driver)
				goto found;
		}
	}
```

匹配完成后进行绑定

```cpp
found:
	ret = udc_bind_to_driver(udc, driver);
```

注意，此时的driver为复合层composite.c提供的gadget driver模板

```cpp
static const struct usb_gadget_driver composite_driver_template = {
	.bind		= composite_bind,
	.unbind		= composite_unbind,

	.setup		= composite_setup,
	.reset		= composite_disconnect,
	.disconnect	= composite_disconnect,

	.suspend	= composite_suspend,
	.resume		= composite_resume,

	.driver	= {
		.owner		= THIS_MODULE,
	},
};
```

`udc_bind_to_driver`通过回调driver->bind进行复合层的初始化，代码如下，复合层初始化结束之后enable USB控制器。

```cpp
/*driver is composite_driver_template，开始回调*/
ret = driver->bind(udc->gadget, driver);
	if (ret)
		goto err1;
	/*start USB Device Controller*/
	ret = usb_gadget_udc_start(udc);
	if (ret) {
		driver->unbind(udc->gadget);
		goto err1;
	}
	usb_udc_connect_control(udc);
```

#### 2.2 至下而上遍历：完成初始化
通过一系列的回调进行结构体的初始化，首先就是udc-core中driver->bind，对应的接口是

```cpp
usb/gadget/composite.c

static int composite_bind(struct usb_gadget *gadget,
		struct usb_gadget_driver *gdriver)
		{
	struct usb_composite_dev	*cdev;
	struct usb_composite_driver	*composite = to_cdriver(gdriver);
	int				status = -ENOMEM;

	cdev = kzalloc(sizeof *cdev, GFP_KERNEL);
	if (!cdev)
		return status;

	spin_lock_init(&cdev->lock);
	cdev->gadget = gadget;
	set_gadget_data(gadget, cdev);
	INIT_LIST_HEAD(&cdev->configs);
	INIT_LIST_HEAD(&cdev->gstrings);

	/*初始化复合设备，包括分配用来响应usb标准请求的request和buffer，创建设备文件，reset配置*/
	status = composite_dev_prepare(composite, cdev);
	if (status)
		goto fail;

	/* composite gadget needs to assign strings for whole device (like
	 * serial number), register function drivers, potentially update
	 * power state and consumption, etc
	 */
	status = composite->bind(cdev);
	if (status < 0)
		goto fail;

	if (cdev->use_os_string) {
		status = composite_os_desc_req_prepare(cdev, gadget->ep0);
		if (status)
			goto fail;
	}

	update_unchanged_dev_desc(&cdev->desc, composite->dev);

	/* has userspace failed to provide a serial number? */
	if (composite->needs_serial && !cdev->desc.iSerialNumber)
		WARNING(cdev, "userspace failed to provide iSerialNumber\n");

	INFO(cdev, "%s ready\n", composite->name);
	return 0;

fail:
	__composite_unbind(gadget, false);
	return status;
}
```

在composite_bind获取第一步初始化时绑定的struct usb_composite_driver，回调composite->bind，此处的bind具体为

```cpp
usb/gadget/legacy/hid.c		hidg_driver->bind

static int hid_bind(struct usb_composite_dev *cdev)
{
	struct usb_gadget *gadget = cdev->gadget;
	struct list_head *tmp;
	struct hidg_func_node *n, *m;
	struct f_hid_opts *hid_opts;
	int status, funcs = 0;

	/*probe平台设备时候添加的function对象*/
	list_for_each(tmp, &hidg_func_list)
		funcs++;

	if (!funcs)
		return -ENODEV;

	list_for_each_entry(n, &hidg_func_list, node) {
		/*搜索功能function实例，在f_hid中初始化，初始化接口位于usb/gadget/functions.c*/
		n->fi = usb_get_function_instance("hid");
		if (IS_ERR(n->fi)) {
			status = PTR_ERR(n->fi);
			goto put;
		}
		/*把function实例和platform specific配置进行绑定*/
		hid_opts = container_of(n->fi, struct f_hid_opts, func_inst);
		hid_opts->subclass = n->func->subclass;
		hid_opts->protocol = n->func->protocol;
		hid_opts->report_length = n->func->report_length;
		hid_opts->report_desc_length = n->func->report_desc_length;
		hid_opts->report_desc = n->func->report_desc;
	}

	/* Allocate string descriptor numbers ... note that string
	 * contents can be overridden by the composite_dev glue.
	 */

	status = usb_string_ids_tab(cdev, strings_dev);
	if (status < 0)
		goto put;
	device_desc.iManufacturer = strings_dev[USB_GADGET_MANUFACTURER_IDX].id;
	device_desc.iProduct = strings_dev[USB_GADGET_PRODUCT_IDX].id;

	if (gadget_is_otg(gadget) && !otg_desc[0]) {
		struct usb_descriptor_header *usb_desc;

		usb_desc = usb_otg_descriptor_alloc(gadget);
		if (!usb_desc)
			goto put;
		usb_otg_descriptor_init(gadget, usb_desc);
		otg_desc[0] = usb_desc;
		otg_desc[1] = NULL;
	}

	/* register our configuration */
	status = usb_add_config(cdev, &config_driver, do_config);
	if (status < 0)
		goto free_otg_desc;

	usb_composite_overwrite_options(cdev, &coverwrite);
	dev_info(&gadget->dev, DRIVER_DESC ", version: " DRIVER_VERSION "\n");

	return 0;

free_otg_desc:
	kfree(otg_desc[0]);
	otg_desc[0] = NULL;
put:
	list_for_each_entry(m, &hidg_func_list, node) {
		if (m == n)
			break;
		usb_put_function_instance(m->fi);
	}
	return status;
}
```

在复合层绑定的过程中，最关键的是通过

```cpp
status = usb_add_config(cdev, &config_driver, do_config);
	if (status < 0)
		goto free_otg_desc;
```

进行配置的初始化，配置完成之后，这个ugadget就具有hid的功能了。

```cpp
int usb_add_config(struct usb_composite_dev *cdev,
		struct usb_configuration *config,
		int (*bind)(struct usb_configuration *))
{
	int				status = -EINVAL;

	if (!bind)
		goto done;

	DBG(cdev, "adding config #%u '%s'/%p\n",
			config->bConfigurationValue,
			config->label, config);

	/*把config交给cdev管理*/
	status = usb_add_config_only(cdev, config);
	if (status)
		goto done;

	/*do_config, 往config中添加function*/
	status = bind(config);
	if (status < 0) {
		/*绑定config和function失败*/
		while (!list_empty(&config->functions)) {
			struct usb_function		*f;

			f = list_first_entry(&config->functions,
					struct usb_function, list);
			list_del(&f->list);
			if (f->unbind) {
				DBG(cdev, "unbind function '%s'/%p\n",
					f->name, f);
				f->unbind(config, f);
				/* may free memory for "f" */
			}
		}
		list_del(&config->list);
		config->cdev = NULL;
	} else {
		/*绑定成功，报告配置信息*/
		unsigned	i;

		DBG(cdev, "cfg %d/%p speeds:%s%s%s\n",
			config->bConfigurationValue, config,
			config->superspeed ? " super" : "",
			config->highspeed ? " high" : "",
			config->fullspeed
				? (gadget_is_dualspeed(cdev->gadget)
					? " full"
					: " full/low")
				: "");

		for (i = 0; i < MAX_CONFIG_INTERFACES; i++) {
			struct usb_function	*f = config->interface[i];

			if (!f)
				continue;
			DBG(cdev, "  interface %d = %s/%p\n",
				i, f->name, f);
		}
	}

	/* set_alt(), or next bind(), sets up ep->claimed as needed */
	usb_ep_autoconfig_reset(cdev->gadget);

done:
	if (status)
		DBG(cdev, "added config '%s'/%u --> %d\n", config->label,
				config->bConfigurationValue, status);
	return status;
}
```

最后一步绑定的关键在于上面的bind回调，也就是do_config函数

```cpp
usb/gadget/legacy/hid.c

static int do_config(struct usb_configuration *c)
{
	struct hidg_func_node *e, *n;
	int status = 0;

	if (gadget_is_otg(c->cdev->gadget)) {
		c->descriptors = otg_desc;
		c->bmAttributes |= USB_CONFIG_ATT_WAKEUP;
	}

	list_for_each_entry(e, &hidg_func_list, node) {
		e->f = usb_get_function(e->fi);
		if (IS_ERR(e->f))
			goto put;
		/*向config中添加function*/
		status = usb_add_function(c, e->f);
		if (status < 0) {
			usb_put_function(e->f);
			goto put;
		}
	}

	return 0;
put:
	list_for_each_entry(n, &hidg_func_list, node) {
		if (n == e)
			break;
		usb_remove_function(c, n->f);
		usb_put_function(n->f);
	}
	return status;
}
```

do_config通过usb_add_dunction完成config和function的绑定

```cpp
usb/gadget/composite.c

int usb_add_function(struct usb_configuration *config,
		struct usb_function *function)
{
	int	value = -EINVAL;

	DBG(config->cdev, "adding '%s'/%p to config '%s'/%p\n",
			function->name, function,
			config->label, config);

	if (!function->set_alt || !function->disable)
		goto done;

	function->config = config;
	list_add_tail(&function->list, &config->functions);

	if (function->bind_deactivated) {
		value = usb_function_deactivate(function);
		if (value)
			goto done;
	}

	/* REVISIT *require* function->bind? */
	if (function->bind) {
		value = function->bind(config, function);
		if (value < 0) {
			list_del(&function->list);
			function->config = NULL;
		}
	} else
		value = 0;

	/* We allow configurations that don't work at both speeds.
	 * If we run into a lowspeed Linux system, treat it the same
	 * as full speed ... it's the function drivers that will need
	 * to avoid bulk and ISO transfers.
	 */
	if (!config->fullspeed && function->fs_descriptors)
		config->fullspeed = true;
	if (!config->highspeed && function->hs_descriptors)
		config->highspeed = true;
	if (!config->superspeed && function->ss_descriptors)
		config->superspeed = true;

done:
	if (value)
		DBG(config->cdev, "adding '%s'/%p --> %d\n",
				function->name, function, value);
	return value;
}
```

这里通过function->bind完成最终usb function的初始化。function->bind指向

```cpp
usb/gadget/function/f_hid.c

/*	
 *	分配interrupt-in端点和interrupt-out端点；
 *	配置接口描述符和端点描述符;
 *	注册字符设备 
 */
static int hidg_bind(struct usb_configuration *c, struct usb_function *f);
```

至此，一个hid gadget就添加完成了，操作系统可以看到一个hidg设备文件。

## 三. hid gadget应用
关于如何应用可以参考kernel/Documentation/usb/gadget_hid.txt

这里摘出了其中的Sample code部分，以供参考。

```cpp
/* hid_gadget_test */

#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <ctype.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define BUF_LEN 512

struct options {
	const char    *opt;
	unsigned char val;
};

static struct options kmod[] = {
	{.opt = "--left-ctrl",		.val = 0x01},
	{.opt = "--right-ctrl",		.val = 0x10},
	{.opt = "--left-shift",		.val = 0x02},
	{.opt = "--right-shift",	.val = 0x20},
	{.opt = "--left-alt",		.val = 0x04},
	{.opt = "--right-alt",		.val = 0x40},
	{.opt = "--left-meta",		.val = 0x08},
	{.opt = "--right-meta",		.val = 0x80},
	{.opt = NULL}
};

static struct options kval[] = {
	{.opt = "--return",	.val = 0x28},
	{.opt = "--esc",	.val = 0x29},
	{.opt = "--bckspc",	.val = 0x2a},
	{.opt = "--tab",	.val = 0x2b},
	{.opt = "--spacebar",	.val = 0x2c},
	{.opt = "--caps-lock",	.val = 0x39},
	{.opt = "--f1",		.val = 0x3a},
	{.opt = "--f2",		.val = 0x3b},
	{.opt = "--f3",		.val = 0x3c},
	{.opt = "--f4",		.val = 0x3d},
	{.opt = "--f5",		.val = 0x3e},
	{.opt = "--f6",		.val = 0x3f},
	{.opt = "--f7",		.val = 0x40},
	{.opt = "--f8",		.val = 0x41},
	{.opt = "--f9",		.val = 0x42},
	{.opt = "--f10",	.val = 0x43},
	{.opt = "--f11",	.val = 0x44},
	{.opt = "--f12",	.val = 0x45},
	{.opt = "--insert",	.val = 0x49},
	{.opt = "--home",	.val = 0x4a},
	{.opt = "--pageup",	.val = 0x4b},
	{.opt = "--del",	.val = 0x4c},
	{.opt = "--end",	.val = 0x4d},
	{.opt = "--pagedown",	.val = 0x4e},
	{.opt = "--right",	.val = 0x4f},
	{.opt = "--left",	.val = 0x50},
	{.opt = "--down",	.val = 0x51},
	{.opt = "--kp-enter",	.val = 0x58},
	{.opt = "--up",		.val = 0x52},
	{.opt = "--num-lock",	.val = 0x53},
	{.opt = NULL}
};

int keyboard_fill_report(char report[8], char buf[BUF_LEN], int *hold)
{
	char *tok = strtok(buf, " ");
	int key = 0;
	int i = 0;

	for (; tok != NULL; tok = strtok(NULL, " ")) {

		if (strcmp(tok, "--quit") == 0)
			return -1;

		if (strcmp(tok, "--hold") == 0) {
			*hold = 1;
			continue;
		}

		if (key < 6) {
			for (i = 0; kval[i].opt != NULL; i++)
				if (strcmp(tok, kval[i].opt) == 0) {
					report[2 + key++] = kval[i].val;
					break;
				}
			if (kval[i].opt != NULL)
				continue;
		}

		if (key < 6)
			if (islower(tok[0])) {
				report[2 + key++] = (tok[0] - ('a' - 0x04));
				continue;
			}

		for (i = 0; kmod[i].opt != NULL; i++)
			if (strcmp(tok, kmod[i].opt) == 0) {
				report[0] = report[0] | kmod[i].val;
				break;
			}
		if (kmod[i].opt != NULL)
			continue;

		if (key < 6)
			fprintf(stderr, "unknown option: %s\n", tok);
	}
	return 8;
}

static struct options mmod[] = {
	{.opt = "--b1", .val = 0x01},
	{.opt = "--b2", .val = 0x02},
	{.opt = "--b3", .val = 0x04},
	{.opt = NULL}
};

int mouse_fill_report(char report[8], char buf[BUF_LEN], int *hold)
{
	char *tok = strtok(buf, " ");
	int mvt = 0;
	int i = 0;
	for (; tok != NULL; tok = strtok(NULL, " ")) {

		if (strcmp(tok, "--quit") == 0)
			return -1;

		if (strcmp(tok, "--hold") == 0) {
			*hold = 1;
			continue;
		}

		for (i = 0; mmod[i].opt != NULL; i++)
			if (strcmp(tok, mmod[i].opt) == 0) {
				report[0] = report[0] | mmod[i].val;
				break;
			}
		if (mmod[i].opt != NULL)
			continue;

		if (!(tok[0] == '-' && tok[1] == '-') && mvt < 2) {
			errno = 0;
			report[1 + mvt++] = (char)strtol(tok, NULL, 0);
			if (errno != 0) {
				fprintf(stderr, "Bad value:'%s'\n", tok);
				report[1 + mvt--] = 0;
			}
			continue;
		}

		fprintf(stderr, "unknown option: %s\n", tok);
	}
	return 3;
}

static struct options jmod[] = {
	{.opt = "--b1",		.val = 0x10},
	{.opt = "--b2",		.val = 0x20},
	{.opt = "--b3",		.val = 0x40},
	{.opt = "--b4",		.val = 0x80},
	{.opt = "--hat1",	.val = 0x00},
	{.opt = "--hat2",	.val = 0x01},
	{.opt = "--hat3",	.val = 0x02},
	{.opt = "--hat4",	.val = 0x03},
	{.opt = "--hatneutral",	.val = 0x04},
	{.opt = NULL}
};

int joystick_fill_report(char report[8], char buf[BUF_LEN], int *hold)
{
	char *tok = strtok(buf, " ");
	int mvt = 0;
	int i = 0;

	*hold = 1;

	/* set default hat position: neutral */
	report[3] = 0x04;

	for (; tok != NULL; tok = strtok(NULL, " ")) {

		if (strcmp(tok, "--quit") == 0)
			return -1;

		for (i = 0; jmod[i].opt != NULL; i++)
			if (strcmp(tok, jmod[i].opt) == 0) {
				report[3] = (report[3] & 0xF0) | jmod[i].val;
				break;
			}
		if (jmod[i].opt != NULL)
			continue;

		if (!(tok[0] == '-' && tok[1] == '-') && mvt < 3) {
			errno = 0;
			report[mvt++] = (char)strtol(tok, NULL, 0);
			if (errno != 0) {
				fprintf(stderr, "Bad value:'%s'\n", tok);
				report[mvt--] = 0;
			}
			continue;
		}

		fprintf(stderr, "unknown option: %s\n", tok);
	}
	return 4;
}

void print_options(char c)
{
	int i = 0;

	if (c == 'k') {
		printf("	keyboard options:\n"
		       "		--hold\n");
		for (i = 0; kmod[i].opt != NULL; i++)
			printf("\t\t%s\n", kmod[i].opt);
		printf("\n	keyboard values:\n"
		       "		[a-z] or\n");
		for (i = 0; kval[i].opt != NULL; i++)
			printf("\t\t%-8s%s", kval[i].opt, i % 2 ? "\n" : "");
		printf("\n");
	} else if (c == 'm') {
		printf("	mouse options:\n"
		       "		--hold\n");
		for (i = 0; mmod[i].opt != NULL; i++)
			printf("\t\t%s\n", mmod[i].opt);
		printf("\n	mouse values:\n"
		       "		Two signed numbers\n"
		       "--quit to close\n");
	} else {
		printf("	joystick options:\n");
		for (i = 0; jmod[i].opt != NULL; i++)
			printf("\t\t%s\n", jmod[i].opt);
		printf("\n	joystick values:\n"
		       "		three signed numbers\n"
		       "--quit to close\n");
	}
}

int main(int argc, const char *argv[])
{
	const char *filename = NULL;
	int fd = 0;
	char buf[BUF_LEN];
	int cmd_len;
	char report[8];
	int to_send = 8;
	int hold = 0;
	fd_set rfds;
	int retval, i;

	if (argc < 3) {
		fprintf(stderr, "Usage: %s devname mouse|keyboard|joystick\n",
			argv[0]);
		return 1;
	}

	if (argv[2][0] != 'k' && argv[2][0] != 'm' && argv[2][0] != 'j')
	  return 2;

	filename = argv[1];

	if ((fd = open(filename, O_RDWR, 0666)) == -1) {
		perror(filename);
		return 3;
	}

	print_options(argv[2][0]);

	while (42) {

		FD_ZERO(&rfds);
		FD_SET(STDIN_FILENO, &rfds);
		FD_SET(fd, &rfds);

		retval = select(fd + 1, &rfds, NULL, NULL, NULL);
		if (retval == -1 && errno == EINTR)
			continue;
		if (retval < 0) {
			perror("select()");
			return 4;
		}

		if (FD_ISSET(fd, &rfds)) {
			cmd_len = read(fd, buf, BUF_LEN - 1);
			printf("recv report:");
			for (i = 0; i < cmd_len; i++)
				printf(" %02x", buf[i]);
			printf("\n");
		}

		if (FD_ISSET(STDIN_FILENO, &rfds)) {
			memset(report, 0x0, sizeof(report));
			cmd_len = read(STDIN_FILENO, buf, BUF_LEN - 1);

			if (cmd_len == 0)
				break;

			buf[cmd_len - 1] = '\0';
			hold = 0;

			memset(report, 0x0, sizeof(report));
			if (argv[2][0] == 'k')
				to_send = keyboard_fill_report(report, buf, &hold);
			else if (argv[2][0] == 'm')
				to_send = mouse_fill_report(report, buf, &hold);
			else
				to_send = joystick_fill_report(report, buf, &hold);

			if (to_send == -1)
				break;

			if (write(fd, report, to_send) != to_send) {
				perror(filename);
				return 5;
			}
			if (!hold) {
				memset(report, 0x0, sizeof(report));
				if (write(fd, report, to_send) != to_send) {
					perror(filename);
					return 6;
				}
			}
		}
	}

	close(fd);
	return 0;
}
```

## 四. 参考文献:
--------------------
[1] $(kernel_root)/Documentation/usb/gadget_hid.txt
