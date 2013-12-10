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



# 登录帐号信息
ACCOUNT_NAME = ''
ACCOUNT_PWD = ''


# 机型代号列表
DEVICE_TYPES = {
    'J': 's3-16-白-?',
    'K': 's3-16-黑-TD',
    'L': 's3-16-银-TD',
    'N': 's3-64-黑-?',
    'F': 'h-?-灰-移动',
    'M': 'h-?-灰-联通',
    'B': 's2-32-?-标准',
    'C': 'S2-32-?-电信',
}


# TODO 活动时间标志(很多地方在用,目前先手工更新)
DATE_TIME = '20131210'

# 登录页
URL_PAGE = 'https://account.xiaomi.com/pass/serviceLogin'
# 登录API
URL_LOGIN = 'https://account.xiaomi.com/pass/serviceLoginAuth2'
# 检测API
URL_CHECK = 'http://tc.hd.xiaomi.com/hdget?callback=hdcontrol&_=%s'
# 检测API的referer(==抢购页)
URL_CHECK_REFERER = 'http://p.www.xiaomi.com/m/op/page/%s/index.html' % ( DATE_TIME )
# 订单页
URL_ORDER_WEB = 'http://t.hd.xiaomi.com/s/%s&_m=1'
# URL_ORDER_WEB = 'http://127.0.0.1:8848/order.html%s&_m=1'
# 验证码， 注意：第一参数需替换 _op=choose 为 _op=authcode
URL_IMGCODE = 'http://t.hd.xiaomi.com/s/%s&_m=1&r=%s'

# 登录成功后跳转URL
RE_URL_LOGIN_SUCCESS = r'^http[s]?://account.xiaomi.com/pass/userInfo'
# 检测API结果过滤(这里要注意要与`URL_CHECK`的callback参数值对应)
RE_CHECK_BODY = r'\s?hdcontrol\((.*?)\)\s?'
# 订单页表单field数据配置信息过滤(js动态初始化的)
RE_FORM_FIELDS_ORDER = r'insertDom\((.*?)\);'
# 订单页表单field中对应设备代号的字段名
RE_FORM_FIELD_MID = r'document\.getElementById\(\'(\w+)\'\)\.value\s?=\s?mid\s?'
# 订单页已售罄的设备所在DOM包含的class
RE_ORDER_DEVICE_SOLDOVER = r'soldOver'
# 订单页可选购的设备所在DOM包含的mid属性值(即设备代号mid)
RE_ORDER_MID_ATTR = r'mid="(\w+)"'
