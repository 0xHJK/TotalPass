# CONTRIBUTING

TotalPass was created by HJK [@0xHJK](https://github.com/0xHJK).

项目主要参考或使用了以下项目，向其开发者表示感谢。
- https://github.com/ztgrace/changeme
- https://github.com/psf/requests
- https://github.com/pallets/click
- https://github.com/paramiko/paramiko
- 其他引用的第三方库

## Authors

- [@0xHJK](https://github.com/0xHJK)

## Development

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
