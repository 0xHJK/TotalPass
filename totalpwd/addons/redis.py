#!/usr/bin/env python3
# -*- coding=utf-8 -*-

"""
    Redis 密码扫描器
"""

import redis
from ..settings import opts
from ..scanner import Scanner

class RedisScanner(Scanner):
    """
        Redis 密码扫描器
    """
    def __init__(self, pwd, target, username, password):
        super(RedisScanner, self).__init__(pwd, target, username, password)
        self.port = self.port or 6379
    
    def _check(self):
        r = redis.StrictRedis(host=self.host, port=self.port)
        info = r.info()
        evidence = "redis_version: %s, os: %s" % (info['redis_version'], info['os'])
        return evidence


def mkscanner(pwd, target, username, password):
    return RedisScanner(pwd, target, username, password)
 