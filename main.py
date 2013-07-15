#!/usr/bin/env python

import webapp2
import json
from datetime import datetime
import time

from lib import feedparser

import model

def _get_feed_data(raw_url):
    data = feedparser.parse(raw_url)
    return data

def _set_entries(entries, channel):
    if not entries:
        raise ValueError('No feed items.')

    for item in entries:
        if channel.items.guid != item.id:
            feed_item = PRFeedItem(
                    key         = model.PRFeedItem.feed_item_key(
                                    channel.items.guid
                                    ),
                    title       = item.title,
                    link        = item.link,
                    description = item.summary,
                    pub_date    = item.published_parsed,
                    guid        = item.id
                    )
            item_key = feed_item.put()
            channel.items.append(feed_item)

    channel.put()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(d)

class ChannelHandler(webapp2.RequestHandler):
    def post(self):
        """This method handles RSS registration"""
        url = self.request.get('url')
        feeddata = _get_feed_data(url)

        rspn_msg = {'status': 200}
        self.response.content_type_params = {
                'content-type':'application/json',
                'charset':'utf8'
                }

        if not feeddata.version:
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

            rspn_msg['msg'] = 'Saved Successfully; Now the channel needs reloading.'
        else:
            rspn_msg['msg'] = 'Channel already exists.'

        self.response.write(json.JSONEncoder().encode(rspn_msg))

    def get(self, num_limit=10):
        chs = {}
        ch_list = model.PRFeedChannel.query().fetch(int(num_limit))
        for ch in ch_list:
            chs[ch.title] = ch.to_dict(exclude=['key', 'rss_link',
                                                'pub_date', 'last_build_date',
                                                'ttl'])
        self.response.content_type_params = {
                'content-type':'application/json',
                'charset':'utf8'
                }

        self.response.write(json.JSONEncoder(
                                    ensure_ascii=False, encoding='utf8').encode(chs))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/channel', ChannelHandler),
    ('/channel/(\d+)', ChannelHandler)
], debug=True)
