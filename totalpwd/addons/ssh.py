#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    SSH 扫描器
"""

import logging
import paramiko
from ..scanner import Scanner
from ..settings import opts


class SSHScanner(Scanner):
    """
        SSH 扫描器
    """

    def __init__(self, pwd, target, username, password):
        super(SSHScanner, self).__init__(pwd, target, username, password)
        self.port = self.port or 22

    def _check(self):
        c = paramiko.SSHClient()
        c.set_missing_host_key_policy(
            paramiko.MissingHostKeyPolicy()
        )  # ignore unknown hosts
        c.connect(
            hostname=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            timeout=opts.timeout,
            banner_timeout=200,
        )
        stdin, stdout, stderr = c.exec_command("uname -a")
        evidence = stdout.readlines()[0]
        c.close()
        return evidence


def mkscanner(pwd, target, username, password):
    return SSHScanner(pwd, target, username, password)
