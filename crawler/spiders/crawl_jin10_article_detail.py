# -*- coding: utf-8 -*-
import scrapy
import datetime
import crawler.util as util
import json
from crawler.items import ArticleItem
import redis
from crawler.spiders.articel_parse import ArticleParser, get_sourceid
import random
import time
import os
import re


class CrawlJin10ArticleDetailSpider(scrapy.Spider):
    name = 'crawl_jin10_article_detail'
    allowed_domains = ['news.jin10.com']
    start_urls = ['http://www.jin10.com/']
    r = redis.Redis(host="127.0.0.1", port=6379, db=0)

    custom_settings = {
        'LOG_FILE': '../logs/jin10_article_detail_{dt}.log'.format(dt=datetime.datetime.now().strftime('%Y%m%d'))
    }

    def start_requests(self):
        #保存cookie，同时模拟浏览器访问过程，设置refer
        details_first = self.r.zrange('detail_pages', 0, 1, withscores=True)
        if len(details_first) > 0 and int(details_first[0][1]) == 0:
            yield scrapy.Request(details_first[0][0], meta={'cookiejar': self.name}, callback=self.parse_body)

    def parse_body(self, response):
        self.r.zadd('detail_pages', response.url, 1)
        parser = ArticleParser(response)
        item = parser.parse()
        yield item

        id_reg = re.compile(r"details\/(\d+)\.json")
        id = id_reg.findall(response.url)
        id = id[0]
        yaml_file = "../yaml/{id}.md".format(id=id)
        try:
            with open(yaml_file, "a+") as fs:
                fs.write("\n{body}".format(body=item['body']))
        except Exception as e:
            print e

        rand = random.randint(3, 7)
        print response.url, "sleep ", rand
        time.sleep(rand)
        details_first = self.r.zrange('detail_pages', 0, 0, withscores=True)
        if len(details_first) > 0 and int(details_first[0][1]) == 0:
            yield scrapy.Request(details_first[0][0], meta={'cookiejar': self.name}, callback=self.parse_body)