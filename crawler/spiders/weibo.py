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
from crawler.items import ArticleItem
from scrapy.selector import Selector

class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.com']
    start_urls = ['http://weibo.com/']

    custom_settings = {
        'LOG_FILE': '../logs/weibo_{dt}.log'.format(dt=datetime.datetime.now().strftime('%Y%m%d'))
    }

    r = redis.Redis(host="127.0.0.1", port=6379, db=0)
    # base_url = "http://weibo.com/p/1005051961271625/wenzhang?cfs=600&Pl_Core_ArticleList__62_filter=&Pl_Core_ArticleList__62_page={page}#Pl_Core_ArticleList__62"
    base_url = "http://weibo.com/p/1002061684012053/wenzhang?cfs=600&Pl_Core_ArticleList__46_filter=&Pl_Core_ArticleList__46_page={page}#Pl_Core_ArticleList__46"
    page_now = 1
    page_total = 0

    def start_requests(self):
        # 保存cookie，同时模拟浏览器访问过程，设置refer
        return [scrapy.Request("https://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&url=http%3A%2F%2Fweibo.com%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.23&_rand=1504681177.4204",
                               meta={'cookiejar': self.name, 'handle_httpstatus_list': [301, 302]}, callback=self.parse_cookie)]

    def parse_cookie(self, response):
        with open("weibo.html", "w") as fs:
            fs.write(response.body)

        yield scrapy.Request("https://passport.weibo.com/visitor/visitor?a=incarnate&t=ozD4QaZDtghqkBlmJyBrr9BAhFtSZHzidvH18aseoYI%3D&w=2&c=095&gc=&cb=cross_domain&from=weibo&_rand=0.7829101177189541",
                             meta={'cookiejar': self.name, 'handle_httpstatus_list': [301, 302]},
                             callback=self.parse_redirect)

    def parse_redirect(self, response):
        with open("weibo2.html", "w") as fs:
            fs.write(response.body)

        yield scrapy.Request(self.base_url.format(page=self.page_now),
                             meta={'cookiejar': self.name, 'handle_httpstatus_list': [301, 302]}, callback=self.parse_page)

    def parse_page(self, response):
        script = response.xpath(".//script")

        if len(script) > 0:
            script_html = script[-1].xpath("text()").extract_first()
            html_re = re.compile(r"html\":\"(.*)\"\}")
            html = html_re.findall(script_html)
            if len(html) > 0:
                html = html[0].replace(r"\r", "").replace(r"\t", "").replace(r"\n", "").replace(r"\/", "/").replace(r"\"", "\"")
                with open("weibo_{p}.html".format(p=self.page_now), "w") as fs:
                    fs.write(html)


                st = Selector(text=html, type='html')

                if self.page_total == 0:
                    page = st.xpath(".//div[@class='W_pages']//a[@class='page S_txt1']")
                    if len(page) > 0:
                        page = page[-1].xpath("text()").extract_first()
                        if page is not None and str(page).isdigit():
                            self.page_total = int(page)

                lis = st.xpath(".//ul[@class='pt_ul clearfix']/li[@class='pt_li']")
                for li in lis:
                    image = li.xpath(".//div[@class='pic_box']/a/img/@src").extract_first()
                    info = li.xpath(".//div[@class='info_box S_bg1']")
                    text = info.xpath(".//div[@class='text_box']//div[@class='title W_autocut']/a")
                    title = text.xpath("text()").extract_first()
                    source_url = text.xpath("@href").extract_first()
                    if source_url is not None and "http" not in str(source_url):
                        source_url = "http://weibo.com{url}".format(url=source_url.strip())

                    title = title.strip() if title is not None else ""

                    publish_time = li.xpath(".//div[@class='subinfo_box']/span[@class='subinfo S_txt2']/text()").extract_first()
                    if publish_time is not None:
                        publish_time = datetime.datetime.strptime(publish_time, "%Y 年 %m 月 %d 日 %H:%M")


                    item = ArticleItem()
                    item['image'] = image
                    item['title'] = title
                    item['source_url'] = source_url
                    item['publish_time'] = publish_time
                    item['source_id'] = get_sourceid(source_url)
                    item['source_site'] = "weibo"

                    if not self.r.zscore("weibo_detai_url", source_url):
                        self.r.zadd("weibo_detai_url", source_url, 0)
                    yield item

        sleep_time = random.randint(1, 5)
        time.sleep(sleep_time)

        self.page_now += 1
        print "page now: ", self.page_now
        if self.page_now <= self.page_total:
            yield scrapy.Request(self.base_url.format(page=self.page_now),
                                 meta={'cookiejar': self.name, 'handle_httpstatus_list': [301, 302]},
                                 callback=self.parse_page)