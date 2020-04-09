#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    基本扫描器类
"""

import sys
import click
import logging
import socket
from .settings import opts
from .exceptions import InvalidCredential


class Scanner(object):
    """
        基本扫描器类
        1. 根据目标和帐号密码生成扫描器列表
        2. 对目标的扫描确认（由具体子类完成）
    """

    def __init__(self, pwd, target, username, password):
        self.logger = logging.getLogger("TotalPwd")
        self.pwd = pwd
        self.vendor = pwd.vendor
        self.target = target
        self.host = target.host
        self.port = target.port or opts.port or pwd.port
        self.username = username
        self.password = password
        self.evidence = ""

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __hash__(self):
        """
            用来去重
        """
        return hash(self.__repr__())

    def __repr__(self):
        return "%s:%s@%s:%s" % (self.username, self.password, self.host, self.port)

    def __str__(self):
        return "#%s %s" % (self.vendor, self.__repr__())

    def scan(self) -> bool:
        """
            处理扫描结果并返回是否成功
        """
        if not opts.running:
            return False
        click.echo("Trying to scan %s " % self.__str__())
        try:
            self.evidence = self._check()
            if not self.evidence:
                raise InvalidCredential
            # 只取第一行结果
            self.evidence = self.evidence.split("\n")[0]
            msg = "[+] Found %s credential %s:%s at %s" % (
                self.vendor,
                self.username,
                self.password,
                self.target,
            )
            click.secho(msg, fg="green")
            click.secho(self.evidence, fg="green")
            opts.result.append(msg)
            return True
        # except EOFError as e:
        # print(e)
        except Exception as e:
            self.logger.info(
                "Invalid %s credential %s:%s at %s"
                % (self.vendor, self.username, self.password, self.target)
            )
            self.logger.info("%s Exception: %s" % (type(e).__name__, str(e)))

    def isopen(self) -> bool:
        """
            检查端口是否开放
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((self.host, int(self.port)))
            s.shutdown(2)
            self.logger.info("%s:%s is open." % (self.host, self.port))
            return True
        except:
            self.logger.error("%s:%s is close." % (self.host, self.port))
            return False

    def _check(self) -> str:
        """
            具体的扫描工作由子类完成并返回结果
        """
        pass
