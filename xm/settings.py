#!/usr/bin/python
#-*-coding:utf-8-*-

BOT_NAME = 'xm'

SPIDER_MODULES = ['xm.spiders']
NEWSPIDER_MODULE = 'xm.spiders'

# LOG_ENABLED = True
# LOG_ENCODING = 'utf-8'
LOG_FILE = 'scrapy.log'

COOKIES_ENABLED = True
COOKIES_DEBUG = True

DOWNLOAD_DELAY = 1 # 1000 ms of delay
DOWNLOAD_TIMEOUT = 300 # sec
REDIRECT_MAX_TIMES = 15000 # must DOWNLOAD_DELAY > 0

# for active custom middleware
USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'

DOWNLOADER_MIDDLEWARES = {
	'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
	'xm.contrib.downloadermiddleware.useragent.RandomUserAgentMiddleware': 400,
}

# proxy list
PROXY_LIST = []


# 登录帐号信息(留空时，登录前会要求再次输入)
ACCOUNT_NAME = ''
ACCOUNT_PWD = ''
ACCOUNT_PROVINCE = '2' # 北京
ACCOUNT_CITY = '36' # 北京市
ACCOUNT_DIS = '384' # 海淀区
ACCOUNT_ADDRESS = '上地十街10号'
ACCOUNT_CODE = '100085'


# 机型代号列表
DEVICE_TYPES = {
    'J': 's3-16-白-移动',
    'S': 's3-16-?-联通',
    'K': 's3-16-黑-TD',
    'L': 's3-16-银-TD',
    'N': 's3-64-黑-?',
    'F': 'h-?-灰-移动',
    'M': 'h-?-灰-联通',
    'B': 's2-32-?-标准',
    'C': 'S2-32-?-电信',
}

# 活动开始前每次检测的休眠间隔(s)
SLEEP_TIME = 10


# 首页(主要用来获取'开放时间点'')
URL_HOME = 'http://www.xiaomi.com/index.php'
# 移动端首页地址(主要用来给一些从移动首页点击过去的页面模拟使用)
URL_HOME_RERERER = 'http://m.xiaomi.com/index.html'
# 预约页
URL_SUBSCRIBE = 'http://a.hd.xiaomi.com/register/book/m/1/a/%s'
# 预约页跳转
URL_SUBSCRIBE_FINAL = 'http://p.www.xiaomi.com/open/index.html'
# 预约表单确认页
URL_SUBSCRIBE_FORM = 'http://a.hd.xiaomi.com/product/book/a/1/m/1'
# 登录页
URL_PASS = 'https://account.xiaomi.com/pass/serviceLogin'
# 登录API
URL_LOGIN = 'https://account.xiaomi.com/pass/serviceLoginAuth2'
# 检测API
URL_CHECK = 'http://tc.hd.xiaomi.com/hdget?callback=hdcontrol&_=%s'
# 检测API的referer(==抢购页)
URL_CHECK_REFERER = 'http://p.www.xiaomi.com/m/op/page/%s/index.html'
# 检测是否已预约当前轮
# URL_CHECK_SUBSCRIBE = 'http://t.hd.xiaomi.com/c/?_a=4&_op=check'
# URL_CHECK_SUBSCRIBE = 'http://a.hd.xiaomi.com/register/check/a/%s/m/1'
URL_CHECK_SUBSCRIBE = 'http://p.www.xiaomi.com/m/yy/%s/%s/index.html'
# 检测是否有待支付的
URL_CHECK_PAYMENT = 'http://tc.hd.xiaomi.com/check?_a=payment_check&_m=1'
# 订单页
URL_ORDER_WEB = 'http://t.hd.xiaomi.com/s/%s&_m=1'
# 验证码， 注意：第一参数需替换 _op=choose 为 _op=authcode
URL_IMGCODE = 'http://t.hd.xiaomi.com/s/%s&_m=1&r=%s'

# 活动开始时间(从首页的Tip处分析获取,得到格式为: [ '年', '月', '时' ])
RE_TIME_START = r'(\d+)'
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
# 预约地址构造之aid参数 - 手机
RE_SUBSCRIBE_AID_PHONE = r'_el=(\d+)&'
# 预约地址构造之aid参数 - 电视
RE_SUBSCRIBE_AID_TV = r'_pf=(\d+)&'
# 预约地址构造之aid参数 - 电源
RE_SUBSCRIBE_AID_PW = r'_zm=(\d+)&'
