#
# Copyright 2012-2017 Ghent University
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
Tests for the vsc.utils.run module.

@author: Stijn De Weirdt (Ghent University)
"""
import pkgutil
import os
import re
import stat
import sys
import tempfile
import time
import shutil
from unittest import TestLoader, main

from vsc.utils.run import CmdList, run, run_simple, run_asyncloop, run_timeout, RunQA, RunTimeout
from vsc.utils.run import RUNRUN_TIMEOUT_OUTPUT, RUNRUN_TIMEOUT_EXITCODE, RUNRUN_QA_MAX_MISS_EXITCODE
from vsc.install.testing import TestCase


SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'runtests')
SCRIPT_SIMPLE = os.path.join(SCRIPTS_DIR, 'simple.py')
SCRIPT_QA = os.path.join(SCRIPTS_DIR, 'qa.py')
SCRIPT_NESTED = os.path.join(SCRIPTS_DIR, 'run_nested.sh')


class RunQAShort(RunQA):
    LOOP_MAX_MISS_COUNT = 3  # approx 3 sec

run_qas = RunQAShort.run


class TestRun(TestCase):
    """Test for the run module."""

    def setUp(self):
        super(TestCase, self).setUp()
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        super(TestCase, self).tearDown()
        shutil.rmtree(self.tempdir)

    def test_simple(self):
        ec, output = run_simple([sys.executable, SCRIPT_SIMPLE, 'shortsleep'])
        self.assertEqual(ec, 0)
        self.assertTrue('shortsleep' in output.lower())

    def test_startpath(self):
        cwd = os.getcwd()

        cmd = "echo foo > bar"

        self.assertErrorRegex(ValueError, '.*', run_simple, cmd, startpath='/no/such/directory')

        ec, out = run_simple(cmd, startpath=self.tempdir)

        # successfull command, no output
        self.assertEqual(ec, 0)
        self.assertEqual(out, '')

        # command was actually executed, in specified directory
        self.assertTrue(os.path.exists(os.path.join(self.tempdir, 'bar')))
        txt = open(os.path.join(self.tempdir, 'bar')).read()
        self.assertEqual(txt, 'foo\n')

        # we should still be in directory we were in originally
        self.assertEqual(cwd, os.getcwd())

    def test_simple_asyncloop(self):
        ec, output = run_asyncloop([sys.executable, SCRIPT_SIMPLE, 'shortsleep'])
        self.assertEqual(ec, 0)
        self.assertTrue('shortsleep' in output.lower())

    def test_simple_glob(self):
        ec, output = run_simple('ls test/sandbox/testpkg/*')
        self.assertEqual(ec, 0)
        self.assertTrue(all(x in output.lower() for x in ['__init__.py', 'testmodule.py', 'testmodulebis.py']))
        ec, output = run_simple(['ls','test/sandbox/testpkg/*'])
        self.assertEqual(ec, 0)
        self.assertTrue(all(x in output.lower() for x in ['__init__.py', 'testmodule.py', 'testmodulebis.py']))

    def test_noshell_glob(self):
        ec, output = run('ls test/sandbox/testpkg/*')
        self.assertTrue(ec > 0)
        self.assertTrue('test/sandbox/testpkg/*: No such file or directory' in output)
        ec, output = run_simple(['ls','test/sandbox/testpkg/*'])
        self.assertEqual(ec, 0)
        self.assertTrue(all(x in output.lower() for x in ['__init__.py', 'testmodule.py', 'testmodulebis.py']))

    def test_noshell_executable(self):
        ec, output = run("echo '(foo bar)'")
        self.assertEqual(ec, 0)
        self.assertTrue('(foo bar)' in output)

        ec, output = run(['echo', "(foo bar)"])
        self.assertEqual(ec, 0)
        self.assertTrue('(foo bar)' in output)

        # to run Python command, it's required to use the right executable (Python shell rather than default)
        ec, output = run("""%s -c 'print ("foo")'""" % sys.executable)
        self.assertEqual(ec, 0)
        self.assertTrue('foo' in output)

        ec, output = run([sys.executable, '-c', 'print ("foo")'])
        self.assertEqual(ec, 0)
        self.assertTrue('foo' in output)


    def test_timeout(self):
        timeout = 3

        # longsleep is 10sec
        start = time.time()
        ec, output = run_timeout([sys.executable, SCRIPT_SIMPLE, 'longsleep'], timeout=timeout)
        stop = time.time()
        self.assertEqual(ec, RUNRUN_TIMEOUT_EXITCODE, msg='longsleep stopped due to timeout')
        self.assertEqual(RUNRUN_TIMEOUT_OUTPUT, output, msg='longsleep expected output')
        self.assertTrue(stop - start < timeout + 1, msg='longsleep timeout within margin')  # give 1 sec margin

        # run_nested is 15 seconds sleep
        # 1st arg depth: 2 recursive starts
        # 2nd arg file: output file: format 'depth pid' (only other processes are sleep)

        def check_pid(pid):
            """ Check For the existence of a unix pid. """
            try:
                os.kill(pid, 0)
            except OSError:
                return False
            else:
                return True

        default = RunTimeout.KILL_PGID

        def do_test(kill_pgid):
            depth = 2 # this is the parent
            res_fn = os.path.join(self.tempdir, 'nested_kill_pgid_%s' % kill_pgid)
            start = time.time()
            RunTimeout.KILL_PGID = kill_pgid
            ec, output = run_timeout([SCRIPT_NESTED, str(depth), res_fn], timeout=timeout)
            # reset it to default
            RunTimeout.KILL_PGID = default
            stop = time.time()
            self.assertEqual(ec, RUNRUN_TIMEOUT_EXITCODE, msg='run_nested kill_pgid %s stopped due to timeout'  % kill_pgid)
            self.assertTrue(stop - start < timeout + 1, msg='run_nested kill_pgid %s timeout within margin' % kill_pgid)  # give 1 sec margin
            # make it's not too fast
            time.sleep(5)
            # there's now 6 seconds to complete the remainder
            pids = range(depth+1)
            # normally this is ordered output, but you never know
            for line in open(res_fn).readlines():
                dep, pid, _ = line.strip().split(" ") # 3rd is PPID
                pids[int(dep)] = int(pid)

            # pids[0] should be killed
            self.assertFalse(check_pid(pids[depth]), "main depth=%s pid (pids %s) is killed by timeout" % (depth, pids,))

            if kill_pgid:
                # others should be killed as well
                test_fn = self.assertFalse
                msg = ""
            else:
                # others should be running
                test_fn = self.assertTrue
                msg = " not"

            for dep, pid in enumerate(pids[:depth]):
                test_fn(check_pid(pid), "depth=%s pid (pids %s) is%s killed kill_pgid %s" % (dep, pids, msg, kill_pgid))

            # clean them all
            for pid in pids:
                try:
                    os.kill(pid, 0) # test first
                    os.kill(pid, 9)
                except OSError:
                    pass

        do_test(False)
        # TODO: find a way to change the pid group before starting this test
        #       now it kills the test process too ;)
        #       It's ok not to test, as it is not the default, and it's not easy to change it
        #do_test(True)

    def test_qa_simple(self):
        """Simple testing"""
        ec, output = run_qas([sys.executable, SCRIPT_QA, 'noquestion'])
        self.assertEqual(ec, 0)

        qa_dict = {
                   'Simple question:': 'simple answer',
                   }
        ec, output = run_qas([sys.executable, SCRIPT_QA, 'simple'], qa=qa_dict)
        self.assertEqual(ec, 0)

    def test_qa_regex(self):
        """Test regex based q and a (works only for qa_reg)"""
        qa_dict = {
                   '\s(?P<time>\d+(?:\.\d+)?).*?What time is it\?': '%(time)s',
                   }
        ec, output = run_qas([sys.executable, SCRIPT_QA, 'whattime'], qa_reg=qa_dict)
        self.assertEqual(ec, 0)

    def test_qa_noqa(self):
        """Test noqa"""
        # this has to fail
        qa_dict = {
                   'Now is the time.': 'OK',
                   }
        ec, output = run_qas([sys.executable, SCRIPT_QA, 'waitforit'], qa=qa_dict)
        self.assertEqual(ec, RUNRUN_QA_MAX_MISS_EXITCODE)

        # this has to work
        no_qa = ['Wait for it \(\d+ seconds\)']
        ec, output = run_qas([sys.executable, SCRIPT_QA, 'waitforit'], qa=qa_dict, no_qa=no_qa)
        self.assertEqual(ec, 0)

    def test_qa_list_of_answers(self):
        """Test qa with list of answers."""
        # test multiple answers in qa
        qa_dict = {
            "Enter a number ('0' to stop):": ['1', '2', '4', '0'],
        }
        ec, output = run_qas([sys.executable, SCRIPT_QA, 'ask_number', '4'], qa=qa_dict)
        self.assertEqual(ec, 0)
        answer_re = re.compile(".*Answer: 7$")
        self.assertTrue(answer_re.match(output), "'%s' matches pattern '%s'" % (output, answer_re.pattern))

        # test multple answers in qa_reg
        # and test premature exit on 0 while we're at it
        qa_reg_dict = {
            "Enter a number \(.*\):": ['2', '3', '5', '0'] + ['100'] * 100,
        }
        ec, output = run_qas([sys.executable, SCRIPT_QA, 'ask_number', '100'], qa_reg=qa_reg_dict)
        self.assertEqual(ec, 0)
        answer_re = re.compile(".*Answer: 10$")
        self.assertTrue(answer_re.match(output), "'%s' matches pattern '%s'" % (output, answer_re.pattern))

        # verify type checking on answers
        self.assertErrorRegex(TypeError, "Invalid type for answer", run_qas, [], qa={'q': 1})

        # test more questions than answers, both with and without cycling
        qa_reg_dict = {
            "Enter a number \(.*\):": ['2', '7'],
        }
        # loop 3 times, with cycling (the default) => 2 + 7 + 2 + 7 = 18
        self.assertTrue(RunQAShort.CYCLE_ANSWERS)
        orig_cycle_answers = RunQAShort.CYCLE_ANSWERS
        RunQAShort.CYCLE_ANSWERS = True
        ec, output = run_qas([sys.executable, SCRIPT_QA, 'ask_number', '4'], qa_reg=qa_reg_dict)
        self.assertEqual(ec, 0)
        answer_re = re.compile(".*Answer: 18$")
        self.assertTrue(answer_re.match(output), "'%s' matches pattern '%s'" % (output, answer_re.pattern))
        # loop 3 times, no cycling => 2 + 7 + 7 + 7 = 23
        RunQAShort.CYCLE_ANSWERS = False
        ec, output = run_qas([sys.executable, SCRIPT_QA, 'ask_number', '4'], qa_reg=qa_reg_dict)
        self.assertEqual(ec, 0)
        answer_re = re.compile(".*Answer: 23$")
        self.assertTrue(answer_re.match(output), "'%s' matches pattern '%s'" % (output, answer_re.pattern))
        # restore
        RunQAShort.CYCLE_ANSWERS = orig_cycle_answers

    def test_qa_no_newline(self):
        """Test we do not add newline to the answer."""
        qa_dict = {
                   'Do NOT give me a newline': 'Sure',
                   }
        qas = RunQAShort(add_newline=False)
        ec, _ = qas.run([sys.executable, SCRIPT_QA, 'nonewline'], qa=qa_dict)
        self.assertEqual(ec, 0)


    def test_cmdlist(self):
        """Tests for CmdList."""

        # starting with empty command is supported
        # this is mainly useful when parts of a command are put together separately (cfr. mympirun)
        cmd = CmdList()
        self.assertEqual(cmd, [])
        cmd.add('-x')
        self.assertEqual(cmd, ['-x'])

        cmd = CmdList('test')
        self.assertEqual(cmd, ['test'])

        # can add options/arguments via string or list of strings
        cmd.add('-t')
        cmd.add(['--opt', 'foo', '-o', 'bar', '--optbis=baz'])

        expected = ['test', '-t', '--opt', 'foo', '-o', 'bar', '--optbis=baz']
        self.assertEqual(cmd, ['test', '-t', '--opt', 'foo', '-o', 'bar', '--optbis=baz'])

        # add options/arguments via a template
        cmd.add('%(name)s', tmpl_vals={'name': 'namegoeshere'})
        cmd.add(['%(two)s', '%(one)s'], tmpl_vals={'one': 1, 'two': 2})
        cmd.add('%(three)s%(five)s%(one)s', tmpl_vals={'one': '1', 'three': '3', 'five': '5'})
        cmd.add('%s %s %s', tmpl_vals=('foo', 'bar', 'baz'))

        expected.extend(['namegoeshere', '2', '1', '351', 'foo bar baz'])
        self.assertEqual(cmd, expected)

        # .append and .extend are broken, on purpose, to force use of add
        self.assertErrorRegex(NotImplementedError, "Use add", cmd.append, 'test')
        self.assertErrorRegex(NotImplementedError, "Use add", cmd.extend, ['test1', 'test2'])

        # occurence of spaces can be disallowed (but is allowed by default)
        cmd.add('this has spaces')

        err = "Found one or more spaces"
        self.assertErrorRegex(ValueError, err, cmd.add, 'this has spaces', allow_spaces=False)

        kwargs = {
            'tmpl_vals': {'foo': 'this has spaces'},
            'allow_spaces': False,
        }
        self.assertErrorRegex(ValueError, err, cmd.add, '%(foo)s', **kwargs)

        kwargs = {
            'tmpl_vals': {'one': 'one ', 'two': 'two'},
            'allow_spaces': False,
        }
        self.assertErrorRegex(ValueError, err, cmd.add, '%(one)s%(two)s', **kwargs)

        expected.append('this has spaces')
        self.assertEqual(cmd, expected)

        # can also init with multiple arguments
        cmd = CmdList('echo', "hello world", 'test')
        self.assertEqual(cmd, ['echo', "hello world", 'test'])

        # can also create via template
        self.assertEqual(CmdList('%(one)s', tmpl_vals={'one': 1}), ['1'])

        # adding non-string items yields an error
        self.assertErrorRegex(ValueError, "Non-string item", cmd.add, 1)
        self.assertErrorRegex(ValueError, "Non-string item", cmd.add, None)
        self.assertErrorRegex(ValueError, "Non-string item", cmd.add, ['foo', None])

        # starting with non-string stuff also fails
        self.assertErrorRegex(ValueError, "Non-string item", CmdList, 1)
        self.assertErrorRegex(ValueError, "Non-string item", CmdList, ['foo', None])
        self.assertErrorRegex(ValueError, "Non-string item", CmdList, ['foo', ['bar', 'baz']])
        self.assertErrorRegex(ValueError, "Found one or more spaces", CmdList, 'this has spaces', allow_spaces=False)
