#!/usr/bin/env python

import unittest
import webapp2
import webtest
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext import testbed

from  main import MainHandler
from  main import ChannelHandler
from  main import ChannelRegHandler

class TestMain(unittest.TestCase):
    def setUp(self):
        # setup for web handlers
        # app = webapp2.WSGIApplication([('/', main.MainHandler)])

        app = webapp2.WSGIApplication([
            ('/', MainHandler),
            ('/channel', ChannelRegHandler),
            ('/channel/(\d+)', ChannelHandler)
        ], debug=True)
        self.testapp = webtest.TestApp(app)

        # create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # active the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # declare which service stubs to be used.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()


    def tearDown(self):
        self.testbed.deactivate()


    def testMainHandlerGetMethod(self):
        response = self.testapp.get('/')
        self.assertTrue(response, 'Check if MainHandler responses right')
        self.assertEqual(response.normal_body, '{}', 'Case of complete response')
        self.assertNotEqual(response.normal_body, '{', 'Case of incomplete response')
