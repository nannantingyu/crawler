# -*- coding: utf-8 -*-

# Scrapy settings for crawler project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
import logging
from os import environ
from os.path import join, dirname
from dotenv import load_dotenv

APP_DIR = dirname(dirname(__file__))
load_dotenv(join(APP_DIR, '.env'))

BOT_NAME = 'crawler'
SPIDER_MODULES = ['crawler.spiders']
NEWSPIDER_MODULE = 'crawler.spiders'

#FEED_URI = 'file:///' + join(APP_DIR, 'data/spider.csv')
#FEED_FORMAT = 'CSV'
#FEED_EXPORT_ENCODING = 'utf-8'

LOG_LEVEL = logging.INFO
#LOG_STDOUT = True
LOG_FILE = join(APP_DIR, 'logs/spider.log')
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# 图片下载设置
IMAGES_STORE = environ.get("images_path")
IMAGES_EXPIRES = 30  # 30天内抓取的都不会被重抓
# 图片链接前缀
URL_PREFIX = environ.get("images_url_prefix")

DATABASE = {
    'drivername': 'mysql+pymysql',
    'host':     environ.get("db_host"),
    'port':     environ.get("db_port"),
    'username': environ.get("db_username"),
    'password': environ.get("db_password"),
    'database': environ.get("db_database"),
    'query': {'charset': 'utf8'}
}

ITEM_PIPELINES = {
    # 'crawler.pipelines.DuplicatesPipeline': 1,
    #'crawler.pipelines.FilterWordsPipeline': 2,
    'crawler.pipelines.database.JianKongPipeline': 3,
}

REDIRECT_ENABLED = False

DOWNLOADER_MIDDLEWARES = {
    # 这里是下载中间件
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'crawler.middlewares.RotateUserAgentMiddleware': 400,
    'crawler.middlewares.CookiesSaveingMiddleware': 699,
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# 几个反正被Ban的策略设置
DOWNLOAD_TIMEOUT = 60
DOWNLOAD_DELAY = 5
# 禁用Cookie
COOKIES_ENABLES = True
COOKIES_DEBUG = False

# 扩展-定义爬取数量
CLOSESPIDER_ITEMCOUNT = 0

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'crawler (+http://www.yourdomain.com)'

# Obey robots.txt rules
# 是否遵循robot协议，scrapy默认先去爬取 host/robots.txt，如果遵循协议，会按照robots.txt规定的抓取
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'crawler.middlewares.CrawlerSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'crawler.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    'crawler.pipelines.CrawlerPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
