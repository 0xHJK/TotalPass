#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    配置和全局变量
"""
import os


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Options(metaclass=Singleton):
    """
        全局配置
    """

    def __init__(self):
        self.pwds_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "pwds"
        )
        self.pwds = []
        self.targets = []
        self.categories = []
        self.port = 0
        self.threads = 10
        self.timeout = 7
        self.timeout_alive = 2
        self.common = ""
        self.port_map = dict(
            ftp=21,
            ssh=22,
            telnet=23,
            smtp=25,
            http=80,
            snmp=161,
            mysql=3306,
            rdp=3389,
            redis=6379,
        )
        self.result = []
        self.running = False

    def __repr__(self):
        return self.info()

    def info(self):
        s = ""
        s += "Pwds Path: %s\n" % self.pwds_path
        s += "Pwds Count: %s\n" % len(self.pwds)
        s += "Categories: %s\n" % ", ".join(self.categories)
        s += "Port: %s\n" % self.port
        s += "Targets:\n > "
        s += ",\n > ".join([str(t) for t in self.targets])
        return s


opts = Options()
