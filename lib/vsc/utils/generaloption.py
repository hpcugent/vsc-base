##
#
# Copyright 2011-2012 Ghent University
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
A class that can be used to generated options to python scripts in a general way.
"""

import copy
import operator
import os
import re
import StringIO
import sys
from optparse import OptionParser, OptionGroup, Option, NO_DEFAULT
from optparse import SUPPRESS_HELP as nohelp  # supported in optparse of python v2.4
from optparse import _ as _gettext  # this is gettext normally
from vsc.utils.dateandtime import date_parser, datetime_parser
from vsc.fancylogger import getLogger, setLogLevelDebug

import shlex
import subprocess


def shell_quote(x):
    """Add quotes so it can be apssed to shell"""
    # TODO move to vsc/utils/missing
    # use undocumented subprocess API call to quote whitespace (executed with Popen(shell=True))
    # (see http://stackoverflow.com/questions/4748344/whats-the-reverse-of-shlex-split for alternatives if needed)
    return subprocess.list2cmdline([str(x)])


def shell_unquote(x):
    """Take a literal string, remove the quotes as if it were passed by shell"""
    # TODO move to vsc/utils/missing
    # it expects a string
    return shlex.split(str(x))[0]


def set_columns(cols=None):
    """Set os.environ COLUMNS variable
        - only if it is not set already
    """
    if 'COLUMNS' in os.environ:
        # do nothing
        return

    if cols is None:
        stty = '/usr/bin/stty'
        if os.path.exists(stty):
            try:
                cols = int(os.popen('%s size 2>/dev/null' % stty).read().strip().split(' ')[1])
            except:
                # do nothing
                pass

    if cols is not None:
        os.environ['COLUMNS'] = "%s" % cols


class ExtOption(Option):
    """Extended options class
        enable/disable support
        actions
            shorthelp : hook for shortend help messages
            store_debuglog : turns on fancylogger debugloglevel
            extend : extend default list (or create new one if is None)
            date : convert into datetime.date
            datetime : convert into datetime.datetime
            store_or_None : set default to None if no option passed,
                            set to default if option without value passed,
                            set to value if option with value passed
    """
    ENABLE = 'enable' # do nothing
    DISABLE = 'disable' # inverse action

    EXTOPTION_EXTRA_OPTIONS = ("extend", "date", "datetime",)
    EXTOPTION_STORE_OR = ('store_or_None',) # callback type

    # shorthelp has no extra arguments
    ACTIONS = Option.ACTIONS + EXTOPTION_EXTRA_OPTIONS + EXTOPTION_STORE_OR + ('shorthelp', 'store_debuglog',)
    STORE_ACTIONS = Option.STORE_ACTIONS + EXTOPTION_EXTRA_OPTIONS + ('store_debuglog', 'store_or_None',)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + EXTOPTION_EXTRA_OPTIONS + EXTOPTION_STORE_OR
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + EXTOPTION_EXTRA_OPTIONS

    def _set_attrs(self, attrs):
        """overwrite _set_attrs to allow store_or callbacks"""
        Option._set_attrs(self, attrs)
        if self.action in self.EXTOPTION_STORE_OR:
            setattr(self, 'store_or', self.action)

            def store_or(option, opt_str, value, parser, *args, **kwargs):
                """Callback for supporting options with optional values."""
                # see http://stackoverflow.com/questions/1229146/parsing-empty-options-in-python
                # ugly code, optparse is crap
                if parser.rargs and not parser.rargs[0].startswith('-'):
                    val = parser.rargs[0]
                    parser.rargs.pop(0)
                else:
                    val = kwargs.get('orig_default', None)

                setattr(parser.values, option.dest, val)

            # without the following, --x=y doesn't work; only --x y
            self.nargs = 0 # allow 0 args, will also use 0 args
            if self.type is None:
                # set to not None, for takes_value to return True
                self.type = 'string'

            self.callback = store_or
            self.callback_kwargs = {'orig_default': copy.deepcopy(self.default),
                                    }
            self.action = 'callback' # act as callback
            if self.store_or == 'store_or_None':
                self.default = None
            else:
                raise ValueError("_set_attrs: unknown store_or %s" % self.store_or)

    def take_action(self, action, dest, opt, value, values, parser):
        """extended take_action"""
        orig_action = action # keep copy

        if action == 'shorthelp':
            parser.print_shorthelp()
            parser.exit()
        elif action in ('store_true', 'store_false', 'store_debuglog'):
            if action == 'store_debuglog':
                action = 'store_true'

            if opt.startswith("--%s-" % self.ENABLE):
                # keep action
                pass
            elif opt.startswith("--%s-" % self.DISABLE):
                # reverse action
                if action in ('store_true', 'store_debuglog'):
                    action = 'store_false'
                elif action in ('store_false',):
                    action = 'store_true'

            if orig_action == 'store_debuglog' and action == 'store_true':
                setLogLevelDebug()

            Option.take_action(self, action, dest, opt, value, values, parser)
        elif action in self.EXTOPTION_EXTRA_OPTIONS:
            if action == "extend":
                # comma separated list convert in list
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
        limits the -h / --shorthelp to short opts only, -H / --help for all options
        pass options through environment
            eg export PROGNAME_SOMEOPTION = value will generate --someoption=value
                      PROGNAME_OTHEROPTION = 1 will generate --otheroption
                      PROGNAME_OTHEROPTION = 0 (or no or false) won't do anything
            distinction is made based on option.action in TYPED_ACTIONS
        allow --enable- / --disable- (using eg ExtOption option_class)
    """
    shorthelp = ('h', "--shorthelp",)
    longhelp = ('H', "--help",)

    def __init__(self, *args, **kwargs):
        self.help_to_string = kwargs.pop('help_to_string', None)
        self.help_to_file = kwargs.pop('help_to_file', None)
        OptionParser.__init__(self, *args, **kwargs)

        if self.epilog is None:
            self.epilog = []

        if hasattr(self.option_class, 'ENABLE') and hasattr(self.option_class, 'DISABLE'):
            epilogtxt = 'Boolean options support %(disable)s prefix to do the inverse of the action,'
            epilogtxt += ' e.g. option --someopt also supports --disable-someopt.'
            self.epilog.append(epilogtxt % {'disable': self.option_class.DISABLE})

    def format_epilog(self, formatter):
        """Allow multiple epilog parts"""
        res = []
        if not isinstance(self.epilog, (list, tuple,)):
            self.epilog = [self.epilog]
        for epi in self.epilog:
            res.append(formatter.format_epilog(epi))
        return "".join(res)

    def print_shorthelp(self, fh=None):
        """print a shortened help (no longopts)"""
        for opt in self._get_all_options():
            if opt._short_opts is None or len([x for x in opt._short_opts if len(x) > 0]) == 0:
                opt.help = nohelp
            opt._long_opts = []  # remove all long_opts

        removeoptgrp = []
        for optgrp in self.option_groups:
            # remove all option groups that have only nohelp options
            if reduce(operator.and_, [opt.help == nohelp for opt in optgrp.option_list]):
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
        """Add shorthelp and longhelp"""
        self.add_option("-%s" % self.shorthelp[0],
                        self.shorthelp[1], # *self.shorthelp[1:], syntax error in Python 2.4
                        action="shorthelp",
                        help=_gettext("show short help message and exit"))
        self.add_option("-%s" % self.longhelp[0],
                        self.longhelp[1], # *self.longhelp[1:], syntax error in Python 2.4
                        action="help",
                        help=_gettext("show full help message and exit"))

    def _get_args(self, args):
        """prepend the options set through the environment"""
        regular_args = OptionParser._get_args(self, args)
        env_args = self.get_env_options()
        return env_args + regular_args # prepend the environment options as longopts

    def get_env_options_prefix(self):
        """Return the prefix to use for options passed through the environment"""
        # sys.argv[0] or the prog= argument of the optionparser, strip possible extension
        prefix = self.get_prog_name().rsplit('.', 1)[0].upper()
        return prefix

    def get_env_options(self):
        """Retrieve options from the environment: prefix _ longopt.upper()"""
        env_long_opts = []
        prefix = self.get_env_options_prefix()

        epilogprefixtxt = "All long option names can be passed as environment variables. "
        epilogprefixtxt += "Variable name is %(prefix)s_<LONGNAME> "
        epilogprefixtxt += "eg. --someopt is same as setting %(prefix)s_SOMEOPT in the environment."
        self.epilog.append(epilogprefixtxt % {'prefix':prefix})

        for opt in self._get_all_options():
            if opt._long_opts is None: continue
            for lo in opt._long_opts:
                if len(lo) == 0: continue
                env_opt_name = "%s_%s" % (prefix, lo.lstrip('-').upper())
                val = os.environ.get(env_opt_name, None)
                if not val is None:
                    if opt.action in opt.TYPED_ACTIONS: # not all typed actions are mandatory, but let's assume so
                        env_long_opts.append("%s=%s" % (lo, val))
                    else:
                        # interpretation of values: 0/no/false means: don't set it
                        if not ("%s" % val).lower() in ("0", "no", "false",):
                            env_long_opts.append("%s" % lo)

        return env_long_opts


