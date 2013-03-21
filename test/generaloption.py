#
# Copyright 2012-2013 Ghent University
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
Unit tests for generaloption

@author: Stijn De Weirdt (Ghent University)
"""
import datetime
import os
from tempfile import NamedTemporaryFile
from unittest import TestCase, TestLoader, main

from vsc import fancylogger
from vsc.utils.generaloption import GeneralOption
from vsc.utils.missing import shell_quote, shell_unquote

class TestOption1(GeneralOption):
    """Create simple test class"""
    DEFAULT_LOGLEVEL = 'INFO'
    def base_options(self):
        """Make base options"""
        self._opts_base = {"base":("Long and short base option", None, "store_true", False, 'b'),
                           "longbase":("Long-only base option", None, "store_true", True),
                           "store":("Store option", None, "store", None),
                           "store-with-dash":("Store option with dash in name", None, "store", None),
                           }
        descr = ["Base", "Base level of options"]

        prefix = None  # base, no prefixes
        self.add_group_parser(self._opts_base, descr, prefix=prefix)

    def level1_options(self):
        """Make the level1 related options"""
        self._opts_level1 = {"level":("Long and short option", None, "store_true", False, 'l'),
                             "longlevel"  :("Long-only level option", None, "store_true", True),
                             "prefix-and-dash":("Test combination of prefix and dash", None, "store", True),
                             }
        descr = ["Level1", "1 higher level of options"]

        prefix = 'level'
        self.add_group_parser(self._opts_level1, descr, prefix=prefix)

    def ext_options(self):
        """Make ExtOption options"""
        self._opts_ext = {"extend":("Test action extend", None, 'extend', None),
                          "extenddefault":("Test action extend with default set", None, 'extend', ['zero', 'one']),
                          "date":('Test action datetime.date', None, 'date', None),
                          "datetime":('Test action datetime.datetime', None, 'datetime', None),
                          "optional":('Test action optional', None, 'store_or_None', 'DEFAULT', 'o'),
                          # default value is not part of choice!
                          "optionalchoice":('Test action optional', 'choice', 'store_or_None', 'CHOICE0', ['CHOICE1', 'CHOICE2']),
                          # list type
                          "strlist":('Test strlist type', 'strlist', 'store', ['x']),
                          "strtuple":('Test strtuple type', 'strtuple', 'store', ('x',)),
                          }
        descr = ["ExtOption", "action from ExtOption"]

        prefix = 'ext'
        self.add_group_parser(self._opts_ext, descr, prefix=prefix)


class GeneralOptionTest(TestCase):
    """Tests for general option"""

    def test_basic(self):
        """Basic creation and verification of generaloption"""

    def test_help_short(self):
        """Generate short help message"""
        topt = TestOption1(go_args=['-h'],
                           go_nosystemexit=True,  # when printing help, optparse ends with sys.exit
                           go_columns=100,  # fix col size for reproducible unittest output
                           help_to_string=True,  # don't print to stdout, but to StingIO fh,
                           prog='optiontest1',  # generate as if called from generaloption.py
                           )
        self.assertEqual(topt.parser.help_to_file.getvalue().find("--level-longlevel"), -1,
                         "Long documentation not expanded in short help")

    def test_help_long(self):
        """Generate long help message"""
        topt = TestOption1(go_args=['-H'],
                           go_nosystemexit=True,
                           go_columns=100,
                           help_to_string=True,
                           prog='optiontest1',
                           )
        self.assertTrue(topt.parser.help_to_file.getvalue().find("--level-longlevel") > 0,
                        "Long documentation expanded in long help")

    def test_dest_with_dash(self):
        """Test the renaming of long opts to dest"""
        topt = TestOption1(go_args=['--store-with-dash', 'XX', '--level-prefix-and-dash=YY'])
        self.assertEqual(topt.options.store_with_dash, 'XX')
        self.assertEqual(topt.options.level_prefix_and_dash, 'YY')

    def test_quote(self):
        """Test quote/unquote"""
        value = 'value with whitespace'
        txt = '--option=%s' % value
        # this looks strange, but is correct
        self.assertEqual(str(txt), '--option=value with whitespace')
        self.assertEqual(txt , shell_unquote(shell_quote(txt)))

    def test_generate_cmdline(self):
        """Test the creation of cmd_line args to match options"""
        ign = r'(^(base|debug|info|quiet)$)|(^ext)'
        topt = TestOption1(go_args=['--level-level', '--longbase', '--level-prefix-and-dash=YY',
                                    shell_unquote('--store="some whitespace"')])
        self.assertEqual(topt.options.__dict__ ,
                         {
                          'store': 'some whitespace',
                          'debug': False,
                          'info':False,
                          'quiet':False,
                          'level_level': True,
                          'longbase': True,
                          'level_longlevel': True,
                          'store_with_dash':None,
                          'level_prefix_and_dash':'YY',  # this dict is about destinations
                          'ignoreconfigfiles': None,
                          'configfiles': None,
                          'base': False,
                          'ext_optional': None,
                          'ext_extend': None,
                          'ext_date': None,
                          'ext_extenddefault': ['zero', 'one'],
                          'ext_datetime': None,
                          'ext_optionalchoice': None,
                          'ext_strlist': ['x'],
                          'ext_strtuple': ('x',),
                          })

        # cmdline is ordered alphabetically
        self.assertEqual(topt.generate_cmd_line(ignore=ign),
                         ['--level-level', '--level-prefix-and-dash=YY', '--store="some whitespace"'])
        all_args = topt.generate_cmd_line(add_default=True, ignore=ign)
        self.assertEqual([shell_unquote(x) for x in all_args],
                         ['--level-level', '--level-longlevel',
                          '--level-prefix-and-dash=YY',
                          '--longbase', '--store=some whitespace'])

        topt = TestOption1(go_args=[shell_unquote(x) for x in all_args], go_nosystemexit=True)
        self.assertEqual(topt.generate_cmd_line(add_default=True, ignore=ign),
                         ['--level-level', '--level-longlevel',
                          '--level-prefix-and-dash=YY',
                          '--longbase', '--store="some whitespace"'])
        self.assertEqual(all_args, topt.generate_cmd_line(add_default=True, ignore=ign))

    def test_enable_disable(self):
        """Test the enable/disable prefix
            longbase is a store_true with default True; with --disable one can set it to False
            level_level : --enable- keeps the defined action
        """
        ign = r'(^(base|debug)$)|(^ext)'
        topt = TestOption1(go_args=['--enable-level-level', '--disable-longbase'])
        self.assertEqual(topt.options.longbase, False)
        self.assertEqual(topt.options.level_level, True)

        self.assertEqual(topt.generate_cmd_line(ignore=ign), ['--level-level', '--disable-longbase'])

    def test_ext_date_datetime(self):
        """Test date and datetime action"""
        topt = TestOption1(go_args=['--ext-date=1970-01-01'])
        self.assertEqual(topt.options.ext_date , datetime.date(1970, 1, 1))

        topt = TestOption1(go_args=['--ext-date=TODAY'])
        self.assertEqual(topt.options.ext_date , datetime.date.today())

        topt = TestOption1(go_args=['--ext-datetime=1970-01-01 01:01:01.000001'])
        self.assertEqual(topt.options.ext_datetime , datetime.datetime(1970, 1, 1, 1, 1, 1, 1))

    def test_ext_extend(self):
        """Test extend action"""
        # extend to None default
        topt = TestOption1(go_args=['--ext-extend=two,three'])
        self.assertEqual(topt.options.ext_extend, ['two', 'three'])

        # default ['zero'], will be extended
        topt = TestOption1(go_args=['--ext-extenddefault=two,three'])
        self.assertEqual(topt.options.ext_extenddefault, ['zero', 'one', 'two', 'three'])

    def test_str_list_tuple(self):
        """Test strlist / strtuple type"""
        # extend to None default
        topt = TestOption1(go_args=['--ext-strlist=two,three', '--ext-strtuple=two,three'])
        self.assertEqual(topt.options.ext_strlist, ['two', 'three'])
        self.assertEqual(topt.options.ext_strtuple, ('two', 'three',))

    def test_store_or_None(self):
        """Test store_or_None action"""
        ign = r'^(?!ext_optional)'
        topt = TestOption1(go_args=[], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, None)
        self.assertEqual(topt.generate_cmd_line(add_default=True, ignore=ign) , [])

        topt = TestOption1(go_args=['--ext-optional'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'DEFAULT')
        self.assertEqual(topt.generate_cmd_line(add_default=True, ignore=ign) , ['--ext-optional'])

        topt = TestOption1(go_args=['-o'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'DEFAULT')

        topt = TestOption1(go_args=['--ext-optional', 'REALVALUE'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'REALVALUE')

        topt = TestOption1(go_args=['--ext-optional=REALVALUE'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'REALVALUE')

        topt = TestOption1(go_args=['-o', 'REALVALUE'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'REALVALUE')

        topt = TestOption1(go_args=['--ext-optionalchoice'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optionalchoice, 'CHOICE0')

        topt = TestOption1(go_args=['--ext-optionalchoice', 'CHOICE1'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optionalchoice, 'CHOICE1')

    def test_configfiles(self):
        """Test configfiles (base section for empty prefix from auto_section_name)"""
        CONFIGFILE1 = """
