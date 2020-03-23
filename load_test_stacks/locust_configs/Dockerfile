FROM locustio/locust
LABEL maintainer="https://github.com/miztiik"

# Lets copy the app source code to the container image
RUN mkdir -p /var/locust
ADD locustfile.py /var/locust/locustfile.py

# Expose Ports(add 8089 for webUI)
EXPOSE 80 443
