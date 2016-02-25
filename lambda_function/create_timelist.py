from boto3 import Session, resource
from pprint import pprint
import json, random

TMP_DIR = '/tmp'
AWS_S3_BUCKET_NAME = "* enter your backet name *"
AWS_S3_OBJECT_NAME = "TimeList.json"

def _exists(bucket, key):
    return 'Contents' in Session().client('s3').list_objects(Prefix=key, Bucket=bucket)

def _getTimeList(keyName):
    if( _exists(AWS_S3_BUCKET_NAME, keyName) == False ):
        print("No JSON FILE"); return False

    s3 = resource('s3', region_name='ap-northeast-1')
    obj = s3.Bucket(AWS_S3_BUCKET_NAME).Object(keyName)

    response = obj.get()
    body = response['Body'].read()
    return body.decode('utf-8')

def _createList(num):
    start = 0
    advance = 60/num
    end = advance

    list = {}
    for x in xrange(1,num+1):
        list["t"+str(x)] = random.randint(start, end)
        start = end
        end = end + advance

    return list

def _putTimeList(data):
    f = open(TMP_DIR+"/output.json",'w+')
    json.dump(data,f,ensure_ascii=False)
    f.close()

    s3 = resource('s3', region_name='ap-northeast-1')
    obj = s3.Object(AWS_S3_BUCKET_NAME, AWS_S3_OBJECT_NAME)
    ret = obj.upload_file(TMP_DIR+"/output.json")
    return ret

def lambda_handler(event, context):
    json_data = _getTimeList(AWS_S3_OBJECT_NAME)
    if (json_data != False):
        dict_data = json.loads(json_data)
        timeList = []
        for row in dict_data:
            newrow = {'hour':row['hour'],'tweet':row['tweet']}
            if (newrow['tweet'] > 0):
                list = _createList(int(newrow['tweet']))
                newrow.update(list)
            timeList.append(newrow)
        pprint(timeList)
        ret = _putTimeList(timeList)
        return ret
    else:
        return "no object"
