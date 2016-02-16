from boto3 import Session, resource
from requests_oauthlib import OAuth1Session
from pprint import pprint
import json

# Twitter API
CK = 'tesqN15WBtgAdUh7Vhmo324vx'
CS = '9W0032VdGypVazVlDZrPkNnJ0q4kS5gWgsyAvBHhUOoAuxWBIm'
AT = '4125247939-LDgZXnixcybiW4YrXPYbJug3qm8so8NVyfbx7kk'
AS = 'SIYLMtd7s9w06NZuJSj91HLsWOswvpaLtKZmlnRKgznKg'

FOLLOWERS_LIST_URL     = 'https://api.twitter.com/1.1/followers/list.json'
FRIENDSHIPS_CREATE_URL = 'https://api.twitter.com/1.1/friendships/create.json'
STATUSES_USERTIMELINE_URL = 'https://api.twitter.com/1.1/statuses/user_timeline.json'

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

def _getFollowers():
    params = {"cursor":"-1","screen_name":"Yo_twitapi","skip_status":True,"include_user_entities":False, "count":"20"}
    tw = OAuth1Session(CK, CS, AT, AS)
    req = tw.get(FOLLOWERS_LIST_URL, params = params)
    pprint(req)

    if req.status_code == 200:
        return json.loads(req.text)
    else:
        return req.status_code

def _findList(text, lists):
    if type(lists) == list or type(lists) == tuple:
        values = lists
    elif type(lists) == dict:
        values = lists.values()
    else:
        values = [lists]

    for val in values:
        if val in text:
            return True
    return False

def _createFriend(user_id):
    params = {"user_id":user_id}
    tw = OAuth1Session(CK, CS, AT, AS)
    req = tw.post(FRIENDSHIPS_CREATE_URL, params = params)
    pprint(req)

    if req.status_code == 200:
        return json.loads(req.text)
    else:
        return req.status_code

def lambda_handler(event, context):
    ids = _getFollowers()
    # no followers case
    if 'users' not in ids:
        return "no id[users] data"

    blacklist = _getS3Object('BlackWord.json')
    if blacklist:
        lists = []
        friends = []
        for word in json.loads(blacklist):
            lists.append(word['word'])
        for user in ids['users']:
            if user['following'] == False and user['blocking'] == False and user['follow_request_sent'] == False:
                flag1 = _findList(user['name'],lists)
                flag2 = _findList(user['description'],lists)
                if flag1 == False and flag2 == False:
                    status = _createFriend(user['id'])
                    friends.append(user['screen_name'])
        return friends
    else:
        return 'no blacklist data'

