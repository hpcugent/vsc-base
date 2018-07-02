#
# Copyright 2016-2017 Ghent University
#
# This file is part of vsc-base,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/hpcugent/vsc-base
#
# vsc-base is free software: you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation, either version 2 of
# the License, or (at your option) any later version.
#
# vsc-base is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with vsc-base. If not, see <http://www.gnu.org/licenses/>.
#
"""
Simple, ugly test script for QA
"""
import time
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
    'nonewline': ('Do NOT give me a newline', 'Sure'),
}

for k, v in qa.items():
    if k == sys.argv[1]:

        # sanity case: no answer and no question
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

                # for all regular cases, we do not care if there was a newline
                # but for the case where no newline is added to the answer, we
                # better not strip it :)
                if k != 'nonewline':
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
        elif 'nonewline' in k:
            if v[1][-1] == '\n':
                failed += 1
                print "Test %s NOT OK, did not expect a newline in the answer" % (k,)
        elif v[0]:
            print "Test %s OK" % k
        else:
            failed += 1
            print "Test %s NOT OK expected answer '%s', received '%s'" % (k, qa[k][1], v[1])

    sys.exit(failed)
