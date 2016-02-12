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

UPDATE_URL = 'https://api.twitter.com/1.1/statuses/update.json'
UPDATE_MEDIA = 'https://upload.twitter.com/1.1/media/upload.json'
IMAGES_SELECTOR = '.sing-cop,.pageImg'
IMAGES_NUM = 4

AWS_S3_BUCKET_NAME = "osaka-sugoroku-bot" # * enter your backet name *
INTERVAL = 5

def _exists(bucket, key):
    return 'Contents' in Session().client('s3').list_objects(Prefix=key, Bucket=bucket)

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
        filename = '/tmp/'+str(count)+ext
        urllib.urlretrieve(img_url, filename)
        filenames.append(filename)
        count = count+1

    return filenames

def _getTweetList(keyName):
    if( _exists(AWS_S3_BUCKET_NAME, keyName) == False ):
        print("No JSON FILE"); return False

    s3 = resource('s3', region_name='ap-northeast-1')
    obj = s3.Bucket(AWS_S3_BUCKET_NAME).Object(keyName)

    response = obj.get()
    body = response['Body'].read()
    return body.decode('utf-8')

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

def _testAllFunction(event, context):
    ret = {}
    ret['getImages']        = _getImages("http://sugoroku.osaka/?p=6185")
    ret['uploadTweetImage'] = _uploadTweetImage(['/tmp/1.jpg', '/tmp/2.jpg', '/tmp/3.jpg', '/tmp/4.jpg'])
    ret['tweet']            = _tweet("Hello", [])
    ret['exists']           = _exists(AWS_S3_BUCKET_NAME, '20160209.json')
    ret['getTweetList']     = _getTweetList('20160209.json')

    return ret

def lambda_handler(event, context):
    ret = {}
    jst = pytz.timezone('Asia/Tokyo')
    jst_now = datetime.now(jst)

    today = jst_now.strftime("%Y%m%d")
    object_name = today + ".json"
    pprint(object_name)

    json_data = _getTweetList(object_name)

    if ( json_data != False ):
        tweets = json.loads(json_data)
        td_now = timedelta(hours=jst_now.hour, minutes=jst_now.minute)
        ret['main'] = [{'now': str(jst_now.hour)+':'+str(jst_now.minute)}]

        targetTweetList = []
        for tweet in tweets:
            td_tweet = timedelta(hours=tweet["hour"], minutes=tweet["minute"])
            if(td_now < td_tweet and (td_tweet - td_now).seconds/60 < INTERVAL):
                # targetTweetList.append( { "text" : tweet["text"], "link": tweet["link"] } )
                targetTweetList.append( { "text" : str(tweet["hour"])+":"+str(tweet["minute"]),"link": tweet["link"] } )

        pprint(targetTweetList)
        for ttweet in targetTweetList:
            images = _getImages(ttweet["link"])
            media_ids = _uploadTweetImage(images)
            status = _tweet(ttweet["text"], media_ids)
            ret['main'].append(status)

    else:
        ret['main'] = "no data"

    return ret
