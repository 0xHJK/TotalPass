#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import sys
import logging
import click
from prettytable import PrettyTable
from .core import TPCore
from .pwd import Pwd
from .target import Target
from .settings import opts
from .__version__ import __version__, __author__


def banner():
    s1 = """
      _____    _        _ ___            _ 
     |_   _|__| |_ __ _| | _ \__ __ ____| |
       | |/ _ \  _/ _` | |  _/\ V  V / _` |
       |_|\___/\__\__,_|_|_|   \_/\_/\__,_|
    ----------------------------------------
    """
    s2 = "                     By %s v%s\n" % (__author__, __version__)
    return s1 + s2


def version():
    s1 = "\nTotalPwd, Version %s, By %s\n" % (__version__, __author__)
    return s1


@click.group()
@click.version_option(message=version())
def main():
    print(banner())


@main.command()
def list():
    """ 列出所有支持的设备信息和服务类型 """
    pt = PrettyTable(["Name", "Category", "Port", "Pwd Count"])
    pt.align["Name"] = "l"
    info = Pwd.info()
    for row in info:
        pt.add_row(row)
    print(pt.get_string())
    click.secho("[+] Loaded %s pwd profiles." % len(info), fg="green")


@main.command()
def update():
    """ 从 cirt.net 更新密码库"""
    click.echo("Updating passwords from cirt.net...")
    from .cirt import CirtPass

    try:
        CirtPass.update()
        click.secho("[+] Passwords update completed.", fg="green")
    except Exception as e:
        click.secho("[x] Passwords update failed.", fg="red")
        print("%s Exception: %s" % (type(e).__name__, str(e)))


@main.command()
@click.option("-x", "--name", help="指定设备型号或品牌")
def search():
    """ 从密码库中搜索密码 """
    click.echo("Searching...")


@main.command()
@click.argument("target", nargs=-1, required=True)
@click.option("-x", "--name", help="指定设备型号或品牌")
@click.option("-c", "--category", multiple=True, help="指定扫描类型")
@click.option("-p", "--port", type=int, help="指定扫描端口")
@click.option("--common", is_flag=True, default=False, help="使用常见弱口令字典")
@click.option("-t", "--threads", default=10, type=int, help="指定线程数量")
@click.option("-v", "--verbose", count=True, help="详细输出模式")
def scan(target, name, common, category, port, threads, verbose):
    """ 指定目标进行密码扫描 """
    click.echo("Scaning...")

    if verbose < 1:
        level = logging.WARNING
    elif verbose < 2:
        level = logging.INFO
    else:
        level = logging.DEBUG
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)-8s | %(msg)s ",
        datefmt="%H:%M:%S",
    )

    opts.threads = threads

    if name:
        opts.name = name.upper()

    if common:
        opts.common = "common"

    if category:
        opts.categories = category
    else:
        from . import addons

        opts.categories = addons.__all__

    opts.port = port
    # pwds会影响categories，所以必须先load pwds
    opts.pwds = Pwd.load()
    opts.targets = Target.parse(target)

    opts.running = True
    try:
        tpc = TPCore()
        tpc.anyscan()
    except KeyboardInterrupt as e:
        opts.running = False
        click.echo("Exit.")
        sys.exit()
    finally:
        click.echo("\n--- Result -------------")
        if not opts.result:
            click.secho("[x] Not Found", fg="red")
        else:
            for msg in opts.result:
                click.secho(msg, fg="green")
        click.echo("------------------------\n")


if __name__ == "__main__":
    main()
