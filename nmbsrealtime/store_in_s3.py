import os
from datetime import datetime

import boto3
import requests

from config import Config


def store_in_s3(url, bucket_name, key_prefix):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    print "retrieve url %s" % url
    response = requests.get(url)
    if response.status_code == 200:
        key_name = '%s/%s.protobuf' % (key_prefix, datetime.now().strftime('%Y/%m/%d/%H%M%S'))
        print "store url %s" % key_name
        bucket.put_object(Key=key_name, Body=response.content)


def lambda_handler(event, context):
    print event
    print context
    store_in_s3(os.environ['nmbs_realtime_feed_url'], os.environ['bucket'], os.environ['key_prefix'])


def run_local():
    config = Config()
    store_in_s3(config.feed_url, config.bucket, config.key_prefix)
