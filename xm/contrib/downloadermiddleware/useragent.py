#!/usr/bin/python
#-*-coding:utf-8-*-

import random
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware


USER_AGENT_LIST = [
    # iphone ios5
    'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
    # iphone ios4
    'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_2 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8H7 Safari/6533.18.5',
    # ipad ios5
    'Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3',
    # ipad ios4
    'Mozilla/5.0 (iPad; CPU OS 4_3_2 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8H7 Safari/6533.18.5',
]


class RandomUserAgentMiddleware( UserAgentMiddleware ):
    
    """docstring for RandomUserAgentMiddleware"""
    def __init__( self, user_agent = '' ):
        self.user_agent = user_agent

    def _user_agent( self, spider ):
        if hasattr( spider, 'user_agent' ):
            return spider.user_agent
        elif self.user_agent:
            return self.user_agent

        return random.choice( USER_AGENT_LIST )

    def process_request( self, request, spider ):
        ua = self._user_agent( spider )
        # print ''
        # print '>>>>>>>>', ua
        # print ''
        if ua:
            request.headers.setdefault( 'User-Agent', ua )





