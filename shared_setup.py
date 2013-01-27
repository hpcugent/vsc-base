#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Copyright 2009-2013 Ghent University
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
@author: Stijn De Weirdt (Ghent University)
@author: Andy Georges (Ghent University)
Shared module for vsc-base setup
"""
import glob
import os
import shutil
import sys
from distutils import log  # also for setuptools
from distutils.dir_util import remove_tree

# 0 : WARN (default), 1 : INFO, 2 : DEBUG
log.set_verbosity(2)

has_setuptools = None

EXTRA_SDIST_FILES = ['shared_setup.py', 'setup.py']

def find_extra_sdist_files():
    filelist = []
    for fn in EXTRA_SDIST_FILES:
        if os.path.isfile(fn):
            filelist.append(fn)
        else:
            print "sdist add_defaults Failed to find %s" % fn
            sys.exit(1)
    log.info("find_extra_sdist_files: %s" % filelist)
    return filelist

try:
    # setuptools makes copies of the scripts, does not preserve symlinks
    # raise("no setuptools")  # to try distutils, uncomment
    from setuptools import setup
    from setuptools.command.install_scripts import install_scripts
    from setuptools.command.build_py import build_py
    from setuptools.command.sdist import sdist
    # egg_info uses sdist directly through manifest_maker
    from setuptools.command.egg_info import egg_info
    class vsc_egg_info(egg_info):
        def find_sources(self):
            egg_info.find_sources(self)
            self.filelist.extend(find_extra_sdist_files())
    has_setuptools = True
except:
    from distutils.core import setup
    from distutils.command.install_scripts import install_scripts
    from distutils.command.build_py import build_py
    from distutils.command.sdist import sdist

    class vsc_egg_info(object):
        pass  # dummy class for distutils

    has_setuptools = False


# authors
ag = ('Andy Georges', 'andy.georges@ugent.be')
jt = ('Jens Timmermans', 'jens.timmermans@ugent.be')
kh = ('Kenneth Hoste', 'kenneth.hoste@ugent.be')
lm = ('Luis Fernando Munoz Meji�as', 'luis.munoz@ugent.be')
sdw = ('Stijn De Weirdt', 'stijn.deweirdt@ugent.be')
wdp = ('Wouter Depypere', 'wouter.depypere@ugent.be')


class vsc_install_scripts(install_scripts):
    """Create the (fake) links for mympirun
        also remove .sh and .py extensions from the scripts
    """
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
            if script.endswith(".py") or script.endswith(".sh"):
                shutil.move(script, script[:-3])
                script = script[:-3]
            self.outfiles.append(script)

class vsc_build_py(build_py):
    def find_package_modules (self, package, package_dir):
        """Extend build_by (not used for now)"""
        result = build_py.find_package_modules(self, package, package_dir)
        return result

class vsc_sdist(sdist):
    def add_defaults(self):
        """Add shared_setup.py"""
        sdist.add_defaults()
        self.filelist.extend(find_extra_sdist_files())

# shared target config
SHARED_TARGET = {
    'url': 'http://hpcugent.github.com/vsc-base',
    'download_url': 'https://github.com/hpcugent/vsc-base',
    'package_dir': {'': 'lib'},
    'cmdclass': {
        "install_scripts": vsc_install_scripts,
        # "build_py":vsc_build_py,
        "sdist":vsc_sdist,
        "egg_info":vsc_egg_info,
    },
}

def cleanup(prefix=''):
    dirs=[prefix+'build']+glob.glob(prefix + 'lib/*.egg-info')
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

def make_setup(name='base',prefix=''):
    """Create the setup.py
        - default is base
    """
    fn = '%ssetup_%s.py' % (prefix, name)
    if os.path.isfile(fn):
        shutil.copyfile(fn, 'setup.py')
    else:
        log.error("setup file %s for name %s not found" % (fn, name))

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


def action_target(target, setupfn=setup, extra_sdist=[]):
    EXTRA_SDIST_FILES.extend(extra_sdist)
    name = '_'.join(target['name'].split('-')[1:])

    cleanup()

    build_setup_cfg_for_bdist_rpm(target)
    x = parse_target(target)
    setupfn(**x)
    cleanup()

if __name__ == '__main__':
    # print all supported packages
    all_setups = [x[len('setup_'):-len('.py')] for x in glob.glob('setup_*.py')]
    all_packages = ['-'.join(['vsc'] + x.split('_')) for x in all_setups]
    print " ".join(all_packages)
