#!/usr/bin/python
"""
Simple, ugly test script for QA
"""
import time
import os
import re
import sys

TIMEOUT = 5  # should be enough
now = time.time()

res = {}

qa = {
    'ask_number': ("Enter a number ('0' to stop):", r'^\d+$'),
    'noquestion': (None, None),
    'simple': ('Simple question: ', 'simple answer'),
    'whattime': ('Now it is %s. What time is it? ' % now, "%s" % now),
    'waitforit': ('Now is the time.', 'OK'),
}

for k, v in qa.items():
    if k == sys.argv[1]:
        if v[0] is None:
            res[k] = [True, None]
        else:
            loop_cnt = 1
            if k == 'waitforit':
                print 'Wait for it (%d seconds)' % TIMEOUT,
                sys.stdout.flush()
                time.sleep(TIMEOUT)
            elif k == 'ask_number':
                if len(sys.argv) == 3:
                    loop_cnt = int(sys.argv[2])
            for i in range(0, loop_cnt):
                print v[0],
                sys.stdout.flush()
                a = sys.stdin.readline().rstrip('\n')
                a_re = re.compile(v[1])
                if k == 'ask_number':
                    if a == '0':
                        # '0' means stop
                        break
                    prev = 0
                    if k in res:
                        prev = int(res[k][1])
                    a = str(prev + int(a))
                res[k] = [a_re.match(a), a]

if __name__ == '__main__':
    failed = 0

    for k, v in res.items():
        if 'ask_number' in k and v[0]:
            print "Answer: %s" % v[1]
        elif v[0]:
            print "Test %s OK" % k
        else:
            failed += 1
            print "Test %s NOT OK expected answer '%s', received '%s'" % (k, qa[k][1], v[1])

    sys.exit(failed)
