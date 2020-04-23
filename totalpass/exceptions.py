#!/usr/bin/env python3
# -*- coding=utf-8 -*-


class InvalidCredential(RuntimeError):
    """ 帐号或密码错误 """

    def __init__(self, *args, **kwargs):
        pass
