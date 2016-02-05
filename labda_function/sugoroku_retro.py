from requests_oauthlib import OAuth1Session
import commands, boto3, re, json

# Twitter API
CK = 'tesqN15WBtgAdUh7Vhmo324vx'
CS = '9W0032VdGypVazVlDZrPkNnJ0q4kS5gWgsyAvBHhUOoAuxWBIm'
AT = '4125247939-LDgZXnixcybiW4YrXPYbJug3qm8so8NVyfbx7kk'
AS = 'SIYLMtd7s9w06NZuJSj91HLsWOswvpaLtKZmlnRKgznKg'

UPDATE_URL = 'https://api.twitter.com/1.1/statuses/update.json'

AWS_S3_BUCKET_NAME = "***" # * enter your backet name *

def _(cmd):
    return commands.getoutput(cmd)

# get "keyName" obj from S3
def _getTweetList(keyName):
    s3 = boto3.resource('s3', region_name='ap-northeast-1')
    bucket = s3.Bucket(AWS_S3_BUCKET_NAME)
    obj = bucket.Object(keyName)

    response = obj.get()
    body = response['Body'].read()
    return body.decode('utf-8')

# tweet text
def _tweet(text):
    params = {"status": text }
    twitter = OAuth1Session(CK, CS, AT, AS)
    req = twitter.post(UPDATE_URL, params = params)

    if req.status_code == 200:
        return text
    else:   
        return req.status_code

def handler(event, context):
    # yyyy_mm.js
    GET_OBJECT_KEY_NAME = _('date +"%Y_%m" --date "1 year ago"') + ".js"
    tweetList = _getTweetList(GET_OBJECT_KEY_NAME)

    # delete first line ("Grailbird.data.tweets_yyyy_mm =")
    tweetListJson = re.sub(r"^.*\n", "", tweetList)
    tweets = json.loads(tweetListJson)

    # yyyy-mm-dd hh:m
    targetDateTime = _('date +"%Y-%m-%d %H:%M" --date "1 year ago"')[:-1]
    targetTweetList = []
    for tweet in tweets:
        if tweet["created_at"].startswith(targetDateTime):
            # replace mention and hashtag mark
            text = tweet["text"].replace('@','*').replace('#','+')
            targetTweetList.append(text)

    # desc -> asc
    targetTweetList.reverse()

    for text in targetTweetList:
        _tweet(text)
