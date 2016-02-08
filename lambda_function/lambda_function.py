from datetime import datetime
from urllib2 import urlopen
import requests # XXX added
 
SITE = 'https://www.amazon.com/'  # URL of the site to check
EXPECTED = 'Online Shopping'  # String expected to be on the page
 
 
def validate(res):
    '''Return False to trigger the canary
 
    Currently this simply checks whether the EXPECTED string is present.
    However, you could modify this to perform any number of arbitrary
    checks on the contents of SITE.
    '''
    return EXPECTED in res
 
 
def lambda_handler(event, context):
    print('Checking {} at {}...'.format(SITE, event['time']))
    try:
        #if not validate(urlopen(SITE).read()):
        if not validate(requests.get(SITE).text): # XXX changed
            raise Exception('Validation failed')
    except:
        print('Check failed!')
        raise
    else:
        print('Check passed!')
        return event['time']
    finally:
        print('Check complete at {}'.format(str(datetime.now())))
