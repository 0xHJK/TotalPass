# TotalPass

TotalPass 是一款快速扫描目标设备是否存在默认密码（弱口令）的工具

<https://github.com/0xHJK/TotalPass>

主要功能有：
1. 扫描目标设备是否存在默认密码
2. 搜索常见设备默认密码
3. 支持手动和自动更新密码库

目前支持的默认密码扫描类型有
- ssh
- telnet
- snmp
- redis

```
$ totalpass scan 192.168.64.162

TotalPass 0.0.1 created by HJK.
https://github.com/0xHJK/TotalPass

Checking if the target ports are open...
[+] [TCP] 192.168.64.162:23 is open.
[+] [TCP] 192.168.64.162:6379 is open.
[+] [UDP] 192.168.64.162:161 is open.
[+] [TCP] 192.168.64.162:22 is open.

Loaded 1052 credential profiles.
Loaded 207 unique scanners.

Testing #SSH test:test@192.168.64.162:22
[+] Found SSH credential test:test at 192.168.64.162:22
Linux ubuntu 5.3.0-46-generic #38~18.04.1-Ubuntu SMP Tue Mar 31 04:17:56 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
...
[+] Found TELNET credential test:test at 192.168.64.162:23
Last login: Thu Apr 23 01:44:18 PDT 2020 from 192.168.64.1 on pts/7
...
Testing #REDIS None:None@192.168.64.162:6379
[+] Found REDIS credential None:None at 192.168.64.162:6379
redis_version: 4.0.9, os: Linux 5.3.0-46-generic x86_64
Testing #SNMP None:public@192.168.64.162:161
[+] Found SNMP credential None:public at 192.168.64.162:161
SNMPv2-MIB::sysDescr.0 = Linux ubuntu 5.3.0-46-generic #38~18.04.1-Ubuntu SMP Tue Mar 31 04:17:56 UTC 2020 x86_64
...

--- Result -------------
[+] Found SSH credential test:test at 192.168.64.162:22
[+] Found TELNET credential test:test at 192.168.64.162:23
[+] Found REDIS credential None:None at 192.168.64.162:6379
[+] Found SNMP credential None:public at 192.168.64.162:161
------------------------
```

## 快速开始

安装（也可以不安装直接使用python3 totalpass.py）
```bash
$ python3 setup.py install
```

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

对多个IP的指定端口进行所有扫描
```bash
$ totalpass scan -p 22 192.168.1.1 192.168.1.2
```

查看支持的扫描类型
```bash
$ totalpass list
```

在密码库中搜索密码
```bash
$ totalpass search weblogic
```

多个条件搜索
```bash
$ totalpass search oracle unix
```

更新密码库
```bash
$ totalpass update
```

## 使用说明

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
  --common               使用常见弱口令字典
  -t, --threads INTEGER  指定线程数量
  -v, --verbose          详细输出模式
  --help                 Show this message and exit.
```


### 扫描目标

扫描目标支持单个IP、多个IP、子网、指定类型和端口等形式
```bash
$ totalpass scan 192.168.1.1

$ totalpass scan 192.168.1.1 192.168.1.2

$ totalpass scan 192.168.1.1/24

$ totalpass scan redis://192.168.1.1:6379
```

### 设备类型

参数：`-x`或`--name=`

对应payloads目录中的yml文件的name属性

### 扫描类型

参数：`-c`或`--category=`

对应payloads目录中的yml文件的category属性，也和`addons`目录中的插件名称对应，如果不指定则默认使用所有插件

### 扫描端口

参数：`-p`或`--port=`

不指定则使用默认端口

### 线程数量

参数：`-t`或`--threads=`

默认10线程

### 常见弱口令

参数：`--common`

在匹配的yml文件之外，使用csv文件中常见弱口令进行爆破

### 详细模式

参数：`-v` `-vv` `-vvv`

`v`越多，输出越详细


## 开发说明

项目支持插件化开发，只需要在`addons`目录中添加插件，在`passwds`目录中添加密码信息即可使用

### 添加yml密码（推荐）

例如新增一个思科的snmp默认密码文件，可以在`passwds/snmp`目录下创建`cisco.yml`文件

参考格式：

```yml
name: Cisco - NETRANGER/SECURE IDS # 名称中可以包含服务商、型号、版本等信息，是唯一识别符
vendor: CISCO
auth:
  credentials:
  - username: cisco
    password: cisco
  - username: 用户名和密码可以创建多对
    password: 用户名和密码可以创建多对
category: snmp # 类别必须和插件名称一致
port: 161
comment: 这是备注，可以备注来源链接
```

### 添加csv密码

如果需要添加多个密码，可以使用csv文件

csv格式：username, password [, name, category, port, comment]

用户名和密码必须，配置名称、扫描类型、端口、备注可选

### 开发扫描器插件

如果扫描类型不在已支持的插件中，可以选择自行开发插件。

开发插件需要在`addons`目录中创建py文件，文件名为扫描类型，如`mongo.py`。

同时需要在`payloads`目录中添加对应的密码信息。

格式参考：
```python

# 引入必要的包
import pymongo
from ..settings import opts
from ..scanner import Scanner

# 继承Scanner类，类名和扫描类别保持一致
class MongoScanner(Scanner):
    def __init__(self, passwd, target, username, password):
        super(RedisScanner, self).__init__(passwd, target, username, password)
        # 指定默认端口
        self.port = self.port or 27017

    # 核心扫描方法，成功通常返回服务信息，失败返回False
    def _check(self):
        evidence = "mongodb version xxx"
        return evidence

# 被调用的生成扫描器的方法，注意类名一致
def mkscanner(passwd, target, username, password):
    return MongoScanner(passwd, target, username, password)

```