#!/usr/bin/python
#-*-coding:utf-8-*-


import re
import json
import time
from datetime import datetime
from scrapy.selector import Selector
from scrapy.spider import BaseSpider
from scrapy.http import Request, FormRequest


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


# 登录帐号信息
ACCOUNT_NAME = ''
ACCOUNT_PWD = ''





class XMSpider( BaseSpider ):
    name = 'xm'
    allowed_domains = [ 'xiaomi.com' ]


    """请求登录页面，解析出登录所需参数"""
    def start_requests( self ):

        # # FIXME 临时测试
        # return [self.rob_success(
        #     {},
        #     {
        #         'hdurl': '?_a=20131210_phone&_op=choose&_s=11111111111'
        #     }
        # )]
        
        if ACCOUNT_NAME == '' or ACCOUNT_PWD == '':
            print '帐号、密码忘填了!!'
            return []

        print ''
        print '>>>>>> start_requests: ', URL_PAGE
        print ''
        return [Request(
                    url = URL_PAGE,
                    method = 'get',
                    callback = self.parse_request
                )]


    """解析出登录所需参数"""
    def parse_request( self, res ):
        print ''
        print '>>>>>> parse_request: ', res.url

        if res.url == URL_PAGE:
            print '准备解析登录参数: '

            params = {}

            # 解析
            sel = Selector( res )
            for ipt in sel.css( '#loginForm input[type=hidden]' ):
                name = ipt.xpath( '@name' ).extract()[0]
                value = ipt.xpath( '@value' ).extract()[0]
                params[ name ] = value

                print name, ' : ', value

            return self.start_login( params )

        else:
            print '无法识别的request: ', res.url
            print res

            return []


    """执行登录"""
    def start_login( self, params = {} ):
        print ''
        print '>>>>>> start_login: '

        # 合并登录参数
        # formdata = {
        #     'user': ACCOUNT_NAME,
        #     'pwd': ACCOUNT_PWD
        # }.update( params )
        formdata = dict({
            'user': ACCOUNT_NAME,
            'pwd': ACCOUNT_PWD
        }, **params )
        
        print '发送数据: '
        print formdata
        print ''

        return [FormRequest(
                    url = URL_LOGIN,
                    formdata = formdata,
                    callback = self.parse_login
                )]


    """分析登录结果"""
    def parse_login( self, res ):
        print ''
        print '>>>>>> parse_login: '
        print '跳转次数: ', res.meta[ 'redirect_times' ]
        print '跳转列表: ', res.meta[ 'redirect_urls' ]
        print '最终URL: ', res.url

        success = re.match( RE_URL_LOGIN_SUCCESS, res.url, re.I )
        if success:
            print '登录成功'
            print ''

            return self.start_monitor()
        else:
            print '登录失败: '

            msg = Selector( res ).css( '.error_tips .et_con p::text' )
            if msg:
                msg = msg.extract()[0]
            else:
                msg = '未知错误'

            print msg
            print ''

        return



    def start_monitor( self ):
        print ''
        print '>>>>>> start_monitor:'

        now_timestamp = int(time.mktime(datetime.now().timetuple())) * 1000
        url = URL_CHECK % ( now_timestamp )
        request = Request(
            url = url,
            headers = {
                'Referer': URL_CHECK_REFERER
            },
            callback = self.parse_monitor,
            dont_filter = True
        )

        print url
        print ''

        return request

    def parse_monitor( self, res ):
        print ''
        print '>>>>>> parse_monitor:'
        # print res.body
        # print ''

        # 获取&解析 JSON
        d = re.findall(RE_CHECK_BODY, res.body, re.I)[0]
        if ( d ):
            print d

            try:
                d = json.loads(d)
                if d:
                    return self.process_monitor( res, d )
            except Exception, e:
                raise e
        else:
            print 'parse fail'

        return self.rob_fail( res )


    def process_monitor( self, res, data ):
        # log = open( 'monitor.log', 'a' )
        # log.write( json.dumps(data) + '\n' )
        # log.close()

        if ('status' in data) and ('miphone' in data['status']):
            data = data['status']['miphone']

            if len( data['hdurl'] ) > 0:
                return self.rob_success( res, data )
            else:
                if data['reg'] == False:
                    print '没有预约~~~'
                    return
                elif data['hdstart'] == False:
                    print '活动冇开始~~~'
                elif data['hdstop']:
                    print '活动已结束~~'
                    # return
        else:
            print 'status 或 miphone 字段不存在'

        return self.rob_fail( res )


    """抢成功"""
    def rob_success( self, res, data ):
        print '!!!!!! 抢到一个:', data['hdurl']
        log = open( 'rob.log', 'a' )
        log.write( json.dumps(data) + '\n' )
        log.close()


        url = URL_ORDER_WEB % ( data['hdurl'] )
        print '跳转到订单页: ', url

        # 跳转到订单页
        return Request(
                    url = url,
                    headers = {
                        'Referer': URL_CHECK_REFERER
                    },
                    method = 'GET',
                    callback = self.start_order,
                    dont_filter = True
               )

    """抢失败"""
    def rob_fail( self, res ):
        print ''
        print '没抢到~~~, next...'
        return self.start_monitor()

    """下订单"""
    def start_order( self, res ):
        print ''
        print '>>>>>> start_order:'
        # print res.body

        # 存储页面内容，备后续分析
        log = open( 'order.html', 'a' )
        log.write( res.body + '\n-\n-\n-\n' )
        log.close()


        # TODOP 解析生成表单参数并存储到文件
        sel = Selector( res )
        url = sel.css('#selectForm::attr(action)').extract()[0]
        formdata = self.parse_formdata_order( res )

        print '请求订单api:'
        print 'URL: ', url
        print 'DATA: ', formdata

        # TODO 暂时这里先跳过，待完成 pase_order 再放开
        return FormRequest(
                    url = url,
                    formdata = formdata,
                    callback = self.parse_order
               )

        # return

    def parse_order( self, res ):
        print ''
        print '>>>>>> parse_order:'
        print res.request.url

        # 存储页面内容，备后续分析
        log = open( 'order2.html', 'a' )
        log.write( res.body + '\n-\n-\n-\n' )
        log.close()

        # FIXME 测试
        # self.order_success( res )
        print '>>>>>> TODO 检测是否下单成功...order2.html'

        return

    def parse_formdata_order( self, res ):
        print ''
        print '>>>>>> parse_formdata_order:'

        # TODO  解析生成表单参数并存储到文件

        # 过滤出from field数据，供后续解析
        data = re.findall(
            r'insertDom\((.*?)\);',
            res.body,
            re.I
        )[0]

        if data:
            try:
                data = json.loads( data )
            except Exception, e:
                print '解析formdata异常:'
                print data
                raise e
        else:
            print '未找到formdata关键数据'
            return


        # 1. 解析出 form field 列表（动态 + 静态）
        static_kvs = {} # 不会变化的form field
        dynamic_kvs = {} # JS会动态修改的特殊form field
        for d in data:
            if d['type'] == 'hidden':
                if 'id' in d:
                    dynamic_kvs[ d['id'] ] = d['name']
                else:
                    static_kvs[ d['name'] ] = d['value']

        # 2. 解析动态 form field
        
        # 2.1 选择机型代号
        key_mid = re.findall(
            r'document\.getElementById\(\'(\w+)\'\)\.value\s?=\s?mid\s?',
            res.body,
            re.I
        )[0]
        if key_mid:
            print '解析设备代号字段名成功:', key_mid
            print '开始检索动态表获取name:'
            for k in dynamic_kvs:
                print '当前检索:', k, dynamic_kvs[k]
                if k == key_mid:
                    key_mid = dynamic_kvs[k]
                    static_kvs[ key_mid ] = '' # 更新静态表
                    print '找到匹配:', key_mid
                    break
        else:
            print '解析设备代号字段名失败'
            return

        # 2.2 验证码
        print '解析验证码字段:'
        sel = Selector( res )
        key_code = sel.css('input[name="verCode"]')
        if key_code:
            # 先根据DOM查到用户交互的input.id
            key_code = key_code.css('::attr(id)').extract()[0]
            # 根据查询到的ID找到对应的hidden input的id
            key_code = re.findall(
                r'document\.getElementById\(\'(\w+)\'\)\.value\s?=\s?document\.getElementById\(\'' + key_code + '\'\)\.value\s?',
                res.body,
                re.I
            )[0]
            # 根据隐藏input的id解析出name
            if ( key_code ): 
                print '解析成功:', key_code
                for k in dynamic_kvs:
                    print '当前检索:', k, dynamic_kvs[k]
                    if k == key_code:
                        key_code = dynamic_kvs[k]
                        static_kvs[ key_code ] = '' # 更新静态表
                        print '找到匹配:', key_code
                        break
            else:
                print '解析失败'
        else:
            print '解析验证码字段名失败'


        # 3. 解析出可选择的设备列表
        print '解析可选择的设备:'
        device_enable = []
        radios = sel.css('div.radio').extract()
        for r in radios:
            if re.findall( r'soldOver', r, re.I ):
                pass
            else:
                device_enable.append(
                    re.findall( r'mid="(\w+)"', r, re.I )[0]
                )
        print '检索结果:', device_enable


        # 设置选择设备为第一个可买设备
        # TODO 找时间加上优先级策略
        static_kvs[ key_mid ] = device_enable[0]

        # TODO 设置手工输入的验证码, 找时间完成手工输入
        static_kvs[ key_code ] = 'abcd'


        print 'formdata:', data
        print 'static_kvs:', static_kvs
        print 'dynamic_kvs:', dynamic_kvs
        print '硬件代码key_mid', key_mid
        print '验证码key_code', key_code


        return static_kvs

