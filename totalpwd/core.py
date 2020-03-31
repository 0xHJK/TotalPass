#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    核心控制器
    1. 解析命令
    2. 调用对应插件
    3. 返回结果
"""

import sys
import logging
import click
from threading import Thread
from . import addons
from .settings import opts


class TPCore(object):
    """
        核心控制器
    """

    def __init__(self):
        self.logger = logging.getLogger("TotalPwd")

    def any_scan(self):
        click.echo("Checking if the target port is open...")

        scanners = []
        for t in opts.targets:
            if t.alive():
                scanners += t.load_scanners()

        click.echo("\nLoaded %i credential profiles." % len(opts.pwds))
        click.echo("Loaded %i unique scanners.\n" % len(scanners))

        tasks = []
        total = len(scanners)
        step = int(total / opts.threads) + 1
        # 将所有任务平分到各个线程中
        for i in range(0, total, step):
            t = Thread(target=self.scan_task, args=(scanners[i : i + step],))
            t.start()
            tasks.append(t)

        for t in tasks:
            t.join()

    def scan_task(self, scanners):
        for s in scanners:
            s.scan()
