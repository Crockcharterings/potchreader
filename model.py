# Basic Models for RSS feed structure
# Specification refered at http://cyber.law.harvard.edu/rss/rss.html
# Based on RSS 2.0 specification
#
# PRFeedChannel includes collection of PRFeedItem models

# import webapp2

from google.appengine.ext import ndb

class PRFeedItem(ndb.Model):
    """RSS Feed Item Model"""
    title       = ndb.StringProperty(required=True)
    link        = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty()
    pub_date    = ndb.DateTimeProperty(auto_now_add=True)
    guid        = ndb.StringProperty()
    read_status = ndb.BooleanProperty(indexed=False, default=False)

    @classmethod
    def feed_item_key(cls, guid):
        return ndb.Key(cls, guid)

class PRFeedChannel(ndb.Model):
    """RSS Channel Item Model"""
    """ttl = time to live(cachable time in minutes)"""
    title           = ndb.StringProperty(required=True)
    link            = ndb.StringProperty(indexed=True,
                                        repeated=False,
                                        required=True
                                        )
    rss_link        = ndb.StringProperty(indexed=False)
    description     = ndb.TextProperty(repeated=False)
    pub_date        = ndb.DateTimeProperty(required=True)
    last_build_date = ndb.DateTimeProperty(required=True)
    ttl             = ndb.IntegerProperty(repeated=False, default=60)
    items           = ndb.StructuredProperty(PRFeedItem,
                                                repeated=True)
#   @classmethod
#   def query_channel(cls, ancestor_key):
#       return cls.query(ancestor=ancestor_key).order(-cls.pub_date)
    @classmethod
    def feed_channel_key(cls, rss_link):
        return ndb.Key(cls, rss_link)
