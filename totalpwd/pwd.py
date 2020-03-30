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
        credentials=None,
        port=None,
        comment=None,
        raw=None,
    ):
        self.vendor = vendor.upper()
        self.category = category.lower()
        self.credentials = credentials
        self.port = int(port)
        self.comment = comment
        # 用来合并去重
        self.key = "%s-%s-%s" % (self.vendor, self.category, self.port)
        # 用来以后拓展
        self.raw = raw

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        s1 = "Vendor: %s, Category: %s, Port: %s, Credentials: " % (
            self.vendor,
            self.category,
            self.port,
        )
        s2 = str(self.credentials)
        return s1 + s2

    def __str__(self):
        return self.__repr__()

    @classmethod
    def info(cls, pwds_path=opts.pwds_path) -> list:
        """
            返回pwd摘要信息
            vendor, category, credentials count
        """
        pwds = cls.load(pwds_path)
        return [
            [pwd.vendor, pwd.category, pwd.port, len(pwd.credentials)] for pwd in pwds
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
            TODO:合并pwds中的用户名和密码对
        """
        return pwds

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
            cls.logger.info(e)
        return pwds

    @classmethod
    def _load_csv(cls, file) -> list:
        """
            导入csv文件中的pwd
            csv文件格式 username, password [, vendor, category, port, comment]
        """
        cls.logger.info("Loading csv file %s" % file)
        pwds_set = {}
        try:
            with open(file, "r") as f:
                for row in f.readlines():
                    cells = [x.strip() for x in row.split(",")]
                    padding = [None for i in range(6 - len(cells))]  # 补全长度
                    full_cells = cells + padding

                    vendor = full_cells[2] or "COMMON"
                    category = full_cells[3] or full_cells[2] or "common"
                    port = full_cells[4] or 0
                    username, password = full_cells[0:2]

                    key = "%s-%s-%s" % (vendor, category, port)

                    if key in pwds_set:
                        # 合并
                        pwds_set.get(key).credentials.append(
                            dict(username=username, password=password)
                        )
                    else:
                        pwd = Pwd(
                            vendor=vendor,
                            category=category,
                            credentials=[dict(username=username, password=password)],
                            port=full_cells[4] or 0,
                            comment=full_cells[5],
                            raw=cells,
                        )
                        pwds_set[pwd.key] = pwd
        except Exception as e:
            cls.logger.error("Parse csv file %s failed." % file)
            cls.logger.info(e)
        pwds = pwds_set.values()
        return pwds
