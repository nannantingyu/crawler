# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_, func
from crawler.models.util import db_connect, create_news_table
from crawler.models.crawl_china_time import ChinaTime
from crawler.models.crawl_error_top import ErrorTop
from crawler.models.crawl_monitor_area_stastic import MonitorAreaStastic
from crawler.models.crawl_monitor_chart import MonitorChart
from crawler.models.crawl_monitor_province import MonitorProvince
from crawler.models.crawl_monitor_stastic import MonitorStastic
from crawler.models.crawl_monitor_type import MonitorType
from crawler.models.crawl_province_time import ProvinceTime
from crawler.models.crawl_type_time import TypeTime
from crawler.models.crawl_baidu_tongji import BaiduTongji
from crawler.models.crawl_economic_calendar import CrawlEconomicCalendar
from crawler.models.crawl_economic_event import CrawlEconomicEvent
from crawler.models.crawl_economic_holiday import CrawlEconomicHoliday
import crawler.items as items
import datetime

class CrawlerPipeline(object):
    """crawl pipe"""

    def process_item(self, item, spider):
        """process item"""
        return item

@contextmanager
def session_scope(session):
    """Provide a transactional scope around a series of operations."""
    sess = session()
    try:
        yield sess
        sess.commit()
    except:
        sess.rollback()
        raise
    finally:
        sess.close()

class SqlReader(object):
    def __init__(self):
        engine = db_connect()
        create_news_table(engine)
        self.sess = sessionmaker(bind=engine)

    def read_baidutongji_latest_time(self):
        with session_scope(self.sess) as session:
            query = session.query(BaiduTongji.site, func.max(BaiduTongji.access_time).label('access_time')).group_by(BaiduTongji.site).all()
            return query


