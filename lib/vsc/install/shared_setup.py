#!/usr/bin/env python
# -*- coding: latin-1 -*-
# #
# Copyright 2009-2013 Ghent University
#
# This file is part of vsc-utils,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# All rights reserved.
#
# #
"""
Shared module for vsc-base setup

@author: Stijn De Weirdt (Ghent University)
@author: Andy Georges (Ghent University)
"""
import glob
import os
import shutil
import sys
import re
import unittest

from distutils import log  # also for setuptools
from distutils.command.bdist_rpm import bdist_rpm as orig_bdist_rpm
from distutils.dir_util import remove_tree

from setuptools.command.test import test as TestCommand
from setuptools.command.test import ScanningLoader
from setuptools import setup
from setuptools.command.bdist_rpm import bdist_rpm
from setuptools.command.build_py import build_py
from setuptools.command.egg_info import egg_info
from setuptools.command.install_scripts import install_scripts
# egg_info uses sdist directly through manifest_maker
from setuptools.command.sdist import sdist

from unittest import TestSuite

have_xmlrunner = None
try:
    import xmlrunner
    have_xmlrunner = True
except ImportError:
    have_xmlrunner = False


# private class variables to communicate
# between VscScanningLoader and VscTestCommand
# stored in __builtin__ because the (Vsc)TestCommand.run_tests
# reloads and cleans up the modules
import __builtin__
if not hasattr(__builtin__,'__test_filter'):
    setattr(__builtin__, '__test_filter',  {
        'module': None,
        'function': None,
        'allowmods': [],
    })

# Keep this for legacy reasons, setuptools didn't used to be a requirement
has_setuptools = True

# 0 : WARN (default), 1 : INFO, 2 : DEBUG
log.set_verbosity(2)

# available authors
ag = ('Andy Georges', 'andy.georges@ugent.be')
eh = ('Ewan Higgs', 'Ewan.Higgs@UGent.be')
jt = ('Jens Timmermans', 'jens.timmermans@ugent.be')
kh = ('Kenneth Hoste', 'kenneth.hoste@ugent.be')
kw = ('Kenneth Waegeman', 'Kenneth.Waegeman@UGent.be')
lm = ('Luis Fernando Munoz Meji?as', 'luis.munoz@ugent.be')
sdw = ('Stijn De Weirdt', 'stijn.deweirdt@ugent.be')
wdp = ('Wouter Depypere', 'wouter.depypere@ugent.be')
wp = ('Ward Poelmans', 'Ward.Poelmans@UGent.be')

# Regexp used to remove suffixes from scripts when installing(/packaging)
REGEXP_REMOVE_SUFFIX = re.compile(r'(\.(?:py|sh|pl))$')

# We do need all setup files to be included in the source dir
# if we ever want to install the package elsewhere.
EXTRA_SDIST_FILES = ['setup.py']

# Put unittests under this directory
DEFAULT_TEST_SUITE = 'test'

URL_GH_HPCUGENT = 'https://github.com/hpcugent/%(name)s'
URL_GHUGENT_HPCUGENT = 'https://github.ugent.be/hpcugent/%(name)s'


def find_extra_sdist_files():
    """Looks for files to append to the FileList that is used by the egg_info."""
    log.info("looking for extra dist files")
    filelist = []
    for fn in EXTRA_SDIST_FILES:
        if os.path.isfile(fn):
            filelist.append(fn)
        else:
            log.error("sdist add_defaults Failed to find %s. Exiting." % fn)
            sys.exit(1)
    return filelist


def remove_extra_bdist_rpm_files():
    """Provides a list of files that should be removed from the source file list when making an RPM.

    This function should be overridden if necessary in the setup.py

    @returns: empty list
    """
    return []


class vsc_egg_info(egg_info):
    """Class to determine the set of files that should be included.

    This amounts to including the default files, as determined by setuptools, extended with the
    few extra files we need to add for installation purposes.
    """

    def find_sources(self):
        """Default lookup."""
        egg_info.find_sources(self)
        self.filelist.extend(find_extra_sdist_files())

