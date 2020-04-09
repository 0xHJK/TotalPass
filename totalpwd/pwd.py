#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    导入、解析和创建pwd
"""

import os
import logging
import click
import yaml
from .settings import opts


class Pwd(object):
    logger = logging.getLogger("TotalPwd")

    def __init__(
        self,
        vendor=None,
        category=None,
        credentials=[],
        port=None,
        comment=None,
        name=None,
        raw=None,
    ):
        self.vendor = vendor.upper()
        self.category = category.lower()
        self.credentials = credentials
        self.port = int(port)
        self.comment = comment
        # 唯一标识符（设备型号等信息）
        self.name = name or self.vendor
        # 用来合并去重
        self.key = "%s-%s-%s" % (self.name, self.category, self.port)
        # 用来以后拓展
        self.raw = raw

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        s1 = "Name: %s, Vendor: %s, Category: %s, Port: %s, Credentials: " % (
            self.name,
            self.vendor,
            self.category,
            self.port,
        )
        s2 = str(self.credentials)
        return s1 + s2

    def __str__(self):
        return self.__repr__()

    def row(self) -> list:
        """
            返回pwd信息数组（表格中的一行）
        """
        creds = [
            (item.get("username", ""), item.get("password", ""))
            for item in self.credentials
        ]
        return [self.name, self.category, self.port, creds]

    def yaml(self):
        """
            把pwd信息格式化成yaml
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
        """ 关键字匹配 pwd """
        s = str(self.yaml()).lower()
        for kw in keywords:
            if not kw in s:
                return False
        return True

    @classmethod
    def info(cls, pwds_path=opts.pwds_path) -> list:
        """
            返回pwd摘要信息
            name, category, credentials count
        """
        pwds = cls.load(pwds_path)
        return [
            [pwd.name, pwd.category, pwd.port, len(pwd.credentials)] for pwd in pwds
        ]

    @classmethod
    def load(cls, pwds_path=opts.pwds_path) -> list:
        """
            导入pwd的对外接口
        """
        pwds = []
        cls.logger.info("pwds_path: %s" % pwds_path)
        if os.path.isfile(pwds_path):
            pwds = cls._load_file(pwds_path)
        elif os.path.isdir(pwds_path):
            pwds = cls._load_dir(pwds_path)
        else:
            cls.logger.critical("Invalid path.")
            return pwds
        pwds = cls.merge(pwds)
        # total = sum([len(x.credentials) for x in pwds])
        # click.echo("Loaded %i credential profiles." % len(pwds))
        # click.echo("Loaded %i credentials." % total)
        return pwds

    @classmethod
    def merge(cls, pwds) -> list:
        """
            去除不符合要求的密码对
            TODO:合并pwds中的用户名和密码对
        """
        names = []
        if opts.name:
            names.append(opts.name)
        if opts.common:
            names.append("COMMON")
        if not names:
            # 如果没有指定name并且设置了通用密码则直接返回
            return pwds
        # 否则需要去除不符合要求的pwds
        ret_pwds = []
        catgories = set()
        for pwd in pwds:
            for vn in names:
                if vn.upper() in pwd.name.upper():
                    ret_pwds.append(pwd)
                    catgories.add(pwd.category)
                    continue
        # 对于分类也取并集
        opts.categories = [cat for cat in opts.categories if cat in catgories]
        return ret_pwds

    @classmethod
    def _load_dir(cls, dirname) -> list:
        """
            遍历目录导入pwd
        """
        pwds = []
        cls.logger.info("Loading dir %s" % dirname)
        for root, dirs, files in os.walk(dirname):
            for fname in files:
                file = os.path.join(root, fname)
                pwds += cls._load_file(file)
        return pwds

    @classmethod
    def _load_file(cls, file) -> list:
        """
            从文件导入pwd
        """
        if file.endswith(".yml"):
            return cls._load_yaml(file)
        elif file.endswith(".csv"):
            return cls._load_csv(file)
        else:
            # cls.logger.error(
            #     "Format is not supported, please use .yml or .csv file.\n%s" % file
            # )
            return []

    @classmethod
    def _load_yaml(cls, file) -> list:
        """
            导入yml文件中的pwd
        """
        cls.logger.info("Loading yaml file %s" % file)
        pwds = []
        try:
            raw = open(file, "r").read()
            parsed = yaml.safe_load(raw)
            pwd = Pwd(
                name=parsed["name"],
                vendor=parsed["vendor"],
                category=parsed["category"],
                credentials=parsed["auth"]["credentials"],
                port=parsed["port"],
                comment=parsed.get("comment", ""),
                raw=parsed,
            )
            pwds.append(pwd)
        except Exception as e:
            cls.logger.error("Parse yaml file %s failed." % file)
            cls.logger.error(e)
        return pwds

    @classmethod
    def _load_csv(cls, file) -> list:
        """
            导入csv文件中的pwd
            csv文件格式 username, password [, name, category, port, comment]
        """
        cls.logger.info("Loading csv file %s" % file)
        pwds_map = {}
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
                    if key in pwds_map:
                        # 合并
                        pwds_map.get(key).credentials.append(cred)
                    else:
                        pwd = Pwd(
                            name=name,
                            vendor=name,
                            category=category,
                            credentials=[cred],
                            port=full_cells[4] or 0,
                            comment=full_cells[5],
                            raw=cells,
                        )
                        pwds_map[pwd.key] = pwd
        except Exception as e:
            cls.logger.error("Parse csv file %s failed." % file)
            cls.logger.info(e)
        pwds = pwds_map.values()
        return pwds
