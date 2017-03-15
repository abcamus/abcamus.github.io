---
layout: post
title:  "Linux Kernel(4.1) API Reference "
date:   2016-09-23 21:22:37 +0800
categories: 嵌入式开发
tags: Linux
topics: Linux内核移植
excerpt: 摘要
---

* menu
{:toc}

### 1 Auxilary Interfaces

#### 1.1 double linked list

```c
static inline void INIT_LIST_HEAD(struct list_head *list);
list_for_each_entry(pos, struct list_head *head, member);
static inline void list_add_tail(struct list_head *new, struct list_head *head);
static inline void list_del(struct list_head *entry);
```

#### 1.2 bit operation

```c
static inline void set_bit(int nr, unsigned long *addr);
static inline void clear_bit(int nr, unsigned long *addr);
static __always_inline int test_bit(int nr, const volatile unsigned long *addr);
```

#### 1.3 communication between user space and kernel space

* memory copy

```c
static inline long copy_to_user(void __user *to, const void *from, unsigned long n);
static inline long copy_from_user(void *to, const void __user *from, unsigned long n);
get_user(x, p)/put_user(x, p)
```

* async signal

```c
int fasync_helper(int fd, struct file *filp, int on, struct fasync_struct **fapp);
void kill_fasync(struct fasync_struct **fp, int sig, int band);
```

### 2 mutex/semaphore/lock

#### 2.1 mutex

```c
mutex_init(struct mutex *lock);
int __sched mutex_lock_interruptible(struct mutex *lock);
void __sched mutex_unlock(struct mutex *lock);
```

#### 2.2 spin lock

```c
spin_lock_init(spinlock_t *lock);
static inline void spin_lock_irqsave(spinlock_t *lock, unsigned long flags);
static inline void spin_unlock_irqrestore(spinlock_t *lock, unsigned long flags);
static inline void spin_lock_irq(spinlock_t *lock);
static inline void spin_unlock_irq(spinlock_t *lock);
```

#### 2.3 read/write lock

```c
static DEFINE_RWLOCK(name);
write_lock(rwlock_t *lock);
write_unlock(rwlock_t *lock);
read_lock(rwlock_t *lock);
read_unlock(rwlock_t *lock);
```

### 3 Process Schedule & event deal

#### 3.1 wait queue

```c
DEFINE_WAIT(wait)/DECLARE_WAITQUEUE(wait, task);
init_waitqueue_head(wait_queue_head_t *q);

void add_wait_queue(wait_queue_head_t *q, wait_queue_t *wait);
void remove_wait_queue(wait_queue_head_t *q, wait_queue_t *wait);

void prepare_to_wait(wait_queue_head_t *q, wait_queue_t *wait, int state);
void schedule();
wake_up_interruptible(wait_queue_head_t *q);
void finish_wait(wait_queue_head_t *q, wait_queue_t *wait);
set_current_state(state);
```

#### 3.2 work queue

```c
alloc_workqueue(name, flags, max_active, args...);
destroy_workqueue(struct workqueue_struct *hub_wq);

static inline bool queue_work(struct workqueue_struct *wq, struct work_struct *work);
```

#### 3.3 completion

```c
DECLARE_COMPLETION(work)/static inline void init_competion(struct completion *x);
void __sched wait_for_completion(struct completion *x);
unsigned long __sched wait_for_completion_timeout(struct completion *x, unsigned lonf timeout);
void complete(struct completion *x);
void complete_all(struct completion *x);
```

#### 3.4 notifier

```c
BLOCKING_NOTIFIER_HEAD(list_name);
int blocking_notifier_chain_register(struct blocking_notifier_head *nh,
                                     struct notifier_block *n);
int blocking_notifier_chain_unregister(struct blocking_notifier_head *nh,
                                       struct notifier_block *n);
int blocking_notifier_call_chain(struct blocking_notifier_head *nh,
                                 unsigned long val, void *v);
```

### 4 Memory Management

#### 4.1 kzalloc/kmalloc/kfree

```c
static inline void *kzalloc(size_t size, gfp_t flags);
static _always_inline void *kmalloc(size_t size, gfp_t flags);
void kfree(const void *objp);
```

#### 4.2 vzalloc/vfree

```c
void *vzalloc(unsigned long size);
void vfree(const void *addr);
```

#### 4.3 dma pool

```c
struct dma_pool *dma_pool_create(const char *name, struct device *dev, 
                                 size_t size, size_t align, size_t boundary);
void dma_pool_destroy(struct dma_pool *pool);

void *dma_pool_alloc(struct dma_pool *pool, gfp_t mem_flags, dma_addr_t *handle);
void dma_pool_free(struct dma_pool *pool, void *vaddr, dma_addr_t dma);
```

#### 4.4 dma coherent memory

```c
int dma_declare_coherent_memory(struct device *dev, phys_addr_t phys_addr,
                                dma_addr_t device_addr, size_t size, int flags);
void dma_release_declared_memory(struct device *dev);

static inline void *dma_alloc_coherent(struct device *dev, size_t size,
                                       dma_addr_t *dma_handle, gfp_t flag);
static inline void dma_free_coherent(struct device *dev, size_t size,
                                     void *cpu_addr, dma_addr_t dma_handle);
```

