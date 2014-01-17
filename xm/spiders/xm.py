#!/usr/bin/python
#-*-coding:utf-8-*-

# 解决中文解码报错问题
import sys
reload( sys ) 
sys.setdefaultencoding( 'utf-8' )

import re
import json
import time
import random
from datetime import datetime
from scrapy.selector import Selector
from scrapy.spider import BaseSpider
from scrapy.http import Request, FormRequest
from scrapy.utils.response import open_in_browser
# from scrapy.settings import Settings




class XMSpider( BaseSpider ):
    name = 'xm'
    allowed_domains = [ 'xiaomi.com' ]
    
    # 可能会动态修改的配置项
    account = '' # 帐号
    password = '' # 密码
    open_time = '' # 开放购买时间 形如: '20131224'
    url_referer_check = '' # 部分请求需要


    """请求首页获取关键数据"""
    def start_requests( self ):
        print ''
        print '>>>>>> start_requests: '

        return [
            Request(
                url = self.settings[ 'URL_HOME' ],
                method = 'get',
                callback = self.start_init
            )
        ]

    """初始化准备"""
    def start_init( self, res ):
        print ''
        print '>>>>>> start_init: ', res.url

        sel = Selector( res )

        print '获取开放时间:'
        hdStartTip = sel.css( '#kaifanggm::text' )
        if hdStartTip:
            t = hdStartTip.extract()[0]
            t = re.findall( self.settings[ 'RE_TIME_START' ], t, re.I )
            self.open_time = str(datetime.today().year)
            self.open_time += ( '0' if int(t[0]) < 10 else '' ) + t[0]
            self.open_time += ( '0' if int(t[1]) < 10 else '' ) + t[1]
            print '获取成功: ', self.open_time
        else:
            print '开放时间获取失败'
            return

        print '初始化相关url变量:'
        self.url_referer_check = self.settings[ 'URL_CHECK_REFERER' ] % ( self.open_time )
        print 'url_referer_check: ', self.url_referer_check

        return self.start_loginprepare()

    """请求登录页面，解析出登录所需参数"""
    def start_loginprepare( self ):
        print ''
        print '>>>>>> start_loginprepare: '

        if self.settings[ 'ACCOUNT_NAME' ] == '' or self.settings[ 'ACCOUNT_PWD' ] == '':
            print '帐号、密码未配置，需手动输入:'
            while len( self.account ) == 0:
                self.account = raw_input('帐号：')
            while len( self.password ) == 0:
                # self.password = getpass.getpass('密码：')
                self.password = raw_input('密码：')

        print '发送请求 -> ', self.settings[ 'URL_PASS' ]

        return Request(
                    url = self.settings[ 'URL_PASS' ],
                    method = 'get',
                    callback = self.parse_loginprepare
               )

    """解析出登录所需参数"""
    def parse_loginprepare( self, res ):
        print ''
        print '>>>>>> parse_loginprepare: ', res.url

        if res.url == self.settings[ 'URL_PASS' ]:
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

            return


    """执行登录"""
    def start_login( self, params = {} ):
        print ''
        print '>>>>>> start_login: '

        # 合并登录参数
        # formdata = {
        #     'user': self.account or self.settings[ 'ACCOUNT_NAME' ],
        #     'pwd': self.password or self.settings[ 'ACCOUNT_PWD' ]
        # }.update( params )
        formdata = dict({
            'user': self.account or self.settings[ 'ACCOUNT_NAME' ],
            'pwd': self.password or self.settings[ 'ACCOUNT_PWD' ]
        }, **params )
        
        print '发送数据: '
        print formdata
        print ''

        return FormRequest(
                    url = self.settings[ 'URL_LOGIN' ],
                    formdata = formdata,
                    callback = self.parse_login
                )


    """分析登录结果"""
    def parse_login( self, res ):
        print ''
        print '>>>>>> parse_login: '
        print '最终URL: ', res.url

        if 'redirect_times' in res.meta:
            print '跳转次数: ', res.meta[ 'redirect_times' ]
        if 'redirect_urls' in res.meta:
            print '跳转列表: ', res.meta[ 'redirect_urls' ]

        success = re.match( self.settings[ 'RE_URL_LOGIN_SUCCESS' ], res.url, re.I )
        if success:
            print '登录成功'
            print ''
            print '检查是否已预约:'

            return self.start_subscribe()
            # return self.start_monitor()
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





    def start_subscribe( self ):
        print ''
        print '>>>>>> start_subscribe:'
        
        url = self.settings[ 'URL_SUBSCRIBE' ] % ( self.open_time[:4], self.open_time[4:] )
        print url

        return Request(
                    url = url,
                    method = 'get',
                    headers = {
                        'Referer': self.settings[ 'URL_HOME_RERERER' ]
                    },
                    callback = self.process_subscribe
               )

    def process_subscribe( self, res ):
        print ''
        print '>>>>>> process_subscribe:'
        print res.url

        sel = Selector( res )
        btns = sel.css( '.btnbox li > a' )
        if btns:
            for btn in btns:
                txt = btn.css( '::text' ).extract()[0]
                url = btn.xpath( '@href' ).extract()[0]
                print '按钮 -> %s , %s' % ( txt, url )
                
                if '手机' in txt:
                    url = btn.xpath( '@href' ).extract()[0]
                    print '找到手机预约地址: ', url
                    return Request(
                                url = url,
                                headers = {
                                    'Referer': res.url
                                },
                                dont_filter = True,
                                callback = self.parse_subscribe
                           )

        print '获取手机预约地址失败: ', btns
        return

    def parse_subscribe( self, res ):
        print ''
        print '>>>>>> parse_subscribe:'
        print res.url

        # f = open('a.html', 'w')
        # f.write( res.body )
        # f.close()

        sel = Selector( res )

        # 目前根据是否找到验证码元素，确定是否为提交页面
        # TODO 找时间换成更稳定的方式
        captcha = sel.css( '#img_captcha' )
        if captcha:
            print '确认是预订页了: 目前是检测验证码元素存在与否，后续换更稳定方式~~'

            codeUrl = captcha.xpath( '@src' ).extract()[0]
            print '得到初始验证码地址: ', codeUrl

            print '分析表单数据项:'
            # 参考 http://p.www.xiaomi.com/m/choose/js/reserve.js mergeData

            # 基本项
            formdata = {
                'username': sel.css( '#username' ).xpath( '@value' ).extract()[0],
                'email': sel.css( '#email' ).xpath( '@value' ).extract()[0],
                'mobile': sel.css( '#mobile' ).xpath( '@value' ).extract()[0],
                # TODO 目前仅抢米3，直接写死
                'type': 'miphone',
                'tag3': sel.css( '#s li:first-child' ).xpath( '@data-val' ).extract()[0],
                # TODO 目前仅抢米3，直接写死
                'version': 'K',
                # 下面3个数据值必须为 string, 否则 scrapy 会抛错在 FormRequest 时( unicode_to_str 抛的 )
                'tag2': '0',
                # TODO 目前仅抢米3，写死
                'miphone': '1',
                # TODO 目前仅抢米3，写死
                'mibox': '0',

                # 以下为新增字段，为防黄牛 - -!
                'province': self.settings[ 'ACCOUNT_PROVINCE' ],
                'city': self.settings[ 'ACCOUNT_CITY' ],
                'dis': self.settings[ 'ACCOUNT_DIS' ],
                'edittextarea': self.settings[ 'ACCOUNT_ADDRESS' ].decode( 'utf-8' ),
                'postalcode': self.settings[ 'ACCOUNT_CODE' ]
            }
            
            # 高级项
            formdata[ 'miphone' ] = formdata[ 'tag3' ]

            # 附加项
            # 1. 获取配置段，并解析成JSON
            cfg = re.findall( r'var\s+RE\s+=\s+?{([^}]*)', res.body, re.I )
            if cfg:
                # 转换为JSON
                cfg = cfg[0]
                cfg = cfg.strip().replace( ' ', '' ).replace( '\r\n', '' )
                cfg = cfg.replace( '\r', '' ).replace( '\n', '' )
                cfg = cfg.replace( ',', ',"' )
                cfg = cfg.replace( ':"', '":"' )
                cfg = '{"' + cfg + '}'

                try:
                    cfg = json.loads( cfg )
                except Exception, e:
                    print '解析错误:', e
                    print '原始串:', cfg
                    # open_in_browser( res )
                    return

                cfg[ 'captchaURL' ] = cfg[ 'captchaURL' ] + '/r/%s'
                print '更新验证码生成配置(方便使用): ', cfg[ 'captchaURL' ]

            payloads = re.findall( r'RE\.post\s+=\s+?{([^}]*)', res.body, re.I )
            if payloads:
                # 转换为JSON
                payloads = payloads[0]
                payloads = payloads.strip().replace( ' ', '' ).replace( '\r\n', '' )
                payloads = payloads.replace( '\r', '' ).replace( '\n', '' )
                payloads = payloads.replace( '\'', '' )

                for p in payloads.split( ',' ):
                    d = p.split( ':' )
                    if d[0].startswith( '//' ):
                        pass
                    else:
                        # print d[0], ' -> ', d[1]
                        print '表单数据增加: %s -> %s' % ( d[0], d[1] )
                        formdata[ d[0] ] = d[1]

            # 2. 完善formdata
            formdata[ cfg[ 'captchaName' ] ] = ''

            print '表单数据预分析完成:'
            print formdata

            # codeUrl = cfg[ 'captchaURL' ] % ( random.random() )
            print '准备加载验证码: ', codeUrl
            return Request(
                        url = codeUrl,
                        meta = {
                            'form': {
                                'refer': res.url,
                                'action': cfg[ 'ajaxURL' ],
                                'data': formdata,
                                'code': cfg[ 'captchaName' ],
                                'waitingUrl': cfg[ 'errorURL' ],
                                'codeUrl': cfg[ 'captchaURL' ]
                            }
                        },
                        headers = {
                            'Referer': res.url
                        },
                        callback = self.process_code4subscribe
                    )
        else:
            # 是否绑定手机页
            h6 = sel.css( 'h6::text' )
            if h6:
                # TODO 暂时不支持自动绑定手机
                print 'TODO：', h6.extract()[0]
            else:
                if 'tip_NoYY.html' in res.url:
                    print '忘记预约了吧!!唉~~~没救了，洗洗睡吧...'
                elif 'success' in res.url:
                    print '已经预约过了，直接跳过:'
                    return self.start_monitor()
                else:
                    print 'TODO: 未知错误, 已显示在浏览器窗口中'
                    open_in_browser( res )
        return

    def process_code4subscribe( self, res ):
        print ''
        print '>>>>>> process_code4subscribe:'
        print res.url
        # print res.body

        # 1. 存到本地
        img = open( 'tmp/a.png', 'w' )
        img.write( res.body )
        img.close()
        print '验证码已下载: ', 'tmp/a.png'

        # 2. ASCII显示到控制台
        # TODO ..
        print '暂不支持ASCII显示，自己去tmp目录看吧~~'

        # 3. 中断,等待用户输入
        code = raw_input( '请输入验证码:' )
        print '您输入的:', code

        # 4. 恢复，合并输入请求API
        meta = res.meta
        if 'form' in meta:
            # 更新验证码值
            meta[ 'form' ][ 'data' ][ meta[ 'form' ][ 'code' ] ] = code
            print '更新验证码为您输入的: ', code

        # print 'meta: ', meta

        return self.do_subscribe( meta )

    def do_subscribe( self, meta ):
        print ''
        print '>>>>>> do_subscribe:'
        print 'meta: ', meta

        form = meta[ 'form' ]
        return FormRequest(
                    url = form[ 'action' ],
                    formdata = form[ 'data' ],
                    meta = meta,
                    headers = {
                        'Referer': form[ 'refer' ]
                    },
                    callback = self.parse_dosubscribe
                )

    def parse_dosubscribe( self, res ):
        print ''
        print '>>>>>> parse_dosubscribe:'
        print res.url
        print res.body

        d = None
        try:
            d = json.loads( res.body )
        except Exception, e:
            raise e

        if d and 'info' in d:
            meta = res.meta
            form = {}

            if 'form' in meta:
                form = meta[ 'form' ]

            if d['info'] == 'waitingUrl':
                if 'waitingUrl' in form:
                    # return Request(
                    #         url = form[ 'waitingUrl' ],
                    #         callback = self.start_monitor
                    #     )

                    # TODO 这里暂时不处理后续的2个跳转了，麻烦
                    print '预订成功，这里不在做3秒的跳转了，直接回归主逻辑..'
                    return self.start_monitor()

            elif d[ 'info' ] == 'authcodeError':
                print '验证码输入有误或已过期，准备重新验证'
                print 'JSON解析结果: ', d
                print '响应的meta: ', meta
                
                codeUrl = form[ 'codeUrl' ] % ( random.random() )
                print '准备加载验证码: ', codeUrl
                
                return Request(
                    url = codeUrl,
                    meta = {
                        'form': form
                    },
                    headers = {
                        'Referer': form[ 'refer' ]
                    },
                    callback = self.process_code4subscribe
                )

            elif d[ 'info' ] == 'authcodeErrorUrl':
                print '悲剧被锁了~~验证码输入错误太多,等会再试吧'

            elif d[ 'info' ] == 'captchaErrorURL':
                print '完蛋，输入次数太多了，歇会儿吧~~~'
                print 'TODO, 暂时直接结束，回头用休眠'

            else:
                print '输入信息有错，自己查查吧'
                print 'TODO, 暂时不做那么复杂了，自己查查吧'
                print 'JSON解析结果: ', d
                print '响应的meta: ', meta
        else:
            print '返回格式解析失败:'
            print res.body

        return






    def start_monitor( self ):

        now_time = datetime.today()
        start_time = datetime( now_time.year, now_time.month, now_time.day, 11, 59, 0 )
        while now_time < start_time:
            print '活动开始还有%s，休眠%s秒再检测...' % ( start_time - now_time, self.settings[ 'SLEEP_TIME' ] )
            time.sleep( self.settings[ 'SLEEP_TIME' ] )
            now_time = datetime.today()

        print ''
        print '>>>>>> start_monitor:'


        now_timestamp = int(time.mktime(datetime.now().timetuple())) * 1000
        url = self.settings[ 'URL_CHECK' ] % ( now_timestamp )
        request = Request(
            url = url,
            headers = {
                'Referer': self.url_referer_check
            },
            callback = self.parse_monitor,
            dont_filter = True
        )

        # proxy
        proxy = self.settings[ 'PROXY_LIST' ]
        if proxy and len( proxy ) > 0:
            proxy = random.choice( proxy )
            request.meta[ 'proxy' ] = 'http://%s' % ( proxy )
        else:
            proxy = ''

        print url
        print 'proxy: %s' % ( proxy )
        print ''

        return request

    def parse_monitor( self, res ):
        print ''
        print '>>>>>> parse_monitor:'
        # print res.body
        # print ''

        # 获取&解析 JSON
        d = re.findall( self.settings[ 'RE_CHECK_BODY' ], res.body, re.I )[0]
        if ( d ):
            print d

            try:
                d = json.loads( d )
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
                    return self.start_subscribe()
                elif data['hdstop']:
                    print '活动已结束~~'
                    return
                elif data['hdstart'] == False:
                    print '活动冇开始~~~'
                    return
        else:
            print 'status 或 miphone 字段不存在'

        return self.rob_fail( res )



    


    """抢成功"""
    def rob_success( self, res, data ):
        print ''
        print '抢到一个:', data['hdurl']
        log = open( 'rob.log', 'a' )
        log.write( json.dumps(data) + '\n' )
        log.close()


        url = self.settings[ 'URL_ORDER_WEB'] % ( data['hdurl'] )
        print '跳转到订单页: ', url

        # 跳转到订单页
        return Request(
                    url = url,
                    headers = {
                        'Referer': self.url_referer_check
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


        # 解析生成表单参数并存储到文件
        sel = Selector( res )

        # 先确认是否是订单页，这里可能会出现各种错误页
        url = sel.css('#selectForm::attr(action)')

        # 不是订单页
        if not url:
            # 已经抢过了
            # http://p.www.xiaomi.com/m/opentip/phone/tip_OnlyOne.html?v=201312092209
            url = sel.css( '.tips_wrap' )
            if url:
                print url.css( 'h3::text' ).extract()[0]

            return

        # 确定是订单页，则继续逻辑
        url = url.extract()[0]
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

        print '准备往TIP页跳:', 'http://p.www.xiaomi.com/m/opentip/phone/tip_Wait.html?_a=20131217_phone&_s=e439d0e5040c&v=201312121353'

        return

    """解析生成表单参数"""
    def parse_formdata_order( self, res ):
        print ''
        print '>>>>>> parse_formdata_order:'

        # 过滤出from field数据，供后续解析
        data = re.findall(
            self.settings[ 'RE_FORM_FIELDS_ORDER' ],
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
            self.settings[ 'RE_FORM_FIELD_MID' ],
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
            if re.findall( self.settings[ 'RE_ORDER_DEVICE_SOLDOVER' ], r, re.I ):
                pass
            else:
                device_enable.append(
                    re.findall( self.settings[ 'RE_ORDER_MID_ATTR' ], r, re.I )[0]
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

