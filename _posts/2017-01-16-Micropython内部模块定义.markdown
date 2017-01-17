---
layout: post
title:  "Micropython开发：内部模块定义及扩展"
author: 裘凯
date:   2017-01-16 12:04:37 +0800
categories: Micropython
tags: Micropython
excerpt: Micropython需要支持导入模块，同时，设备驱动也要能够以python模块的形式工作，那么在python解释中必须实现这种接口，这篇文章就介绍Micropython是如何支持模块的。
---

* menu
{:toc}

>本文介绍mp内部模块的实现，如何自定义内部模块，面向读者：对python编译器内部实现有兴趣。要求：只需具有python应用经验即可。

Micropython需要支持导入模块，同时，设备驱动也要能够以python模块的形式工作，那么在python解释中必须实现这种接口。外部模块的定义位于$(tree)/extmod中。模块名字命名为modxxx.c。譬如modframebuf.c

## 一 Python内部模块概览

所有的python全局模块从`STATIC const mp_rom_map_elem_t mp_builtin_module_table[]`中查找，这张查找表位于py/objmodule.c。

下面列举部分模块供查阅，详细描述参考模块实现

模块名字 | 功能描述
--- | ---
mp_module_thread | 多线程支持
mp_module_gc | 垃圾回收
mp_module_sys | python的sys模块，提供系统操作接口
mp_module_math | 数学运算模块
mp_module_array | 向量运算
mp_module_ujson | json支持
mp_module_websocket | socket支持
mp_module_framebuf | framebuf驱动模块

这些全局模块的价值在于

1. 扩展mp功能
2. 为添加新的模块提供参考

## 二 添加自定义模块
下面以framebuf模块的定义为例介绍如何添加新的内建模块

### 2.1 新类型的定义

```c
STATIC const mp_obj_type_t mp_type_framebuf = {
    { &mp_type_type },
    .name = MP_QSTR_FrameBuffer,
    .make_new = framebuf_make_new,
    .buffer_p = { .get_buffer = framebuf_get_buffer },
    .locals_dict = (mp_obj_t)&framebuf_locals_dict,
};
```

以平常写的python程序为例，当被作为模块import时，每个模块被导入的时候不但包含了一些操作接口，可能还包含新类型的定义，新类型在编译器内部就通过这样的结构表示。

### 2.2 新模块的定义

> 注：模块包含类型

```c
const mp_obj_module_t mp_module_framebuf = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&framebuf_module_globals,
};
```

定义mp_obj_module_t类型的变量，其中只有两个成员：模块对象存放的基址以及模块的符号表。

### 2.3 体验
在mpconfigport.h中定义
```c
#define MICROPY_PY_FRAMEBUF			(1)
```

编译即可，启动后

```python
>>> import framebuf     #导入模块
>>> framebuf.<tab>      #查看模块属性
>>> framebuf.
__name__        FrameBuffer     FrameBuffer1    MVLSB
RGB565

```

这里的属性就是framebuf_module_globals中的成员。

```python
>>> w = 5
>>> h = 16
>>> buf = bytearray(w * h //8)
>>> fbuf = framebuf.FrameBuffer(buf, w, h, framebuf.MVLSB)
>>> fbuf.
fill            fill_rect       pixel           hline
vline           rect            line            blit
scroll          text
>>> fbuf.
>>> fbuf
<FrameBuffer>
```

这样就创建了一个FrameBuffer类型的对象fbuf，可以看到fbuf对象的属性

fbuf属性列表就是framebuf_locals_dict中的内容，这里进一步展示一下，供参考

```c
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(framebuf_text_obj, 4, 5, framebuf_text);

STATIC const mp_rom_map_elem_t framebuf_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_fill), MP_ROM_PTR(&framebuf_fill_obj) },
    { MP_ROM_QSTR(MP_QSTR_fill_rect), MP_ROM_PTR(&framebuf_fill_rect_obj) },
    { MP_ROM_QSTR(MP_QSTR_pixel), MP_ROM_PTR(&framebuf_pixel_obj) },
    { MP_ROM_QSTR(MP_QSTR_hline), MP_ROM_PTR(&framebuf_hline_obj) },
    { MP_ROM_QSTR(MP_QSTR_vline), MP_ROM_PTR(&framebuf_vline_obj) },
    { MP_ROM_QSTR(MP_QSTR_rect), MP_ROM_PTR(&framebuf_rect_obj) },
    { MP_ROM_QSTR(MP_QSTR_line), MP_ROM_PTR(&framebuf_line_obj) },
    { MP_ROM_QSTR(MP_QSTR_blit), MP_ROM_PTR(&framebuf_blit_obj) },
    { MP_ROM_QSTR(MP_QSTR_scroll), MP_ROM_PTR(&framebuf_scroll_obj) },
    { MP_ROM_QSTR(MP_QSTR_text), MP_ROM_PTR(&framebuf_text_obj) },
};
```

对象属性名字为MP_QSTR_name，属性对象指向MP_ROM_PTR(obj)定义的内容，而obj则通过`STATIC MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(framebuf_text_obj, 4, 5, framebuf_text);`定义。

所有属性对象的处理函数都有形如
```c
STATIC mp_obj_t func_name(size_t n_args, const mp_obj_t *args)
```
的形式。


## 三 总结
通过以上的体验，可以感受到其实添加自己的模块是很简单的了，只要定义一系列的属性就可以了。
