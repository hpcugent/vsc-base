##
#
# Copyright 2012 Ghent University
# Copyright 2012 Ghent University
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
import datetime
import os
from unittest import TestCase, TestLoader

from vsc.utils.generaloption import GeneralOption, shell_quote, shell_unquote

class TestOption1(GeneralOption):
    """Create simple test class"""
    def base_options(self):
        """Make base options"""
        opts = {"base":("Long and short base option", None, "store_true", False, 'b'),
                "longbase":("Long-only base option", None, "store_true", True),
                "store":("Store option", None, "store", None),
              }
        descr = ["Base", "Base level of options"]

        prefix = None  # base, no prefixes
        self.add_group_parser(opts, descr, prefix=prefix)

    def level1_options(self):
        """Make the level1 related options"""
        opts = {"level":("Long and short option", None, "store_true", False, 'l'),
                "longlevel":("Long-only level option", None, "store_true", True),
              }
        descr = ["Level1", "1 higher level of options"]

        prefix = 'level'
        self.add_group_parser(opts, descr, prefix=prefix)

    def ext_options(self):
        """Make ExtOption options"""
        opts = {"extend":("Test action extend", None, 'extend', None),
                "extenddefault":("Test action extend with default set", None, 'extend', ['zero']),
                "date":('Test action datetime.date', None, 'date', None),
                "datetime":('Test action datetime.datetime', None, 'datetime', None),
                "optional":('Test action optional', None, 'store_or_None', 'DEFAULT', 'o'), # type is mandatory
                }
        descr = ["ExtOption", "action from ExtOption"]

        prefix = 'ext'
        self.add_group_parser(opts, descr, prefix=prefix)

    def make_init(self):
        self.base_options()
        self.level1_options()
        self.ext_options()

TestOption1HelpShort = """Usage: optiontest1 [options]

Options:
  -h             show short help message and exit
  -H             show full help message and exit

  Debug options:
    -d           Enable debug log mode (def False)

  Base:
    Base level of options

    -b           Long and short base option (def False)

  Level1:
    1 higher level of options

    -l           Long and short option (def False)

  ExtOption:
    action from ExtOption

    -o OPTIONAL  Test action optional (def DEFAULT)

Boolean options support disable prefix to do the inverse of the action, e.g. option --someopt also
supports --disable-someopt.

All long option names can be passed as environment variables. Variable name is
OPTIONTEST1_<LONGNAME> eg. --someopt is same as setting OPTIONTEST1_SOMEOPT in the environment.
"""

TestOption1HelpLong = """Usage: optiontest1 [options]

Options:
  -h, --shorthelp       show short help message and exit
  -H, --help            show full help message and exit

  Debug options:
    -d, --debug         Enable debug log mode (def False)

  Base:
    Base level of options

    -b, --base          Long and short base option (def False)
    --longbase          Long-only base option (def True)
    --store=STORE       Store option

  Level1:
    1 higher level of options

    -l, --level_level   Long and short option (def False)
    --level_longlevel   Long-only level option (def True)

  ExtOption:
    action from ExtOption

    --ext_date=DATE     Test action datetime.date
    --ext_datetime=DATETIME
                        Test action datetime.datetime
    --ext_extend=EXTEND
                        Test action extend (type comma-separated list)
    --ext_extenddefault=EXTENDDEFAULT
                        Test action extend with default set (type comma-separated list; def
                        ['zero'])
    -o OPTIONAL, --ext_optional=OPTIONAL
                        Test action optional (def DEFAULT)

Boolean options support disable prefix to do the inverse of the action, e.g. option --someopt also
supports --disable-someopt.

All long option names can be passed as environment variables. Variable name is
OPTIONTEST1_<LONGNAME> eg. --someopt is same as setting OPTIONTEST1_SOMEOPT in the environment.
"""

