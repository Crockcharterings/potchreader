#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import json
from datetime import datetime
#from time import time
import time

from lib import feedparser

import model
#import jsonutil

def _get_feed_data(raw_url):
    data = feedparser.parse(raw_url)
    return data

def _set_entries(entries, channel):
    if not entries:
        raise ValueError('No feed items.')

    for item in entries:
        if channel.items.guid != item.id:
            feed_item = PRFeedItem(
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
        d = _get_feed_data('http://rss.rssad.jp/rss/ascii/rss.xml')
        self.response.write(d)

class ChannelHandler(webapp2.RequestHandler):
    def post(self):
        """This method handles RSS registration page"""
        url = self.request.get('url')
        feeddata = _get_feed_data(url)

        rspn_msg = {'status': 200}

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

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/channel', ChannelHandler)
], debug=True)
