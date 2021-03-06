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

class Jin10ArticleSpider(scrapy.Spider):
    name = 'jin10_article'
    allowed_domains = ['news.jin10.com']
    start_urls = ['http://news.jin10.com/']
    crawl_all_page = False

    r = redis.Redis(host="127.0.0.1", port=6379, db=0)
    detail_pages = []
    categories = [
        {
            'id': '4',
            'name': '原油',
            'page_count': 0,
            'page_index': 1
        },
        {
            'id': 'thinktank',
            'name': '午读',
            'page_count': 0,
            'page_index': 1
        },
        {
            'id': '5',
            'name': '贵金属',
            'page_count': 0,
            'page_index': 1
        },
        {
            'id': '7',
            'name': '外汇',
            'page_count': 0,
            'page_index': 1
        },
        {
            'id': '19',
            'name': '行情',
            'page_count': 0,
            'page_index': 1
        },
        {
            'id': '13',
            'name': '独家',
            'page_count': 0,
            'page_index': 1
        },
        {
            'id': 'trading',
            'name': '交易智慧',
            'page_count': 0,
            'page_index': 1
        }
    ]
    cat_index = 0
    base_url = 'https://news.jin10.com/list.html?cate={cat}&p={page}'
    detail_url = 'https://news.jin10.com/details.html?id={id}'
    detail_json_url = 'https://news.jin10.com/datas/details/{id}.json'

    custom_settings = {
        'LOG_FILE': '../logs/jin10_article_{dt}.log'.format(dt=datetime.datetime.now().strftime('%Y%m%d'))
    }

    def __init__(self, *args, **kwargs):
        super(Jin10ArticleSpider, self).__init__(*args, **kwargs)
        if kwargs and "all" in kwargs:
            self.crawl_all_page = bool(kwargs['all'])

    def start_requests(self):
        #保存cookie，同时模拟浏览器访问过程，设置refer
        return [scrapy.Request("https://news.jin10.com/", meta={'cookiejar':self.name}, callback=self.parse_cookie)]

    def parse_cookie(self, response):
        yield scrapy.Request(self.base_url.format(cat=self.categories[self.cat_index]['id'], page=self.categories[self.cat_index]['page_index']),
                                                  meta={'cookiejar': self.name}, callback=self.parse_page)

    def parse_page(self, response):
        yield scrapy.Request("https://news.jin10.com/datas/cate/{cat}/main.json".format(cat=self.categories[self.cat_index]['id']),
                             meta={'cookiejar': self.name}, callback=self.parse_list)

    def parse_list(self, response):
        json_data = json.loads(response.body)
        self.categories[self.cat_index]['page_count'] = int(json_data['totalPage'])
        cat_now = self.categories[self.cat_index]

        list_url = "https://news.jin10.com/datas/cate/{cat}/p{page}.json"
        if not cat_now['id'].isdigit():
            list_url = "https://news.jin10.com/datas/tags/{cat}/p{page}.json"

        yield scrapy.Request(
            list_url.format(cat=cat_now['id'], page=(cat_now['page_count'] + 1 -cat_now['page_index'])),
            meta={'cookiejar': self.name}, callback=self.parse_info)

    def parse_info(self, response):
        json_data = json.loads(response.body)
        print "get list, length is ", len(json_data), " cat is ", self.categories[self.cat_index]['name'].encode('gbk'), "page count ", self.categories[self.cat_index]['page_count'], "page now ", self.categories[self.cat_index]['page_index']
        for dt in json_data:
            if not dt['redirect_url']:
                item = ArticleItem()
                item['title'] = dt['title']
                image = os.path.basename(dt['thumb'])
                image_path = util.downfile(dt['thumb'], image)
                item['image'] = image_path
                item['description'] = dt['desc']
                item['keywords'] = dt['keyword']
                item['publish_time'] = datetime.datetime.strptime(dt['time_show'], "%Y-%m-%d %H:%M:%S")
                item['type'] = self.categories[self.cat_index]['name']
                item['source_url'] = self.detail_json_url.format(id=dt['id'])
                item['source_site'] = 'jin10'
                item['source_id'] = util.get_sourceid(item['source_url'])

                item = {
                    'title': dt['title'],
                    'image': image_path,
                    'description': dt['desc'],
                    'keywords': dt['keyword'],
                    'publish_time': datetime.datetime.strptime(dt['time_show'], "%Y-%m-%d %H:%M:%S"),
                    'type': self.categories[self.cat_index]['name'],
                    'source_url': self.detail_json_url.format(id=dt['id']),
                    'source_site': 'jin10',
                    'source_id': util.get_sourceid(item['source_url'])
                }

                r_id = 'jin10:%s' % dt['id']
                self.r.hmset(r_id, item)
                self.r.sadd('jin10:page', item['source_url'])

                # item_in_redis = self.r.zscore('detail_pages', item['source_url'])
                # if item_in_redis is None:
                #     self.r.zadd('detail_pages', item['source_url'], 0)

                # yield item

        self.categories[self.cat_index]['page_index'] += 1
        cat_now = self.categories[self.cat_index]

        rand = random.randint(3, 7)
        time.sleep(rand)

        if self.crawl_all_page and cat_now['page_index'] <= cat_now['page_count']:
            list_url = "https://news.jin10.com/datas/cate/{cat}/p{page}.json"
            if not cat_now['id'].isdigit():
                list_url = "https://news.jin10.com/datas/tags/{cat}/p{page}.json"
            yield scrapy.Request(
                list_url.format(cat=cat_now['id'], page=(
                cat_now['page_count'] + 1 - cat_now['page_index'])),
                meta={'cookiejar': self.name}, callback=self.parse_info)

        elif self.cat_index < len(self.categories)-1:
            self.cat_index += 1
            cat_now = self.categories[self.cat_index]
            main_url = "https://news.jin10.com/datas/cate/{cat}/main.json"
            if not cat_now['id'].isdigit():
                main_url = "https://news.jin10.com/datas/tags/{cat}/main.json"

            yield scrapy.Request(
                main_url.format(cat=self.categories[self.cat_index]['id']),
                meta={'cookiejar': self.name}, callback=self.parse_list)
        else:
            details_first = self.get_detail_page()
            if details_first:
                yield scrapy.Request(details_first, meta={'cookiejar': self.name}, callback=self.parse_body)

    def get_detail_page(self):
        page = self.r.spop('jin10:page')
        return page

    def parse_body(self, response):
        parser = ArticleParser(response)
        item = parser.parse()

        item_id_pat = re.compile(r"details\/(\d+)\.json")
        item_id = item_id_pat.findall(response.url)[0]
        r_id = 'jin10:%s' % item_id
        item_detail = self.r.hgetall(r_id)

        item['publish_time'] = item_detail['publish_time']
        item['source_site'] = 'jin10'
        item['source_id'] = item_detail['source_id']
        item['title'] = item_detail['title']
        item['image'] = item_detail['image']
        item['type'] = item_detail['type']
        item['keywords'] = item_detail['keywords']
        item['description'] = item_detail['description']
        item['source_url'] = response.url

        yield item

        # rand = random.randint(3, 7)
        # time.sleep(rand)
        details_first = self.get_detail_page()
        if details_first:
            yield scrapy.Request(details_first, meta={'cookiejar': self.name}, callback=self.parse_body)