class GeneralOptionTest(TestCase):
    """Tests for general option"""

    def test_basic(self):
        """Basic creation and verification of generaloption"""

    def test_help_short(self):
        """Generate short help message"""
        topt = TestOption1(go_args=['-h'],
                           go_nosystemexit=True, # when printing help, optparse ends with sys.exit
                           go_columns=100, # fix col size for reproducible unittest output
                           help_to_string=True, # don't print to stdout, but to StingIO fh,
                           prog='optiontest1', # generate as if called from generaloption.py
                           )
        self.assertEqual(topt.parser.help_to_file.getvalue(), TestOption1HelpShort)

    def test_help_long(self):
        """Generate long help message"""
        topt = TestOption1(go_args=['-H'],
                           go_nosystemexit=True,
                           go_columns=100,
                           help_to_string=True,
                           prog='optiontest1',
                           )
        self.assertEqual(topt.parser.help_to_file.getvalue(), TestOption1HelpLong)

    def test_quote(self):
        """Test quote/unquote"""
        value = 'value with whitespace'
        txt = '--option=%s' % value
        # this looks strange, but is correct
        self.assertEqual(str(txt), '--option=value with whitespace')
        self.assertEqual(txt , shell_unquote(shell_quote(txt)))


    def test_generate_cmdline(self):
        """Test the creation of cmd_line args to match options"""
        ign = r'(^(base|debug)$)|(^ext)'
        topt = TestOption1(go_args=['--level_level', '--longbase', shell_unquote('--store="some whitespace"')])
        self.assertEqual(topt.options ,
                         {'level_level': True, 'ext_date': None, 'longbase': True, 'level_longlevel': True,
                          'base': False, 'ext_optional': None, 'ext_extend': None, 'debug': False,
                          'ext_extenddefault': ['zero'], 'store': 'some whitespace', 'ext_datetime': None})

        self.assertEqual(topt.generate_cmd_line(ignore=ign), ['--level_level', '--store="some whitespace"'])
        all_args = topt.generate_cmd_line(add_default=True, ignore=ign)
        self.assertEqual([shell_unquote(x) for x in all_args],
                         ['--level_level', '--level_longlevel', '--longbase', '--store=some whitespace'])

        topt = TestOption1(go_args=[shell_unquote(x) for x in all_args], go_nosystemexit=True)
        self.assertEqual(topt.generate_cmd_line(add_default=True, ignore=ign),
                         ['--level_level', '--level_longlevel', '--longbase', '--store="some whitespace"'])
        self.assertEqual(all_args, topt.generate_cmd_line(add_default=True, ignore=ign))


    def test_enable_disable(self):
        """Test the enable/disable prefix
            longbase is a store_true with default True; with --disable one can set it to False
            level_level : --enable- keeps the defined action
        """
        ign = r'(^(base|debug)$)|(^ext)'
        topt = TestOption1(go_args=['--enable-level_level', '--disable-longbase'])
        self.assertEqual(topt.options.longbase, False)
        self.assertEqual(topt.options.level_level, True)

        self.assertEqual(topt.generate_cmd_line(ignore=ign), ['--level_level', '--disable-longbase'])

    def test_ext_date_datetime(self):
        """Test date and datetime action"""
        topt = TestOption1(go_args=['--ext_date=1970-01-01'])
        self.assertEqual(topt.options.ext_date , datetime.date(1970, 1, 1))

        topt = TestOption1(go_args=['--ext_date=TODAY'])
        self.assertEqual(topt.options.ext_date , datetime.date.today())

        topt = TestOption1(go_args=['--ext_datetime=1970-01-01 01:01:01.000001'])
        self.assertEqual(topt.options.ext_datetime , datetime.datetime(1970, 1, 1, 1, 1, 1, 1))

    def test_ext_extend(self):
        """Test extend action"""
        # extend to None default
        topt = TestOption1(go_args=['--ext_extend=one,two,three'])
        self.assertEqual(topt.options.ext_extend, ['one', 'two', 'three'])

        # default ['zero'], will be extended
        topt = TestOption1(go_args=['--ext_extenddefault=one,two,three'])
        self.assertEqual(topt.options.ext_extenddefault, ['zero', 'one', 'two', 'three'])

    def test_store_or_None(self):
        """Test store_or_None action"""
        ign = r'^(?!ext_optional)'
        topt = TestOption1(go_args=[], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, None)
        self.assertEqual(topt.generate_cmd_line(add_default=True, ignore=ign) , [])

        topt = TestOption1(go_args=['--ext_optional'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'DEFAULT')
        self.assertEqual(topt.generate_cmd_line(add_default=True, ignore=ign) , ['--ext_optional'])

        topt = TestOption1(go_args=['-o'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'DEFAULT')

        topt = TestOption1(go_args=['--ext_optional', 'REALVALUE'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'REALVALUE')

        topt = TestOption1(go_args=['--ext_optional=REALVALUE'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'REALVALUE')

        topt = TestOption1(go_args=['-o', 'REALVALUE'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'REALVALUE')


def suite():
    """ returns all the testcases in this module """
    return TestLoader().loadTestsFromTestCase(GeneralOptionTest)

if __name__ == '__main__':
    """Use this __main__ block to help write and test unittests
        just uncomment the parts you need
    """
#    # help
#    topt = TestOption1(go_args=['-h'], go_nosystemexit=True, go_columns=100,
#                       help_to_string=True,
#                       prog='optiontest1',
#                       )
#    print topt.parser.help_to_file.getvalue()
#
#    topt = TestOption1(go_args=['-H'], go_nosystemexit=True, go_columns=100,
#                       help_to_string=True,
#                       prog='optiontest1',
#                       )
#    print topt.parser.help_to_file.getvalue()

#    ## test shell_quote/shell_unquote
#    value = 'value with whitespace'
#    txt = '--option=%s' % value
#    print txt # this looks strange, but is correct
#    print txt == shell_unquote(shell_quote(txt))

#    ## cmd_line /enable/disable
#    ign = r'(^(base|debug)$)|(^ext)'
#    topt = TestOption1(go_args=['--level_level', '--longbase', shell_unquote('--store="some whitespace"')])
#    print topt.options
#    print topt.generate_cmd_line(ignore=ign)
#    all_args = topt.generate_cmd_line(add_default=True, ignore=ign)
#    print all_args
#    print [shell_unquote(x) for x in all_args]
#
#    topt = TestOption1(go_args=[shell_unquote(x) for x in all_args], go_nosystemexit=True)
#    print topt.generate_cmd_line(add_default=True, ignore=ign)
#    print all_args == topt.generate_cmd_line(add_default=True, ignore=ign)

#    topt = TestOption1(go_args=['--enable-level_level', '--disable-longbase'])
#    print topt.options
#    print topt.generate_cmd_line(ignore=ign)


#    ## test ExtOptions
#    topt = TestOption1(go_args=['--ext_date=1970-01-01'])
#    print topt.options.ext_date
#    print topt.options.ext_date == datetime.date(1970, 1, 1)
#
#    topt = TestOption1(go_args=['--ext_datetime=1970-01-01 01:01:01.000001'])
#    print topt.options.ext_datetime
#    print topt.options.ext_datetime == datetime.datetime(1970, 1, 1, 1, 1, 1, 1)
#
#    ## extend to None default
#    topt = TestOption1(go_args=['--ext_extend=one,two,three'])
#    print topt.options.ext_extend.__repr__()
#
#    # default ['zero'], will be extended
#    topt = TestOption1(go_args=['--ext_extenddefault=one,two,three'])
#    print topt.options.ext_extenddefault.__repr__()

#    ## store_or_None
#    ign = r'^(?!ext_optional)'
#    topt = TestOption1(go_args=[], go_nosystemexit=True,)
#    print topt.options.ext_optional == None
#    print topt.generate_cmd_line(add_default=True, ignore=ign) == []
#
#    topt = TestOption1(go_args=[ '--ext_optional'], go_nosystemexit=True,)
#    print topt.options.ext_optional == 'DEFAULT'
#    print topt.generate_cmd_line(add_default=True, ignore=ign) == ['--ext_optional']
#    print topt.generate_cmd_line(add_default=True, ignore=ign)
#    print topt.generate_cmd_line(ignore=ign)
#
#    topt = TestOption1(go_args=['-o'], go_nosystemexit=True,)
#    print topt.options.ext_optional == 'DEFAULT'
#
#    topt = TestOption1(go_args=['--ext_optional', 'REALVALUE'], go_nosystemexit=True,)
#    print topt.options.ext_optional == 'REALVALUE'
#    print topt.generate_cmd_line(add_default=True, ignore=ign) == ['--ext_optional=REALVALUE']
#
#    topt = TestOption1(go_args=['--ext_optional=REALVALUE'], go_nosystemexit=True,)
#    print topt.options.ext_optional == 'REALVALUE'
#
#    topt = TestOption1(go_args=['-o', 'REALVALUE'], go_nosystemexit=True,)
#    print topt.options.ext_optional == 'REALVALUE'
