from boto3 import Session, resource
from requests_oauthlib import OAuth1Session
from bs4 import BeautifulSoup
import pytz 
from pprint import pprint
from datetime import datetime,timedelta
import urllib2
import random
import os.path
import urllib
import json

# Twitter API
CK = 'tesqN15WBtgAdUh7Vhmo324vx'
CS = '9W0032VdGypVazVlDZrPkNnJ0q4kS5gWgsyAvBHhUOoAuxWBIm'
AT = '4125247939-LDgZXnixcybiW4YrXPYbJug3qm8so8NVyfbx7kk'
AS = 'SIYLMtd7s9w06NZuJSj91HLsWOswvpaLtKZmlnRKgznKg'

TMP_DIR = '/tmp'

UPDATE_URL = 'https://api.twitter.com/1.1/statuses/update.json'
UPDATE_MEDIA = 'https://upload.twitter.com/1.1/media/upload.json'
IMAGES_SELECTOR = '.sing-cop,.pageImg'
IMAGES_NUM = 4

AWS_S3_BUCKET_NAME = "osaka-sugoroku-bot" # * enter your backet name *

def _exists(bucket, key):
    return 'Contents' in Session().client('s3').list_objects(Prefix=key, Bucket=bucket)

def _getS3Object(object_name):
    if( _exists(AWS_S3_BUCKET_NAME, object_name) == False ):
        print("No JSON FILE"); return False

    s3 = resource('s3', region_name='ap-northeast-1')
    obj = s3.Bucket(AWS_S3_BUCKET_NAME).Object(object_name)
    response = obj.get()
    body = response['Body'].read()

    return body.decode('utf-8')

def _checkTimeList(time):
    body = _getS3Object('TimeList.json')
    list = json.loads(body)
    for row in list:
        if (time.hour == int(row['hour'])):
            for k,v in row.iteritems():
                if (k != 'hour' and k != 'tweet' and time.minute == v):
                    return True
    return False

def _pickupTweet():
    body = _getS3Object('TweetList.json')
    list = json.loads(body)
    tweet = list[random.randint(0,len(list))]

    return tweet

def _getImages(url):
    img_urls = []
    html = urllib2.urlopen(url)
    soup = BeautifulSoup(html, "html.parser")

    for img in soup.select(IMAGES_SELECTOR):
        img_urls.append(img['src']) 

    if len(img_urls) > IMAGES_NUM:
        fetch_urls = random.sample(img_urls, IMAGES_NUM)
    else:
        fetch_urls = img_urls

    filenames = []
    count = 1
    for img_url in fetch_urls:
        name, ext = os.path.splitext(img_url)
        filename = TMP_DIR+'/'+str(count)+ext
        urllib.urlretrieve(img_url, filename)
        filenames.append(filename)
        count = count+1

    return filenames

def _uploadTweetImage( images ):
    media_ids = []
    tw = OAuth1Session(CK, CS, AT, AS)

    for image in images:
        files = {"media": open(image, 'rb')}
        req_media = tw.post(UPDATE_MEDIA, files = files)
        if req_media.status_code == 200:
            media_ids.append(json.loads(req_media.text)['media_id'])
        else:
            media_ids.append(req_media.status_code)

    return media_ids

def _tweet(text, media_ids):
    params = {"status": text, "media_ids": media_ids}
    tw = OAuth1Session(CK, CS, AT, AS)
    req = tw.post(UPDATE_URL, params = params)

    if req.status_code == 200:
        return text
    else:
        return req.status_code

def lambda_handler(event, context):
    ret = {}
    jst = pytz.timezone('Asia/Tokyo')
    jst_now = datetime.now(jst)

    flag = _checkTimeList(jst_now)
    if (flag):
        tweet = _pickupTweet()
        images = _getImages(tweet["link"])
        media_ids = _uploadTweetImage(images)
        status = _tweet(tweet["text"], media_ids)
        return status
    else:
        pprint(flag)
        return flag

