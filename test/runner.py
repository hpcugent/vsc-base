# -*- encoding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import test.asyncprocess as a
import test.dateandtime as td
import test.exceptions as te
import test.fancylogger as tf
import test.generaloption as tg
import test.missing as tm
import test.rest as trest
import test.run as trun
import test.testing as tt
import test.optcomplete as topt
import test.wrapper as wrapt
import unittest


from vsc.utils import fancylogger
fancylogger.logToScreen(enable=False)

suite = unittest.TestSuite([x.suite() for x in (a, td, tg, tf, te, tm, trest, trun, tt, topt, wrapt)])

try:
    import xmlrunner
    rs = xmlrunner.XMLTestRunner(output="test-reports").run(suite)
except ImportError, err:
    rs = unittest.TextTestRunner().run(suite)

if not rs.wasSuccessful():
    sys.exit(1)
