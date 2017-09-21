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
from crawler.util import handle_body, img_downloader
from crawler.items import ArticleItem
from scrapy.selector import Selector

class WeiboArticleDetailSpider(scrapy.Spider):
    name = 'weibo_article_detail'
    cookie_name = 'weibo'
    allowed_domains = ['weibo.com']
    start_urls = ['http://weibo.com/']

    custom_settings = {
        'LOG_FILE': '../logs/weibo_detail_{dt}.log'.format(dt=datetime.datetime.now().strftime('%Y%m%d'))
    }

    r = redis.Redis(host="127.0.0.1", port=6379, db=0)

    def get_detail_page(self):
        detail_first = self.r.zrangebyscore("weibo_detai_url", 0, 0, withscores=True)
        next_url = None
        if len(detail_first) > 0 and int(detail_first[0][1]) == 0:
            next_url = detail_first[0][0]

        # return next_url
        return "http://weibo.com/ttarticle/p/show?id=2309404148391708868967&mod=zwenzhang"

    def start_requests(self):
        # 保存cookie，同时模拟浏览器访问过程，设置refer
        next_url = self.get_detail_page()
        if next_url is not None:
            return [scrapy.Request(next_url,
                               meta={'cookiejar': self.cookie_name, 'handle_httpstatus_list': [301, 302]}, callback=self.parse_detail)]

    def parse_detail(self, response):
        description = response.xpath(".//div[@class='preface']/text()").extract_first()
        body = response.xpath(".//div[@class='WB_editor_iframe']").extract_first()

        print response.url
        print response.headers
        with open("detail.html", "w") as fs:
            fs.write(response.body)

        if body:
            source_id = get_sourceid(response.url)
            item = ArticleItem()
            item['source_id'] = source_id
            item['body'] = handle_body(body)
            item['description'] = description

            yield item
            print item

        self.r.zadd("weibo_detai_url", response.url, 1)
        next_url = self.get_detail_page()
        if next_url is not None:
            yield scrapy.Request(next_url,
                                   meta={'cookiejar': self.cookie_name, 'handle_httpstatus_list': [301, 302]},
                                   callback=self.parse_detail)