class JianKongPipeline(object):
    """保存文章到数据库"""

    def __init__(self):
        engine = db_connect()
        create_news_table(engine)
        self.sess = sessionmaker(bind=engine)
        self.recent_newsid = None

    def open_spider(self, spider):
        """This method is called when the spider is opened."""
        logging.info('open spider')

    def process_item(self, item, spider):
        """process news item"""
        if spider.name in ["jiankongbao", "jiankong-tongji"]:
            # 焦点新闻
            self.process_jiankongbao(item)
        elif spider.name in ['baidu_tongji_nologin', 'baidu-tongji']:
            self.process_baidutongji(item)
        elif spider.name in ['cj-calendar']:
            self.parse_calendar(item)

    def parse_calendar(self, item):
        if item and len(item) > 0:
            if 0 in item and isinstance(item[0], items.CrawlEconomicCalendarItem):
                with session_scope(self.sess) as session:
                    all_data = []
                    for ditem in item:
                        ditem = item[ditem]
                        crawlEconomicCalendar = CrawlEconomicCalendar(**ditem)

                        query = session.query(CrawlEconomicCalendar.id).filter(and_(
                            CrawlEconomicCalendar.source_id == crawlEconomicCalendar.source_id,
                            CrawlEconomicCalendar.pub_time == crawlEconomicCalendar.pub_time
                        )).one_or_none()

                        if query is not None:
                            data = {}
                            if crawlEconomicCalendar.country is not None:
                                data['country'] = crawlEconomicCalendar.country
                            if crawlEconomicCalendar.quota_name is not None:
                                data['quota_name'] = crawlEconomicCalendar.quota_name
                            if crawlEconomicCalendar.importance is not None:
                                data['importance'] = crawlEconomicCalendar.importance
                            if crawlEconomicCalendar.former_value is not None:
                                data['former_value'] = crawlEconomicCalendar.former_value
                            if crawlEconomicCalendar.predicted_value is not None:
                                data['predicted_value'] = crawlEconomicCalendar.predicted_value
                            if crawlEconomicCalendar.published_value is not None:
                                data['published_value'] = crawlEconomicCalendar.published_value
                            if crawlEconomicCalendar.influence is not None:
                                data['influence'] = crawlEconomicCalendar.influence
                            if crawlEconomicCalendar.next_pub_time is not None:
                                data['next_pub_time'] = crawlEconomicCalendar.next_pub_time
                            if crawlEconomicCalendar.pub_agent is not None:
                                data['pub_agent'] = crawlEconomicCalendar.pub_agent
                            if crawlEconomicCalendar.pub_frequency is not None:
                                data['pub_frequency'] = crawlEconomicCalendar.pub_frequency
                            if crawlEconomicCalendar.count_way is not None:
                                data['count_way'] = crawlEconomicCalendar.count_way
                            if crawlEconomicCalendar.data_influence is not None:
                                data['data_influence'] = crawlEconomicCalendar.data_influence
                            if crawlEconomicCalendar.data_define is not None:
                                data['data_define'] = crawlEconomicCalendar.data_define
                            if crawlEconomicCalendar.funny_read is not None:
                                data['funny_read'] = crawlEconomicCalendar.funny_read

                            if data:
                                session.query(CrawlEconomicCalendar).filter(
                                    CrawlEconomicCalendar.id == query[0]).update(data)

                        else:
                            all_data.append(crawlEconomicCalendar)

                    if len(all_data) > 0:
                        session.add_all(all_data)

            elif 0 in item and isinstance(item[0], items.CrawlEconomicEventItem):
                all_data = []

                with session_scope(self.sess) as session:
                    crawlEconomicEvent = CrawlEconomicEvent(**item[0])
                    session.query(CrawlEconomicEvent).filter(
                        CrawlEconomicEvent.date == crawlEconomicEvent.date).delete()

                    for ditem in item:
                        ditem = item[ditem]
                        crawlEconomicEvent = CrawlEconomicEvent(**ditem)
                        all_data.append(crawlEconomicEvent)

                    if len(all_data) > 0:
                        session.add_all(all_data)

            elif 0 in item and isinstance(item[0], items.CrawlEconomicHolidayItem):
                all_data = []

                with session_scope(self.sess) as session:
                    crawlEconomicHoliday = CrawlEconomicHoliday(**item[0])
                    session.query(CrawlEconomicHoliday).filter(CrawlEconomicHoliday.date == crawlEconomicHoliday.date).delete()

                    for ditem in item:
                        ditem = item[ditem]
                        crawlEconomicHoliday = CrawlEconomicHoliday(**ditem)
                        all_data.append(crawlEconomicHoliday)

                    if len(all_data) > 0:
                        session.add_all(all_data)



    def process_jiankongbao(self, item):
        if isinstance(item, items.ChinaTimeItem):
            chinaTime = ChinaTime(**item)
            with session_scope(self.sess) as session:
                session.add(chinaTime)

        elif isinstance(item.values()[0], items.ErrorTopItem):
            all_items = []
            for it in item.values():
                all_items.append(ErrorTop(**it))
            with session_scope(self.sess) as session:
                session.add_all(all_items)

        elif isinstance(item.values()[0], items.MonitorAreaStasticItem):
            all_items = []
            for it in item.values():
                all_items.append(MonitorAreaStastic(**it))

            with session_scope(self.sess) as session:
                session.add_all(all_items)

        elif isinstance(item.values()[0], items.MonitorChartItem):
            all_items = []
            for it in item.values():
                all_items.append(MonitorChart(**it))
            with session_scope(self.sess) as session:
                for db_item in all_items:
                    query = session.query(MonitorChart.id).filter(and_(
                        MonitorChart.time == db_item.time,
                        MonitorChart.type == db_item.type,
                        MonitorChart.site == db_item.site,
                        MonitorChart.monitor_name == db_item.monitor_name
                    )).one_or_none()

                    if query is None:
                        session.add(db_item)
                    else:
                        data = {}
                        if db_item.value is not None:
                            data['value'] = db_item.value

                        if data:
                            session.query(MonitorChart).filter(
                                MonitorChart.id == query[0]).update(data)


        elif isinstance(item.values()[0], items.MonitorProvinceItem):
            all_items = []
            for it in item.values():
                all_items.append(MonitorProvince(**it))
            with session_scope(self.sess) as session:
                session.add_all(all_items)
        elif isinstance(item.values()[0], items.MonitorStasticItem):
            all_items = []
            for it in item.values():
                all_items.append(MonitorStastic(**it))
            with session_scope(self.sess) as session:
                session.add_all(all_items)

        elif isinstance(item.values()[0], items.MonitorTypeItem):
            all_items = []
            for it in item.values():
                all_items.append(MonitorType(**it))
            with session_scope(self.sess) as session:
                session.add_all(all_items)
        elif isinstance(item.values()[0], items.ProvinceTimeItem):
            all_items = []
            for it in item.values():
                all_items.append(ProvinceTime(**it))
            with session_scope(self.sess) as session:
                session.add_all(all_items)
        elif isinstance(item.values()[0], items.TypeTimeItem):
            all_items = []
            for it in item.values():
                all_items.append(TypeTime(**it))
            with session_scope(self.sess) as session:
                    session.add_all(all_items)
    def process_baidutongji(self, item):
        all_data = []
        with session_scope(self.sess) as session:
            for ditem in item:
                baiduTongji = BaiduTongji(**item[ditem])

                query = session.query(BaiduTongji.id).filter(and_(
                    BaiduTongji.user_id == baiduTongji.user_id,
                    BaiduTongji.access_time == baiduTongji.access_time
                )).one_or_none()

                if query is None:
                    all_data.append(baiduTongji)
                else:
                    data = {}
                    if baiduTongji.area is not None:
                        data['area'] = baiduTongji.area
                    if baiduTongji.keywords is not None:
                        data['keywords'] = baiduTongji.keywords
                    if baiduTongji.entry_page is not None:
                        data['entry_page'] = baiduTongji.entry_page
                    if baiduTongji.ip is not None:
                        data['ip'] = baiduTongji.ip
                    if baiduTongji.visit_time is not None:
                        data['visit_time'] = baiduTongji.visit_time
                    if baiduTongji.visit_pages is not None:
                        data['visit_pages'] = baiduTongji.visit_pages
                    if baiduTongji.visitorType is not None:
                        data['visitorType'] = baiduTongji.visitorType
                    if baiduTongji.visitorFrequency is not None:
                        data['visitorFrequency'] = baiduTongji.visitorFrequency
                    if baiduTongji.lastVisitTime is not None:
                        data['lastVisitTime'] = baiduTongji.lastVisitTime
                    if baiduTongji.endPage is not None:
                        data['endPage'] = baiduTongji.endPage
                    if baiduTongji.deviceType is not None:
                        data['deviceType'] = baiduTongji.deviceType
                    if baiduTongji.fromType is not None:
                        data['fromType'] = baiduTongji.fromType
                    if baiduTongji.fromurl is not None:
                        data['fromurl'] = baiduTongji.fromurl
                    if baiduTongji.fromAccount is not None:
                        data['fromAccount'] = baiduTongji.fromAccount
                    if baiduTongji.isp is not None:
                        data['isp'] = baiduTongji.isp
                    if baiduTongji.os is not None:
                        data['os'] = baiduTongji.os
                    if baiduTongji.osType is not None:
                        data['osType'] = baiduTongji.osType
                    if baiduTongji.browser is not None:
                        data['browser'] = baiduTongji.browser
                    if baiduTongji.browserType is not None:
                        data['browserType'] = baiduTongji.browserType
                    if baiduTongji.language is not None:
                        data['language'] = baiduTongji.language
                    if baiduTongji.resolution is not None:
                        data['resolution'] = baiduTongji.resolution
                    if baiduTongji.color is not None:
                        data['color'] = baiduTongji.color
                    if baiduTongji.accessPage is not None:
                        data['accessPage'] = baiduTongji.accessPage
                    if baiduTongji.antiCode is not None:
                        data['antiCode'] = baiduTongji.antiCode

                    if data:
                        session.query(BaiduTongji).filter(
                            baiduTongji.id == query[0]).update(data)

            if len(all_data) > 0:
                session.add_all(all_data)

    def close_spider(self, spider):
        """close spider"""
        logging.info('close spider')