# TODO: this should be in the setup.py, here we should have a placeholder, so we need not change this for every
# package we deploy
class vsc_bdist_rpm_egg_info(vsc_egg_info):
    """Class to determine the source files that should be present in an (S)RPM.

    All __init__.py files that augment namespace packages should be installed by the
    dependent package, so we need not install it here.
    """

    def find_sources(self):
        """Finds the sources as default and then drop the cruft."""
        vsc_egg_info.find_sources(self)
        for fn in remove_extra_bdist_rpm_files():
            log.debug("removing %s from source list" % (fn))
            self.filelist.files.remove(fn)


class vsc_install_scripts(install_scripts):
    """Create the (fake) links for mympirun also remove .sh and .py extensions from the scripts."""

    def __init__(self, *args):
        install_scripts.__init__(self, *args)
        self.original_outfiles = None

    def run(self):
        # old-style class
        install_scripts.run(self)

        self.original_outfiles = self.get_outputs()[:]  # make a copy
        self.outfiles = []  # reset it
        for script in self.original_outfiles:
            # remove suffixes for .py and .sh
            if REGEXP_REMOVE_SUFFIX.search(script):
                newscript = REGEXP_REMOVE_SUFFIX.sub('', script)
                shutil.move(script, newscript)
                script = newscript
            self.outfiles.append(script)


class vsc_build_py(build_py):
    def find_package_modules (self, package, package_dir):
        """Extend build_by (not used for now)"""
        result = build_py.find_package_modules(self, package, package_dir)
        return result


class vsc_bdist_rpm(bdist_rpm):
    """Custom class to build the RPM, since the __init__.py cannot be included for the packages that have namespace spread across all of the machine."""
    def run(self):
        log.error("vsc_bdist_rpm = %s" % (self.__dict__))
        SHARED_TARGET['cmdclass']['egg_info'] = vsc_bdist_rpm_egg_info  # changed to allow removal of files
        self.run_command('egg_info')  # ensure distro name is up-to-date
        orig_bdist_rpm.run(self)


def filter_testsuites(testsuites):
    """(Recursive) filtering of (suites of) tests"""
    test_filter = getattr(__builtin__, '__test_filter')['function']

    res = type(testsuites)()

    for ts in testsuites:
        # ts is either a test or testsuite of more tests
        if isinstance(ts, TestSuite):
            res.addTest(filter_testsuites(ts))
        else:
            if re.search(test_filter, ts._testMethodName):
                res.addTest(ts)
    return res


class VscScanningLoader(ScanningLoader):
    """The class to look for tests"""

    TEST_LOADER_MODULE = __name__

    def loadTestsFromModule(self, module):
        """
        Support test module and function name based filtering
        """
        testsuites = ScanningLoader.loadTestsFromModule(self, module)

        test_filter = getattr(__builtin__,'__test_filter')

        res = testsuites

        if test_filter['module'] is not None:
            name = module.__name__
            if name in test_filter['allowmods']:
                # a parent name space
                pass
            elif re.search(test_filter['module'], name):
                if test_filter['function'] is not None:
                    res = filter_testsuites(testsuites)
                # add parents (and module itself)
                pms = name.split('.')
                for pm_idx in range(len(pms)):
                    pm = '.'.join(pms[:pm_idx])
                    if not pm in test_filter['allowmods']:
                        test_filter['allowmods'].append(pm)
            else:
                res = type(testsuites)()

        return res


