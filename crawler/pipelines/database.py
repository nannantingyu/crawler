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
from crawler.models.crawl_fx678_economic_calendar import CrawlFx678EconomicCalendar
from crawler.models.crawl_fx678_economic_event import CrawlFx678EconomicEvent
from crawler.models.crawl_fx678_economic_holiday import CrawlFx678EconomicHoliday
from crawler.models.crawl_economic_calendar import CrawlEconomicCalendar
from crawler.models.crawl_economic_event import CrawlEconomicEvent
from crawler.models.crawl_economic_holiday import CrawlEconomicHoliday
from crawler.models.crawl_zhanzhang import CrawlZhanzhang
from crawler.models.crawl_jin10_article import CrawlJin10Article
from crawler.models.crawl_article import CrawlArticle
from crawler.models.crawl_ibrebates import Ibrebates
from crawler.models.crawl_economic_jiedu import CrawlEconomicJiedu

from crawler.models.crawl_ssi_trend import CrawlSsiTrend
from crawler.models.crawl_ssi_trend_forxfact import CrawlSsiTrend as CrawlSsiTrend_forxfact
from crawler.models.crawl_ssi_trend_saxobank import CrawlSsiTrend as CrawlSsiTrend_saxobank
from crawler.models.crawl_ssi_trend_myfxbook import CrawlSsiTrend as CrawlSsiTrend_myfxbook
from crawler.models.crawl_ssi_trend_instfor import CrawlSsiTrend as CrawlSsiTrend_instfor
from crawler.models.crawl_ssi_trend_ftroanda import CrawlSsiTrend as CrawlSsiTrend_ftroanda
from crawler.models.crawl_ssi_trend_fiboforx import CrawlSsiTrend as CrawlSsiTrend_fiboforx
from crawler.models.crawl_ssi_trend_dukscopy import CrawlSsiTrend as CrawlSsiTrend_dukscopy
from crawler.models.crawl_ssi_trend_alpari import CrawlSsiTrend as CrawlSsiTrend_alpari
from crawler.models.crawl_ssi_trend_fxcm import CrawlSsiTrend as CrawlSsiTrend_fxcm

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

    def read_jiedu(self):
        with session_scope(self.sess) as session:
            query = session.query(CrawlEconomicCalendar.dataname_id, CrawlEconomicCalendar.source_id).filter(
                CrawlEconomicCalendar.dataname_id != None
            ).group_by(CrawlEconomicCalendar.dataname_id).all()

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
        elif spider.name in ['zhanzhang']:
            self.parse_zhanzhang(item)
        # elif spider.name in []:
        #     self.parse_jin10_article(item)
        elif spider.name in ['jin10_article', 'crawl_jin10_article_detail', 'weibo', 'weibo_article_detail', 'fx678_article']:
            self.parse_article(item)
        elif spider.name in ['ibrebates']:
            self.parse_ibrebates(item)
        elif spider.name in ['jin10_ssi_trends']:
            self.parse_ssi_trends(item)
        elif spider.name in ['jin10_ssi_trends_today']:
            self.parse_ssi_trends_today(item)
        elif spider.name in ['cj_jiedu']:
            self.parse_jiedu(item)
        elif spider.name in ['cj_fx678']:
            self.parse_fx678_calendar(item)

    def parse_jiedu(self, item):
        with session_scope(self.sess) as session:
            crawlEconomicCalendar = CrawlEconomicCalendar(**item)
            session.query(CrawlEconomicCalendar).filter(CrawlEconomicCalendar.dataname_id == crawlEconomicCalendar.dataname_id).update({
                CrawlEconomicCalendar.next_pub_time: crawlEconomicCalendar.next_pub_time,
                CrawlEconomicCalendar.pub_agent: crawlEconomicCalendar.pub_agent,
                CrawlEconomicCalendar.pub_frequency: crawlEconomicCalendar.pub_frequency,
                CrawlEconomicCalendar.count_way: crawlEconomicCalendar.count_way,
                CrawlEconomicCalendar.data_influence: crawlEconomicCalendar.data_influence,
                CrawlEconomicCalendar.data_define: crawlEconomicCalendar.data_define,
                CrawlEconomicCalendar.funny_read: crawlEconomicCalendar.funny_read
            })

    def parse_ssi_trends_today(self, item):
        with session_scope(self.sess) as session:
            all_item = []
            for it in item:
                crawlSSiTrend = CrawlSsiTrend(**item[it])
                all_item.append(crawlSSiTrend)

            if len(all_item) > 0:
                session.add_all(all_item)

    def parse_ssi_trends(self, item):
        with session_scope(self.sess) as session:
            CrawlSsiTrend = eval("CrawlSsiTrend_" + item[0]['platform'])
            query = session.query(func.max(CrawlSsiTrend.time).label("max_time")).filter(
                and_(
                    CrawlSsiTrend.type == item[0]['type'],
                    CrawlSsiTrend.platform == item[0]['platform'],
                )
            ).one_or_none()

            max_time = query[0] if query else None

            all_item = []
            for it in item:
                if max_time is None or item[it]['time'] > max_time.strftime('%Y-%m-%d %H:%M:%I'):
                    crawlSSiTrend = CrawlSsiTrend(**item[it])
                    all_item.append(crawlSSiTrend)

            if len(all_item) > 0:
                session.add_all(all_item)

    def parse_ibrebates(self, item):
        ibrebates = Ibrebates(**item)
        with session_scope(self.sess) as session:
            query = session.query(Ibrebates.id).filter(and_(
                Ibrebates.name == ibrebates.name
            )).one_or_none()

            if query is None:
                session.add(ibrebates)
            else:
                data = {}
                update_field = ["description", "spread_type", "om_spread", "gold_spread", "offshore", "a_share", "regulatory_authority", "trading_varieties", "platform_type", "account_type", "scalp", "hedging", "min_transaction", "least_entry", "maximum_leverage", "maximum_trading", "deposit_method", "entry_method", "commission_fee", "entry_fee", "account_currency", "rollovers", "explosion_proportion", "renminbi"]
                for field in update_field:
                    try:
                        attr_value = getattr(ibrebates, field)
                        data[field] = attr_value
                    except AttributeError as err:
                        pass

                if data:
                    session.query(Ibrebates).filter(Ibrebates.id == query[0]).update(data)

    def parse_article(self, item):
        article = CrawlArticle(**item)
        with session_scope(self.sess) as session:
            query = session.query(CrawlArticle.id).filter(and_(
                CrawlArticle.source_id == article.source_id,
            )).one_or_none()

            if query is None:
                session.add(article)
            else:
                data = {}
                if article.body is not None:
                    data['body'] = article.body
                if article.author is not None:
                    data['author'] = article.author

                if data:
                    session.query(CrawlArticle).filter(CrawlArticle.id == query[0]).update(data)

    def parse_jin10_article(self, item):
        article = CrawlJin10Article(**item)
        with session_scope(self.sess) as session:
            query = session.query(CrawlJin10Article.id).filter(and_(
                CrawlJin10Article.source_id == article.source_id,
            )).one_or_none()

            if query is None:
                session.add(article)
            else:
                data = {}
                if article.body is not None:
                    data['body'] = article.body
                if article.author is not None:
                    data['author'] = article.author

                if data:
                    session.query(CrawlJin10Article).filter(
                        CrawlJin10Article.id == query[0]).update(data)

    def parse_zhanzhang(self, item):
        all_data = [CrawlZhanzhang(**item[it]) for it in item]
        with session_scope(self.sess) as session:
            session.add_all(all_data)

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
                            # CrawlEconomicCalendar.pub_time == crawlEconomicCalendar.pub_time
                        )).one_or_none()

                        if query is not None:
                            data = {}
                            if crawlEconomicCalendar.country is not None:
                                data['country'] = crawlEconomicCalendar.country
                            if crawlEconomicCalendar.pub_time is not None:
                                data['pub_time'] = crawlEconomicCalendar.pub_time
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
                    # crawlEconomicEvent = CrawlEconomicEvent(**item[0])
                    # session.query(CrawlEconomicEvent).filter(
                    #     CrawlEconomicEvent.date == crawlEconomicEvent.date).delete()

                    for ditem in item:
                        ditem = item[ditem]
                        crawlEconomicEvent = CrawlEconomicEvent(**ditem)

                        query = session.query(CrawlEconomicEvent.id).filter(and_(
                            CrawlEconomicEvent.source_id == crawlEconomicEvent.source_id,
                            # CrawlEconomicCalendar.pub_time == crawlEconomicCalendar.pub_time
                        )).one_or_none()

                        if query:
                            data = {}
                            if crawlEconomicEvent.country is not None:
                                data['country'] = crawlEconomicEvent.country
                            if crawlEconomicEvent.time is not None:
                                data['time'] = crawlEconomicEvent.time
                            if crawlEconomicEvent.city is not None:
                                data['city'] = crawlEconomicEvent.city
                            if crawlEconomicEvent.importance is not None:
                                data['importance'] = crawlEconomicEvent.importance
                            if crawlEconomicEvent.event is not None:
                                data['event'] = crawlEconomicEvent.event
                            if crawlEconomicEvent.date is not None:
                                data['date'] = crawlEconomicEvent.date

                            if data:
                                session.query(CrawlEconomicEvent).filter(
                                    CrawlEconomicEvent.id == query[0]).update(data)
                        else:
                            all_data.append(crawlEconomicEvent)

                    if len(all_data) > 0:
                        session.add_all(all_data)

            elif 0 in item and isinstance(item[0], items.CrawlEconomicHolidayItem):
                all_data = []

                with session_scope(self.sess) as session:
                    # crawlEconomicHoliday = CrawlEconomicHoliday(**item[0])
                    # session.query(CrawlEconomicHoliday).filter(CrawlEconomicHoliday.date == crawlEconomicHoliday.date).delete()

                    for ditem in item:
                        ditem = item[ditem]
                        crawlEconomicHoliday = CrawlEconomicHoliday(**ditem)

                        query = session.query(CrawlEconomicHoliday.id).filter(and_(
                            CrawlEconomicHoliday.source_id == crawlEconomicHoliday.source_id,
                            # CrawlEconomicCalendar.pub_time == crawlEconomicCalendar.pub_time
                        )).one_or_none()

                        if query:
                            data = {}
                            if crawlEconomicHoliday.country is not None:
                                data['country'] = crawlEconomicHoliday.country
                            if crawlEconomicHoliday.time is not None:
                                data['time'] = crawlEconomicHoliday.time
                            if crawlEconomicHoliday.market is not None:
                                data['market'] = crawlEconomicHoliday.market
                            if crawlEconomicHoliday.holiday_name is not None:
                                data['holiday_name'] = crawlEconomicHoliday.holiday_name
                            if crawlEconomicHoliday.detail is not None:
                                data['detail'] = crawlEconomicHoliday.detail
                            if crawlEconomicHoliday.date is not None:
                                data['date'] = crawlEconomicHoliday.date

                            if data:
                                session.query(CrawlEconomicHoliday).filter(
                                    CrawlEconomicHoliday.id == query[0]).update(data)
                        else:
                            all_data.append(crawlEconomicHoliday)

                    if len(all_data) > 0:
                        session.add_all(all_data)

            elif 0 in item and isinstance(item[0], items.CrawlEconomicJieduItem):
                with session_scope(self.sess) as session:
                    crawlEconomicJiedu = CrawlEconomicJiedu(**item[0])

                    query = session.query(CrawlEconomicJiedu.dataname_id).filter(and_(
                        CrawlEconomicJiedu.dataname_id == crawlEconomicJiedu.dataname_id,
                        # CrawlEconomicCalendar.pub_time == crawlEconomicCalendar.pub_time
                    )).one_or_none()

                    if query:
                        data = {
                            'next_pub_time': crawlEconomicJiedu.next_pub_time,
                            'pub_agent': crawlEconomicJiedu.pub_agent,
                            'pub_frequency': crawlEconomicJiedu.pub_frequency,
                            'count_way': crawlEconomicJiedu.count_way,
                            'data_influence': crawlEconomicJiedu.data_influence,
                            'data_define': crawlEconomicJiedu.data_define,
                            'funny_read': crawlEconomicJiedu.funny_read
                        }

                        session.query(CrawlEconomicJiedu).filter(
                            CrawlEconomicJiedu.dataname_id == crawlEconomicJiedu.dataname_id).update(data)
                    else:
                        session.add(crawlEconomicJiedu)

    def parse_fx678_calendar(self, item):
        if item and len(item) > 0:
            if 0 in item and isinstance(item[0], items.CrawlFx678EconomicCalendarItem):
                with session_scope(self.sess) as session:
                    all_data = []
                    for ditem in item:
                        ditem = item[ditem]
                        crawlfx678EconomicCalendar = CrawlFx678EconomicCalendar(**ditem)

                        query = session.query(CrawlFx678EconomicCalendar.id).filter(and_(
                            CrawlFx678EconomicCalendar.source_id == crawlfx678EconomicCalendar.source_id,
                            # CrawlEconomicCalendar.pub_time == crawlEconomicCalendar.pub_time
                        )).one_or_none()

                        if query is not None:
                            data = {}
                            if crawlfx678EconomicCalendar.country is not None:
                                data['country'] = crawlfx678EconomicCalendar.country
                            if crawlfx678EconomicCalendar.pub_time is not None:
                                data['pub_time'] = crawlfx678EconomicCalendar.pub_time
                            if crawlfx678EconomicCalendar.quota_name is not None:
                                data['quota_name'] = crawlfx678EconomicCalendar.quota_name
                            if crawlfx678EconomicCalendar.importance is not None:
                                data['importance'] = crawlfx678EconomicCalendar.importance
                            if crawlfx678EconomicCalendar.former_value is not None:
                                data['former_value'] = crawlfx678EconomicCalendar.former_value
                            if crawlfx678EconomicCalendar.predicted_value is not None:
                                data['predicted_value'] = crawlfx678EconomicCalendar.predicted_value
                            if crawlfx678EconomicCalendar.published_value is not None:
                                data['published_value'] = crawlfx678EconomicCalendar.published_value
                            if crawlfx678EconomicCalendar.influence is not None:
                                data['influence'] = crawlfx678EconomicCalendar.influence
                            if crawlfx678EconomicCalendar.position is not None:
                                data['position'] = crawlfx678EconomicCalendar.position

                            if data:
                                session.query(CrawlFx678EconomicCalendar).filter(
                                    CrawlFx678EconomicCalendar.id == query[0]).update(data)

                        else:
                            all_data.append(crawlfx678EconomicCalendar)

                    if len(all_data) > 0:
                        session.add_all(all_data)

            elif 0 in item and isinstance(item[0], items.CrawlEconomicEventItem):
                all_data = []

                with session_scope(self.sess) as session:
                    # crawlEconomicEvent = CrawlEconomicEvent(**item[0])
                    # session.query(CrawlEconomicEvent).filter(
                    #     CrawlEconomicEvent.date == crawlEconomicEvent.date).delete()

                    for ditem in item:
                        ditem = item[ditem]
                        crawlEconomicEvent = CrawlFx678EconomicEvent(**ditem)
                        print crawlEconomicEvent.source_id
                        query = session.query(CrawlFx678EconomicEvent.id).filter(and_(
                            CrawlFx678EconomicEvent.source_id == crawlEconomicEvent.source_id,
                            # CrawlEconomicCalendar.pub_time == crawlEconomicCalendar.pub_time
                        )).one_or_none()

                        if query:
                            data = {}
                            if crawlEconomicEvent.country is not None:
                                data['country'] = crawlEconomicEvent.country
                            if crawlEconomicEvent.time is not None:
                                data['time'] = crawlEconomicEvent.time
                            if crawlEconomicEvent.city is not None:
                                data['city'] = crawlEconomicEvent.city
                            if crawlEconomicEvent.importance is not None:
                                data['importance'] = crawlEconomicEvent.importance
                            if crawlEconomicEvent.event is not None:
                                data['event'] = crawlEconomicEvent.event
                            if crawlEconomicEvent.date is not None:
                                data['date'] = crawlEconomicEvent.date

                            if data:
                                session.query(CrawlFx678EconomicEvent).filter(
                                    CrawlFx678EconomicEvent.id == query[0]).update(data)
                        else:
                            all_data.append(crawlEconomicEvent)

                    if len(all_data) > 0:
                        session.add_all(all_data)

            elif 0 in item and isinstance(item[0], items.CrawlEconomicHolidayItem):
                all_data = []

                with session_scope(self.sess) as session:
                    # crawlEconomicHoliday = CrawlEconomicHoliday(**item[0])
                    # session.query(CrawlEconomicHoliday).filter(CrawlEconomicHoliday.date == crawlEconomicHoliday.date).delete()

                    for ditem in item:
                        ditem = item[ditem]
                        crawlEconomicHoliday = CrawlFx678EconomicHoliday(**ditem)

                        query = session.query(CrawlFx678EconomicHoliday.id).filter(and_(
                            CrawlFx678EconomicHoliday.source_id == crawlEconomicHoliday.source_id,
                            # CrawlEconomicCalendar.pub_time == crawlEconomicCalendar.pub_time
                        )).one_or_none()

                        if query:
                            data = {}
                            if crawlEconomicHoliday.country is not None:
                                data['country'] = crawlEconomicHoliday.country
                            if crawlEconomicHoliday.time is not None:
                                data['time'] = crawlEconomicHoliday.time
                            if crawlEconomicHoliday.market is not None:
                                data['market'] = crawlEconomicHoliday.market
                            if crawlEconomicHoliday.holiday_name is not None:
                                data['holiday_name'] = crawlEconomicHoliday.holiday_name
                            if crawlEconomicHoliday.detail is not None:
                                data['detail'] = crawlEconomicHoliday.detail
                            if crawlEconomicHoliday.date is not None:
                                data['date'] = crawlEconomicHoliday.date

                            if data:
                                session.query(CrawlFx678EconomicHoliday).filter(
                                    CrawlFx678EconomicHoliday.id == query[0]).update(data)
                        else:
                            all_data.append(crawlEconomicHoliday)

                    if len(all_data) > 0:
                        session.add_all(all_data)

            elif 0 in item and isinstance(item[0], items.CrawlEconomicJieduItem):
                with session_scope(self.sess) as session:
                    crawlEconomicJiedu = CrawlEconomicJiedu(**item[0])

                    query = session.query(CrawlEconomicJiedu.dataname_id).filter(and_(
                        CrawlEconomicJiedu.dataname_id == crawlEconomicJiedu.dataname_id,
                        # CrawlEconomicCalendar.pub_time == crawlEconomicCalendar.pub_time
                    )).one_or_none()

                    if query:
                        data = {
                            'next_pub_time': crawlEconomicJiedu.next_pub_time,
                            'pub_agent': crawlEconomicJiedu.pub_agent,
                            'pub_frequency': crawlEconomicJiedu.pub_frequency,
                            'count_way': crawlEconomicJiedu.count_way,
                            'data_influence': crawlEconomicJiedu.data_influence,
                            'data_define': crawlEconomicJiedu.data_define,
                            'funny_read': crawlEconomicJiedu.funny_read
                        }

                        session.query(CrawlEconomicJiedu).filter(
                            CrawlEconomicJiedu.dataname_id == crawlEconomicJiedu.dataname_id).update(data)
                    else:
                        session.add(crawlEconomicJiedu)

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