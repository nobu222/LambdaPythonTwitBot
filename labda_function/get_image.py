#!/usr/bin/env python
# coding: utf-8

from urlparse import urljoin
from pyquery import PyQuery as pq
from pprint import pprint
import wget

url = 'http://www.yahoo.co.jp'

dom = pq(url)
result = set()
for img in dom('img').items():
    img_url = img.attr['src']
    if img_url.startswith('http'):
        result.add(img_url)
    else:
        result.add(urljoin(url, img_url))

pprint(result)

i = 1
for url in result:
    filename = wget.download(url, str(i)+".jpg")
    pprint(filename)
    i = i+1
