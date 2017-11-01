# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
import re
from crawler.util import get_url_param
from crawler.items import CrawlEconomicCalendarItem
from crawler.items import CrawlEconomicEventItem
from crawler.items import CrawlEconomicHolidayItem
import redis
import urllib
from crawler.pipelines.database import SqlReader

class CjJieduSpider(scrapy.Spider):
    name = 'cj_jiedu'
    allowed_domains = ['jin10.com']
    start_urls = ['https://www.jin10.com/']
    url_format = "https://rili.jin10.com/datas/jiedu/{dataid}.json?ori={ori}&source={source}"
    index = 1

    def __init__(self):
        self.reader = SqlReader()
        self.r = redis.Redis(host='127.0.0.1')

    def start_requests(self):
        all = self.reader.read_jiedu()
        for i in all:
            print i[0]
            if not self.r.sismember("jiedu_ori", i[0]):
                self.r.sadd("jiedu", "%s_%s" % i)
                self.r.sadd("jiedu_ori", i[0])

        url = self.next_url()
        return [scrapy.Request(url, meta={"cookiejar": self.name, 'dont_redirect': True},
                callback=self.parse_jiedu)]

    def next_url(self):
        id = self.r.spop("jiedu")
        url = None

        if id:
            id = id.split("_")
            url = self.url_format.format(dataid=id[1], ori=id[0], source=id[1])

        return url

    def parse_jiedu(self, response):
        url = response.url
        params = get_url_param(url)

        data = json.loads(response.body)
        item = CrawlEconomicCalendarItem()
        item['next_pub_time'] = data['publictime']
        item['pub_agent'] = data['institutions']
        item['pub_frequency'] = data['frequency']
        item['count_way'] = data['method']
        item['data_influence'] = data['impact']
        item['data_define'] = data['paraphrase']
        item['funny_read'] = data['focus']
        item['dataname_id'] = params['ori']
        item['source_id'] = params['source']

        yield item
        print self.index
        self.index += 1

        url = self.next_url()
        if url:
            yield scrapy.Request(url, meta={"cookiejar": self.name, 'dont_redirect': True},
                                   callback=self.parse_jiedu)