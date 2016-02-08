from requests_oauthlib import OAuth1Session
import commands, boto3, re, json, datetime

# Twitter API
CK = 'tesqN15WBtgAdUh7Vhmo324vx'
CS = '9W0032VdGypVazVlDZrPkNnJ0q4kS5gWgsyAvBHhUOoAuxWBIm'
AT = '4125247939-LDgZXnixcybiW4YrXPYbJug3qm8so8NVyfbx7kk'
AS = 'SIYLMtd7s9w06NZuJSj91HLsWOswvpaLtKZmlnRKgznKg'

UPDATE_URL = 'https://api.twitter.com/1.1/statuses/update.json'

AWS_S3_BUCKET_NAME = "osaka-sugoroku-bot" # * enter your backet name *

INTERVAL = 10

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
    _tweet("hogehoge")
