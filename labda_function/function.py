#!/usr/bin/env python
# coding: utf-8

import json
import wget
import os
import glob
from requests_oauthlib import OAuth1Session
from urlparse import urljoin
from pyquery import PyQuery as pq
from pprint import pprint

#スクレイピング開始 画像のダウンロード
url = 'http://sugoroku.osaka/'

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
    filename = wget.download(url, "./images/"+str(i)+".jpg")
    pprint(filename)
    i = i+1

# Twitter API
CK = 'tesqN15WBtgAdUh7Vhmo324vx'
CS = '9W0032VdGypVazVlDZrPkNnJ0q4kS5gWgsyAvBHhUOoAuxWBIm'
AT = '4125247939-LDgZXnixcybiW4YrXPYbJug3qm8so8NVyfbx7kk'
AS = 'SIYLMtd7s9w06NZuJSj91HLsWOswvpaLtKZmlnRKgznKg'

url_media = "https://upload.twitter.com/1.1/media/upload.json"
url_text = "https://api.twitter.com/1.1/statuses/update.json"

# OAuth認証 セッションを開始
twitter = OAuth1Session(CK, CS, AT, AS)

# 画像投稿
files = {"media" : open('./images/1.jpg', 'rb')}
req_media = twitter.post(url_media, files = files)

# レスポンスを確認
if req_media.status_code != 200:
    print ("画像アップデート失敗: %s", req_media.text)
    exit()

# Media ID を取得
media_id = json.loads(req_media.text)['media_id']
print ("Media ID: %d" % media_id)

# Media ID を付加してテキストを投稿
params = {'status': '画像投稿テスト', "media_ids": [media_id]}
req_media = twitter.post(url_text, params = params)

# 再びレスポンスを確認
if req_media.status_code != 200:
    print ("テキストアップデート失敗: %s", req_text.text)
    exit()

test = './images/*'
r = glob.glob(test)
for i in r:
   os.remove(i)

print ("OK")
