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