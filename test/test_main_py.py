#!/usr/bin/env python

import unittest
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed

class TestMain(unittest.TestCase):
    def setUp(self):
        # create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # active the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # declare which service stubs to be used.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testMainMethod(self):
        from main import MainHandler
        main_handler = MainHandler()
        json = main_handler.get()
        self.assertIsInstance(json, str, 'Check if MainHandler Returns str')

# def main():
#     unittest.main()
# if __name__ == '__main__':
#     main()
