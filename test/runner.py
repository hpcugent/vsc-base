# -*- encoding: utf-8 -*-
import sys
import os
import test.cache as tc
import test.dateandtime as td
import test.nagios as tn
import test.generaloption as tg
import test.nagios_results as tr
import test.fancylogger as tf
import unittest


suite = unittest.TestSuite([x.suite() for  x in (tc, td, tn, tg, tr, tf)])

try:
    import xmlrunner
    rs = xmlrunner.XMLTestRunner(output="test-reports").run(suite)
except ImportError, err:
    rs = unittest.TextTestRunner().run(suite)

if not rs.wasSuccessful():
    sys.exit(1)
