#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    Telnet 扫描器
"""

import socket
import time
import logging
from telnetlib import Telnet
from ..scanner import Scanner
from ..settings import opts


class TelnetScanner(Scanner):
    """
        Telnet 扫描器
    """

    def __init__(self, pwd, target, username, password):
        super(TelnetScanner, self).__init__(pwd, target, username, password)
        self.port = self.port or 23

    def _check(self):
        tn = Telnet(host=self.host, port=self.port, timeout=opts.timeout)
        self._command(tn, "login: ", self.username)
        self._command(tn, "Password: ", self.password or "")
        evidence = self._command(tn, "$", "").strip()
        # TODO: 有些系统不一定是$符号
        if not evidence.endswith("$"):
            # if not evidence or evidence.endswith("login:"):
            evidence = False
        tn.close()
        return evidence

    def _command(self, tn, flag, cmd):
        data = tn.read_until(flag.encode(), timeout=opts.timeout / 2)
        tn.write(cmd.encode() + b"\n")
        return data.decode(errors="ignore")


def mkscanner(pwd, target, username, password):
    return TelnetScanner(pwd, target, username, password)
