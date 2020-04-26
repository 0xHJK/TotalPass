#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    核心控制器
    1. 解析命令
    2. 调用对应插件
    3. 返回结果
"""

import sys
import queue
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
        self.logger = logging.getLogger("TotalPass")
        self._q_scanners = queue.Queue()

    def anyscan(self):
        click.echo("Checking if the target ports are open...")

        scanners = []
        for t in opts.targets:
            if t.alive():
                scanners += t.load_scanners()

        click.echo("\nLoaded %i credential profiles." % len(opts.passwds))
        click.echo("Loaded %i unique scanners.\n" % len(scanners))

        for s in scanners:
            self._q_scanners.put(s)

        tasks = []
        for i in range(opts.threads):
            t = Thread(target=self.scan_worker)
            t.start()
            tasks.append(t)

        self._q_scanners.join()
        opts.running = False
        for i in range(opts.threads):
            self._q_scanners.put(None)

        for t in tasks:
            t.join()

    def scan_worker(self):
        while opts.running and not self._q_scanners.empty():
            s = self._q_scanners.get()
            if s is None:
                break
            s.scan()
            self._q_scanners.task_done()

    # def anyping(self):
    #     click.echo("Checking if the targets are up...")
    #     hosts = [t.host for t in opts.targets]
    #     # TODO
