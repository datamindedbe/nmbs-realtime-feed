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

 aws lambda update-function-code \
 --function-name NmbsRealtime \
 --zip-file fileb://deploy/package.zip



#rm -rv release/