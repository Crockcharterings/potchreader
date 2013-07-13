# Basic Models for RSS feed structure
# Specification refered at http://cyber.law.harvard.edu/rss/rss.html
# Based on RSS 2.0 specification
#
# PRFeedChannel includes collection of PRFeedItem models

# import webapp2

from google.appengine.ext import ndb

class PRFeedItem(ndb.Model):
    """RSS Feed Item Model"""
    title = ndb.StringProperty(required=True)
    link = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty()
    pub_date = ndb.DateTimeProperty(auto_now_add=True)
    guid = ndb.StringProperty()
    read_status = ndb.BooleanProperty(indexed=False, default=False)

class PRFeedChannel(ndb.Model):
    """RSS Channel Item Model"""
    """ttl = time to live(cachable time in minutes)"""
    title = ndb.StringProperty(required=True)
    link = ndb.StringProperty(indexed=False, required=True)
    description = ndb.TextProperty()
    pub_date = ndb.DateTimeProperty(required=True)
    last_build_date = ndb.DateTimeProperty(required=True)
    ttl = ndb.IntegerProperty(repeated=False)
    items = ndb.StructuredProperty(PRFeedItem, repeated=True)
