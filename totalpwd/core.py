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
        targets = [t for t in opts.targets if t.alive()]
        if not targets:
            return

        click.echo("\nLoaded %i credential profiles." % len(opts.pwds))

        scanners = self.load_scanners(
            pwds=opts.pwds, categories=opts.categories, targets=targets
        )

        click.echo("Loaded %i unique scanners.\n" % len(scanners))
        for s in scanners:
            s.scan()

    def load_scanners(self, pwds, categories, targets):
        scanners = []
        for cat in categories:
            # 按需加载插件
            if cat in addons.__all__:
                addon = sys.modules.get("%s.addons.%s" % (__package__, cat))
                scanners += addon.mkscanners(pwds, targets)
        # click.echo("Loaded %i scanners." % len(scanners))
        scanners = list(set(scanners))

        return scanners
