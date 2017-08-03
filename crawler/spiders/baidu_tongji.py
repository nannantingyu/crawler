# -*- coding: utf-8 -*-
import scrapy
import random
import sys
from PIL import Image
import pytesseract
import logging
reload(sys)
from crawler.util import *
import urllib
import time
import datetime
import json
sys.setdefaultencoding('utf8')
from crawler.items import BaiduTongjiItem
from crawler.pipelines.database import SqlReader
pytesseract.pytesseract.tesseract_cmd = 'E:\\Tool\\Python\\Lib\\site-packages\\pytesser\\tesseract.exe'

class BaiduTongjiSpider(scrapy.Spider):
    name = "baidu-tongji"
    allowed_domains = ["baidu.com"]
    handle_httpstatus_list = [404, 500, 302, 301]
    start_urls = ['http://tongji.baidu.com/']
    login_url = 'https://cas.baidu.com/?action=login'
    verify_url = 'http://cas.baidu.com/?action=image&key={rand}'
    page_now = 1
    max_page = 51
    formdata = {
        "siteId": "7802984",
        "order": "start_time,desc",
        "offset": "0",
        "pageSize": "100",
        "tab": "visit",
        "timeSpan": "14",
        "indicators": "start_time,area,source,access_page,searchword,visitorId,ip,visit_time,visit_pages",
        "reportId": "4",
        "method": "trend/latest/a",
        "queryId": ""
    }
    lastest_access_time = None

    def start_requests(self):
        sql_reader = SqlReader()
        data = sql_reader.read_baidutongji_latest_time()
        if len(data) > 0:
            self.lastest_access_time = datetime.datetime.strftime(data[0][0], "%Y/%m/%d %H:%I:%S")

        # 看用既有的cookie能否成功登录
        return [scrapy.Request("https://tongji.baidu.com/web/24229627/trend/latest?siteId=8918649", meta={'cookiejar': self.name},
                               callback=self.checkState)]

    def checkState(self, response):
        if response.status == 302:
            verify_url = self.verify_url.format(rand=random.randint(1500000000, 1511111111))
            yield scrapy.Request(verify_url, meta={'cookiejar': response.meta['cookiejar']}, callback=self.check_verify)
        else:
            yield scrapy.FormRequest(url="https://tongji.baidu.com/web/24229627/ajax/post",
                                     meta={'cookiejar': self.name},
                                     formdata=self.formdata,
                                     callback=self.parseData)

    def check_verify(self, response):
        verify_img = "verify.jpg"
        with open(verify_img, "wb") as fs:
            fs.write(response.body)

        verify_code = parse_verify(verify_img)
        if verify_code and len(verify_code) == 4:
            form_data = {
                "entered_login": "18513788638",
                "entered_password": "Jj8@ops...",
                "appid": "12",
                "entered_imagecode": verify_code,
                "charset": "utf-8",
                "fromu": "https://tongji.baidu.com/web/24229627/trend/latest?siteId=8918649",
                "selfu": "https://tongji.baidu.com/web/welcome/login",
                "senderr": "1"
            }

            yield scrapy.FormRequest(
                url=self.login_url,
                formdata=form_data,
                meta={"cookiejar": response.meta['cookiejar'], 'dont_redirect': True, 'handle_httpstatus_list': [301, 302]},
                callback=self.login
            )
        else:
            verify_url = self.verify_url.format(rand=random.randint(1500000000, 1511111111))
            yield scrapy.Request(verify_url, meta={'cookiejar': response.meta['cookiejar']}, callback=self.check_verify)

    def login(self, response):
        login_back = response.xpath("//script").re(r'var\surl="(.+)";')
        if login_back and len(login_back) > 0:
            login_back = urllib.unquote(str(login_back[0])).decode("utf-8")

            params = get_url_param(login_back)
            if 'errno' in params and params['errno'] == '131':
                logging.info("[crawl baidu] verify code error!")
                time.sleep(5)
                verify_url = self.verify_url.format(rand=random.randint(1500000000, 1511111111))
                yield scrapy.Request(verify_url, meta={'cookiejar': response.meta['cookiejar']}, callback=self.check_verify)
            else:
                yield scrapy.Request(login_back,
                                     meta={'cookiejar': response.meta['cookiejar'],
                                           'dont_redirect': True,
                                           'handle_httpstatus_list': [301, 302]},
                                     callback=self.parse_check)

    def parse_check(self, response):
        if "Location" in response.headers:
            yield scrapy.Request(response.headers['Location'],
                                 meta={'cookiejar': response.meta['cookiejar'],
                                       'dont_redirect': True,
                                       'handle_httpstatus_list': [301, 302]},
                                 callback=self.parse_loginback)

    def parse_loginback(self, response):
        yield scrapy.Request("https://tongji.baidu.com/web/24229627/homepage/index",
                             meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_visit)

    def parse_visit(self, response):
        yield scrapy.FormRequest(url="https://tongji.baidu.com/web/24229627/ajax/post",
                                   meta={'cookiejar': self.name},
                                   formdata=self.formdata,
                                   callback=self.parseData)

    def parseData(self, response):
        with open("data.json", "w") as fb:
            fb.write(response.body)

        print "crawl page ", self.page_now
        json_data = json.loads(response.body)
        data = json_data['data']
        for index,item in enumerate(data['items'][0]):
            for jindex, subitem in enumerate(item):
                item = BaiduTongjiItem()
                detail = subitem['detail']
                sub_detail = data['items'][1][index]

                item['visitorType'] = detail['visitorType']
                item['visitorFrequency'] = detail['visitorFrequency']
                item['lastVisitTime'] = detail['lastVisitTime']
                item['endPage'] = detail['endPage']
                item['deviceType'] = detail['deviceType']
                item['fromType'] = detail['fromType']['fromType'] if 'fromType' in detail['fromType'] else ""
                item['fromurl'] = detail['fromType']['url'] if 'url' in detail['fromType'] else ""
                item['fromAccount'] = detail['fromType']['fromAccount'] if 'fromAccount' in detail['fromType'] else ""
                item['isp'] = detail['isp']
                item['os'] = detail['os']
                item['osType'] = detail['osType']
                item['browser'] = detail['browser']
                item['browserType'] = detail['browserType']
                item['language'] = detail['language']
                item['resolution'] = detail['resolution']
                item['color'] = detail['color']
                item['accessPage'] = detail['accessPage']
                item['antiCode'] = detail['antiCode']

                item['visit_pages'] = sub_detail[8]
                item['access_time'] = sub_detail[0]
                item['user_id'] = sub_detail[6]
                item['visit_time'] = sub_detail[7]
                item['area'] = sub_detail[1]
                item['keywords'] = sub_detail[3]
                item['entry_page'] = sub_detail[4]
                item['ip'] = sub_detail[5]

                yield item

        new_time = data['items'][1][0][0]

        self.page_now += 1
        if self.page_now < self.max_page and (self.lastest_access_time is None or new_time > self.lastest_access_time):
            self.formdata['offset'] = str((self.page_now - 1) * 100)
            yield scrapy.FormRequest(url="https://tongji.baidu.com/web/24229627/ajax/post",
                                   meta={'cookiejar': self.name},
                                   formdata=self.formdata,
                                   callback=self.parseData)



def parse_verify(name):
    threshold = 140
    letter_range = [chr(c) for c in range(ord('A'), ord('Z')+1)]
    letter_range.extend([chr(c) for c in range(ord('0'), ord('9')+1)])
    while threshold > 100:
        table = image_split(threshold)
        im = Image.open(name)
        imgry = im.convert('L')
        imgry.save('g' + name)
        out = imgry.point(table, '1')
        out.save('b' + name)
        text = pytesseract.image_to_string(out)
        text = text.strip()
        text = text.upper()

        passed = True
        if len(text) != 4:
            passed = False
        else:
            for c in text:
                if c not in letter_range:
                    passed = False
                    break

        if passed:
            return text
        else:
            threshold -= 1

def image_split(threshold):
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    return table