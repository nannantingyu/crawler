# -*- coding: utf-8 -*-
import hashlib
import contextlib
import logging
import urllib2
import os
import datetime
import re
import sys
import json
from urlparse import urljoin, urlparse
import crawler.settings as setting
from crawler.items import ArticleItem
from urllib2 import URLError
import logging

reload(sys)
sys.setdefaultencoding('utf8')

def get_sourceid(url):
    ''' 根据url 生成MD5作为原新闻id '''
    md5 = hashlib.md5()
    md5.update(url)
    return md5.hexdigest()

class ArticleParser(object):
    ''' 新闻文章分析类'''
    base_url = ''
    item = None

    def __init__(self, response):
        self.response = response

    def parse(self):
        '''分析文章'''
        try:
            self.base_url = self.response.url
            self.item = ArticleItem()
            # body
            self.get_body()
            self.item['source_id'] = get_sourceid(self.base_url)

            if self.item['body'] is not None:
                return self.item

        except Exception as e:
            logging.error(e)

    def get_body(self):
        ''' 获取文章内容 '''
        json_data = json.loads(self.response.body)
        htmlcontent = json_data['text']
        self.item['author'] = json_data['Author']['nick'] if 'Author' in json_data else ""
        pat_img = re.compile(r'\ssrc="(.*?\.[jpg|gif|png]+)"')

        now = datetime.datetime.now()
        img_urlpath = "%d/%d/%d" % (now.year, now.month, now.day)

        img_path = os.path.join(setting.IMAGES_STORE, img_urlpath)
        is_exists = os.path.exists(img_path)
        if not is_exists:
            os.makedirs(img_path)

        uuids = []
        for _, match in enumerate(pat_img.finditer(htmlcontent)):
            img_name = match.group(1)
            full_img_url = None
            if img_name.startswith('.'):
                img_name = img_name[2:]
            if img_name.startswith('https://cdn.jin10.com/video/pic') or img_name.startswith('http://cdn.jin10x.com/news/pic'):
                full_img_url = urljoin(self.base_url, img_name)
                img_name = img_name.split('/')[-1]


            if full_img_url is None:
                full_img_url = urljoin(self.base_url, img_name)

            full_img_path = os.path.join(img_path, img_name)
            uuids.append((img_urlpath + '/' + img_name).replace("\\", "/"))
            if os.path.isfile(full_img_path):
                continue

            try:
                with contextlib.closing(urllib2.urlopen(full_img_url)) as fimg:
                    with open(full_img_path, 'wb') as bfile:
                        bfile.write(fimg.read())
            except URLError as e:
                logging.error("[crawl image] failed open image url: " + full_img_url)

        htmlcontent = pat_img.sub(Nth(uuids), htmlcontent)
        self.item['body'] = htmlcontent

class Nth(object):
    ''' 替换新闻内容中的图片url '''
    def __init__(self, uuids):
        self.uuids = uuids
        self.calls = 0

    def __call__(self, matchobj):
        strreplace = " src=\"" + setting.URL_PREFIX + \
            self.uuids[self.calls] + "\""

        self.calls += 1
        return strreplace