class VscTestCommand(TestCommand):
    """
    The cmdclass for testing
    """

    # make 2 new 'python setup.py test' options available
    user_options = TestCommand.user_options + [
        ('test-filterf=', 'f', "Regex filter on test function names"),
        ('test-filterm=', 'F', "Regex filter on test (sub)modules"),
        ('test-xmlrunner=', 'X', "use XMLTestRunner with value as output name (e.g. test-reports)"),
    ]

    TEST_LOADER_CLASS = VscScanningLoader

    def initialize_options(self):
        """
        Add attributes for new commandline options and set test_loader
        """
        TestCommand.initialize_options(self)
        self.test_filterm = None
        self.test_filterf = None
        self.test_xmlrunner = None

        self.test_loader = '%s:%s' % (self.TEST_LOADER_CLASS.TEST_LOADER_MODULE, self.TEST_LOADER_CLASS.__name__)
        log.info("test_loader set to %s" % self.test_loader)

    def setup_sys_path(self):
        """
        Prepare sys.path to be able to
            use the modules provided by this package (assumeing they are in 'lib')
            use any scripts as modules (for unittesting)
            use the test modules as modules (for unittesting)
        Returns a list of directories to cleanup
        """
        cleanup = []

        # determine the base directory of the repository
        # we will assume that the tests are called from
        # a 'setup.py' like file in the basedirectory
        # (but could be called anything, as long as it is in the basedir)
        setup_py = os.path.abspath(sys.argv[0])
        log.info('run_tests from %s' % setup_py)
        base_dir = os.path.dirname(setup_py)

        # make a lib dir to trick setup.py to package this properly
        # and git ignore empty dirs, so recreate it if necessary
        lib_dir = os.path.join(base_dir, 'lib')
        if not os.path.exists(lib_dir):
            os.mkdir(lib_dir)
            cleanup.append(lib_dir)

        test_dir = os.path.join(base_dir, DEFAULT_TEST_SUITE)
        if os.path.isdir(test_dir):
            sys.path.insert(0, test_dir)
        else:
            raise Exception("Can't find location of testsuite directory %s in %s" % (DEFAULT_TEST_SUITE, base_dir))

        # make sure we can import the script as a module
        scripts_dir = os.path.join(base_dir, 'bin')
        if os.path.isdir(scripts_dir):
            sys.path.insert(0, scripts_dir)

        return cleanup

    def reload_vsc_modules(self):
        """
        Cleanup and restore vsc namespace becasue we use vsc namespace tools very early
        So we need to make sure they are picked up from the paths as specified
        in setup_sys_path, not to mix with installed and already loaded modules
        """
        loaded_vsc_modules = [name for name in sys.modules.keys() if name == 'vsc' or name.startswith('vsc.')]
        reload_vsc_modules = []
        for name in loaded_vsc_modules:
            if hasattr(sys.modules[name], '__file__'):
                # only actual modules
                reload_vsc_modules.append(name)
            del(sys.modules[name])

        # reimport
        for name in reload_vsc_modules:
            __import__(name)

    def force_xmlrunner(self):
        """
        A monkey-patch attempt to run the tests with
        xmlrunner.XMLTestRunner(output=xyz).run(suite)

        E.g. in case of jenkins and you want junit compatible reports
        """
        xmlrunner_output = self.test_xmlrunner

        class OutputXMLTestRunner(xmlrunner.XMLTestRunner):
            """Force the output"""
            def __init__(self, *args, **kwargs):
                kwargs['output'] = xmlrunner_output
                xmlrunner.XMLTestRunner.__init__(self, *args, **kwargs)

        main_orig = unittest.main

        class XmlMain(main_orig):
            """This is unittest.main with forced usage of XMLTestRunner"""
            def __init__(self, *args, **kwargs):
                kwargs['testRunner'] = OutputXMLTestRunner
                main_orig.__init__(self, *args, **kwargs)

        unittest.main = XmlMain

    def run_tests(self):
        """
        Actually run the tests, but start with
            passing the filter options via __builtin__
            set sys.path
            reload vsc modules
        """
        getattr(__builtin__,'__test_filter').update({
            'function': self.test_filterf,
            'module': self.test_filterm,
        })

        if self.test_xmlrunner is not None:
            if not have_xmlrunner:
                raise Exception('test-xmlrunner requires xmlrunner module')
            self.force_xmlrunner()

        cleanup = self.setup_sys_path()

        self.reload_vsc_modules()

        res = TestCommand.run_tests(self)

        # clenaup any diretcories created
        for directory in cleanup:
            shutil.rmtree(directory)

        return res

