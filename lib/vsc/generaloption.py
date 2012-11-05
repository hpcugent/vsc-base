##
# Copyright 2011-2012 Stijn De Weirdt
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

"""
@author Stijn De Weirdt HPCUgent / VSC

A class that can be used to generated options to python scripts in a general way.
"""

import os
import re
import StringIO
import sys
from optparse import OptionParser, OptionGroup, Option
from vsc.dateandtime import date_parser, datetime_parser
from vsc.fancylogger import getLogger, setLogLevelDebug

class ExtOption(Option):
    """Extended options class"""
    ENABLE = 'enable' # do nothing
    DISABLE = 'disable' # inverse action

    EXTOPTION_EXTRA_OPTIONS = ("extend", "date", "time",)

    ACTIONS = Option.ACTIONS + EXTOPTION_EXTRA_OPTIONS + ('shorthelp', 'store_debuglog') ## shorthelp has no extra arguments
    STORE_ACTIONS = Option.STORE_ACTIONS + EXTOPTION_EXTRA_OPTIONS + ('store_debuglog',)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + EXTOPTION_EXTRA_OPTIONS
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + EXTOPTION_EXTRA_OPTIONS

    def take_action(self, action, dest, opt, value, values, parser):
        if action == 'shorthelp':
            parser.print_shorthelp()
            parser.exit()
        elif action == 'store_debuglog':
            setLogLevelDebug()
            Option.take_action(self, 'store_true', dest, opt, value, values, parser)
        elif action in ('store_true', 'store_false'):
            if opt.startswith("--%s-" % self.ENABLE):
                ## keep action
                pass
            elif opt.startswith("--%s-" % self.DISABLE):
                ## reverse action
                if action == 'store_true':
                    action = 'store_false'
                elif action == 'store_false':
                    action = 'store_true'

            Option.take_action(self, action, dest, opt, value, values, parser)
        elif action in self.EXTOPTION_EXTRA_OPTIONS:
            if action == "extend":
                ## comma separated list convert in list
                lvalue = value.split(",")
                values.ensure_value(dest, []).extend(lvalue)
            elif action == "date":
                lvalue = date_parser(value)
                setattr(values, dest, lvalue)
            elif action == "datetime":
                lvalue = datetime_parser(value)
                setattr(values, dest, lvalue)
            else:
                raise(Exception("Unknown extended option action %s (known: %s)" %
                                (action, self.EXTOPTION_EXTRA_OPTIONS)))
        else:
            Option.take_action(self, action, dest, opt, value, values, parser)

class ExtOptionParser(OptionParser):
    """Make an option parser that
        limits the - h / - -shorthelp to short opts only, -H / - -help for all options
        pass options through environment
            eg export PROGNAME_SOMEOPTION = value will generate - -someoption = value
                      PROGNAME_OTHEROPTION = 1 will generate - -otheroption
                      PROGNAME_OTHEROPTION = 0 (or no or false) won't do anything
            distinction is made based on option.action in TYPED_ACTIONS
    """
    shorthelp = ('h', "--shorthelp",)
    longhelp = ('H', "--help",)

    def __init__(self, *args, **kwargs):
        self.help_to_string = kwargs.pop('help_to_string', None)
        self.help_to_file = kwargs.pop('help_to_file', None)
        OptionParser.__init__(self, *args, **kwargs)

    def print_shorthelp(self, fh=None):
        from optparse import SUPPRESS_HELP as nohelp ## supported in optparse of python v2.4

        for opt in self._get_all_options():
            if opt._short_opts is None or len([x for x in opt._short_opts if len(x) > 0]) == 0:
                opt.help = nohelp
            opt._long_opts = []            ## remove all long_opts

        removeoptgrp = []
        for optgrp in self.option_groups:
            ## remove all option groups that have only nohelp options
            remove = True
            for opt in optgrp.option_list:
                if not opt.help == nohelp:
                    remove = False
            if remove:
                removeoptgrp.append(optgrp)
        for optgrp in removeoptgrp:
            self.option_groups.remove(optgrp)

        self.print_help(fh)

    def print_help(self, fh=None):
        """Intercept print to file to print to string"""
        if self.help_to_string:
            self.help_to_file = StringIO.StringIO()
        if fh is None:
            fh = self.help_to_file


        if hasattr(self.option_class, 'ENABLE') and hasattr(self.option_class, 'DISABLE'):
            def _is_enable_disable(x):
                """Does the option start with ENABLE/DISABLE"""
                _e = x.startswith("--%s-" % self.option_class.ENABLE)
                _d = x.startswith("--%s-" % self.option_class.DISABLE)
                return _e or _d
            for opt in self._get_all_options():
                # remove all long_opts with ENABLE/DISABLE naming
                opt._long_opts = [x for x in opt._long_opts if not _is_enable_disable(x)]

        OptionParser.print_help(self, fh)

    def _add_help_option(self):
        from optparse import _ ## this is gettext normally
        self.add_option("-%s" % self.shorthelp[0],
                        self.shorthelp[1], ## *self.shorthelp[1:], syntax error in Python 2.4
                        action="shorthelp",
                        help=_("show short help message and exit"))
        self.add_option("-%s" % self.longhelp[0],
                        self.longhelp[1], ## *self.longhelp[1:], syntax error in Python 2.4
                        action="help",
                        help=_("show full help message and exit"))

    def _get_args(self, args):
        regular_args = OptionParser._get_args(self, args)
        env_args = self.get_env_options()
        return env_args + regular_args ## prepend the environment options as longopts

    def get_env_options_prefix(self):
        """Return the prefix to use for options passed through the environment"""
        prefix = self.get_prog_name().rsplit('.', 1)[0].upper() ## sys.argv[0] or the prog= argument of the optionparser, strip possible extension
        return prefix

    def get_env_options(self):
        """Retrieve options from the environment: prefix _ longopt.upper()"""
        env_long_opts = []
        prefix = self.get_env_options_prefix()

        epilogprefixtxt = "All long option names can be passed as environment variables. "
        epilogprefixtxt += "Variable name is %(prefix)s_<LONGNAME> "
        epilogprefixtxt += "eg. --debug is same as setting %(prefix)s_DEBUG in environment"
        if self.epilog is None:
            self.epilog = ''
        self.epilog += epilogprefixtxt % {'prefix':prefix}

        for opt in self._get_all_options():
            if opt._long_opts is None: continue
            for lo in opt._long_opts:
                if len(lo) == 0: continue
                env_opt_name = "%s_%s" % (prefix, lo.lstrip('-').upper())
                val = os.environ.get(env_opt_name, None)
                if not val is None:
                    if opt.action in opt.TYPED_ACTIONS: ## not all typed actions are mandatory, but let's assume so
                        env_long_opts.append("%s=%s" % (lo, val))
                    else:
                        ## interpretation of values: 0/no/false means: don't set it
                        if not ("%s" % val).lower() in ("0", "no", "false",):
                            env_long_opts.append("%s" % lo)

        return env_long_opts

