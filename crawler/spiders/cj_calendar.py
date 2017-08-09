# -*- coding: utf-8 -*-
import scrapy
import datetime
import json
import re
from crawler.util import get_url_param
from crawler.items import CrawlEconomicCalendarItem
from crawler.items import CrawlEconomicEventItem
from crawler.items import CrawlEconomicHolidayItem
import urllib
import logging

class CjCalendarSpider(scrapy.Spider):
    name = "cj-calendar"
    allowed_domains = ["jin10.com"]
    start_urls = ['https://rili.jin10.com/']
    date_now = datetime.datetime.now()
    max_days = None
    after_days = 60
    date_end = None
    all_data = []
    jiedu_index = 0
    jiedu = None

    custom_settings = {
        'LOG_FILE': '../logs/jin10_cj_calendar_{dt}.log'.format(dt=datetime.datetime.now().strftime('%Y%m%d'))
    }

    def __init__(self, *args, **kwargs):
        super(CjCalendarSpider, self).__init__(*args, **kwargs)
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

    def start_requests(self):
        return [scrapy.Request("https://rili.jin10.com/", meta={'cookiejar': self.name},
                               callback=self.parse_cookie)]

    def parse_cookie(self, response):
        yield scrapy.Request('https://ucenter.jin10.com/info?jsonpCallback=jQuery111106577188087567758_1502096954188&_=1502096954189',
                             meta={"cookiejar": response.meta['cookiejar'], 'dont_redirect': True,
                                   'handle_httpstatus_list': [301, 302]}, callback=self.parse_index)

    def parse_index(self, response):
        yield scrapy.Request('https://rili.jin10.com/datas/{year}/{monthday}/economics.json'.format(year=self.date_now.year, monthday=self.date_now.strftime("%m%d")),
                             meta={"cookiejar": response.meta['cookiejar'], 'dont_redirect': True},
                             callback=self.parse_calendar)

    def parse_calendar(self, response):

        data = json.loads(response.body)
        all_data = {}
        all_index = 0
        for dt in data:
            item = CrawlEconomicCalendarItem()
            item['country'] = dt['country']
            item['quota_name'] = dt['title']
            item['pub_time'] = dt['publictime']
            item['importance'] = dt['star']
            item['former_value'] = dt['previous']
            item['predicted_value'] = dt['consensus']
            item['published_value'] = dt['actual']
            item['influence'] = dt['status_name']
            item['source_id'] = dt['dataId']

            self.all_data.append({"dataid":dt['dataId'], 'pub_time':dt['publictime']})
            all_data[all_index] = item
            all_index += 1

        yield all_data
        logging.info("[crawl] " + str(self.date_now.strftime("%Y-%m-%d")))
        with open("../tmp/calendar.log", 'a') as fs:
            fs.write(self.date_now.strftime("%Y-%m-%d") + ": " + str(len(data)) + "\n")

        #抓取财经事件
        yield scrapy.Request("https://rili.jin10.com/datas/{year}/{monthday}/event.json".format(year=self.date_now.year, monthday=self.date_now.strftime("%m%d")),
                             meta={"cookiejar": response.meta['cookiejar'],
                                   'dont_redirect': True},
                             callback=self.parse_event)

    def parse_event(self, response):
        data = json.loads(response.body)
        all_data = {}
        all_index = 0
        time_re = re.compile(r"^\d{2}:\d{2}")
        for dt in data:
            item = CrawlEconomicEventItem()
            dt_time = dt['public_time']
            if len(time_re.findall(dt_time)) > 0:
                dt_time = self.date_now.strftime("%Y-%m-%d {ori}:00".format(ori=dt_time[0]))

            item['time'] = dt_time
            item['country'] = dt['country']
            item['city'] = dt['city']
            item['importance'] = dt['star']
            item['event'] = dt['eventcontent']
            item['date'] = self.date_now

            all_data[all_index] = item
            all_index += 1

        yield all_data

        with open("../tmp/event.log", 'a') as fs:
            fs.write(self.date_now.strftime("%Y-%m-%d") + ": " + str(len(data)) + "\n")

        yield scrapy.Request("https://rili.jin10.com/datas/{year}/{monthday}/holiday.json".format(year=self.date_now.year,
                                                                                                monthday=self.date_now.strftime("%m%d")),
                             meta={"cookiejar": response.meta['cookiejar'],
                                   'dont_redirect': True},
                             callback=self.parse_holiday)

    def parse_holiday(self, response):
        data = json.loads(response.body)
        all_data = {}
        all_index = 0
        for dt in data:
            item = CrawlEconomicHolidayItem()
            item['time'] = dt['date'][0:10]
            item['country'] = dt['country']
            item['market'] = dt['exchangename']
            item['holiday_name'] = dt['holidayname']
            item['detail'] = dt['note']
            item['date'] = self.date_now.strftime("%Y-%m-%d")

            all_data[all_index] = item
            all_index += 1

        yield all_data

        with open("../tmp/holiday.log", 'a') as fs:
            fs.write(self.date_now.strftime("%Y-%m-%d") + ": " + str(len(data)) + "\n")

        dtadd = datetime.timedelta(days=1)
        self.date_now = self.date_now + dtadd

        if self.date_now < self.date_end:
            yield scrapy.Request(
                'https://rili.jin10.com/datas/{year}/{monthday}/economics.json'.format(year=self.date_now.year,
                                                                                       monthday=self.date_now.strftime(
                                                                                           "%m%d")),
                meta={"cookiejar": response.meta['cookiejar'],
                      'dont_redirect': True},
                callback=self.parse_calendar)
        elif len(self.all_data) > 0 and self.jiedu is not None:
            # now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # for i in range(0, len(self.all_data)):
            #     if self.all_data[i]['pub_time'] < now:
            #         self.jiedu_index += 1

            if self.jiedu_index < len(self.all_data):
                dataid = self.all_data[self.jiedu_index]['dataid']
                pub_time = self.all_data[self.jiedu_index]['pub_time']
                yield scrapy.Request(
                    'https://rili.jin10.com/datas/jiedu/{dataid}.json?pubtime={pubtime}'.format(dataid=dataid,
                                                                                                pubtime=pub_time),
                    meta={"cookiejar": response.meta['cookiejar'], 'dont_redirect': True},
                    callback=self.parse_jiedu)

    def parse_jiedu(self, response):
        url = response.url
        dataid_re = re.compile(r"jiedu\/(\d+)\.")
        dataid = dataid_re.findall(url)[-1]
        params = get_url_param(url)
        pubtime = urllib.unquote(params['pubtime'])

        with open("../tmp/calendar-jiedu.log", 'a') as fs:
            fs.write(dataid + ": " + str(response.body) + "\n")

        data = json.loads(response.body)
        item = CrawlEconomicCalendarItem()
        item['next_pub_time'] = data['publictime']
        item['pub_time'] = pubtime
        item['pub_agent'] = data['institutions']
        item['pub_frequency'] = data['frequency']
        item['count_way'] = data['method']
        item['data_influence'] = data['impact']
        item['data_define'] = data['paraphrase']
        item['funny_read'] = data['focus']
        item['source_id'] = dataid

        yield {0:item}

        self.jiedu_index += 1
        if self.jiedu_index < len(self.all_data):
            dataid = self.all_data[self.jiedu_index]['dataid']
            pub_time = self.all_data[self.jiedu_index]['pub_time']
            yield scrapy.Request(
                'https://rili.jin10.com/datas/jiedu/{dataid}.json?pubtime={pubtime}'.format(dataid=dataid,
                                                                                            pubtime=pub_time),
                meta={"cookiejar": response.meta['cookiejar'], 'dont_redirect': True},
                callback=self.parse_jiedu)



