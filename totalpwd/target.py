#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    格式化目标对象
"""

import os
import re
import sys
import copy
import logging
import socket
import click
from netaddr import IPNetwork
from netaddr.core import AddrFormatError
from .settings import opts


class Target(object):
    """
        测试目标对象
    """

    logger = logging.getLogger("TotalPwd")

    def __init__(self, host=None, port=None, protocol=None, url=None):
        self.host = host
        port = port or opts.port
        port = int(re.sub(r"\D", "", str(port))) if port else None
        self.port = port if port and 0 < port < 65535 else None
        self.protocal = protocol
        self.url = url

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        s1 = "%s://" % self.protocal if self.protocal else ""
        s2 = self.host or ""
        s3 = ":%s" % self.port if self.port else ""
        s = s1 + s2 + s3 if s2 else ""
        return s

    def alive(self) -> bool:
        """
            检查端口是否开放
        """
        if not self.port:
            click.secho("[x] %s No port specified." % self.host, fg="red")
            return False
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(opts.timeout_alive)
        try:
            s.connect((self.host, int(self.port)))
            # s.shutdown(opts.timeout_alive)
            s.close()
            click.secho("[+] %s:%s is open." % (self.host, self.port), fg="green")
            return True
        except Exception as e:
            click.secho("[x] %s:%s is close." % (self.host, self.port), fg="red")
            logging.debug("%s Exception: %s" % (type(e).__name__, str(e)))
            return False

    @classmethod
    def parse(cls, target) -> list:
        """
            解析目标主机生成target list
            target 可能是tuple/list/str或文件
        """
        mid_targets = []  # 中间结果
        ret_targets = []  # 最终结果（补全了端口）
        if isinstance(target, str):
            if os.path.isfile(target):
                # TODO
                pass
            else:
                mid_targets = cls._parse_str(target)
        elif isinstance(target, tuple) or isinstance(target, list):
            for t in target:
                mid_targets += cls._parse_str(t)
        # 为targets补全端口
        for t in mid_targets:
            if t.port:
                ret_targets.append(t)
                continue
            for cat in opts.categories:
                port = opts.port_map.get(cat, 0)
                if port:
                    nt = copy.deepcopy(t)
                    nt.port = port
                    ret_targets.append(nt)
        return ret_targets

    @classmethod
    def _parse_str(cls, target) -> list:
        """
            解析字符串形式的目标
        """
        cls.logger.info("Parsing target %s" % target)
        if not isinstance(target, str):
            cls.logger.error("Target %s is not str" % target)
            return []
        target = target.strip().rstrip("/")
        targets = []
        try:
            for ip in IPNetwork(target).iter_hosts():  # (covers IP or cidr) #3,4
                targets.append(Target(host=str(ip)))
        except AddrFormatError:
            if len(target.split(":")) == 3:
                # mysql://127.0.0.1:3306
                protocol = target.split(":")[0]
                host = target.split(":")[1].replace("//", "")
                port = target.split(":")[2]
                targets.append(Target(host=host, port=port, protocol=protocol))
            elif "://" in target:
                # snmp://127.0.0.1
                protocol = target.split(":")[0]
                host = target.split(":")[1].replace("//", "")
                targets.append(Target(host=host, protocol=protocol))
            elif ":" in target:
                # 127.0.0.1:8080
                host = target.split(":")[0]
                port = target.split(":")[1]
                targets.append(Target(host=host, port=port))
            else:
                targets.append(Target(host=target))

        return targets
