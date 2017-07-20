# -*- coding: utf-8 -*-
import scrapy
import json

class TestSpider(scrapy.Spider):
    name = "test"
    allowed_domains = ["localhost"]
    start_urls = ['http://localhost/ajax_wrapper.html']

    def parse(self, response):
        trs = response.xpath("//tr[starts-with(@class, 'int')]")
        for tr in trs:
            id = tr.xpath(".//td[3]/a/@id").extract_first()
            id = id.split("_")[-1]
            title = tr.xpath(".//td[4]/a/text()").extract_first()
            title = title.replace("https://", "").replace("http://", "").strip("/")
            print id, title