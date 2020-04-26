#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    导入、解析和创建passwd
"""

import os
import logging
import click
import yaml
from .settings import opts


class Passwd(object):
    logger = logging.getLogger("TotalPass")

    def __init__(
        self,
        name="",
        vendor="",
        category="",
        credentials=[],
        port=0,
        comment="",
        raw=None,
    ):
        # 唯一标识符（设备型号等信息）
        self.name = name
        self.vendor = vendor or name
        self.category = category.lower()
        self.credentials = credentials
        self.port = int(port)
        self.comment = comment
        # 用来合并去重
        self.key = "%s-%s-%s" % (self.name, self.category, self.port)
        # 用来以后拓展
        self.raw = raw

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.__repr__())

    def __repr__(self):
        return "Name: %s, Category: %s, Port: %s\nCredentials: %s" % tuple(self.row())

    def __str__(self):
        return self.__repr__()

    def row(self) -> list:
        """
            返回passwd信息数组（表格中的一行）
        """
        creds = [
            (item.get("username", ""), item.get("password", ""))
            for item in self.credentials
        ]
        return [self.name, self.category, self.port, str(creds)]

    def creds(self) -> list:
        """
            返回帐号和密码
        """
        return [
            "%s,%s" % (item.get("username", ""), item.get("password", ""))
            for item in self.credentials
        ]

    def cred_rows(self) -> list:
        """
            返回帐号、密码、名称
        """
        return [
            [item.get("username", ""), item.get("password", ""), self.name]
            for item in self.credentials
        ]

    def yaml(self):
        """
            把passwd信息格式化成yaml
        """
        schema = {
            "name": self.name,
            "vendor": self.vendor,
            "category": self.category,
            "auth": {"credentials": self.credentials},
            "port": int(self.port),
            "comment": self.comment,
        }
        return yaml.dump(schema)

    def match(self, keywords) -> bool:
        """ 关键字匹配 passwd """
        s = str(self.yaml()).lower()
        for kw in keywords:
            if not kw in s:
                return False
        return True

    @classmethod
    def table(cls, passwds_path="") -> list:
        """
            返回passwd摘要信息
            name, category, credentials count
        """
        # 不可以直接在函数参数中设置，否则在调用之前就已经使用了旧的passwds_path
        passwds_path = passwds_path or opts.passwds_path
        passwds = cls.load(passwds_path)
        return [
            [passwd.name, passwd.category, passwd.port, len(passwd.credentials)]
            for passwd in passwds
        ]

    @classmethod
    def load(cls, passwds_path="") -> list:
        """
            导入passwd的对外接口
        """
        passwds = []
        passwds_path = passwds_path or opts.passwds_path
        cls.logger.info("passwds_path: %s" % passwds_path)
        if os.path.isfile(passwds_path):
            passwds = cls._load_file(passwds_path)
        elif os.path.isdir(passwds_path):
            passwds = cls._load_dir(passwds_path)
        else:
            cls.logger.critical("Invalid path.")
            return passwds
        passwds = cls.merge(passwds)
        return passwds

    @classmethod
    def merge(cls, passwds) -> list:
        """
            如果命令行中指定了name参数，则需要去除不符合要求的密码对
            TODO:合并passwds中的用户名和密码对
        """
        names = []
        if opts.name:
            names.append(opts.name)
        if opts.common:
            names.append("COMMON")
        if not names:
            # 如果没有指定name则直接返回
            return passwds
        # 否则需要去除不符合要求的passwds
        ret_passwds = []
        catgories = set()
        for passwd in passwds:
            for vn in names:
                if vn.upper() in passwd.name.upper():
                    ret_passwds.append(passwd)
                    catgories.add(passwd.category)
                    continue
        # 对于分类也取并集
        opts.categories = [cat for cat in opts.categories if cat in catgories]
        return ret_passwds

    @classmethod
    def _load_dir(cls, dirname) -> list:
        """
            遍历目录导入passwd
        """
        passwds = []
        cls.logger.info("Loading dir %s" % dirname)
        for root, dirs, files in os.walk(dirname):
            for fname in files:
                file = os.path.join(root, fname)
                passwds += cls._load_file(file)
        return passwds

    @classmethod
    def _load_file(cls, file) -> list:
        """
            从文件导入passwd
        """
        if file.endswith(".yml"):
            return cls._load_yaml(file)
        elif file.endswith(".csv"):
            return cls._load_csv(file)
        else:
            cls.logger.debug("%s is not supported." % file)
            return []

    @classmethod
    def _load_yaml(cls, file) -> list:
        """
            导入yml文件中的passwd
        """
        cls.logger.info("Loading yaml file %s" % file)
        passwds = []
        try:
            raw = open(file, "r").read()
            parsed = yaml.safe_load(raw)
            passwd = Passwd(
                name=parsed["name"],
                vendor=parsed["vendor"],
                category=parsed["category"],
                credentials=parsed["auth"]["credentials"],
                port=parsed["port"],
                comment=parsed.get("comment", ""),
                raw=parsed,
            )
            passwds.append(passwd)
        except Exception as e:
            cls.logger.error("Parse yaml file %s failed." % file)
            cls.logger.error(e)
        return passwds

    @classmethod
    def _load_csv(cls, file) -> list:
        """
            导入csv文件中的passwd
            csv文件格式 username, password [, name, category, port, comment]
        """
        cls.logger.info("Loading csv file %s" % file)
        passwds_map = {}
        try:
            with open(file, "r") as f:
                for row in f.readlines():
                    cells = [x.strip() for x in row.split(",")]
                    padding = [None for i in range(6 - len(cells))]  # 补全长度
                    full_cells = cells + padding

                    name = full_cells[2] or "COMMON"
                    category = full_cells[3] or full_cells[2] or "common"
                    port = full_cells[4] or 0
                    username, password = full_cells[0:2]

                    key = "%s-%s-%s" % (name, category, port)
                    cred = dict(username=username, password=password)
                    if key in passwds_map:
                        # 合并
                        passwds_map.get(key).credentials.append(cred)
                    else:
                        passwd = Passwd(
                            name=name,
                            vendor=name,
                            category=category,
                            credentials=[cred],
                            port=full_cells[4] or 0,
                            comment=full_cells[5],
                            raw=cells,
                        )
                        passwds_map[passwd.key] = passwd
        except Exception as e:
            cls.logger.error("Parse csv file %s failed." % file)
            cls.logger.info(e)
        passwds = passwds_map.values()
        return passwds
