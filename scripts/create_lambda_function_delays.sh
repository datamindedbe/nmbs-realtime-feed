#!/usr/bin/env bash
rm -r deploy/
mkdir deploy/
virtualenv venv
source venv/bin/activate
pip install --upgrade -r requirements.txt
cp -rv venv/lib/python2.7/site-packages/* deploy
cp -rv libs/* deploy
cp -rv nmbsrealtime/*.py deploy
cp -rv scripts/ deploy/scripts
touch deploy/google/__init__.py # otherwise can't import google.transit
cd deploy
zip -r package.zip ./*
cd ../

aws lambda delete-function \
--function-name NmbsCalculateDelays \

aws lambda create-function \
--region eu-west-1 \
--function-name NmbsCalculateDelays \
--zip-file fileb://deploy/package.zip \
--role arn:aws:iam::453068821114:role/lambda_full_access_s3  \
--handler compute_delay.lambda_handler \
--runtime python2.7 \
--timeout 90 \
--memory-size 128



#rm -rv release/