# -*- encoding: utf-8 -*-
"""
定义数据库模型实体 
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func, Index, SmallInteger, DECIMAL, Date
from crawler.models.util import Base

class CrawlEconomicCalendar(Base):
    __tablename__ = 'crawl_economic_calendar'

    id = Column(Integer, primary_key=True)
    country = Column(String(64))
    quota_name = Column(String(512))
    pub_time = Column(String(32))
    importance = Column(String(24))
    former_value = Column(String(32))
    predicted_value = Column(String(32))
    published_value = Column(String(32))
    influence = Column(String(64))
    source_id = Column(Integer)
    next_pub_time = Column(String(64))
    pub_agent = Column(String(64))
    pub_frequency = Column(String(64))
    count_way = Column(String(64))
    data_influence = Column(String(512))
    data_define = Column(String(512))
    funny_read = Column(String(512))
    created_time = Column(DateTime, default=func.now())
    updated_time = Column(DateTime, default=func.now(), onupdate=func.now())