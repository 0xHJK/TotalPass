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
    TPCore.anylist()


@main.command()
def update():
    """ 从 cirt.net 更新密码库"""
    TPCore.anyupdate()


@main.command()
@click.argument("keywords", nargs=-1, required=True)
@click.option("-v", "--verbose", count=True, help="详细输出模式")
def search(keywords, verbose):
    """ 从密码库中搜索密码 """
    TPCore.anysearch(keywords, verbose)


@main.command()
@click.argument("target", nargs=-1, required=True)
@click.option("-x", "--name", help="指定设备型号或品牌")
@click.option("-c", "--category", multiple=True, help="指定扫描类型")
@click.option("-p", "--port", type=int, help="指定扫描端口")
@click.option("-d", "--dirname", help="指定字典目录或文件")
@click.option("--common", is_flag=True, default=False, help="使用常见弱口令字典")
@click.option("-t", "--threads", default=10, type=int, help="指定线程数量")
@click.option("-v", "--verbose", count=True, help="详细输出模式")
def scan(target, name, common, category, port, dirname, threads, verbose):
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

    if dirname and os.path.exists(dirname):
        opts.passwds_path = dirname
    # passwds会影响categories，所以必须先load passwds
    opts.passwds = Passwd.load()
    opts.targets = Target.parse(target)

    opts.running = True
    
    try:
        TPCore.anyscan()
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
