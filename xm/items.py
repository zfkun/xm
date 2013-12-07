#!/usr/bin/python
#-*-coding:utf-8-*-

from scrapy.item import Item, Field

class LoginFormDataItem(Item):
	user = Field()
	pwd = Field()
    # callback = Field()
    # sid = Field()
    # qs = Field()
    # _sign = Field()
