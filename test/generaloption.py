#
# Copyright 2012-2016 Ghent University
#
# This file is part of vsc-base,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
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
Unit tests for generaloption

@author: Stijn De Weirdt (Ghent University)
"""
import datetime
import logging
import os
import re
import sys
import tempfile
from tempfile import NamedTemporaryFile

from vsc.utils import fancylogger
from vsc.utils.generaloption import GeneralOption, HELP_OUTPUT_FORMATS
from vsc.utils.missing import shell_unquote
from vsc.utils.optcomplete import gen_cmdline
from vsc.utils.run import run_simple
from vsc.install.shared_setup import REPO_BASE_DIR
from vsc.install.testing import TestCase


_init_configfiles = ['/not/a/real/configfile']

class TestOption1(GeneralOption):
    """Create simple test class"""
    DEFAULT_LOGLEVEL = 'INFO'
    DEFAULT_CONFIGFILES = _init_configfiles[:]
    def base_options(self):
        """Make base options"""
        self._opts_base = {
            "base":("Long and short base option", None, "store_true", False, 'b'),
            "longbase":("Long-only base option", None, "store_true", True),
            "justatest":("Another long based option", None, "store_true", True),
            "store":("Store option", None, "store", None, 's'),
            "store-with-dash":("Store option with dash in name", None, "store", None),
            "aregexopt":("A regex option", None, "regex", None),
            }
        descr = ["Base", "Base level of options"]

        prefix = None  # base, no prefixes
        self.add_group_parser(self._opts_base, descr, prefix=prefix)

    def level1_options(self):
        """Make the level1 related options"""
        self._opts_level1 = {
            "level":("Long and short option", None, "store_true", False, 'l'),
            "longlevel"  :("Long-only level option", None, "store_true", True),
            "prefix-and-dash":("Test combination of prefix and dash", None, "store", True),
            }
        descr = ["Level1", "1 higher level of options"]

        prefix = 'level'
        self.add_group_parser(self._opts_level1, descr, prefix=prefix)

    def ext_options(self):
        """Make ExtOption options"""
        self._opts_ext = {
            "extend":("Test action extend", None, 'extend', None),
            "extenddefault":("Test action extend with default set", None, 'extend', ['zero', 'one']),
            # add / add_first
            "add":("Test action add", None, 'add', None),
            "add-default":("Test action add", None, 'add', 'now'),
            "add-list":("Test action add", 'strlist', 'add', None),
            "add-list-default":("Test action add", 'strlist', 'add', ['now']),
            "add-list-first":("Test action add", 'strlist', 'add_first', ['now']),
            "add-list-flex":('Test strlist type with add_flex', 'strlist', 'add_flex', ['x', 'y']),
            "add-pathlist-flex":('Test strlist type with add_flex', 'pathlist', 'add_flex', ['p2', 'p3']),

            # date
            "date":('Test action datetime.date', None, 'date', None),
            "datetime":('Test action datetime.datetime', None, 'datetime', None),
            "optional":('Test action optional', None, 'store_or_None', 'DEFAULT', 'o'),
            # default value is not part of choice!
            "optionalchoice":('Test action optional', 'choice', 'store_or_None', 'CHOICE0', ['CHOICE1', 'CHOICE2']),
            # list type
            "strlist":('Test strlist type', 'strlist', 'store', ['x']),
            "strtuple":('Test strtuple type', 'strtuple', 'store', ('x',)),
            "pathlist":('Test pathlist type', 'pathlist', 'store', ['x']),
            "pathtuple":('Test pathtuple type', 'pathtuple', 'store', ('x',)),

            "pathliststorenone":('Test pathlist type with store_or_None', 'pathlist', 'store_or_None', ['x']),
            "pathliststorenone2":('Test pathlist type with store_or_None (2nd attempt)', 'pathlist', 'store_or_None', ['x2']),

            }
        descr = ["ExtOption", "action from ExtOption"]

        prefix = 'ext'
        self.add_group_parser(self._opts_ext, descr, prefix=prefix)


class GeneralOptionTest(TestCase):
    """Tests for general option"""

    def test_help_short(self):
        """Generate short help message"""
        topt = TestOption1(go_args=['-h'],
                           go_nosystemexit=True,  # when printing help, optparse ends with sys.exit
                           go_columns=100,  # fix col size for reproducible unittest output
                           help_to_string=True,  # don't print to stdout, but to StingIO fh,
                           prog='optiontest1',  # generate as if called from generaloption.py
                           )
        helptxt = topt.parser.help_to_file.getvalue()
        self.assertEqual(helptxt.find("--level-longlevel"), -1, "Long documentation not expanded in short help")

    def test_help(self):
        """Generate (long) help message"""
        topt = TestOption1(go_args=['--help'],
                           go_nosystemexit=True,
                           go_columns=100,
                           help_to_string=True,
                           prog='optiontest1',
                           )
        helptxt = topt.parser.help_to_file.getvalue()

        # default format should be textual output
        self.assertTrue(helptxt.startswith('Usage'))

        self.assertTrue(helptxt.find("--level-longlevel") > -1, "Long documentation expanded in long help")

    def test_help_long(self):
        """Generate long help message"""
        topt = TestOption1(go_args=['-H'],
                           go_nosystemexit=True,
                           go_columns=100,
                           help_to_string=True,
                           prog='optiontest1',
                           )

        helptxt = topt.parser.help_to_file.getvalue()
        self.assertTrue(helptxt.find("--level-longlevel") > -1, "Long documentation expanded in long help")

    def test_help_outputformats(self):
        """Generate (long) rst help message"""
        for output_format in HELP_OUTPUT_FORMATS:
            topt = TestOption1(go_args=['--help=%s' % output_format],
                               go_nosystemexit=True,
                               go_columns=100,
                               help_to_string=True,
                               prog='optiontest1',
                              )
            helptxt = topt.parser.help_to_file.getvalue()
            if output_format == 'short':
                self.assertEqual(helptxt.find("--level-longlevel"), -1, "Long documentation not expanded in short help")
            elif output_format == 'config':
                self.assertTrue(helptxt.find("#level-longlevel") > -1, "Configuration option in config help")
            else:
                self.assertTrue(helptxt.find("--level-longlevel") > -1, "Long documentation expanded in long help (format: %s)" % output_format)

    def test_help_confighelp(self):
        """Generate long help message"""
        topt = TestOption1(go_args=['--confighelp'],
                           go_nosystemexit=True,
                           go_columns=100,
                           help_to_string=True,
                           prog='optiontest1',
                           )

        for section in ['MAIN', 'base', 'level', 'ext']:
            self.assertTrue(topt.parser.help_to_file.getvalue().find("[%s]" % section) > -1,
                            "Looking for [%s] section marker" % section)
        for opt in ['store-with-dash', 'level-prefix-and-dash', 'ext-strlist', 'level-level', 'debug']:
            self.assertTrue(topt.parser.help_to_file.getvalue().find("#%s" % opt) > -1,
                            "Looking for '#%s' option marker" % opt)

    def test_dest_with_dash(self):
        """Test the renaming of long opts to dest"""
        topt = TestOption1(go_args=['--store-with-dash', 'XX', '--level-prefix-and-dash=YY'])
        self.assertEqual(topt.options.store_with_dash, 'XX')
        self.assertEqual(topt.options.level_prefix_and_dash, 'YY')

    def test_generate_cmdline(self):
        """Test the creation of cmd_line args to match options"""
        self.maxDiff = None

        ign = r'(^(base|debug|info|quiet)$)|(^ext(?!_(?:strlist|pathlist|add_list_first)))'
        topt = TestOption1(go_args=['--level-level',
                                    '--longbase',
                                    '--level-prefix-and-dash=YY',
                                    shell_unquote('--store="some whitespace"'),
                                    '--ext-pathlist=x:y',
                                    '--ext-pathliststorenone',
                                    '--ext-pathliststorenone2=y2:z2',
                                    '--ext-strlist=x,y',
                                    '--ext-add-list-first=two,three',
                                    '--ext-add-list-flex=a,,b',
                                    '--ext-add-pathlist-flex=p1/foo::p4',
                                    '--debug',
                                    ])
        self.assertEqual(topt.options.__dict__,
                         {
                          'help': None,
                          'store': 'some whitespace',
                          'debug': True,
                          'info': False,
                          'quiet': False,
                          'level_level': True,
                          'longbase': True,
                          'justatest': True,
                          'level_longlevel': True,
                          'store_with_dash': None,
                          'level_prefix_and_dash':'YY',  # this dict is about destinations
                          'ignoreconfigfiles': None,
                          'configfiles': ['/not/a/real/configfile'],
                          'base': False,
                          'ext_optional': None,
                          'ext_extend': None,
                          'ext_extenddefault': ['zero', 'one'],
                          'ext_add': None,
                          'ext_add_default': 'now',
                          'ext_add_list': None,
                          'ext_add_list_default': ['now'],
                          'ext_add_list_first': ['two', 'three', 'now'],
                          'ext_add_list_flex': ['a','x', 'y', 'b'],
                          'ext_add_pathlist_flex': ['p1/foo','p2', 'p3', 'p4'],
                          'ext_date': None,
                          'ext_datetime': None,
                          'ext_optionalchoice': None,
                          'ext_strlist': ['x', 'y'],
                          'ext_strtuple': ('x',),
                          'ext_pathlist': ['x', 'y'],
                          'ext_pathliststorenone': ['x'],
                          'ext_pathliststorenone2': ['y2', 'z2'],
                          'ext_pathtuple': ('x',),
                          'aregexopt': None,
                          })

        # cmdline is ordered alphabetically
        self.assertEqual(topt.generate_cmd_line(ignore=ign),
                         [
                          "--ext-add-list-first='two,three'",
                          "--ext-pathlist='x:y'",
                          "--ext-pathliststorenone",
                          "--ext-pathliststorenone2='y2:z2'",
                          "--ext-strlist='x,y'",
                          "--level-level",
                          "--level-prefix-and-dash='YY'",
                          "--store='some whitespace'",
                          ])
        all_args = topt.generate_cmd_line(add_default=True, ignore=ign)
        self.assertEqual([shell_unquote(x) for x in all_args],
                         [
                          '--ext-add-list-first=two,three',
                          '--ext-pathlist=x:y',
                          '--ext-pathliststorenone',
                          '--ext-pathliststorenone2=y2:z2',
                          '--ext-strlist=x,y',
                          '--justatest',
                          '--level-level',
                          '--level-longlevel',
                          '--level-prefix-and-dash=YY',
                          '--longbase',
                          '--store=some whitespace',
                          ])

        topt = TestOption1(go_args=[shell_unquote(x) for x in all_args], go_nosystemexit=True)
        self.assertEqual(topt.generate_cmd_line(add_default=True, ignore=ign),
                         [
                          "--ext-add-list-first='two,three'",
                          "--ext-pathlist='x:y'",
                          "--ext-pathliststorenone",
                          "--ext-pathliststorenone2='y2:z2'",
                          "--ext-strlist='x,y'",
                          "--justatest",
                          "--level-level",
                          "--level-longlevel",
                          "--level-prefix-and-dash='YY'",
                          "--longbase",
                          "--store='some whitespace'",
                          ])
        self.assertEqual(all_args, topt.generate_cmd_line(add_default=True, ignore=ign))

        topt = TestOption1(go_args=["--aregexopt=%s" % '^foo.*bar$'])
        self.assertTrue("--aregexopt='^foo.*bar$'" in topt.generate_cmd_line())
        self.assertTrue(topt.options.aregexopt is not None)
        self.assertEqual(topt.options.aregexopt.pattern, "^foo.*bar$")

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

    def test_ext_add(self):
        """Test add and add_first action"""

        # add to None default
        topt = TestOption1(go_args=['--ext-add=two,three'])
        # use default type, no strlist implied or anything
        self.assertEqual(topt.options.ext_add, 'two,three')

        topt = TestOption1(go_args=['--ext-add-default=two,three'])
        # use default type, no strlist implied or anything
        self.assertEqual(topt.options.ext_add_default, 'nowtwo,three')

        # add to None default
        topt = TestOption1(go_args=['--ext-add-list=two,three'])
        self.assertEqual(topt.options.ext_add_list, ['two', 'three'])

        topt = TestOption1(go_args=['--ext-add-list-default=two,three'])
        self.assertEqual(topt.options.ext_add_list_default, ['now', 'two', 'three'])

        topt = TestOption1(go_args=['--ext-add-list-first=two,three'])
        self.assertEqual(topt.options.ext_add_list_first, ['two', 'three', 'now'])

        # now alias to add+strlist
        # extend to None default
        topt = TestOption1(go_args=['--ext-extend=two,three'])
        self.assertEqual(topt.options.ext_extend, ['two', 'three'])

        # default ['zero'], will be extended
        topt = TestOption1(go_args=['--ext-extenddefault=two,three'])
        self.assertEqual(topt.options.ext_extenddefault, ['zero', 'one', 'two', 'three'])

        # flex
        for args, val in [
                (',b', ['x', 'y', 'b']),
                ('b,', ['b', 'x', 'y']),
                ('a,b', ['a', 'b']),
                ('a,,b', ['a', 'x', 'y', 'b']),
        ]:
            cmd = '--ext-add-list-flex=%s' % args
            topt = TestOption1(go_args=[cmd])
            self.assertEqual(topt.options.ext_add_list_flex, val)
            self.assertEqual(topt.generate_cmd_line(ignore=r'(?<!_flex)$'), [cmd])

    def test_ext_add_multi(self):
        """Test behaviour when 'add' options are used multiple times."""
        fd, cfgfile = tempfile.mkstemp()
        os.close(fd)

        f = open(cfgfile, 'w')
        f.write('[ext]\nadd-default=two')
        f.close()
        args = ['--configfiles=%s' % cfgfile]
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_default, 'nowtwo')

        # environment overrides config file
        os.environ['TEST_EXT_ADD_DEFAULT'] = 'three'
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_default, 'nowthree')

        # command line overrides environment + config file, last value wins
        args.extend(['--ext-add-default=four', '--ext-add-default=five'])
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_default, 'nowfive')
        del os.environ['TEST_EXT_ADD_DEFAULT']

        f = open(cfgfile, 'w')
        f.write('[ext]\nadd-list-default=two,three')
        f.close()
        args = ['--configfiles=%s' % cfgfile]
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_list_default, ['now', 'two', 'three'])

        os.environ['TEST_EXT_ADD_LIST_DEFAULT'] = 'four,five'
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_list_default, ['now', 'four', 'five'])

        args.extend([
            '--ext-add-list-default=six',
            '--ext-add-list-default=seven,eight',
        ])
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_list_default, ['now', 'seven', 'eight'])
        del os.environ['TEST_EXT_ADD_LIST_DEFAULT']

        f = open(cfgfile, 'w')
        f.write('[ext]\nadd-list-flex=two,,three')
        f.close()
        args = ['--configfiles=%s' % cfgfile]
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_list_flex, ['two', 'x', 'y', 'three'])

        os.environ['TEST_EXT_ADD_LIST_FLEX'] = 'four,,five'
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_list_flex, ['four', 'x', 'y', 'five'])

        args.extend([
            '--ext-add-list-flex=six,',
            '--ext-add-list-flex=seven,,eight',
            '--ext-add-list-flex=,last',
        ])
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_list_flex, ['x', 'y', 'last'])
        del os.environ['TEST_EXT_ADD_LIST_FLEX']

        f = open(cfgfile, 'w')
        f.write('[ext]\nadd-pathlist-flex=two::three')
        f.close()
        args = ['--configfiles=%s' % cfgfile]
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_pathlist_flex, ['two', 'p2', 'p3', 'three'])

        os.environ['TEST_EXT_ADD_PATHLIST_FLEX'] = 'four::five'
        args = ['--configfiles=%s' % cfgfile]
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_pathlist_flex, ['four', 'p2', 'p3', 'five'])

        args.extend([
            '--ext-add-pathlist-flex=six:',
            '--ext-add-pathlist-flex=:last',
            '--ext-add-pathlist-flex=seven::eight',
        ])
        topt = TestOption1(go_args=args, envvar_prefix='TEST')
        self.assertEqual(topt.options.ext_add_pathlist_flex, ['seven', 'p2', 'p3', 'eight'])
        del os.environ['TEST_EXT_ADD_PATHLIST_FLEX']

    def test_str_list_tuple(self):
        """Test strlist / strtuple type"""
        # extend to None default
        topt = TestOption1(go_args=['--ext-strlist=two,three',
                                    '--ext-strtuple=two,three',
                                    '--ext-pathlist=two,three:four:five',
                                    '--ext-pathtuple=two,three:four:five',
                                    ])
        self.assertEqual(topt.options.ext_strlist, ['two', 'three'])
        self.assertEqual(topt.options.ext_strtuple, ('two', 'three',))
        self.assertEqual(topt.options.ext_pathlist, ['two,three', 'four', 'five'])
        self.assertEqual(topt.options.ext_pathtuple, ('two,three', 'four', 'five',))

    def test_store_or_None(self):
        """Test store_or_None action"""
        ign = r'^(?!ext_optional)'
        topt = TestOption1(go_args=[], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, None)
        self.assertEqual(topt.generate_cmd_line(add_default=True, ignore=ign), [])

        topt = TestOption1(go_args=['--ext-optional'], go_nosystemexit=True,)
        self.assertEqual(topt.options.ext_optional, 'DEFAULT')
        self.assertEqual(topt.generate_cmd_line(add_default=True, ignore=ign), ['--ext-optional'])

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

[remainder]
opt1=value1

"""
        tmp1 = NamedTemporaryFile()
        tmp1.write(CONFIGFILE1)
        tmp1.flush()  # flush, otherwise empty

        topt = TestOption1(go_configfiles=[tmp1.name], go_args=[])

        # nothing passed by commandline
        self.assertEqual(topt.options.configfiles, _init_configfiles);
        self.assertEqual(topt.configfiles, [tmp1.name] + _init_configfiles);

        self.assertEqual(topt.options.store, 'ok')
        self.assertEqual(topt.options.longbase, True)
        self.assertEqual(topt.options.justatest, True)
        self.assertEqual(topt.options.store_with_dash, 'XX')
        self.assertEqual(topt.options.level_prefix_and_dash, 'YY')
        self.assertEqual(topt.options.ext_extend, ['one', 'two', 'three'])
        self.assertEqual(topt.options.ext_strtuple, ('a', 'b'))
        self.assertEqual(topt.options.ext_strlist, ['x', 'y'])

        self.assertTrue('remainder' in topt.configfile_remainder)
        self.assertFalse('base' in topt.configfile_remainder)
        self.assertEqual(topt.configfile_remainder['remainder'], {'opt1': 'value1'})

        topt1b = TestOption1(go_configfiles=[tmp1.name], go_args=['--store=notok'])

        self.assertEqual(topt1b.options.store, 'notok')

        self.assertEqual(topt1b.options.configfiles, _init_configfiles);
        self.assertEqual(topt1b.configfiles, [tmp1.name] + _init_configfiles);


        CONFIGFILE2 = """
[base]
store=notok2
longbase=0
justatest=0
debug=1

"""
        tmp2 = NamedTemporaryFile()
        tmp2.write(CONFIGFILE2)
        tmp2.flush()  # flush, otherwise empty

        # multiple config files, last one wins
        # cmdline wins always
        topt2 = TestOption1(go_configfiles=[tmp1.name, tmp2.name], go_args=['--store=notok3'])

        self.assertEqual(topt2.options.configfiles, _init_configfiles);
        self.assertEqual(topt2.configfiles, [tmp1.name, tmp2.name] + _init_configfiles);

        self.assertEqual(topt2.options.store, 'notok3')
        self.assertEqual(topt2.options.justatest, False)
        self.assertEqual(topt2.options.longbase, False)
        self.assertEqual(topt2.options.debug, True)

        # add test for _action_taken
        for dest in ['ext_strlist', 'longbase', 'store']:
            self.assertTrue(topt2.options._action_taken.get(dest, None))

        for dest in ['level_longlevel']:
            self.assertFalse(dest in topt2.options._action_taken)

        # This works because we manipulate DEFAULT and use all uppercase name
        CONFIGFILE3 = """
[base]
store=%(FROMINIT)s
"""
        tmp3 = NamedTemporaryFile()
        tmp3.write(CONFIGFILE3)
        tmp3.flush()  # flush, otherwise empty

        initenv = {'DEFAULT': {'FROMINIT' : 'woohoo'}}
        topt3 = TestOption1(go_configfiles=[tmp3.name, tmp2.name], go_args=['--ignoreconfigfiles=%s' % tmp2.name],
                            go_configfiles_initenv=initenv)

        self.assertEqual(topt3.options.configfiles, _init_configfiles);
        self.assertEqual(topt3.configfiles, [tmp3.name, tmp2.name] + _init_configfiles);
        self.assertEqual(topt3.options.ignoreconfigfiles, [tmp2.name])

        self.assertEqual(topt3.options.store, 'woohoo')

        # remove files
        tmp1.close()
        tmp2.close()
        tmp3.close()

    def test_get_options_by_property(self):
        """Test get_options_by_property and firends like get_options_by_prefix"""
        topt = TestOption1(go_args=['--ext-optional=REALVALUE'], go_nosystemexit=True,)

        self.assertTrue(len(topt._opts_ext) > 0)
        self.assertEqual(len(topt.get_options_by_prefix('ext')), len(topt._opts_ext))
        self.assertEqual(topt.get_options_by_prefix('ext')['optional'], 'REALVALUE')

    def test_loglevel(self):
        """Test the loglevel default setting"""
        def _loglevel(lvl, msg):
            lvl_int = topt.log.getEffectiveLevel()
            lvl_name = [k for k,v in logging._levelNames.items() if v == lvl_int][0]
            self.assertEqual(lvl_int,
                             fancylogger.getLevelInt(lvl),
                             msg="%s (expected %s got %s)" % (msg, lvl, lvl_name))


        topt = TestOption1(go_args=['--ext-optional=REALVALUE'], go_nosystemexit=True,)
        _loglevel(topt.DEFAULT_LOGLEVEL.upper(), 'Test default loglevel')

        topt = TestOption1(go_args=['--debug'], go_nosystemexit=True,)
        _loglevel('DEBUG', '--debug gives DEBUG')

        topt = TestOption1(go_args=['--info'], go_nosystemexit=True,)
        _loglevel('INFO', '--info gives INFO')

        topt = TestOption1(go_args=['--quiet'], go_nosystemexit=True,)
        _loglevel('WARNING', '--quiet gives WARNING')

        # last one wins
        topt = TestOption1(go_args=['--debug', '--info', '--quiet'], go_nosystemexit=True,)
        _loglevel('WARNING', 'last wins: --debug --info --quiet gives WARNING')

        CONFIGFILE1 = """
[base]
debug=1
"""
        tmp1 = NamedTemporaryFile()
        tmp1.write(CONFIGFILE1)
        tmp1.flush()  # flush, otherwise empty
        envvar = 'logactionoptiontest'.upper()
        topt = TestOption1(go_configfiles=[tmp1.name],
                           go_args=[],
                           go_nosystemexit=True,
                           envvar_prefix=envvar
                           )
        _loglevel('DEBUG', 'DEBUG set via configfile')

        # set via environment; environment wins over cfg file
        os.environ['%s_INFO' % envvar] = '1';
        topt = TestOption1(go_configfiles=[tmp1.name],
                           go_args=[],
                           go_nosystemexit=True,
                           envvar_prefix=envvar
                           )
        _loglevel('INFO', 'env wins: debug in configfile and _INFO in env gives INFO')

        # commandline always wins
        topt = TestOption1(go_configfiles=[tmp1.name],
                           go_args=['--quiet'],
                           go_nosystemexit=True,
                           envvar_prefix=envvar
                           )
        _loglevel('WARNING', 'commandline wins: debug in configfile, _INFO in env and --quiet gives WARNING')

        # remove tmp1
        del os.environ['%s_INFO' % envvar]
        tmp1.close()

    def test_optcomplete(self):
        """Test optcomplete support"""

        reg_reply = re.compile(r'^COMPREPLY=\((.*)\)$')

        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'runtests', 'simple_option.py')

        partial = '-'
        cmd_list = [script, partial]

        pythonpath = 'PYTHONPATH=%s' % os.pathsep.join([p for p in sys.path if p.startswith(REPO_BASE_DIR)])
        ec, out = run_simple('%s %s; test $? == 1' % (pythonpath, gen_cmdline(cmd_list, partial, shebang=False)))
        # tabcompletion ends with exit 1!; test returns this to 0
        # avoids run.log.error message
        self.assertEqual(ec, 0)

        compl_opts = reg_reply.search(out).group(1).split()
        basic_opts = ['--debug', '--enable-debug', '--disable-debug', '-d',
                      '--help', '-h', '-H', '--shorthelp',
                      '--configfiles', '--info',
                      ]
        for opt in basic_opts:
            self.assertTrue(opt in compl_opts)

        # test --deb autocompletion
        partial = '--deb'
        cmd_list = [script, partial]

        ec, out = run_simple('%s %s; test $? == 1' % (pythonpath, gen_cmdline(cmd_list, partial, shebang=False)))
        # tabcompletion ends with exit 1!; test returns this to 0
        # avoids run.log.error message
        self.assertEqual(ec, 0)

        compl_opts = reg_reply.search(out).group(1).split()
        self.assertEqual(compl_opts, ['--debug'])

    def test_get_by_prefix(self):
        """Test dict by prefix"""
        topt = TestOption1(go_args=['--level-level',
                            '--longbase',
                            '--level-prefix-and-dash=YY',
                            ])
        #
        noprefixopts_dict = topt.get_options_by_prefix('')
        noprefix_opts = ['debug', 'info', 'longbase']
        for opt in noprefix_opts:
            self.assertTrue(opt in noprefixopts_dict)

        dbp = topt.dict_by_prefix()
        for prefix in ['', 'ext', 'level']:
            self.assertTrue(prefix in dbp)
        for noprefix_opt in noprefix_opts:
            self.assertFalse(noprefix_opt in dbp)

        dbp = topt.dict_by_prefix(merge_empty_prefix=True)
        for prefix in ['', 'ext', 'level']:
            self.assertTrue(prefix in dbp)
        for noprefix_opt in noprefix_opts:
            self.assertTrue(noprefix_opt in dbp)

    def test_multiple_init(self):
        """Test behaviour when creating multiple instances of same GO class"""
        inst1 = TestOption1(go_args=['--level-level'])
        inst2 = TestOption1(go_args=['--level-level'])

        expected = ['/not/a/real/configfile']
        # not really "initial instance", but let's assume this test runs first
        self.assertEqual(inst1.options.configfiles, expected)
        self.assertEqual(inst2.options.configfiles, expected)

        self.assertEqual(inst1.configfiles, expected)
        self.assertEqual(inst2.configfiles, expected)

    def test_error_env_options(self):
        """Test log error on unknown environment option"""
        self.reset_logcache()
        mylogger = fancylogger.getLogger('ExtOptionParser')
        mylogger.error = self.mock_logmethod(mylogger.error)
        mylogger.debug = self.mock_logmethod(mylogger.debug)

        self.assertEqual(self.count_logcache('error'), 0)

        os.environ['GENERALOPTIONTEST_XYZ'] = '1'
        topt1 = TestOption1(go_args=['--level-level'], envvar_prefix='GENERALOPTIONTEST')
        self.assertEqual(self.count_logcache('error'), 0,
                         msg='no errors logged, got %s' % self.count_logcache('error'))

        topt1 = TestOption1(go_args=['--level-level'], envvar_prefix='GENERALOPTIONTEST', error_env_options=True)
        print self.LOGCACHE['error']
        self.assertEqual(self.count_logcache('error'), 1,
                         msg='one error should be logged, got %s' % self.count_logcache('error'))

        # using a custom error method
        def raise_error(msg, *args):
            """Raise error with given message and string arguments to format it."""
            raise Exception(msg % args)

        self.assertErrorRegex(Exception, "Found 1 environment variable.* prefixed with GENERALOPTIONTEST", TestOption1,
                              go_args=['--level-level'], envvar_prefix='GENERALOPTIONTEST', error_env_options=True,
                              error_env_option_method=raise_error)

    def _match_testoption1_sysexit(self, args, msg):
        """Check whether parsing supplied arguments with TestOption1 results in SystemExit error being raised."""
        system_exit = False
        self.mock_stderr(True)  # reset
        # purposely not using self.assertErrorRegex, since we're mocking stderr...
        try:
            TestOption1(go_args=args)
        except SystemExit:
            system_exit = True
        finally:
            stderr = self.get_stderr()
            self.mock_stderr(False)
        self.assertTrue(system_exit)
        self.assertTrue(msg in stderr)

    def test_nosuchoption(self):
        """Test catching of non-existing options."""
        self._match_testoption1_sysexit(['--nosuchoptiondefinedfoobar'],
                                        "no such option: --nosuchoptiondefinedfoobar")

    def test_is_value_a_commandline_option(self):
        """Test ExtOptionParser is_value_a_commandline_option method"""
        topt = TestOption1(go_args=[])
        tp = topt.parser

        self.assertEqual(tp.ALLOW_OPTION_NAME_AS_VALUE, False,
                         msg="default do not allow option name as value")
        self.assertEqual(tp.ALLOW_OPTION_AS_VALUE, False,
                         msg="default do not allow option as value")
        self.assertEqual(tp.ALLOW_DASH_AS_VALUE, False,
                         msg="default do not allow value starting with -")
        self.assertEqual(tp.ALLOW_TYPO_AS_VALUE, True,
                         msg="default do allow value similar to option")

        # fake commandline args
        # this is purely to test the function, actual usage is in test_option_as_value
        tp.commandline_arguments = ['--base', '-something', 'base', '-base']
        def check(fail, tpl):
            """Check whether expected failures/success occur with given message template."""
            for idx, value in enumerate(tp.commandline_arguments):
                msg = tpl % value
                res = tp.is_value_a_commandline_option('--opt', value, index=idx)
                if idx in fail:
                    self.assertFalse(res is None, "failure should not return None for value %s" % value)
                    self.assertTrue(msg in res, msg='%s in %s' % (msg, res))
                else:
                    self.assertTrue(res is None)

        # anything goes
        tp.ALLOW_OPTION_NAME_AS_VALUE = True
        tp.ALLOW_OPTION_AS_VALUE = True
        tp.ALLOW_DASH_AS_VALUE = True
        tp.ALLOW_TYPO_AS_VALUE = True

        check([], 'x%sx') # all ok

        tp.ALLOW_OPTION_AS_VALUE = False
        check([0], "Value '%s' is also a valid option")
        tp.ALLOW_OPTION_AS_VALUE = True

        tp.ALLOW_DASH_AS_VALUE = False
        # options also start with a -
        check([0, 1, 3], "Value '%s' starts with a '-'")
        tp.ALLOW_DASH_AS_VALUE = True

        tp.ALLOW_TYPO_AS_VALUE = False
        # an option is a close match for an option, who'd guessed that...
        check([0, 2, 3], "Value '%s' too close match to option(s) ")
        tp.ALLOW_TYPO_AS_VALUE = True

        tp.ALLOW_OPTION_NAME_AS_VALUE = False
        check([3], "'-%s' is a valid option")
        tp.ALLOW_OPTION_NAME_AS_VALUE = True

    def test_option_as_value(self):
        """Test how valid options being used as values are handled."""
        # -s requires an argument
        self._match_testoption1_sysexit(['-b', '-s'],
                                        "-s option requires an argument")

        # only valid way of specifying '-b' as a value to --store
        topt = TestOption1(go_args=['--store=-b'])
        self.assertEqual(topt.options.store, '-b')
        self.assertFalse(topt.options.base)  # remain False (default value)

        # when -b/--base is an option, the following are not accepted, since they're likely not what intended
        self._match_testoption1_sysexit(['-sb'],
                                        "'-b' is a valid option")
        self._match_testoption1_sysexit(['-s', 'b'],
                                        "'-b' is a valid option")
        self._match_testoption1_sysexit(['--store', 'b'],
                                        "'-b' is a valid option")
        self._match_testoption1_sysexit(['--store', '-base'],
                                        "'--base' is a valid option")
        self._match_testoption1_sysexit(['-s', '-base'],
                                        "'--base' is a valid option")
        self._match_testoption1_sysexit(['-s-base'],
                                        "'--base' is a valid option")

        # -s -b is not a valid list of flags, since it's ambiguous: is '-b' a value for '-s', or an option?
        self._match_testoption1_sysexit(['-s', '-b'],
                                        "Value '-b' is also a valid option")

        # same for --store -b
        self._match_testoption1_sysexit(['--store', '-b'],
                                        "Value '-b' is also a valid option")

        # same for --store --base
        self._match_testoption1_sysexit(['--store', '--base'],
                                        "Value '--base' is also a valid option")

        # including a non-existing option will result in it being treated as a value, but is not allowed
        self._match_testoption1_sysexit(['--store', '-f'],
                                        "Value '-f' starts with a '-'")

        self._match_testoption1_sysexit(['--store', '--foo'],
                                        "Value '--foo' starts with a '-'")

        # non-existing options are still reported if they're not consumed as a value
        self._match_testoption1_sysexit(['--nosuchoptiondefinedfoobar', '--store', '--foo'],
                                        "no such option: --nosuchoptiondefinedfoobar")

        # but first error still wins
        self._match_testoption1_sysexit(['--store', '--foo', '--nosuchoptiondefinedfoobar'],
                                        "Value '--foo' starts with a '-'")