class GeneralOption(object):
    """Simple wrapper class for option parsing"""
    OPTIONNAME_SEPARATOR = '_'

    DEBUG_OPTIONS_BUILD = False ## enable debug mode when building the options ?

    USAGE = None
    ALLOPTSMANDATORY = True
    PARSER = ExtOptionParser
    INTERSPERSED = True ## mix args with options

    def __init__(self, **kwargs):
        go_args = kwargs.pop('go_args', None)
        self.no_system_exit = kwargs.pop('go_nosystemexit', None) # unit test option

        kwargs.update({'option_class':ExtOption,
                       'usage':self.USAGE,
                       })
        self.parser = self.PARSER(**kwargs)
        self.parser.allow_interspersed_args = self.INTERSPERSED

        self.log = getLogger(self.__class__.__name__)
        self.options = None
        self.args = None
        self.processed_options = {}


        self.set_debug()

        self.make_debug_options()

        self.make_init()

        self.parseoptions(options_list=go_args)

        self.postprocess()


    def set_debug(self):
        """Check if debug options are on and then set fancylogger to debug"""
        if self.options is None:
            if self.DEBUG_OPTIONS_BUILD:
                setLogLevelDebug()

    def make_debug_options(self):
        """Add debug option"""
        opts = {'debug':("Enable debug log mode (default %default)", None, "store_debuglog", False, 'd')
                }
        descr = ['Debug options', '']
        self.log.debug("Add debug options descr %s opts %s (no prefix)" % (descr, opts))
        self.add_group_parser(opts, descr, prefix=None)

    def make_init(self):
        """Trigger all inits"""
        self.log.error("Not implemented")

    def add_group_parser(self, opt_dict, description, prefix=None, otherdefaults=None):
        """Make a group parser from a dict
            -key: long opt --prefix_key
            -value: tuple (help,type,action,default(,optional short option))
            --help will be extended with type and default
          Description is a 2 element list (short and long description)
        """
        if otherdefaults is None:
            otherdefaults = {}

        opt_grp = OptionGroup(self.parser, description[0], description[1])
        keys = opt_dict.keys()
        keys.sort() ## alphabetical
        for key in keys:
            details = opt_dict[key]

            hlp = details[0]
            typ = details[1]
            action = details[2]
            default = details[3]
            ## easy override default with otherdefault
            if key in otherdefaults:
                default = otherdefaults.get(key)

            extra_help = []
            if action in ("extend",):
                extra_help.append("type comma-separated list")
            elif typ is not None:
                extra_help.append("type %s" % typ)

            if default is not None:
                if len("%s" % default) == 0:
                    extra_help.append("def ''") ## empty string
                else:
                    extra_help.append("def %s" % default)

            if len(extra_help) > 0:
                hlp += " (%s)" % (";".join(extra_help))

            ## can be ''
            if prefix is None or len(prefix) == 0:
                dest = key
            else:
                dest = "".join([prefix, self.OPTIONNAME_SEPARATOR, key])

            self.processed_options[dest] = [typ, default, action] ## add longopt


            nameds = {'dest':dest, 'help':hlp, 'action':action, 'metavar':key.upper()}
            if default is not None:
                nameds['default'] = default

            if typ:
                nameds['type'] = typ

            args = ["--%s" % dest]
            try:
                shortopt = details[4]
                args.insert(0, "-%s" % shortopt)
            except IndexError:
                shortopt = None

            if hasattr(self.parser.option_class, 'ENABLE') and hasattr(self.parser.option_class, 'DISABLE'):
                args.append("--%s-%s" % (self.parser.option_class.ENABLE, dest))
                args.append("--%s-%s" % (self.parser.option_class.DISABLE, dest))
            opt_grp.add_option(*args, **nameds)
        self.parser.add_option_group(opt_grp)


    def parseoptions(self, options_list=None):
        """parse the options"""
        if options_list is None:
            options_list = sys.argv[1:]

        try:
            (self.options, self.args) = self.parser.parse_args(options_list)
        except SystemExit, err:
            if self.no_system_exit:
                self.log.debug("parseoptions: no_system_exit set after parse_args err %s code %s" %
                               (err.message, err.code))
                return
            else:
                sys.exit(err.code)

        #args should be empty, since everything is optional
        if len(self.args) > 1:
            self.log.debug("Found remaining args %s" % self.args)
            if self.ALLOPTSMANDATORY:
                self.parser.error("Invalid arguments args %s" % self.args)

        self.log.debug("Found options %s args %s" % (self.options, self.args))

    def postprocess(self):
        """Some additional processing"""
        pass

    def dict_by_prefix(self):
        """Break the options dict by prefix in sub-dict"""
        subdict = {}
        for k in self.options.__dict__.keys():
            levels = k.split(self.OPTIONNAME_SEPARATOR)
            lastlvl = subdict
            for lvl in levels[:-1]: ## 0 or more
                lastlvl.setdefault(lvl, {})
                lastlvl = lastlvl[lvl]
            lastlvl[levels[-1]] = self.options.__dict__[k]
        self.log.debug("Returned subdict %s" % subdict)
        return subdict

    def generate_cmd_line(self, ignore=None):
        """Create the commandline options that would create the current self.options
            - this assumes that optname is longopt!
        """
        if ignore:
            self.log.debug("generate_cmd_line ignore %s" % ignore)
            ignore = re.compile(ignore)
        else:
            self.log.debug("generate_cmd_line no ignore")

        args = []
        opt_names = self.options.__dict__.keys()
        opt_names.sort()

        for opt_name in opt_names:
            opt_value = self.options.__dict__[opt_name]
            if ignore and ignore.search(opt_name):
                self.log.debug("generate_cmd_line adding %s value %s matches ignore. not adding to args." %
                               (opt_name, opt_value))
                continue

            typ, default, action = self.processed_options[opt_name]
            if opt_value == default:
                ## do nothing
                self.log.debug("generate_cmd_line adding %s value %s default found. not adding to args." %
                               (opt_name, opt_value))
                continue
            elif opt_value is None:
                ## do nothing
                self.log.debug("generate_cmd_line adding %s value %s. None found. not adding to args." %
                               (opt_name, opt_value))
                continue

            if action in ("store_true", "store_false",):
                ## not default!
                self.log.debug("generate_cmd_line adding %s value %s. store action found" %
                               (opt_name, opt_value))
                args.append("--%s" % opt_name)
            elif action in ("extend",):
                ## comma separated
                self.log.debug("generate_cmd_line adding %s value %s. extend action, return as comma-separated list" %
                               (opt_name, opt_value))
                args.append("--%s=%s" % (opt_name, ",".join(opt_value)))
            elif action in ("append",):
                ## add multiple times
                self.log.debug("generate_cmd_line adding %s value %s. append action, return as multiple args" %
                               (opt_name, opt_value))
                for v in opt_value:
                    args.append("--%s='%s'" % (opt_name, v))
            else:
                self.log.debug("generate_cmd_line adding %s value %s" % (opt_name, opt_value))
                args.append("--%s='%s'" % (opt_name, opt_value))

        self.log.debug("commandline args %s" % args)
        return args

if __name__ == '__main__':
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

    topt = TestOption1(go_args=[], go_nosystemexit=True)
    print topt.options

    topt = TestOption1(go_args=['--level_level', '--longbase'])
    print topt.options
    topt = TestOption1(go_args=['--enable-level_level', '--disable-longbase'])
    print topt.options

