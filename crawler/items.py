# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ChinaTimeItem(scrapy.Item):
    """中国平均时间"""
    value = scrapy.Field()
    type = scrapy.Field()
    day = scrapy.Field()
    site = scrapy.Field()

class ErrorTopItem(scrapy.Item):
    """故障统计"""
    monitor_name = scrapy.Field()
    type = scrapy.Field()
    value = scrapy.Field()
    day = scrapy.Field()
    site = scrapy.Field()

class MonitorAreaStasticItem(scrapy.Item):
    """监控地区统计"""
    monitor_name = scrapy.Field()
    type = scrapy.Field()
    province = scrapy.Field()
    area = scrapy.Field()
    mid = scrapy.Field()
    site = scrapy.Field()
    day = scrapy.Field()

class MonitorChartItem(scrapy.Item):
    """监控图表数据"""
    monitor_name = scrapy.Field()
    time = scrapy.Field()
    type = scrapy.Field()
    value = scrapy.Field()
    day = scrapy.Field()
    site = scrapy.Field()

class MonitorProvinceItem(scrapy.Item):
    """监控省份统计"""
    monitor_name = scrapy.Field()
    monitor_province = scrapy.Field()
    value = scrapy.Field()
    type = scrapy.Field()
    day = scrapy.Field()
    site = scrapy.Field()

class MonitorStasticItem(scrapy.Item):
    """监控统计"""
    mid = scrapy.Field()
    day = scrapy.Field()
    min = scrapy.Field()
    max = scrapy.Field()
    avg = scrapy.Field()
    time_st = scrapy.Field()
    all_time = scrapy.Field()
    site = scrapy.Field()

class MonitorTypeItem(scrapy.Item):
    """监控类型统计"""
    monitor_name = scrapy.Field()
    province = scrapy.Field()
    rate = scrapy.Field()
    catname = scrapy.Field()
    type_name = scrapy.Field()
    day = scrapy.Field()
    site = scrapy.Field()

class ProvinceTimeItem(scrapy.Item):
    """监控省份响应时间"""
    province_name = scrapy.Field()
    value = scrapy.Field()
    type = scrapy.Field()
    day = scrapy.Field()
    site = scrapy.Field()

class TypeTimeItem(scrapy.Item):
    """监控运营商响应时间"""
    type_name = scrapy.Field()
    value = scrapy.Field()
    type = scrapy.Field()
    day = scrapy.Field()
    site = scrapy.Field()

class BaiduTongjiItem(scrapy.Item):
    """百度统计"""
    access_time = scrapy.Field()
    area = scrapy.Field()
    keywords = scrapy.Field()
    entry_page = scrapy.Field()
    ip = scrapy.Field()
    user_id = scrapy.Field()
    visit_time = scrapy.Field()
    visit_pages = scrapy.Field()
    visitorType = scrapy.Field()
    visitorFrequency = scrapy.Field()
    lastVisitTime = scrapy.Field()
    endPage = scrapy.Field()
    deviceType = scrapy.Field()
    fromType = scrapy.Field()
    fromurl = scrapy.Field()
    fromAccount = scrapy.Field()
    isp = scrapy.Field()
    os = scrapy.Field()
    osType = scrapy.Field()
    browser = scrapy.Field()
    browserType = scrapy.Field()
    language = scrapy.Field()
    resolution = scrapy.Field()
    color = scrapy.Field()
    accessPage = scrapy.Field()
    antiCode = scrapy.Field()
    site = scrapy.Field()

class CrawlEconomicCalendarItem(scrapy.Item):
    """金10财经日历"""
    country = scrapy.Field()
    quota_name = scrapy.Field()
    pub_time = scrapy.Field()
    importance = scrapy.Field()
    former_value = scrapy.Field()
    predicted_value = scrapy.Field()
    published_value = scrapy.Field()
    influence = scrapy.Field()
    source_id = scrapy.Field()
    next_pub_time = scrapy.Field()
    pub_agent = scrapy.Field()
    pub_frequency = scrapy.Field()
    count_way = scrapy.Field()
    data_influence = scrapy.Field()
    data_define = scrapy.Field()
    funny_read = scrapy.Field()

class CrawlEconomicEventItem(scrapy.Item):
    """金10财经事件"""
    time = scrapy.Field()
    country = scrapy.Field()
    city = scrapy.Field()
    importance = scrapy.Field()
    event = scrapy.Field()
    date = scrapy.Field()

class CrawlEconomicHolidayItem(scrapy.Item):
    """金10财经假期"""
    time = scrapy.Field()
    country = scrapy.Field()
    market = scrapy.Field()
    holiday_name = scrapy.Field()
    detail = scrapy.Field()
    date = scrapy.Field()