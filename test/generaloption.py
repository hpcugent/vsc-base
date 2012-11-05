##
# Copyright 2012 Stijn De Weirdt
#
# This file is part of VSC-tools,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/VSC-tools
#
# VSC-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# VSC-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VSC-tools. If not, see <http://www.gnu.org/licenses/>.
##
import os
from unittest import TestCase, TestLoader

from vsc.generaloption import GeneralOption

class TestOption1(GeneralOption):
    """Create simple test class"""
    def base_options(self):
        """Make base options"""
        opts = {"base":("Long and short base option", None, "store_true", False, 'b'),
                "longbase":("Long-only base option", None, "store_true", True),
              }
        descr = ["Base", "Base level of options"]

        prefix = None ## base, no prefixes
        self.add_group_parser(opts, descr, prefix=prefix)

    def level1_options(self):
        """Make the level1 related options"""
        opts = {"level":("Long and short option", None, "store_true", False, 'l'),
                "longlevel":("Long-only level option", None, "store_true", True),
              }
        descr = ["Level1", "1 higher level of options"]

        prefix = 'level'
        self.add_group_parser(opts, descr, prefix=prefix)

    def make_init(self):
        self.base_options()
        self.level1_options()

TestOption1HelpShort = """Usage: optiontest1 [options]

Options:
  -h    show short help message and exit
  -H    show full help message and exit

  Debug options:
    -d  Enable debug log mode (default False) (def False)

  Base:
    Base level of options

    -b  Long and short base option (def False)

  Level1:
    1 higher level of options

    -l  Long and short option (def False)

All long option names can be passed as environment variables. Variable name is
OPTIONTEST1_<LONGNAME> eg. --debug is same as setting OPTIONTEST1_DEBUG in
environment
"""

TestOption1HelpLong = """Usage: optiontest1 [options]

Options:
  -h, --shorthelp      show short help message and exit
  -H, --help           show full help message and exit

  Debug options:
    -d, --debug        Enable debug log mode (default False) (def False)

  Base:
    Base level of options

    -b, --base         Long and short base option (def False)
    --longbase         Long-only base option (def True)

  Level1:
    1 higher level of options

    -l, --level_level  Long and short option (def False)
    --level_longlevel  Long-only level option (def True)

All long option names can be passed as environment variables. Variable name is
OPTIONTEST1_<LONGNAME> eg. --debug is same as setting OPTIONTEST1_DEBUG in
environment
"""

class GeneralOptionTest(TestCase):
    """Tests for general option"""

    def test_basic(self):
        """Basic creation and verification of generaloption"""

    def test_help_short(self):
        """Generate short help message"""
        topt = TestOption1(go_args=['-h'],
                           go_nosystemexit=True, # when printing help, optparse ends with sys.exit
                           help_to_string=True, # don't print to stdout, but to StingIO fh,
                           prog='optiontest1', # generate as if called from generaloption.py
                           )
        self.assertEqual(topt.parser.help_to_file.getvalue(), TestOption1HelpShort)

    def test_help_long(self):
        """Generate long help message"""
        topt = TestOption1(go_args=['-H'],
                           go_nosystemexit=True,
                           help_to_string=True,
                           prog='optiontest1',
                           )
        self.assertEqual(topt.parser.help_to_file.getvalue(), TestOption1HelpLong)


def suite():
    """ returns all the testcases in this module """
    return TestLoader().loadTestsFromTestCase(GeneralOptionTest)
