#!/usr/bin/python
#-*-coding:utf-8-*-

BOT_NAME = 'xm'

SPIDER_MODULES = ['xm.spiders']
NEWSPIDER_MODULE = 'xm.spiders'

COOKIES_ENABLED = True
COOKIES_DEBUG = True

DOWNLOAD_DELAY = 1 # 1000 ms of delay
DOWNLOAD_TIMEOUT = 240 # sec
REDIRECT_MAX_TIMES = 1000 # must DOWNLOAD_DELAY > 0

# for active custom middleware
USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'

DOWNLOADER_MIDDLEWARES = {
	'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
	'xm.contrib.downloadermiddleware.useragent.RandomUserAgentMiddleware': 400,
}
