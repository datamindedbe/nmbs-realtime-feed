#!/usr/bin/env bash
pip install -r requirements.txt -t .
zip -r nmbs-realtime-s3.zip store_in_s3/

aws lambda create-function \
--region eu-west-1 \
--function-name NmbsRealtime \
--zip-file fileb://nmbs-realtime-s3.zip \
--role arn:aws:iam::453068821114:role/lambda_full_access_s3  \
--handler s3.lambda_handler \
--runtime python2.7 \
--timeout 15 \
--memory-size 128

rm nmbs-realtime.zip