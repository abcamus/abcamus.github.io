---
layout:	post
title:	"Linux Mint搭建Jekyll环境"
date:	2017-01-03
categories:	Linux
---
Linux Mint下搭建Jekyll环境，首先要更新ruby，系统仓库里最新的是1.9.3，而Jekyll要求>=2.0

最终版本信息：
```
$ ruby -v
ruby 2.3.3p222 (2016-11-21 revision 56859) [x86_64-linux]
$ jekyll -v
jekyll 3.3.1
```

#### 安装rvm 

参考这里： http://rvm.io/

```
$ gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3
$ curl -sSL https://get.rvm.io | bash -s stable
```

#### 更新ruby

```
$ rvm install ruby-2.2.0
```

一开始安装的时候遇到了apt-get 404错误，于是换了个软件源，把上交的换成了清华的，基础源换成了阿里云的。update一下再执行就好了。

如果太慢看这里： https://ruby-china.org/wiki/ruby-mirror


#### Jekyll安装测试

安装参考： http://jekyll.com.cn/docs/installation/

```
$ gem install jekyll bundler
```

测试参考： http://jekyll.com.cn/docs/quickstart/

>注意：运行jekyll new myblog的时候说找不到gem jekyll，原因是GEM_HOME没有配置

我的系统GEM_HOME设为`.rvm/gems/ruby-2.3.3`

Could not find gem 'minima (~> 2.0)'
Could not find gem 'jekyll-feed (~> 0.6)'

```
$ gem install minima jekyll-feed
```

然后按照测试参考执行，在浏览器里打开localhost:4000就看到了主页
