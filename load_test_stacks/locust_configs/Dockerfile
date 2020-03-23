FROM locustio/locust
LABEL maintainer="https://github.com/miztiik"

# Lets copy locust configuration file
RUN pwd
ADD locustfile.py locustfile.py
RUN ls -l locustfile.py

# Expose Ports(add 8089 for webUI)
EXPOSE 80 443
