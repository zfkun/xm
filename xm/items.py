#!/usr/bin/python
#-*-coding:utf-8-*-

from scrapy.item import Item, Field

class ProxyItem( Item ):
    ip = Field()
    port = Field()
    country = Field()
    anonymity = Field()
    https = Field()