class GeneralOption(object):
    """'Used-to-be simple' wrapper class for option parsing
        go_ options are for this class, the remainder is passed to the parser
            go_args : use these instead of of sys.argv[1:]
            go_columns : specify column width (in columns)

        - TODO read from config file:
            http://stackoverflow.com/questions/1880404/using-a-file-to-store-optparse-arguments
    """
    OPTIONNAME_SEPARATOR = '_'

    DEBUG_OPTIONS_BUILD = False  # enable debug mode when building the options ?

    USAGE = None
    ALLOPTSMANDATORY = True
    PARSER = ExtOptionParser
    INTERSPERSED = True  # mix args with options

    def __init__(self, **kwargs):
        go_args = kwargs.pop('go_args', None)
        self.no_system_exit = kwargs.pop('go_nosystemexit', None)  # unit test option

        set_columns(kwargs.pop('go_columns', None))

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
        opts = {'debug':("Enable debug log mode", None, "store_debuglog", False, 'd')
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
        keys.sort() # alphabetical
        for key in keys:
            details = opt_dict[key]

            hlp = details[0]
            typ = details[1]
            action = details[2]
            default = details[3]
            # easy override default with otherdefault
            if key in otherdefaults:
                default = otherdefaults.get(key)

            extra_help = []
            if action in ("extend",):
                extra_help.append("type comma-separated list")
            elif typ is not None:
                extra_help.append("type %s" % typ)

            if default is not None:
                if len("%s" % default) == 0:
                    extra_help.append("def ''")  # empty string
                else:
                    extra_help.append("def %s" % default)

            if len(extra_help) > 0:
                hlp += " (%s)" % ("; ".join(extra_help))

            ## can be ''
            if prefix is None or len(prefix) == 0:
                dest = key
            else:
                dest = "".join([prefix, self.OPTIONNAME_SEPARATOR, key])

            self.processed_options[dest] = [typ, default, action]  # add longopt

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

    def default_parseoptions(self):
        """Return default options"""
        return sys.argv[1:]

    def parseoptions(self, options_list=None):
        """parse the options"""
        if options_list is None:
            options_list = self.default_parseoptions()

        try:
            (self.options, self.args) = self.parser.parse_args(options_list)
        except SystemExit, err:
            if self.no_system_exit:
                self.log.debug("parseoptions: no_system_exit set after parse_args err %s code %s" %
                               (err.message, err.code))
                return
            else:
                sys.exit(err.code)

        # args should be empty, since everything is optional
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
            for lvl in levels[:-1]:  # 0 or more
                lastlvl.setdefault(lvl, {})
                lastlvl = lastlvl[lvl]
            lastlvl[levels[-1]] = self.options.__dict__[k]
        self.log.debug("Returned subdict %s" % subdict)
        return subdict

    def generate_cmd_line(self, ignore=None, add_default=None):
        """Create the commandline options that would create the current self.options
            opt_name is destination
            - ignore : regex on destination
            - add_default : print value that are equal to default
        """
        if ignore is not None:
            self.log.debug("generate_cmd_line ignore %s" % ignore)
            ignore = re.compile(ignore)
        else:
            self.log.debug("generate_cmd_line no ignore")

        args = []
        opt_names = self.options.__dict__.keys()
        opt_names.sort()

        for opt_name in opt_names:
            opt_value = self.options.__dict__[opt_name]
            if ignore is not None and ignore.search(opt_name):
                self.log.debug("generate_cmd_line adding %s value %s matches ignore. Not adding to args." %
                               (opt_name, opt_value))
                continue

            # this is the action as parsed by the class, not the actual action set in option
            # (eg action store_or_None is shown here as store_or_None, not as callback)
            default, action = self.processed_options[opt_name][1:] # skip 0th element type

            if opt_value == default:
                # do nothing
                # except for store_or_None and friends
                msg = ''
                if not (add_default or action in ('store_or_None',)):
                    msg = ' Not adding to args.'
                self.log.debug("generate_cmd_line adding %s value %s default found.%s" %
                               (opt_name, opt_value, msg))
                if not (add_default or action in ('store_or_None',)):
                    continue

            if opt_value is None:
                # do nothing
                self.log.debug("generate_cmd_line adding %s value %s. None found. not adding to args." %
                               (opt_name, opt_value))
                continue

            if action in ('store_or_None',):
                if opt_value == default:
                    self.log.debug("generate_cmd_line %s adding %s (value is default value %s)" %
                                   (action, opt_name, opt_value))
                    args.append("--%s" % (opt_name))
                else:
                    self.log.debug("generate_cmd_line %s adding %s non-default value %s" %
                                   (action, opt_name, opt_value))
                    args.append("--%s=%s" % (opt_name, shell_quote(opt_value)))
            elif action in ("store_true", "store_false", 'store_debuglog'):
                # not default!
                self.log.debug("generate_cmd_line adding %s value %s. store action found" %
                               (opt_name, opt_value))
                if (action in ('store_true', 'store_debuglog',)  and default == True and opt_value == False) or \
                    (action in ('store_false',) and default == False and opt_value == True):
                    if hasattr(self.parser.option_class, 'ENABLE') and hasattr(self.parser.option_class, 'DISABLE'):
                        args.append("--%s-%s" % (self.parser.option_class.DISABLE, opt_name))
                    else:
                        self.log.error(("generate_cmd_line: %s : can't set inverse of default %s with action %s "
                                        "with missing ENABLE/DISABLE in option_class") %
                                       (opt_name, default, action))
                else:
                    if opt_value == default and ((action in ('store_true', 'store_debuglog',) and default == False) \
                                                 or (action in ('store_false',) and default == True)):
                        if hasattr(self.parser.option_class, 'ENABLE') and \
                            hasattr(self.parser.option_class, 'DISABLE'):
                            args.append("--%s-%s" % (self.parser.option_class.DISABLE, opt_name))
                        else:
                            self.log.debug(("generate_cmd_line: %s : action %s can only set to inverse of default %s "
                                            "and current value is default. Not adding to args.") %
                                           (opt_name, action, default))
                    else:
                        args.append("--%s" % opt_name)
            elif action in ("extend",):
                # comma separated
                self.log.debug("generate_cmd_line adding %s value %s. extend action, return as comma-separated list" %
                               (opt_name, opt_value))

                if default is not None:
                    # remove these. if default is set, extend extends the default!
                    for def_el in default:
                        opt_value.remove(def_el)

                if len(opt_value) == 0:
                    self.log.debug('generate_cmd_line skipping.')
                    continue

                args.append("--%s=%s" % (opt_name, shell_quote(",".join(opt_value))))
            elif action in ("append",):
                # add multiple times
                self.log.debug("generate_cmd_line adding %s value %s. append action, return as multiple args" %
                               (opt_name, opt_value))
                args.extend(["--%s=%s" % (opt_name, shell_quote(v)) for v in opt_value])
            else:
                self.log.debug("generate_cmd_line adding %s value %s" % (opt_name, opt_value))
                args.append("--%s=%s" % (opt_name, shell_quote(opt_value)))

        self.log.debug("commandline args %s" % args)
        return args

