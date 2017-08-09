## 运维爬虫项目
1. scrapy crawl jiankongbao -a www.91pme.com,m.91pme.com,www.91guoxin.com   
        监控宝爬虫，其中可配置爬取的网站，参数a：网站按名称以“,”分割
2. scrapy crawl jiankong-tongji -a www.91pme.com,m.91pme.com    
        同上
3. scrapy crawl baidu-tongji
        抓取百度统计项目，需要安装验证码识别库

        yum -y install python-image
        pip install pytesseract
4. 可以在命令中加 --logfile spider-name.log指定每一个spider的log文件
    
        scrapy crawl baidu-tongji --logfile ../logs/baidu-tongji.log

    或者修改lib/python2.7/site-packages/scrapy/crawler.py
        1. 注释掉class CrawlerProcess(CrawlerRunner):中，__init__中的configure_logging(self.settings)
        2. 在这个文件中的self.spidercls.update_settings(self.settings)的下一行添加configure_logging(self.settings)
        3. 在每个spider中添加

        class BaiduTongjiSpider(scrapy.Spider):
            custom_settings = {
                'LOG_FILE': '../logs/baidu_tongji_{dt}.log'.format(dt=datetime.datetime.now().strftime('%Y%m%d'))
            }

5. scrapy crawl cj-calendar -a args=start:2015-02-02,after:30,max:100
        抓取jin10财经日历项目
        参数：
            start:  抓取的开始时间，默认今天
            after:  抓到限定的时间之后往后抓取的天数，如没有给定max时，默认抓到今天，如果after=60，则再往后抓60天
            max:    从start开始往后抓取的天数，没有时默认抓取到当前时间