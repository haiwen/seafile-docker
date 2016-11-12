# lastet phusion baseimage as of 2016.11, based on ubuntu 16.04
FROM phusion/baseimage:0.9.19

ENV UPDATED_AT 20161110

RUN apt-get update -qq && apt-get -qq -y install memcached sqlite3 nginx \
        python2.7-dev python-imaging python-ldap python-mysqldb

# Utility tools
RUN apt-get install -qq -y vim htop net-tools psmisc git wget curl

# Install latest version of pip & wheel
RUN curl -sSL -o /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py && \
    python /tmp/get-pip.py && \
    rm -rf /tmp/get-pip.py && \
    pip install -U wheel

ADD requirements.txt  /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY services /services

RUN mkdir -p /etc/service/memcached && \
    mv /services/memcached.sh /etc/service/memcached/run

RUN mkdir -p /etc/service/nginx && \
    rm -f /etc/nginx/sites-enabled/* /etc/nginx/conf.d/* && \
    mv /services/nginx.conf /etc/nginx/nginx.conf && \
    mv /services/nginx.sh /etc/service/nginx/run

CMD ["/sbin/my_init", "--", "bash", "-l"]
