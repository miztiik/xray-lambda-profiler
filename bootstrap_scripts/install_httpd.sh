#!/bin/bash -xe

# version: 27Mar2020

# Prepare the server for python3
yum -y install python-pip python3 git
pip3 install boto3

# Install AWS XRay Daemon for telemetry
curl https://s3.dualstack.us-east-2.amazonaws.com/aws-xray-assets.us-east-2/xray-daemon/aws-xray-daemon-3.x.rpm -o /home/ec2-user/xray.rpm
yum install -y /home/ec2-user/xray.rpm

# Git Clone
pip3 install flask gunicorn aws_xray_sdk Wikipedia-API
# mkdir -p /var/
cd /var
git clone https://github.com/miztiik/xray-lambda-profiler.git
cd /var/xray-lambda-profiler/app_stacks/back_end/wiki_search
# Start the App Server to receive traffic
gunicorn --bind 0.0.0.0:80 wsgi:application --access-logfile - --error-logfile - --capture-output --enable-stdio-inheritance &

# Killing gunicorn
# kill $(ps aux | grep 'gunicorn' | awk '{print $2}')

function install_xray(){
    # Install AWS XRay Daemon for telemetry
    curl https://s3.dualstack.us-east-2.amazonaws.com/aws-xray-assets.us-east-2/xray-daemon/aws-xray-daemon-3.x.rpm -o /home/ec2-user/xray.rpm
    yum install -y /home/ec2-user/xray.rpm
}

function install_nginx(){
    echo 'Begin NGINX Installation'
    sudo amazon-linux-extras install -y nginx1.12
    sudo systemctl start nginx
}

