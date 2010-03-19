import unittest
from testproject.tests.core import CoreTestCase
from testproject.tests.flatpages import FlatpagesTestCase


def suite():
    # this must be changed!! and tests must happen for multiple configurations!
    s = unittest.TestSuite()
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CoreTestCase))
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(FlatpagesTestCase))
    return s