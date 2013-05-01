#!/usr/bin/python
"""
Simple, ugly test script for QA
"""
import time
import os
import sys

TIMEOUT = 5  # should be enough
now = time.time()

res = {}

qa = {
      'noquestion': [None, None],
      'simple': ['Simple question: ', 'simple answer'],
      'whattime':['Now it is %s. What time is it? ' % now, "%s" % now],
      'waitforit':['Now is the time.' , 'OK'],
      }

for k, v in qa.items():
    if k in sys.argv:
        if v[0] is None:
            res[k] = [True, None]
        else:
            if 'wait' in k:
                print 'Wait for it (%d seconds)' % TIMEOUT,
                sys.stdout.flush()
                time.sleep(TIMEOUT)
            print v[0],
            sys.stdout.flush()
            a = sys.stdin.readline().rstrip('\n')
            res[k] = [a == v[1], a]

if __name__ == '__main__':
    failed = 0

    for k, v in res.items():
        if v[0]:
            print "Test %s OK" % k
        else:
            failed += 1
            print "Test %s NOT OK expected answer '%s', received '%s'" % (k, qa[k][1], v[1])

    sys.exit(failed)
