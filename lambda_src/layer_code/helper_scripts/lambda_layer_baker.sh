#!/bin/bash

S3_BUCKET='myst-layer'

# Prepare AWS XRay Lambda Layer
mkdir -p /tmp/layer-xray
cd /tmp/layer-requests
rm -rf *
pip3.7 install aws-xray-sdk -t ./python
# Slim the package
cd ./python
find . -type d -name "tests" -exec rm -rfv {} +
find . -type d -name "__pycache__" -exec rm -rfv {} +
rm -r *.whl *.dist-info __pycache__




cd ..
zip -r9 -q aws_xray_python_37.zip ./python 
# zip -r9 -q aws_xray_python_37.zip . -x \*.pyc ./python/pip\* ./python/setuptools\* ./python/wheel\* ./base_pkg\*

aws s3 cp aws_xray_python_37.zip s3://$S3_BUCKET/laws_xray_python_37.zip --profile elf

aws lambda publish-layer-version \
  --layer-name aws_xray \
  --compatible-runtimes python3.7 \
  --content S3Bucket=$S3_BUCKET,S3Key=aws_xray_python_37.zip \
  --profile elf



# Prepare the requests LAYER
mkdir -p /tmp/layer-requests
cd /tmp/layer-requests
rm -rf *
pip3.7 install requests -t ./python
# Slim the package
cd ./python
find . -type d -name "tests" -exec rm -rfv {} +
find . -type d -name "__pycache__" -exec rm -rfv {} +
rm -r *.whl *.dist-info __pycache__


cd ..
zip -r9 -q requests_python_37.zip ./python 

aws s3 cp requests_python_37.zip s3://$S3_BUCKET/requests_python_37.zip --profile elf

aws lambda publish-layer-version \
  --layer-name requests \
  --compatible-runtimes python3.7 \
  --content S3Bucket=$S3_BUCKET,S3Key=requests_python_37.zip \
  --profile elf


#### Invoke Lamba
"""
aws lambda invoke \
    --function-name test-lambda\
    --invocation-type Event \
    --payload '{ "name": "Ak" }' \
    out --log-type Tail \
    --profile elf 
    
"""