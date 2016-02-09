from datetime import datetime
from boto3 import Session, resource
from requests_oauthlib import OAuth1Session
import sys, json, datetime

# Twitter API
CK = 'tesqN15WBtgAdUh7Vhmo324vx'
CS = '9W0032VdGypVazVlDZrPkNnJ0q4kS5gWgsyAvBHhUOoAuxWBIm'
AT = '4125247939-LDgZXnixcybiW4YrXPYbJug3qm8so8NVyfbx7kk'
AS = 'SIYLMtd7s9w06NZuJSj91HLsWOswvpaLtKZmlnRKgznKg'

UPDATE_URL = 'https://api.twitter.com/1.1/statuses/update.json'
AWS_S3_BUCKET_NAME = "osaka-sugoroku-bot" # * enter your backet name *
INTERVAL = 10

def _exists(bucket, key):
    return 'Contents' in Session().client('s3').list_objects(Prefix=key, Bucket=bucket)

def _getTweetList(keyName):
    if( _exists(AWS_S3_BUCKET_NAME, keyName) == False ):
        print("No JSON FILE"); return False

    s3 = resource('s3', region_name='ap-northeast-1')
    obj = s3.Bucket(AWS_S3_BUCKET_NAME).Object(keyName)

    response = obj.get()
    body = response['Body'].read()
    return body.decode('utf-8')

def _tweet(text):
    params = {"status": text}
    tw = OAuth1Session(CK, CS, AT, AS)
    req = tw.post(UPDATE_URL, params = params)

    if req.status_code == 200:
        return text
    else:
        return req.status_code

def lambda_handler(event, context):
    # ret = _tweet("hogehoge")
    # ret = _exists(AWS_S3_BUCKET_NAME, '20160209.json')
    ret = _getTweetList('20160209.json')

    today = datetime.datetime.now().strftime("%Y%m%d")
    object_name = today + ".json"
    json_data = _getTweetList(object_name)

    if ( json_data != False ):
        tweets = json.loads(json_data)
        now = datetime.datetime.now() # get current time
        td_now = datetime.timedelta(hours=now.hour, minutes=now.minute)

        targetTweetList = []
        for tweet in tweets:
            td_tweet = datetime.timedelta(hours=tweet["hour"], minutes=tweet["minute"])
            if(td_now < td_tweet and (td_tweet - td_now).seconds/60 < INTERVAL):
                targetTweetList.append( tweet["text"] )
    else:
        print "no data"

    for text in targetTweetList:
        _tweet(text)

    return
