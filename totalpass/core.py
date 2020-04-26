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
from prettytable import PrettyTable
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

    @classmethod
    def anysearch(cls, keywords, verbose):
        """ 从密码库中搜索密码 """
        click.echo("Searching passwords from profiles...")
        matched = []

        click.echo("[+] Loaded %s passwd profiles." % len(opts.passwds))

        if verbose < 1:
            for passwd in opts.passwds:
                if passwd.match(keywords):
                    matched += passwd.creds()
            matched = set(matched)
            print("\n")
            for x in matched:
                print(x)
            print("\n")
        elif verbose < 2:
            for passwd in opts.passwds:
                if passwd.match(keywords):
                    matched += passwd.cred_rows()
            pt = PrettyTable(["Username", "Password", "Name"])
            pt.align["Name"] = "l"
            for row in matched:
                pt.add_row(row)
            print(pt.get_string())
        else:
            for passwd in opts.passwds:
                if passwd.match(keywords):
                    print("\n-----------------------------")
                    print(passwd.yaml())
                    matched.append(passwd.yaml())

        if matched:
            click.secho("[+] Found %s passwd." % len(matched), fg="green")
        else:
            click.secho("[x] No matching passwd profile found.", fg="red")
