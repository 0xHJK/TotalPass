#!/usr/bin/env python3
# -*- coding=utf-8 -*-

import sys
from os import path

sys.path.insert(1, path.dirname(path.realpath(__file__)))

if sys.version_info >= (3, 7):
    import totalpass

    if __name__ == "__main__":
        totalpass.main()

else:
    print("Python 3.7+ Only.")
