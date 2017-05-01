#!/usr/bin/env bash
pip install -r requirements.txt -t .
zip -r nmbs-realtime.zip .

 aws lambda update-function-code \
 --function-name NmbsRealtime \
 --zip-file fileb://nmbs-realtime.zip

rm nmbs-realtime.zip