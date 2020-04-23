#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    https://cirt.net/passwords 爬虫
    更新默认密码信息
"""

import os
import re
import copy
import logging
import requests
import click
import yaml
from os import path
from threading import Thread
from queue import Queue
from .settings import opts
from .passwd import Passwd
from pyquery import PyQuery as pq


class CirtPass(object):
    """
        cirt.net 密码爬虫
    """

    logger = logging.getLogger("TotalPass")
    key_map = {"User ID": "username", "Password": "password", "Method": "category"}

    qt = Queue()

    def __init__(self):
        pass

    @classmethod
    def mkdir(cls, dirname):
        if path.exists(dirname):
            if not path.isdir(dirname):
                # 如果存在但不是文件夹则删除再创建
                os.remove(dirname)
                os.makedirs(dirname)
        else:
            os.makedirs(dirname)

    @classmethod
    def update(cls):
        """
            更新密码
        """
        cirt_path = path.join(opts.passwds_path, "cirt")
        cls.mkdir(cirt_path)
        # 获取不同厂商的密码链接
        ven_urls = cls.geturls("https://cirt.net/passwords")

        for vendor, url in ven_urls:
            if vendor:
                cls.qt.put((vendor, url))

        for i in range(opts.threads):
            t = Thread(target=cls.fetchpasswds, args=(cirt_path,))
            t.start()

        cls.qt.join()

    @classmethod
    def geturls(cls, url) -> list:
        ven_urls = []  # (name, url)
        try:
            d = pq(cls.fetch(url))
            for td_a in d("td a"):
                ad = pq(td_a)
                vendor, link = ad.text(), ad.attr("href")
                if vendor:
                    link = url + link
                    ven_urls.append((vendor, link))
        except Exception as e:
            click.secho("[x] fetch url %s failed." % url, fg="red")
            cls.logger.error("%s Exception: %s" % (type(e).__name__, str(e)))
        return ven_urls

    @classmethod
    def fetchpasswds(cls, cirt_path):
        """
            从URL获得数据并分析得到passwd保存到文件
        """
        while not cls.qt.empty():
            vendor, url = cls.qt.get()
            # 创建文件夹
            ven_dir = path.join(cirt_path, vendor.lower())
            ven_dir = re.sub("[\.\,]", "", ven_dir)
            ven_dir = re.sub("[\|\*\&\^@]", "-", ven_dir)

            cls.mkdir(ven_dir)

            passwds_map = {}
            try:
                # 从URL获得数据
                d = pq(cls.fetch(url))
                for tb in d("table"):
                    d_tb = pq(tb)
                    model = pq(d_tb("h3 i")).text()
                    title = model
                    count = len(d_tb("td"))
                    table = {"title": title, "comment": ""}  # 把cirt的表格格式化成一个字典
                    for i in range(1, count, 2):  # 从第二个td开始，第一个td是title
                        key = pq(d_tb("td")[i]).text()
                        val = pq(d_tb("td")[i + 1]).text()
                        if not val:
                            continue
                        if key in cls.key_map:
                            table[cls.key_map[key]] = (
                                val.strip() if val != "(none)" else ""
                            )
                        else:
                            table["comment"] += "%s: %s; " % (key, val)

                    # 拆分类别字段
                    categories = table.get("category", "").lower()
                    if not categories:
                        categories = ["unknown"]
                    elif "," in categories:
                        categories = categories.split(",")
                    elif "/" in categories:
                        categories = categories.split("/")
                    else:
                        categories = [categories]

                    for cat in categories:
                        cat = cat.strip()
                        new_table = copy.deepcopy(table)
                        new_table["category"] = cat
                        passwd = passwds_map.get(new_table["title"], None)
                        cred = dict(
                            username=new_table.get("username", ""),
                            password=new_table.get("password", ""),
                        )
                        if passwd:
                            if passwd.category == cat:
                                # 如果passwd已存在并且分类相同则只添加密码
                                passwd.credentials.append(cred)
                                continue
                            else:
                                # 如果分类不同也需要创建新的
                                title = model + " - " + cat
                        # 如果passwd不存在则创建一个
                        passwd = Passwd(
                            vendor=vendor,
                            name=vendor + " - " + title,
                            category=cat,
                            credentials=[cred],
                            port=0,
                            comment=new_table.get("comment", ""),
                        )
                        passwd.title = title
                        passwds_map[title] = passwd

                # 保存获取到的数据
                for title, passwd in passwds_map.items():
                    fname = re.sub("[~`!@#\$%\^&\*\/\?\:\|]", "-", title)
                    fullname = path.join(ven_dir, fname + ".yml")
                    with open(fullname, "w") as f:
                        f.write(passwd.yaml())
                    click.echo("Saved to %s." % fullname)

                cls.qt.task_done()

            except Exception as e:
                click.secho("[x] fetch passwds %s failed." % url, fg="red")
                cls.logger.error("%s Exception: %s" % (type(e).__name__, str(e)))

    @classmethod
    def fetch(cls, url):
        cls.logger.info("Fetching %s..." % url)
        s = requests.Session()
        r = s.get(url)
        return r.text
