#!/usr/bin/env python

import cgi
import os
import jinja2
import webapp2
import json
from datetime import datetime
import time

from lib import feedparser

import model

JINJA_ENVIRONMENT = jinja2.Environment(
                    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                    extensions=['jinja2.ext.autoescape'])

def _date_json_default(obj):
    if isinstance(obj, datetime):
        return int(time.mktime(obj.timetuple()))
    return json.JSONEncoder.default(obj)

def _get_feed_data(raw_url):
    data = feedparser.parse(raw_url)
    return data

def _set_entries(entries, channel):
    if not entries:
        raise ValueError('No feed items.')

    for item in entries:
        _item_id = item.id if hasattr(item, 'id') and item.id else item.link
        if not hasattr(channel.items, 'guid') or channel.items.guid != _item_id:
            _pd = item.published_parsed
            _pub_date = datetime.fromtimestamp(time.mktime(_pd))
            feed_item = model.PRFeedItem(
                    key         = model.PRFeedItem.feed_item_key(
                                    _item_id
                                    ),
                    title       = item.title,
                    link        = item.link,
                    description = item.summary,
                    pub_date    = _pub_date,
                    guid        = _item_id
                    )
            item_key = feed_item.put()
            channel.items.append(feed_item)
            channel.put()

def _get_entries(num_limit=10):
    items = {}
#   feeds_list = model.PRFeedItem.query().fetch(num_limit)
    feeds_list = model.PRFeedItem.query_by_date(num_limit)
    for item in feeds_list:
        items[item.guid] = item.to_dict(exclude=['key'])

    return json.JSONEncoder(ensure_ascii=False, encoding='utf8',
                    default=_date_json_default).encode(items)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(_get_entries())

class ChannelRegHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('template/seturl.html')
        self.response.write(template.render())

    def post(self):
        """This method handles RSS registration"""
        url = self.request.get('url')
        feeddata = _get_feed_data(url)

        rspn_msg = {'status': 200}
        self.response.content_type_params = {
                'content-type':'application/json',
                'charset':'utf8'
                }

        if not hasattr(feeddata, 'version'):
            rspn_msg['msg'] = feeddata.debug_message
            self.response.write(json.JSONEncoder().encode(rspn_msg))

        channel_key = model.PRFeedChannel.feed_channel_key(url)
        channel = channel_key.get()

        if not channel:
            _pd = feeddata.feed.published_parsed
            _lb = feeddata.feed.updated_parsed
            _pub_date = datetime.fromtimestamp(time.mktime(_pd))
            _last_build = datetime.fromtimestamp(time.mktime(_lb))

            channel = model.PRFeedChannel(
                            key             = channel_key,
                            title           = feeddata.feed.title,
                            link            = feeddata.href,
                            rss_link        = feeddata.feed.link,
                            description     = feeddata.feed.description,
                            pub_date        = _pub_date,
                            last_build_date = _last_build,
                            )
            if hasattr(feeddata.feed, "ttl"):
                channel.ttl = int(feeddata.feed.ttl)

            channel.put()

            rspn_msg['msg'] = 'Saved Successfully.'
        else:
            rspn_msg['msg'] = 'Channel already exists.'

        _set_entries(feeddata.entries, channel)

        self.response.write(json.JSONEncoder().encode(rspn_msg))

class ChannelHandler(webapp2.RequestHandler):
    def get(self, num_limit=10):
        chs = {}
        ch_list = model.PRFeedChannel.query().fetch(int(num_limit))
        for ch in ch_list:
            chs[ch.title] = ch.to_dict(exclude=['key','rss_link','ttl','items'])

        self.response.content_type_params = {
                'content-type':'application/json',
                'charset':'utf8'
                }

        self.response.write(json.JSONEncoder(
                            ensure_ascii=False, encoding='utf8', 
                            default=_date_json_default
                            ).encode(chs))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/channel', ChannelRegHandler),
    ('/channel/(\d+)', ChannelHandler)
], debug=True)
