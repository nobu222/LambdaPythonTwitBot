from pyquery import PyQuery
import json

print('Loading function')

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    dom = PyQuery("http://www.google.com")
    return dom
    #raise Exception('Something went wrong')
