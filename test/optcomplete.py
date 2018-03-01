#
# Copyright 2013-2018 Ghent University
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
Tests for the vsc.utils.optcomplete module and its use in generaloption.

@author: Stijn De Weirdt (Ghent University)
"""
import os
import tempfile
from vsc.install.testing import TestCase
from vsc.utils import optcomplete
from vsc.utils.optcomplete import Completer, CompleterMissingCallArgument
from vsc.utils.optcomplete import NoneCompleter, ListCompleter, AllCompleter, KnownHostsCompleter
from vsc.utils.optcomplete import FileCompleter, DirCompleter, RegexCompleter
from vsc.utils.optcomplete import extract_word, gen_cmdline, OPTCOMPLETE_ENVIRONMENT

class OptcompleteTest(TestCase):
    """Tests for optcomplete."""

    def setUp(self):
        """Create fake directory structure with files and directories"""
        self.basetemp = tempfile.mkdtemp()
        self.tempfiles = []
        self.tempdirs = []

        for _ in range(3):
            fhid, fn = tempfile.mkstemp(dir=self.basetemp)
            fh = os.fdopen(fhid, 'w')
            fh.write('')
            fh.close()
            self.tempfiles.append(fn)

        for _ in range(3):
            self.tempdirs.append(tempfile.mkdtemp(dir=self.basetemp))

        self.alltemp = self.tempfiles + self.tempdirs
        super(OptcompleteTest, self).setUp()

    def tearDown(self):
        """cleanup testing"""
        for fn in self.tempfiles:
            os.remove(fn)

        for fn in self.tempdirs:
            os.rmdir(fn)
        os.rmdir(self.basetemp)

    def test_base_completer(self):
        """Test the base Completer class"""
        class NewCompleter(Completer):
            CALL_ARGS = ['x']
            CALL_ARGS_OPTIONAL = ['y']

            def _call(self, **kwargs):
                return sorted(kwargs.keys())

        nc = NewCompleter()
        # missing mandatory CALL_ARGS
        try:
            nc()
        except Exception, e:
            pass

        self.assertEqual(e.__class__, CompleterMissingCallArgument)

        # proper usage : strip any non-mandatory or optional argument from kwargs
        res = nc(x=1, y=2, z=3)
        self.assertEqual(res, sorted(['x', 'y']))

    def test_none_completer(self):
        """Test NoneCompleter class"""

        # ignore all arguments
        nc = NoneCompleter()
        self.assertEqual(nc(x=1, y=1), [])

    def test_list_completer(self):
        """Test ListCompleter class"""
        # return list of strings
        initlist = ['original', 'list', 1]
        lc = ListCompleter(initlist)
        self.assertEqual(lc(), map(str, initlist))

    def test_all_completer(self):
        """Test the AllCompleter class"""
        ac = AllCompleter()
        res = ac(pwd=self.basetemp)
        self.assertEqual([os.path.join(self.basetemp, name) for name in sorted(res)], sorted(self.alltemp))

    def test_known_hosts_completer(self):
        """Test KnownHostsCompleter"""

        kc = KnownHostsCompleter()

        # only proper bash support
        optcomplete.SHELL = optcomplete.BASH
        self.assertEqual(kc(), '_known_hosts')

        # any other must get back []
        optcomplete.SHELL = 'not a real shell'
        self.assertEqual(kc(), [])

    def test_file_completer(self):
        """Test FileCompleter"""
        # test bash
        optcomplete.SHELL = optcomplete.BASH
        fc = FileCompleter()
        self.assertEqual(fc(), '_filedir')

        fc = FileCompleter(['.a'])
        self.assertEqual(fc(), "_filedir '@(.a)'")

    def test_dir_completer(self):
        """Test DirCompleter"""
        # test bash
        optcomplete.SHELL = optcomplete.BASH
        dc = DirCompleter()
        self.assertEqual(dc(), '_filedir -d')

    def test_regex_completer(self):
        """Test RegexCompleter"""
        rc = RegexCompleter(['^tmp'])
        expected_res = self.tempfiles + self.tempdirs + ["%s%s" % (p, os.path.sep) for p in self.tempdirs]
        self.assertEqual(sorted(rc(prefix=os.path.join(self.basetemp, 'tmp'))), sorted(expected_res))

    def test_extract_word(self):
        """Test the extract_word function"""
        testlines = {
            "extraire un mot d'une phrase": {
                    11: ('un', ''),
                    12: ('', 'mot'),
                    13: ('m', 'ot'),
                    14: ('mo', 't'),
                    0: ('', 'extraire'),
                    28: ('phrase', ''),
                    29: ('', ''),
                    - 2: ('', ''),
                },
            "optcomplete-test do": {
                    19: ('do', ''),
                }
            }

        for line, totest in testlines.items():
            for pointer, res in totest.items():
                self.assertEqual(extract_word(line, pointer), res)

    def test_gen_cmdline(self):
        """Test generation of commndline"""
        partial = 'z'
        cmd_list = ['x', 'y', partial]
        cmdline = gen_cmdline(cmd_list, partial)
        for word in [OPTCOMPLETE_ENVIRONMENT, 'COMP_LINE', 'COMP_WORDS', 'COMP_CWORD', 'COMP_POINT']:
            self.assertTrue("%s=" % word in cmdline)


def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestOptcomplete)


if __name__ == '__main__':
    main()
