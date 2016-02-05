from requests_oauthlib import OAuth1Session

# Consumer Key          : CK
# Consumer Secret       : CS
# Access Token          : AT
# Accesss Token Secert  : AS

CK = 'rT8ZIjnHYC5Iucm595Ys7JZLr'
CS = 'PAPneNn8PCnyXinnzYvstjITUSp6y03FWJwf8J5eYc4VBj6USW'
AT = '3343400353-HSk37wIT5jdM14DYNkHdhabHuAGttEdLxeQa61d'
AS = 'uuNxAKJlUuFCG493GjBfMGkQmTJLe0WQpTE7RyMVrOBvs'

URL = 'https://api.twitter.com/1.1/statuses/update.json'


def handler(event, context):
#    msg = event['Records'][0]['Sns']['Message']
    params = {"status": msg }

    twitter = OAuth1Session(CK, CS, AT, AS)
    req = twitter.post(URL, params = params)

    if req.status_code == 200:
        return msg
    else:   
        return req.status_code

