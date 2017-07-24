# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_, or_
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

    def close_spider(self, spider):
        """close spider"""
        logging.info('close spider')