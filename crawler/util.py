import hashlib
import contextlib
import urllib2
import os
import datetime
import crawler.settings as setting
from urllib2 import URLError
import logging

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

    print img_name
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