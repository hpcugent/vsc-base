# -*- encoding: utf-8 -*-
import os
import sys

top = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
print top
sys.path.insert(0, os.path.join(top, 'lib'))

import vsc.test.vsc_base.asyncprocess as a
import vsc.test.vsc_base.dateandtime as td
import vsc.test.vsc_base.docs as tdo
import vsc.test.vsc_base.exceptions as te
import vsc.test.vsc_base.fancylogger as tf
import vsc.test.vsc_base.generaloption as tg
import vsc.test.vsc_base.missing as tm
import vsc.test.vsc_base.rest as trest
import vsc.test.vsc_base.run as trun
import vsc.test.vsc_base.testing as tt
import vsc.test.vsc_base.optcomplete as topt
import vsc.test.vsc_base.wrapper as wrapt
import unittest


from vsc.utils import fancylogger
fancylogger.logToScreen(enable=False)

suite = unittest.TestSuite([x.suite() for x in (a, td, tg, tf, te, tm, trest, trun, tt, topt, wrapt, tdo)])

try:
    import xmlrunner
    rs = xmlrunner.XMLTestRunner(output="test-reports").run(suite)
except ImportError, err:
    rs = unittest.TextTestRunner().run(suite)

if not rs.wasSuccessful():
    sys.exit(1)
