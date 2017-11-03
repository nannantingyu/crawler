# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
import re
from crawler.util import get_url_param, get_sourceid
from crawler.items import CrawlFx678EconomicCalendarItem
from crawler.items import CrawlEconomicEventItem
from crawler.items import CrawlEconomicHolidayItem
from crawler.items import CrawlEconomicJieduItem
import redis
import urllib
import logging

class CjFx678Spider(scrapy.Spider):
    name = 'cj_fx678'
    allowed_domains = ['fx678.com', 'localhost']
    start_urls = ['http://fx678.com/']
    date_now = datetime.datetime.now()

    custom_settings = {
        'LOG_FILE': '../logs/fx678_cj_calendar_{dt}.log'.format(dt=datetime.datetime.now().strftime('%Y%m%d'))
    }

    handle_httpstatus_list = [404, 500, 302, 301]
    r = redis.Redis(host="127.0.0.1", port=6379, db=0)

    country_maps = {
        'c_usa': '美国',
        'c_korea_south': '韩国',
        'c_australia': '澳大利亚',
        'c_china': '中国',
        'c_indea': '印度',
        'c_uk': '英国',
        'c_canada': '加拿大',
        'c_japan': '日本',
        'c_switzerland': '瑞士',
        'c_spain': '西班牙',
        'c_italy': '意大利',
        'c_france': '法国',
        'c_germany': '德国',
        'c_european_union': '欧元区',
        'c_russia': '俄罗斯',
        'c_new_zealand': '新西兰'
    }

    url_format = "http://rl.fx678.com/date/{dt}.html"
    # url_format = "http://localhost/fx678.html?a={dt}"

    def __init__(self, *args, **kwargs):
        super(CjFx678Spider, self).__init__(*args, **kwargs)
        if 'args' in kwargs:
            params = {x[0]:x[1] for x in [[l for l in m.split(":")] for m in kwargs['args'].split(",")]}

            if "start" in params:
                try:
                    date_start = datetime.datetime.strptime(params['start'], "%Y-%m-%d")
                    self.date_now = date_start
                except ValueError as error:
                    print params['start'] + ' 不是正确格式的时间，已默认从今天开始抓取'

            if "max" in params:
                try:
                    self.max_days = int(params['max'])
                except ValueError as err:
                    print params['max'] + ' 不是正确的抓取天数，已默认抓取全部数据'

            if "after" in params:
                try:
                    self.after_days = int(params['after'])
                except ValueError as err:
                    print params['after'] + ' 不是正确的向后抓取天数，已默认抓取今天之后60天的数据'

            if "jiedu" in params:
                self.jiedu = params['jiedu']

            if self.max_days is not None:
                date_diff = datetime.timedelta(days=int(self.max_days))
                self.date_end = self.date_now + date_diff
            else:
                date_diff = datetime.timedelta(days=int(self.after_days))
                self.date_end = datetime.datetime.now() + date_diff

    def get_next_url(self):
        return self.url_format.format(dt=self.date_now.strftime("%Y%m%d"))

    def start_requests(self):
        url = self.get_next_url()
        return [scrapy.Request(url, meta={'cookiejar': self.name},
                               callback=self.parse_page)]

    def parse_page(self, response):
        print 'crawl ' + self.date_now.strftime('%Y-%m-%d'), response.status
        trs = response.xpath('//table[@id="current_data"]//tr')[2:-1]

        pre_time = None
        prev_country = None

        items = {}
        item_index = 0

        sourcesid = []
        for tr in trs:
            _cls = tr.xpath("@class").extract_first()
            if _cls in ['unpublished']:
                continue

            tds = tr.xpath('./td')
            td_start = 0
            if len(tds) == 10:
                td_start = 2
                td_stime = tds[0].xpath('./text()').extract_first()
                pre_time = td_stime.strip()

                td_country = tds[1].xpath('.//div[contains(@class,"circle_flag")]/@class').extract_first()
                prev_country = td_country.replace(" circle_flag", "")

                if prev_country in self.country_maps:
                    prev_country = self.country_maps[prev_country]

            quota_name = tds[td_start].xpath('./a/text()').extract_first()
            check_countrys = ['香港特区', '台湾地区']
            if prev_country == 'c_null_flags':
                for c in check_countrys:
                    if c in quota_name:
                        prev_country = c
                        break


            dataname_pat = re.compile(r"截至\d+月\d+日|第.*季度|\d+月|\d+\-\d+月".encode('utf-8'))
            dataname_date = quota_name.replace(prev_country, "").encode('utf-8')
            datename = dataname_pat.findall(dataname_date)
            datename = datename[0] if len(datename) > 0 else ""
            dataname = dataname_date.replace(datename, "")

            unit_pat = re.compile(r'\((.*)\)')
            unit = unit_pat.findall(dataname)
            unit = unit[0] if len(unit) > 0 else ''
            dataname = dataname.replace("("+unit+")", "")

            former_value = self._strip(tds[td_start + 1].xpath("./text()").extract_first())
            predicted_value = self._strip(tds[td_start + 2].xpath("./text()").extract_first())
            published_value = self._strip(tds[td_start + 3].xpath("./text()").extract_first())
            published_value = published_value if published_value != '' else None

            importance = self._strip(tds[td_start + 4].xpath("./text()").extract_first())
            importance = 4 if importance == '高' else 2

            positions = tds[td_start + 5].xpath("./div[@class='currency']")
            position = []
            for pos in positions:
                pos_name = pos.xpath("./p/text()").extract_first()
                pos_size = pos.xpath("./div[@class='progress']/span/@style").re(r"\d+")[0]
                position.append("%s(%s:%d)" % (pos_name, pos_size, 100 - int(pos_size)))

            position = "\n".join(position)

            influence_liduo = tds[td_start + 6].xpath(".//ul[@class='red_get']/li/text()").extract()
            influence_likong = tds[td_start + 6].xpath(".//ul[@class='green_get']/li/text()").extract()
            influence = ''

            if len(influence_liduo) > 0:
                influence_liduo = influence_liduo[3:]
                influence += '利多' + (",".join([self._strip(x) for x in influence_liduo]))
            if len(influence_likong) > 0:
                influence_likong = influence_likong[3:]
                influence = influence + '\n' if influence else influence
                influence += '利空' + (",".join([self._strip(x) for x in influence_likong]))

            dataname_id = tds[td_start + 7].xpath("./a/@href").re(r"id\/(\d+)\.")
            dataname_id = dataname_id[0] if len(dataname_id) > 0 else ''

            # print pre_time, prev_country.encode('gbk'), quota_name.encode('gbk'), datename.encode('gbk'), \
            #     dataname.encode('gbk'), former_value, predicted_value, published_value, importance, \
            #     influence.encode('gbk'), position.encode('gbk'), dataname_id, unit

            item = CrawlFx678EconomicCalendarItem()
            item['country'] = prev_country
            item['quota_name'] = quota_name
            item['pub_time'] = self.date_now.strftime("%Y-%m-%d ") + pre_time + ":00"
            item['importance'] = importance
            item['former_value'] = former_value
            item['predicted_value'] = predicted_value
            item['published_value'] = published_value
            item['influence'] = influence
            item['dataname'] = dataname
            item['datename'] = datename
            item['position'] = position
            item['dataname_id'] = dataname_id
            item['unit'] = unit
            item['source_id'] = get_sourceid(item['pub_time'] + item['dataname_id'])

            items[item_index] = item
            item_index += 1

            self.r.sadd("fx678_jiedu", "%s" % item['dataname_id'])

            sourcesid.append(item['source_id'])

        yield items

        print len(response.xpath(".//table[@class='cjsj_tab2']"))
        tb_event = response.xpath(".//table[@class='cjsj_tab2']")[1]
        trs_event = tb_event.xpath(".//tr")
        items_event = {}
        item_index = 0
        time_re = re.compile(r"^\d{2}:\d{2}")
        for tr in trs_event[1:-1]:
            tds_event = tr.xpath("./td")

            stime = tds_event[0].xpath("./text()").extract_first()
            if len(time_re.findall(stime)) > 0:
                stime = self.date_now.strftime("%Y-%m-%d {ori}:00".format(ori=stime))

            country = tds_event[1].xpath("./div[@class='flag_bb']/span/text()").extract_first()
            address = tds_event[2].xpath("./text()").extract_first()
            importance = tds_event[3].xpath("./img/@src").re(r"star_(\d+)")
            importance = importance[0]

            event = tds_event[4].xpath("./text()").extract_first()

            item = CrawlEconomicEventItem()
            item['time'] = stime
            item['country'] = country
            item['city'] = address
            item['importance'] = importance
            item['event'] = event
            item['date'] = self.date_now
            item['source_id'] = get_sourceid(item['time'] + item['country'] + item['city'])

            items_event[item_index] = item
            item_index += 1

        yield items_event

        tb_holiday = response.xpath(".//table[@class='cjsj_tab2']")[0]
        trs_holiday = tb_holiday.xpath(".//tr")
        items_holiday = {}
        item_index = 0
        time_re = re.compile(r"^\d{2}:\d{2}")
        for tr in trs_holiday[1:]:
            tds_holiday = tr.xpath("./td")

            stime = tds_holiday[0].xpath("./text()").extract_first()
            if len(time_re.findall(stime)) > 0:
                stime = self.date_now.strftime("%Y-%m-%d {ori}:00".format(ori=stime))

            country = tds_holiday[1].xpath("./div[@class='flag_bb']/span/text()").extract_first()
            address = tds_holiday[2].xpath("./text()").extract_first()
            event = tds_holiday[3].xpath("./text()").extract_first()
            holiday_name = event.split("，")[0]
            detail = event.split("，")[1]

            item = CrawlEconomicHolidayItem()
            item['time'] = stime
            item['country'] = country
            item['market'] = address
            item['holiday_name'] = holiday_name
            item['detail'] = detail
            item['date'] = self.date_now
            item['source_id'] = get_sourceid(item['time'] + item['market'] + item['holiday_name'])

            items_holiday[item_index] = item
            item_index += 1

        yield items_holiday

        self.date_now = self.date_now + datetime.timedelta(days=1)
        if self.date_now < self.date_end:
            url = self.get_next_url()
            yield scrapy.Request(url, meta={'cookiejar': self.name},
                                   callback=self.parse_page)

    def _strip(self, string):
        return str(string).strip() if string is not None else None