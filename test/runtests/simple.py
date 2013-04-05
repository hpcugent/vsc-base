#!/usr/bin/python
"""
Simple, ugly test script
"""
import time
import os
import sys

EC_SUCCES = 0
EC_NOARGS = 1

txt = []
ec = EC_SUCCES

if 'shortsleep' in sys.argv:
    time.sleep(0.1)
    txt.append("Shortsleep completed")

if 'longsleep' in sys.argv:
    time.sleep(10)
    txt.append("Longsleep completed")

if __name__ == '__main__':
    if len(txt) == 0:
        txt.append('Nothing passed')
        ec = EC_NOARGS
    print "\n".join(txt)
    sys.exit(ec)
