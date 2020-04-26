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
from .passwd import Passwd


class TPCore(object):
    """
        核心控制器
    """

    logger = logging.getLogger("TotalPass")
    _q_scanners = queue.Queue()

    def __init__(self):
        pass
        # self.logger = logging.getLogger("TotalPass")
        # self._q_scanners = queue.Queue()

    @classmethod
    def anyscan(cls):
        click.echo("Checking if the target ports are open...")

        scanners = []
        for t in opts.targets:
            if t.alive():
                scanners += t.load_scanners()

        click.echo("\nLoaded %i credential profiles." % len(opts.passwds))
        click.echo("Loaded %i unique scanners.\n" % len(scanners))

        for s in scanners:
            cls._q_scanners.put(s)

        tasks = []
        for i in range(opts.threads):
            t = Thread(target=cls._scan_worker)
            t.start()
            tasks.append(t)

        cls._q_scanners.join()
        opts.running = False
        for i in range(opts.threads):
            cls._q_scanners.put(None)

        for t in tasks:
            t.join()

    @classmethod
    def _scan_worker(cls):
        while opts.running and not cls._q_scanners.empty():
            s = cls._q_scanners.get()
            if s is None:
                break
            s.scan()
            cls._q_scanners.task_done()

    @classmethod
    def anysearch(cls, keywords, verbose):
        """ 从密码库中搜索密码 """
        click.echo("Searching passwords from profiles...")
        passwds = Passwd.load()

        matched = []
        click.echo("[+] Loaded %s passwd profiles." % len(passwds))

        if verbose < 1:
            for passwd in passwds:
                if passwd.match(keywords):
                    matched += passwd.creds()
            matched = set(matched)
            print("\n")
            for x in matched:
                print(x)
            print("\n")
        elif verbose < 2:
            for passwd in passwds:
                if passwd.match(keywords):
                    matched += passwd.cred_rows()
            pt = PrettyTable(["Username", "Password", "Name"])
            pt.align["Name"] = "l"
            for row in matched:
                pt.add_row(row)
            print(pt.get_string())
        else:
            for passwd in passwds:
                if passwd.match(keywords):
                    print("\n-----------------------------")
                    print(passwd.yaml())
                    matched.append(passwd.yaml())

        if matched:
            click.secho("[+] Found %s passwd." % len(matched), fg="green")
        else:
            click.secho("[x] No matching passwd profile found.", fg="red")

    @classmethod
    def anyupdate(cls):
        """ 从 cirt.net 更新密码库"""
        click.echo("Updating passwords from cirt.net...")
        from .cirt import CirtPass

        try:
            CirtPass.update()
            click.secho("[+] Passwords update completed.", fg="green")
        except Exception as e:
            click.secho("[x] Passwords update failed.", fg="red")
            print("%s Exception: %s" % (type(e).__name__, str(e)))

    @classmethod
    def anylist(cls):
        """ 列出所有支持的设备信息和服务类型 """
        click.echo("Loading passwords from profiles...")
        pt = PrettyTable(["Name", "Category", "Port", "Passwd Count"])
        pt.align["Name"] = "l"
        table = Passwd.table()
        for row in table:
            pt.add_row(row)
        print(pt.get_string())
        click.secho("[+] Loaded %s passwd profiles." % len(table), fg="green")