# shared target config
SHARED_TARGET = {
    'url': '',
    'download_url': '',
    'package_dir': {'': 'lib'},
    'cmdclass': {
        "install_scripts": vsc_install_scripts,
        "egg_info": vsc_egg_info,
        "bdist_rpm": vsc_bdist_rpm,
    },
    'cmdclass': {'test': VscTestCommand},
    'test_suite': DEFAULT_TEST_SUITE,
}


def cleanup(prefix=''):
    """Remove all build cruft."""
    dirs = [prefix + 'build'] + glob.glob(prefix + 'lib/*.egg-info')
    for d in dirs:
        if os.path.isdir(d):
            log.warn("cleanup %s" % d)
            try:
                remove_tree(d, verbose=False)
            except OSError, _:
                log.error("cleanup failed for %s" % d)

    for fn in ('setup.cfg',):
        ffn = prefix + fn
        if os.path.isfile(ffn):
            os.remove(ffn)

def sanitize(v):
    """Transforms v into a sensible string for use in setup.cfg."""
    if isinstance(v, str):
        return v

    if isinstance(v, list):
        return ",".join(v)


def parse_target(target):
    """Add some fields"""
    new_target = {}
    new_target.update(SHARED_TARGET)
    for k, v in target.items():
        if k in ('author', 'maintainer'):
            if not isinstance(v, list):
                log.error("%s of config %s needs to be a list (not tuple or string)" % (k, target['name']))
                sys.exit(1)
            new_target[k] = ";".join([x[0] for x in v])
            new_target["%s_email" % k] = ";".join([x[1] for x in v])
        else:
            if isinstance(v, dict):
                # eg command_class
                if not k in new_target:
                    new_target[k] = type(v)()
                new_target[k].update(v)
            else:
                new_target[k] = type(v)()
                new_target[k] += v

    log.debug("New target = %s" % (new_target))
    return new_target


def build_setup_cfg_for_bdist_rpm(target):
    """Generates a setup.cfg on a per-target basis.

    Stores the 'install-requires' in the [bdist_rpm] section

    @type target: dict

    @param target: specifies the options to be passed to setup()
    """

    try:
        setup_cfg = open('setup.cfg', 'w')  # and truncate
    except (IOError, OSError), err:
        print "Cannot create setup.cfg for target %s: %s" % (target['name'], err)
        sys.exit(1)

    s = ["[bdist_rpm]"]
    if 'install_requires' in target:
        s += ["requires = %s" % (sanitize(target['install_requires']))]

    if 'provides' in target:
        s += ["provides = %s" % (sanitize((target['provides'])))]
        target.pop('provides')

    setup_cfg.write("\n".join(s) + "\n")
    setup_cfg.close()


def action_target(target, setupfn=setup, extra_sdist=[], urltemplate=None):
    # EXTRA_SDIST_FILES.extend(extra_sdist)

    do_cleanup = True
    try:
        # very primitive check for install --skip-build
        # in that case, we don't mind "leftover build";
        # it's probably intentional
        install_ind = sys.argv.index('install')
        build_skip = sys.argv.index('--skip-build')
        if build_skip > install_ind:
            do_cleanup = False
    except ValueError:
        pass

    if do_cleanup:
        cleanup()

    if urltemplate:
        target['url'] = urltemplate % target
        if 'github' in urltemplate:
            target['download_url'] = "%s/tarball/master" % target['url']

    build_setup_cfg_for_bdist_rpm(target)
    x = parse_target(target)

    setupfn(**x)

if __name__ == '__main__':
    # print all supported packages
    all_setups = [x[len('setup_'):-len('.py')] for x in glob.glob('setup_*.py')]
    all_packages = ['-'.join(['vsc'] + x.split('_')) for x in all_setups]
    print " ".join(all_packages)
