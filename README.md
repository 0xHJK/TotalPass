# TotalPass

TotalPass (<https://github.com/0xHJK/TotalPass>) 是一款默认口令/弱口令扫描工具。

> ⚠️ 警告：本工具仅用于授权测试，不得用于非法用途，否则后果自负！
> 
> ⚠️ Warning：For authorized testing only. Prohibited for illegal use.

![TotalPass.jpg](https://github.com/0xHJK/TotalPass/raw/master/totalpass.jpg)

## Features

1. 扫描目标设备是否存在默认密码
2. 搜索常见设备默认密码
3. 支持手动和自动更新密码库

目前支持的默认密码扫描类型有
- SSH
- Telnet
- SNMP
- Redis

## QuickStart

```bash
$ pip3 install totalpass
$ totalpass scan 192.168.1.1
```

手动安装
```bash
$ git clone https://github.com/0xHJK/TotalPass
$ cd TotalPass
$ python3 setup.py install
```

## Usage

查看帮助

```bash
$ totalpass --help
Usage: totalpass.py [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  list    列出所有支持的设备信息和服务类型
  scan    指定目标进行密码扫描
  search  从密码库中搜索密码
  update  从 cirt.net 更新密码库
```

查看扫描命令帮助
```bash
$ totalpass scan --help
Usage: totalpass.py scan [OPTIONS] TARGET...

  指定目标进行密码扫描

Options:
  -x, --name TEXT        指定设备型号或品牌
  -c, --category TEXT    指定扫描类型
  -p, --port INTEGER     指定扫描端口
  -d, --dirname TEXT     指定字典目录或文件
  --common               使用常见弱口令字典
  -t, --threads INTEGER  指定线程数量
  -v, --verbose          详细输出模式
  --help                 Show this message and exit.
```

## Scanner

对单一IP进行所有扫描
```bash
$ totalpass scan 192.168.1.1
```

使用详细模式
```bash
$ totalpass scan -v 192.168.1.1
```

指定扫描类型进行扫描
```bash
$ totalpass scan -c ssh 192.168.1.1
```

指定端口进行扫描
```bash
$ totalpass scan -p 22 192.168.1.1
```

自定义字典进行扫描
```bash
$ totalpass scan -d your-wordlist 192.168.1.1
```

对多个IP进行扫描（速度较慢）
```bash
$ totalpass scan 192.168.1.1 192.168.1.2

$ totalpass scan 192.168.1.1/24
```

## Passwords

查看支持的扫描类型
```bash
$ totalpass list
```

在密码库中搜索密码
```bash
$ totalpass search weblogic
```

在密码库中搜索密码（以表格形式显示）
```bash
$ totalpass search -v tomcat
```

在密码库中搜索密码（以完整形式显示）
```bash
$ totalpass search -vv tomcat
```

多个条件搜索
```bash
$ totalpass search oracle unix
```

更新密码库
```bash
$ totalpass update
```

## Options

### 扫描目标

扫描目标支持单个IP、多个IP、子网、指定类型和端口等形式
```bash
$ totalpass scan 192.168.1.1

$ totalpass scan 192.168.1.1 192.168.1.2

$ totalpass scan 192.168.1.1/24

$ totalpass scan redis://192.168.1.1:6379
```

### 设备类型或名称

参数：`-x`或`--name=`

对应payloads目录中的yml文件的name属性

### 扫描类型

参数：`-c`或`--category=`

对应payloads目录中的yml文件的category属性，也和`addons`目录中的插件名称对应，如果不指定则默认使用所有插件。

支持多种类型，如`-c ssh -c telnet`

### 扫描端口

参数：`-p`或`--port=`

不指定则使用默认端口

### 线程数量

参数：`-t`或`--threads=`

默认10线程

### 常见弱口令

参数：`--common`

在匹配的yml文件之外，使用csv文件中常见弱口令进行爆破

### 自定义字典

参数：`-d`或`--dirname=`

可以指定字典目录或字典文件

### 详细模式

参数：`-v` `-vv` `-vvv`

`v`越多，输出越详细


## History

<https://github.com/0xHJK/TotalPass/blob/master/HISTORY.md>

## Contributing

<https://github.com/0xHJK/TotalPass/blob/master/CONTRIBUTING.md>

## License

[MIT License](https://github.com/0xHJK/TotalPass/blob/master/LICENSE)

## Donate

BTC：bc1qn hvev dghq uzc3 fh9c qdja 63ut qqgn va3l h6n2s

Wechat：

![Wechat](https://github.com/0xHJK/music-dl/raw/master/static/wepay.jpg)
