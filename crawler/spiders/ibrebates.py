# -*- coding: utf-8 -*-
import scrapy
import redis
import datetime
import random
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from crawler.items import IbrebatesItem

class IbrebatesSpider(scrapy.Spider):
    name = 'ibrebates'
    allowed_domains = ['www.ibrebates.com']
    start_urls = ['http://www.ibrebates.com/jys_list/']
    base_url = 'http://www.ibrebates.com'
    detail_urls = []

    custom_settings = {
        'LOG_FILE': '../logs/ibrebates_{dt}.log'.format(dt=datetime.datetime.now().strftime('%Y%m%d'))
    }

    index = 0

    def parse(self, response):
        item_lists = response.xpath('.//div[@class="traders_list"]/div[@class="list_left"]/a')
        for it in item_lists:
            href = it.xpath('./@href').extract_first()

            self.detail_urls.append("{baseurl}{url}".format(baseurl=self.base_url, url=href))

        yield scrapy.Request(self.detail_urls[self.index], meta={'cookiejar': self.name, 'handle_httpstatus_list': [301, 302]},
                             callback=self.parse_detail)

    def parse_detail(self, response):
        name = response.xpath('.//div[@class="traders_text"]/p/text()').extract_first()
        info = response.xpath('.//div[@class="p_30"]//div[@id="con_taba_1"]')
        description = info.xpath('.//div[@class="ptjs_2"]')[0]
        description = description.xpath('.//text()').extract()
        description = str(description[2]).strip() if len(description) > 3 else ""

        dc = info.xpath('.//div[@class="ptjs_2"]')[1].xpath('.//table')
        spread_type = dc.xpath('.//tr')[0]
        spread_type = spread_type.xpath('.//td[2]/text()').extract_first()
        spread_type = spread_type.strip() if spread_type is not None else ""

        om_spread = dc.xpath('.//tr[2]/td[2]/text()').extract_first()
        gold_spread = dc.xpath('.//tr[2]/td[4]/text()').extract_first()

        offshore = dc.xpath('.//tr[3]/td[2]/text()').extract_first()
        a_share = dc.xpath('.//tr[3]/td[4]/text()').extract_first()

        base_info = info.xpath('.//div[@class="ptjs_2"]')[2].xpath('.//table')
        regulatory_authority = base_info.xpath('.//tr[1]/td[2]/text()').extract_first()
        trading_varieties = base_info.xpath('.//tr[1]/td[4]/text()').extract_first()
        platform_type = base_info.xpath('.//tr[2]/td[2]/text()').extract_first()
        account_type = base_info.xpath('.//tr[2]/td[4]/text()').extract_first()
        scalp = base_info.xpath('.//tr[3]/td[2]/text()').extract_first()
        hedging = base_info.xpath('.//tr[3]/td[4]/text()').extract_first()
        min_transaction = base_info.xpath('.//tr[4]/td[2]/text()').extract_first()
        least_entry = base_info.xpath('.//tr[4]/td[4]/text()').extract_first()
        maximum_leverage = base_info.xpath('.//tr[5]/td[2]/text()').extract_first()
        maximum_trading = base_info.xpath('.//tr[5]/td[4]/text()').extract_first()
        deposit_method = base_info.xpath('.//tr[6]/td[2]/text()').extract_first()
        entry_method = base_info.xpath('.//tr[6]/td[4]/text()').extract_first()
        commission_fee = base_info.xpath('.//tr[7]/td[2]/text()').extract_first()
        entry_fee = base_info.xpath('.//tr[7]/td[4]/text()').extract_first()
        account_currency = base_info.xpath('.//tr[8]/td[2]/text()').extract_first()
        rollovers = base_info.xpath('.//tr[8]/td[4]/text()').extract_first()
        explosion_proportion = base_info.xpath('.//tr[9]/td[2]/text()').extract_first()
        renminbi = base_info.xpath('.//tr[9]/td[4]/text()').extract_first()

        item = IbrebatesItem()
        item['name'] = name
        item['description'] = description
        item['spread_type'] = spread_type
        item['om_spread'] = om_spread
        item['gold_spread'] = gold_spread
        item['offshore'] = offshore
        item['a_share'] = a_share
        item['regulatory_authority'] = regulatory_authority
        item['trading_varieties'] = trading_varieties
        item['platform_type'] = platform_type
        item['account_type'] = account_type
        item['scalp'] = scalp
        item['hedging'] = hedging
        item['min_transaction'] = min_transaction
        item['least_entry'] = least_entry
        item['maximum_leverage'] = maximum_leverage
        item['maximum_trading'] = maximum_trading

        item['deposit_method'] = deposit_method
        item['entry_method'] = entry_method
        item['commission_fee'] = commission_fee
        item['entry_fee'] = entry_fee
        item['account_currency'] = account_currency
        item['rollovers'] = rollovers
        item['explosion_proportion'] = explosion_proportion
        item['renminbi'] = renminbi

        yield item
        print self.index, len(self.detail_urls)
        self.index += 1
        if self.index < len(self.detail_urls):
            yield scrapy.Request(self.detail_urls[self.index],
                                 meta={'cookiejar': self.name, 'handle_httpstatus_list': [301, 302]},
                                 callback=self.parse_detail)