[base]
store=ok
longbase=1
store-with-dash=XX

[level]
prefix-and-dash=YY

[ext]
extend=one,two,three
strtuple=a,b
strlist=x,y
"""
        tmp1 = NamedTemporaryFile()
        tmp1.write(CONFIGFILE1)
        tmp1.flush()  # flush, otherwise empty

        topt = TestOption1(go_configfiles=[tmp1.name], go_args=[])

        self.assertEqual(topt.options.store, 'ok')
        self.assertEqual(topt.options.longbase, True)
        self.assertEqual(topt.options.store_with_dash, 'XX')
        self.assertEqual(topt.options.level_prefix_and_dash, 'YY')
        self.assertEqual(topt.options.ext_extend, ['one', 'two', 'three'])
        self.assertEqual(topt.options.ext_strtuple, ('a', 'b'))
        self.assertEqual(topt.options.ext_strlist, ['x', 'y'])

        topt2 = TestOption1(go_configfiles=[tmp1.name], go_args=['--store=notok'])
        self.assertEqual(topt2.options.store, 'notok')

        # remove files
        tmp1.close()

    def test_get_options_by_property(self):
        """Test get_options_by_property and firends like get_options_by_prefix"""
        topt = TestOption1(go_args=['--ext-optional=REALVALUE'], go_nosystemexit=True,)

        self.assertTrue(len(topt._opts_ext) > 0)
        self.assertEqual(len(topt.get_options_by_prefix('ext')), len(topt._opts_ext))
        self.assertEqual(topt.get_options_by_prefix('ext')['optional'], 'REALVALUE')

    def test_loglevel(self):
        """Test the loglevel default setting"""
        topt = TestOption1(go_args=['--ext-optional=REALVALUE'], go_nosystemexit=True,)
        self.assertEqual(topt.log.getEffectiveLevel(), fancylogger.getLevelInt(topt.DEFAULT_LOGLEVEL.upper()))

def suite():
    """ returns all the testcases in this module """
    return TestLoader().loadTestsFromTestCase(GeneralOptionTest)

if __name__ == '__main__':
    """Use this __main__ block to help write and test unittests
        just uncomment the parts you need
    """
    main()

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

#    CONFIGFILE1 = """
# [MAIN]
# store=ok
# longbase=1
#
# [ext]
# extend=one,two,three
#    """
#    tmp1 = NamedTemporaryFile()
#    tmp1.write(CONFIGFILE1)
#    tmp1.flush()
#
#    topt = TestOption1(go_configfiles=[tmp1.name], go_args=['-d'])
#    print topt.options
#    print topt.options.store
#    print topt.options.ext_extend

#    topt2 = TestOption1(go_configfiles=[tmp1.name], go_args=['-d', '--store=notok'])
#    print topt2.options
#    print topt2.options.store
#
#    # remove files
#    tmp1.close()

