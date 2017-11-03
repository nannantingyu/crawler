# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
import re
from crawler.util import get_url_param
from crawler.items import CrawlEconomicJieduItem
import redis
import urllib

class CjJieduSpider(scrapy.Spider):
    name = 'fx678_cj_jiedu'
    allowed_domains = ['fx678.com', 'localhost']
    start_urls = ['http://fx678.com/']
    url_format = "http://rl.fx678.com/id/{dataname_id}.html"
    index = 1
    id_x = None
    def __init__(self):
        self.r = redis.Redis(host='127.0.0.1')

    def start_requests(self):
        url = self.next_url()
        return [scrapy.Request(url, meta={"cookiejar": self.name, 'dont_redirect': True},
                callback=self.parse_jiedu)]

    def next_url(self):
        id = self.r.spop("fx678_jiedu")
        url = None

        if id:
            self.id_x = id
            self.r.sadd("fx678_jiedu_ori", id)
            url = self.url_format.format(dataname_id=id)

        return url

    def parse_jiedu(self, response):
        lis = response.xpath("./div[@class='choose_add_1_two']/ul/li")
        item = CrawlEconomicJieduItem()
        item['next_pub_time'] = lis[3].xpath("./text()").extract_first()
        item['pub_agent'] = lis[1].xpath("./text()").extract_first()
        item['pub_frequency'] = lis[2].xpath("./text()").extract_first()
        item['count_way'] = ""
        item['data_influence'] = lis[0].xpath("./text()").extract_first()
        item['data_define'] = response.xpath("./div[@class='choose_add_1_top']")[0].xpath("./text()").extract_first()
        item['funny_read'] = response.xpath("./div[@class='choose_add_1_top']")[1].xpath("./text()").extract_first()
        item['dataname_id'] = self.id_x

        yield item
        print self.index
        self.index += 1

        url = self.next_url()
        if url:
            yield scrapy.Request(url, meta={"cookiejar": self.name, 'dont_redirect': True},
                                   callback=self.parse_jiedu)