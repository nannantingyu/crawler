# -*- coding: utf-8 -*-
import scrapy
import json
import crawler.items as items
import sys
import datetime
import logging
reload(sys)
sys.setdefaultencoding('utf8')
import crawler.util as util
from scrapy.http.cookies import CookieJar
import Cookie

class JiankongbaoSpider(scrapy.Spider):
    handle_httpstatus_list = [404, 500]
    name = "jiankongbao"
    allowed_domains = ["jiankongbao.com"]
    start_urls = ['https://qiye.jiankongbao.com/']
    site_maps = {}
    index = 0
    list_page = 0
    list_url = "https://qiye.jiankongbao.com/ajax_wrapper.php?command=get_task_list_page&type=&owner=&priority=&class_id=&status=&temp=task_list_main&page={page}&s=&domain_id=&period=today&range={now},{now}&m_page=undefined&ent_node_id=&search_status=&cache=71014"
    crawl_site = ["www.91pme.com", "m.91pme.com"]
    start_time = None

    def __init__(self, category=None, *args, **kwargs):
        super(JiankongbaoSpider, self).__init__(*args, **kwargs)
        if kwargs:
            sites = str(kwargs['sites']).split(",")
            if sites and len(sites) > 0:
                self.crawl_site = sites

    def start_requests(self):
        form_data = {
            "email": "yangmingming@91guoxin.com",
            "pwd": "1qaz2wsx",
            "remember_me": "1",
            "referer": "",
        }

        self.start_time = datetime.datetime.now()
        return [scrapy.FormRequest(
            url="https://qiye.jiankongbao.com/jkb/account_dispose/signin/s",
            formdata=form_data,
            meta={"cookiejar": 1},
            cookies={"page_rows": 50},
            callback=self.loged_in
        )]

    def loged_in(self, response):
        logging.info("[crawl site] " + self.list_url.format(page=1, now=datetime.datetime.now().strftime("%Y-%m-%d")))
        yield scrapy.Request(
            self.list_url.format(page=1, now=datetime.datetime.now().strftime("%Y-%m-%d")),
            meta={'cookiejar': response.meta['cookiejar']}, cookies={"page_rows":50}, callback=self.parse_list)

    def parse_list(self, response):
        if self.list_page == 0:
            pages = response.xpath("//div[@class='pages']/a/text()").extract()
            self.list_page = pages[-1] if len(pages) > 0 else 0

        trs = response.xpath("//tr[starts-with(@class, 'int')]")
        for tr in trs:
            id = tr.xpath(".//td[3]/a/@id").extract_first()
            id = id.split("_")[-1]
            title = tr.xpath(".//td[4]/a/text()").extract_first()
            title = title.replace("https://", "").replace("http://", "").strip("/")
            #只抓取要抓的站点
            logging.info("[get site] " + title)
            if title in self.crawl_site:
                self.site_maps[id] = title

        logging.info("[crawl site] " + 'https://qiye.jiankongbao.com/task_report_ajax.php?task_id={id}&sel_action=avail&is_world=china'.format(id=self.site_maps.keys()[self.index]))
        yield scrapy.Request(
            'https://qiye.jiankongbao.com/task_report_ajax.php?task_id={id}&sel_action=avail&is_world=china'.format(id=self.site_maps.keys()[self.index]),
            meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_rate)

    def parse_rate(self, response):
        result = json.loads(response.body)

        error_time_top = result['error_time_top']
        error_time_list = {}
        error_time_index = 0
        for line in error_time_top:
            error_time_top_item = items.ErrorTopItem()
            error_time_top_item['monitor_name'] = line['time']
            error_time_top_item['type'] = 'rate';
            error_time_top_item['value'] = line[u'故障时间']
            error_time_top_item['site'] = self.site_maps.values()[self.index]
            error_time_top_item['day'] = self.start_time
            error_time_list[error_time_index] = error_time_top_item
            error_time_index += 1
        yield error_time_list

        error_count_list = {}
        error_count_index = 0
        error_count_top = result['error_count_top']
        for line in error_count_top:
            error_count_top_item = items.ErrorTopItem()
            error_count_top_item['monitor_name'] = line['time']
            error_count_top_item['type'] = 'count'
            error_count_top_item['value'] = line[u'故障次数']
            error_count_top_item['site'] = self.site_maps.values()[self.index]
            error_count_top_item['day'] = self.start_time
            error_count_list[error_count_index] = error_count_top_item
            error_count_index += 1
        yield error_count_list

        monitor_names = result['monitor_name']
        monitor_chart = result['chart_uprate']
        monitor_chart_list = {}
        monitor_chart_index = 0
        for line in monitor_chart:
            for name in monitor_names:
                monitor_chart_item = items.MonitorChartItem()
                if "-" in line['time']:
                    monitor_chart_item['time'] = datetime.datetime.strptime(
                        str(datetime.datetime.now().year) + "-" + line['time'] + ':00', "%Y-%m-%d %H:%M:%S")
                else:
                    monitor_chart_item['time'] = datetime.datetime.strptime(
                        datetime.datetime.now().strftime("%Y-%m-%d ") + line['time'] + ':00', "%Y-%m-%d %H:%M:%S")

                monitor_chart_item['monitor_name'] = name
                monitor_chart_item['value'] = line[name]
                monitor_chart_item['type'] = 'rate'
                monitor_chart_item['site'] = self.site_maps.values()[self.index]
                monitor_chart_item['day'] = self.start_time
                monitor_chart_list[monitor_chart_index] = monitor_chart_item
                monitor_chart_index += 1
        yield monitor_chart_list

        monitor_prov = result['monitor_prov']
        monitor_province_list = {}
        monitor_province_index = 0
        for province in monitor_prov:
            for line in monitor_prov[province]:
                if line['name']:
                    monitor_province_item = items.MonitorProvinceItem()
                    monitor_province_item['monitor_name'] = line['name']
                    monitor_province_item['monitor_province'] = province
                    monitor_province_item['value'] = line['rate']
                    monitor_province_item['type'] = 'rate'
                    monitor_province_item['site'] = self.site_maps.values()[self.index]
                    monitor_province_item['day'] = self.start_time
                    monitor_province_list[monitor_province_index] = monitor_province_item
                    monitor_province_index += 1
        yield monitor_province_list

        province_time = result['prov_time']
        province_time_list = {}
        province_time_index = 0
        for line in province_time:
            province_time_item = items.ProvinceTimeItem()
            province_time_item['province_name'] = line['name']
            province_time_item['value'] = line['value']
            province_time_item['type'] = 'rate'
            province_time_item['site'] = self.site_maps.values()[self.index]
            province_time_item['day'] = self.start_time
            province_time_list[province_time_index] = province_time_item
            province_time_index += 1
        yield province_time_list

        type_time = result['type_time']
        type_time_list = {}
        type_time_index = 0
        for line in type_time:
            type_time_item = items.TypeTimeItem()
            type_time_item['type_name'] = line['name'] if line['name'] else u"其他"
            type_time_item['value'] = line['value']
            type_time_item['type'] = 'rate'
            type_time_item['site'] = self.site_maps.values()[self.index]
            type_time_item['day'] = self.start_time
            type_time_list[type_time_index] = type_time_item
            type_time_index += 1
        yield type_time_item

        monitor_type = result['monitor_type']
        monitor_type_list = {}
        monitor_type_index = 0
        for line in monitor_type:
            for yy in monitor_type[line]:
                if yy['name']:
                    monitor_type_item = items.MonitorTypeItem()
                    monitor_type_item['monitor_name'] = yy['name']
                    monitor_type_item['province'] = yy['prov']
                    monitor_type_item['rate'] = yy['rate']
                    monitor_type_item['type_name'] = line
                    monitor_type_item['catname'] = 'rate'
                    monitor_type_item['site'] = self.site_maps.values()[self.index]
                    monitor_type_item['day'] = self.start_time
                    monitor_type_list[monitor_type_index] = monitor_type_item
                    monitor_type_index += 1
        yield monitor_type_list

        china_time = result['china_time']
        china_item = items.ChinaTimeItem()
        china_item['value'] = china_time
        china_item['type'] = 'rate'
        china_item['site'] = self.site_maps.values()[self.index]
        china_item['day'] = self.start_time
        yield china_item

        logging.info("[crawl site] " + 'https://qiye.jiankongbao.com/task_report_ajax.php?task_id={id}&sel_action=resp&is_world=china'.format(id=self.site_maps.keys()[self.index]))
        yield scrapy.Request(
            'https://qiye.jiankongbao.com/task_report_ajax.php?task_id={id}&sel_action=resp&is_world=china'.format(id=self.site_maps.keys()[self.index]),
            meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_time)

    def parse_time(self, response):
        result = json.loads(response.body)

        monitor_names = result['monitor_name']
        monitor_chart = result['chart_uprate']
        monitor_chart_list = {}
        monitor_chart_index = 0
        for line in monitor_chart:
            for name in monitor_names:
                monitor_chart_item = items.MonitorChartItem()
                if line['time'] and "-" in line['time']:
                    monitor_chart_item['time'] = datetime.datetime.strptime(
                        str(datetime.datetime.now().year) + "-" + line['time'] + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
                else:
                    monitor_chart_item['time'] = datetime.datetime.strptime(
                        datetime.datetime.now().strftime("%Y-%m-%d ") + line['time'] + ':00', "%Y-%m-%d %H:%M:%S")
                monitor_chart_item['monitor_name'] = name
                monitor_chart_item['value'] = line[name]
                monitor_chart_item['type'] = 'time'
                monitor_chart_item['site'] = self.site_maps.values()[self.index]
                monitor_chart_item['day'] = self.start_time
                monitor_chart_list[monitor_chart_index] = monitor_chart_item
                monitor_chart_index += 1
        yield monitor_chart_list

        monitor_prov = result['monitor_prov']
        monitor_province_list = {}
        monitor_province_index = 0
        for province in monitor_prov:
            for line in monitor_prov[province]:
                if line['name']:
                    monitor_province_item = items.MonitorProvinceItem()
                    monitor_province_item['monitor_name'] = line['name']
                    monitor_province_item['monitor_province'] = province
                    monitor_province_item['value'] = line['time']
                    monitor_province_item['type'] = 'time'
                    monitor_province_item['site'] = self.site_maps.values()[self.index]
                    monitor_province_item['day'] = self.start_time
                    monitor_province_list[monitor_province_index] = monitor_province_item
                    monitor_province_index += 1
        yield monitor_province_list

        province_time = result['prov_time_str']
        province_time_list = {}
        province_time_index = 0
        for line in province_time:
            province_time_item = items.ProvinceTimeItem()
            province_time_item['province_name'] = line['name']
            province_time_item['value'] = line['value'] if "value" in line else ""
            province_time_item['type'] = 'time'
            province_time_item['site'] = self.site_maps.values()[self.index]
            province_time_item['day'] = self.start_time
            province_time_list[province_time_index] = province_time_item
            province_time_index += 1
        yield province_time_list

        type_time = result['type_time_str']
        type_time_list = {}
        type_time_index = 0
        for line in type_time:
            type_time_item = items.TypeTimeItem()
            type_time_item['type_name'] = line['name'] if line['name'] else u"其他"
            type_time_item['value'] = line['value']
            type_time_item['type'] = 'time'
            type_time_item['site'] = self.site_maps.values()[self.index]
            type_time_item['day'] = self.start_time
            type_time_list[type_time_index] = type_time_item
            type_time_index += 1
        yield type_time_list

        monitor_type = result['monitor_type']
        monitor_type_list = {}
        monitor_type_index = 0
        for line in monitor_type:
            for yy in monitor_type[line]:
                if yy['name']:
                    monitor_type_item = items.MonitorTypeItem()
                    monitor_type_item['monitor_name'] = yy['name']
                    monitor_type_item['province'] = yy['prov']
                    monitor_type_item['rate'] = yy['time']
                    monitor_type_item['type_name'] = line
                    monitor_type_item['catname'] = "time"
                    monitor_type_item['site'] = self.site_maps.values()[self.index]
                    monitor_type_item['day'] = self.start_time
                    monitor_type_list[monitor_type_index] = monitor_type_item
                    monitor_type_index += 1
        yield monitor_type_list

        china_time = result['china_time']
        china_item = items.ChinaTimeItem()
        china_item['value'] = china_time
        china_item['type'] = 'time'
        china_item['site'] = self.site_maps.values()[self.index]
        china_item['day'] = self.start_time
        yield china_item

        self.index += 1
        if self.index < len(self.site_maps):
            logging.info(
                "[crawl site] " + 'https://qiye.jiankongbao.com/task_report_ajax.php?task_id={id}&sel_action=avail&is_world=china'.format(
                    id=self.site_maps.keys()[self.index]))
            yield scrapy.Request(
                'https://qiye.jiankongbao.com/task_report_ajax.php?task_id={id}&sel_action=avail&is_world=china'.format(
                    id=self.site_maps.keys()[self.index]),
                meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_rate)