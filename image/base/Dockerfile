# lastet phusion baseimage as of 2016.11, based on ubuntu 16.04
FROM phusion/baseimage:0.9.19

ENV UPDATED_AT 20161110

RUN apt-get update -qq && apt-get -qq -y install python2.7-dev memcached python-pip \
        python-setuptools python-imaging python-mysqldb python-memcache python-ldap \
        python-urllib3 sqlite3 nginx \
        vim htop net-tools psmisc git wget curl && \
    pip install -U wheel && pip install click termcolor prettytable colorlog

COPY services /services

RUN mkdir -p /etc/service/memcached && \
        mv /services/memcached.sh /etc/service/memcached/run && \
    mkdir -p /etc/service/nginx && \
        rm -f /etc/nginx/sites-enabled/* /etc/nginx/conf.d/* && \
        mv /services/nginx.conf /etc/nginx/nginx.conf && \
        mv /services/nginx.sh /etc/service/nginx/run

CMD ["/sbin/my_init", "--", "bash", "-l"]
