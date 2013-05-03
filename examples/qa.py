#!/usr/bin/python
#
# Copyright 2013-2013 Ghent University
#
# This file is part of vsc-base,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/vsc-base
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
Simple QA script

@author: Stijn De Weirdt (Ghent University)
"""
import os

from vsc.utils.run import run_qa, run_qalog, run_qastdout, run_async_to_stdout
from vsc.utils.generaloption import simple_option

go = simple_option(None)

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), '..', 'test', 'runtests')
SCRIPT_QA = os.path.join(SCRIPT_DIR, 'qa.py')


def test_qa():
    qa_dict = {
               'Simple question:': 'simple answer',
               }
    ec, output = run_qa([SCRIPT_QA, 'simple'], qa=qa_dict)
    return ec, output


def test_qalog():
    qa_dict = {
               'Simple question:': 'simple answer',
               }
    ec, output = run_qalog([SCRIPT_QA, 'simple'], qa=qa_dict)
    return ec, output


def test_qastdout():
    run_async_to_stdout([SCRIPT_QA, 'simple'])
    qa_dict = {
               'Simple question:': 'simple answer',
               }
    ec, output = run_qastdout([SCRIPT_QA, 'simple'], qa=qa_dict)
    return ec, output


def test_std_regex():
    qa_dict = {
               r'\s(?P<time>\d+(?:\.\d+)?)\..*?What time is it\?': '%(time)s',
               }
    ec, output = run_qastdout([SCRIPT_QA, 'whattime'], qa_reg=qa_dict)
    return ec, output


def test_qa_noqa():
    qa_dict = {
               'Now is the time.': 'OK',
               }
    no_qa = ['Wait for it \(\d+ seconds\)']
    ec, output = run_qastdout([SCRIPT_QA, 'waitforit'], qa=qa_dict, no_qa=no_qa)
    return ec, output


def test_qanoquestion():
    ec, output = run_qalog([SCRIPT_QA, 'noquestion'])
    return ec, output

if __name__ == '__main__':
    test_qanoquestion()
    test_qastdout()
    test_qa()
    test_qalog()
    test_std_regex()
    test_qa_noqa()
