#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import os
import sys
import logging
import click
from prettytable import PrettyTable
from .core import TPCore
from .passwd import Passwd
from .target import Target
from .settings import opts
from .__version__ import __version__


def banner():
    return (
        "\nTotalPass %s created by HJK.\nhttps://github.com/0xHJK/TotalPass\n"
        % __version__
    )


@click.group()
@click.version_option(message=banner())
def main():
    print(banner())


@main.command()
def list():
    """ 列出所有支持的设备信息和服务类型 """
    pt = PrettyTable(["Name", "Category", "Port", "Passwd Count"])
    pt.align["Name"] = "l"
    table = Passwd.table()
    for row in table:
        pt.add_row(row)
    print(pt.get_string())
    click.secho("[+] Loaded %s passwd profiles." % len(table), fg="green")


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
@click.argument("keywords", nargs=-1, required=True)
def search(keywords):
    """ 从密码库中搜索密码 """
    click.echo("Searching passwords from profiles...")
    passwds = Passwd.load()
    matched_passwds = []
    click.echo("[+] Loaded %s passwd profiles." % len(passwds))
    for passwd in passwds:
        if passwd.match(keywords):
            print("\n------------------------------------")
            print(passwd.yaml())
            matched_passwds.append(passwd)
    if matched_passwds:
        click.secho("[+] Found %s passwd profiles." % len(matched_passwds), fg="green")
    else:
        click.secho("[x] No matching passwd profile found.", fg="red")


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
        opts.name = name

    if common:
        opts.common = "common"

    if category:
        opts.categories = category
    else:
        from . import addons

        opts.categories = addons.__all__

    opts.port = port
    # passwds会影响categories，所以必须先load passwds
    opts.passwds = Passwd.load()
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
