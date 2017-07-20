# -*- coding: utf-8 -*-
import scrapy
import sys
import datetime
import logging
import json
import crawler.items as items
import crawler.util as util
reload(sys)
sys.setdefaultencoding('utf8')

class JiankongTongjiSpider(scrapy.Spider):
    name = "jiankong-tongji"
    handle_httpstatus_list = [404, 500]
    allowed_domains = ["jiankongbao.com"]
    start_urls = ['https://qiye.jiankongbao.com/']
    site_maps = {}
    index = 0
    list_page = 0
    list_url = "https://qiye.jiankongbao.com/ajax_wrapper.php?command=get_task_list_page&type=&owner=&priority=&class_id=&status=&temp=task_list_main&page={page}&s=&domain_id=&period=today&range={now},{now}&m_page=undefined&ent_node_id=&search_status=&cache=71014"
    crawl_site = ["www.91pme.com", "m.91pme.com"]
    start_time = None

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
            meta={"cookiejar": 2},
            cookies={"page_rows": 50},
            callback=self.loged_in
        )]

    def loged_in(self, response):
        logging.info("[crawl site] " + self.list_url.format(page=1, now=datetime.datetime.now().strftime("%Y-%m-%d")))
        yield scrapy.Request(
            self.list_url.format(page=1, now=datetime.datetime.now().strftime("%Y-%m-%d")),
            meta={'cookiejar': response.meta['cookiejar']}, cookies={"page_rows": 50}, callback=self.parse_list)

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
            # 只抓取要抓的站点
            if title in self.crawl_site:
                self.site_maps[id] = title

        logging.info("[crawl site] " + 'https://qiye.jiankongbao.com/task/http/{id}/report/list'.format(
            id=self.site_maps.keys()[self.index]))
        yield scrapy.Request(
            'https://qiye.jiankongbao.com/task/http/{id}/report/list'.format(id=self.site_maps.keys()[self.index]),
            meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_area)


    def parse_area(self, response):
        json_str = response.xpath("//script").re_first(r"monitor_avg_top= (.*);")
        result = json.loads(json_str.strip())
        ids = []
        area_list = {}
        item_index = 0
        for line in result:
            if "name" in result[line] and result[line]['name']:
                area_item = items.MonitorAreaStasticItem()
                area_item['monitor_name'] = result[line]['name']
                area_item['type'] = result[line]['type'] if "type" in result[line] else ""
                area_item['province'] = result[line]['prov'] if "prov" in result[line] else ""
                area_item['mid'] = result[line]['id']
                area_item['area'] = result[line]['area'] if "area" in result[line] else ""
                area_item['site'] = self.site_maps.values()[self.index]
                area_item['day'] = self.start_time
                ids.append(result[line]['id'])
                area_list[item_index] = area_item
                item_index += 1

        yield area_list

        logging.info("[crawl site] " + ('https://qiye.jiankongbao.com/task_report_ajax.php?task_id={id}&sel_action=day_list&m_ids=[' + ",".join(map(str, ids)) + "]").format(id=self.site_maps.keys()[self.index]))
        yield scrapy.Request(
            ('https://qiye.jiankongbao.com/task_report_ajax.php?task_id={id}&sel_action=day_list&m_ids=[' + ",".join(map(str, ids)) + "]").format(id=self.site_maps.keys()[self.index]),
            meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_stastic)
    #
    def parse_stastic(self, response):
        result = json.loads(response.body)
        result = result['data_list']
        monitor_stastic_list = {}
        item_index = 0
        for mid in result:
            for dt in result[mid]:
                monitor_stastic_item = items.MonitorStasticItem()
                monitor_stastic_item['day'] = datetime.datetime.strptime(dt, "%Y-%m-%d")
                monitor_stastic_item['mid'] = mid
                monitor_stastic_item['min'] = result[mid][dt]['min']
                monitor_stastic_item['max'] = result[mid][dt]['max']
                monitor_stastic_item['avg'] = result[mid][dt]['avg']
                monitor_stastic_item['time_st'] = result[mid][dt]['time_st']
                monitor_stastic_item['all_time'] = result[mid][dt]['all_time']
                monitor_stastic_item['site'] = self.site_maps.values()[self.index]
                monitor_stastic_item['day'] = self.start_time
                monitor_stastic_list[item_index] = monitor_stastic_item
        yield monitor_stastic_list

        self.index += 1
        if self.index < len(self.site_maps):
            logging.info("[crawl site] " + 'https://qiye.jiankongbao.com/task/http/{id}/report/list'.format(
                id=self.site_maps.keys()[self.index]))
            yield scrapy.Request(
                'https://qiye.jiankongbao.com/task/http/{id}/report/list'.format(id=self.site_maps.keys()[self.index]),
                meta={'cookiejar': response.meta['cookiejar']}, callback=self.parse_area)