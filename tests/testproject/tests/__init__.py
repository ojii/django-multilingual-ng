import unittest
from testproject.tests.core import CoreTestCase
from testproject.tests.flatpages import FlatpagesTestCase
from testproject.tests.templates import TemplateTestCase


def suite():
    # this must be changed!! and tests must happen for multiple configurations!
    s = unittest.TestSuite()
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(CoreTestCase))
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(FlatpagesTestCase))
    s.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TemplateTestCase))
    return s