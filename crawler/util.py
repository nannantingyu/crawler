import hashlib
import contextlib
import urllib2
import os
import datetime
import crawler.settings as setting
from urllib2 import URLError
import logging
import time
import re

def get_url_param(url):
    if "?" not in url:
        return None

    url = url.split("?")[-1]
    params = {}
    for param in url.split("&"):
        pa = param.split("=")
        params[pa[0]] = pa[1]

    return params

def get_sourceid(url):
    md5 = hashlib.md5()
    md5.update(url)
    return md5.hexdigest()

def downfile(full_img_url, img_name):
    now = datetime.datetime.now()
    img_urlpath = "%d/%d/%d" % (now.year, now.month, now.day)
    img_path = os.path.join(setting.IMAGES_STORE, img_urlpath)
    if not os.path.exists(img_path):
        os.makedirs(img_path)

    try:
        full_img_path = os.path.join(img_path, img_name).replace("\\", "/")

        with contextlib.closing(urllib2.urlopen(full_img_url)) as fimg:
            with open(full_img_path, 'wb') as bfile:
                bfile.write(fimg.read())
    except URLError as e:
        logging.error("[crawl image] failed open image url [UrlError]: " + full_img_url)
    except ValueError as ve:
        logging.error("[crawl image] failed open image url [ValueError]: " + full_img_url)
    except Exception as e:
        logging.error("[crawl image] failed open image url [OtherError]: " + full_img_url)

    return os.path.join(setting.URL_PREFIX, img_urlpath, img_name).replace("\\", "/")

def img_downloader(img_path, _img_name=None):
    now = datetime.datetime.now().strftime("%Y%m%d")
    save_path = os.path.join(setting.IMAGES_STORE, now)

    is_exists = os.path.exists(save_path)
    if not is_exists:
        os.makedirs(save_path)

    r = re.compile(r".*?mmbiz_(.*?)\/(.*?\/).*?")

    try:
        if _img_name is None:
            img_names = r.findall(img_path)
            if len(img_names) == 0:
                r_1 = re.compile(r"mmbiz\/(.*?)\/")
                img_names = r_1.findall(img_path)
                img_name = "{name}.{sufix}".format(name=img_names[0].strip().replace(r"/", ""),
                                                   sufix='jpg')
            else:
                img_name = "{name}.{sufix}".format(name=img_names[0][1].strip().replace(r"/", ""), sufix=img_names[0][0])

        else:
            img_name = _img_name

    except IndexError as err:
        logging.error("[down image error]: " + img_path)
        img_name = str(int(time.time())) + '.jpg'


    full_img_path = os.path.join(save_path, img_name)
    # print img_path, img_name
    with contextlib.closing(urllib2.urlopen(img_path)) as fimg:
        with open(full_img_path, 'wb') as bfile:
            bfile.write(fimg.read())

    return os.path.join(now, img_name).replace("\\", "/")

def handle_body(body):
    htmlcontent = body
    img_src_pat = re.compile(r'\ssrc="(.*?)"')

    now = datetime.datetime.now()
    img_urlpath = datetime.datetime.now().strftime("%Y%m%d")

    img_path = os.path.join(setting.IMAGES_STORE, img_urlpath)
    is_exists = os.path.exists(img_path)
    if not is_exists:
        os.makedirs(img_path)

    img_name_pat = re.compile(r".*/(.*\..*)")
    uuids = []
    for _, match in enumerate(img_src_pat.finditer(htmlcontent)):
        img_src = match.group(1)
        # img_names = img_name_pat.findall(img_src)
        # img_name = "{name}.{sufix}".format(name=img_names[0][1].strip().replace(r"/", ""), sufix=img_names[0][0])

        img_names = img_name_pat.findall(img_src)
        if len(img_names) == 0:
            img_name = "{name}.{sufix}".format(name=str(int(time.time())),
                                                   sufix='jpg')
        else:
            img_name = img_names[0]


        full_img_path = os.path.join(img_path, img_name).replace("\\", "/")
        # print img_src

        uuids.append(os.path.join(img_urlpath, img_name).replace("\\", "/"))
        if os.path.isfile(full_img_path):
            continue

        try:
            with contextlib.closing(urllib2.urlopen(img_src)) as fimg:
                with open(full_img_path, 'wb') as bfile:
                    bfile.write(fimg.read())
        except urllib2.URLError as e:
            logging.error("[crawl image] failed open image url: " + img_src)

    htmlcontent = img_src_pat.sub(Nth(uuids), htmlcontent)

    return htmlcontent

class Nth(object):
    def __init__(self, uuids):
        self.uuids = uuids
        self.calls = 0

    def __call__(self, matchobj):
        strreplace = " src=\"" + setting.URL_PREFIX + self.uuids[self.calls] + "\""

        self.calls += 1
        return strreplace