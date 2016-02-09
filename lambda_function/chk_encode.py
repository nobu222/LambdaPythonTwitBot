# -*- coding:utf-8 -*-
import sys

def lambda_handler(event, context):
    data_orig = "日本語"
    print type( data_orig )
    data_unic = data_orig.decode( 'utf-8' )
    print type( data_unic )
    print data_unic

    print sys.getdefaultencoding()
