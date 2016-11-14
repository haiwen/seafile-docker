# Lastet phusion baseimage as of 2016.11, based on ubuntu 16.04
# See https://hub.docker.com/r/phusion/baseimage/tags/
FROM phusion/baseimage:0.9.19

ENV UPDATED_AT=20161110 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && apt-get -qq -y install memcached mariadb-server nginx

# Utility tools
RUN apt-get install -qq -y vim htop net-tools psmisc git wget curl

# Guidline for installing python libs: if a lib has C-compoment (e.g.
# python-imaging depends on libjpeg/libpng), we install it use apt-get.
# Otherwise we install it with pip.
RUN apt-get install -y python2.7-dev python-imaging python-ldap python-mysqldb
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

RUN mkdir -p /etc/service/mysql && \
    mv /services/mysql.sh /etc/service/mysql/run

RUN mkdir -p /etc/my_init.d && rm -f /etc/my_init.d/00_regen_ssh_host_keys.sh
ADD my_init.d/99_mysql_setup.sh /etc/my_init.d/

CMD ["/sbin/my_init", "--", "bash", "-l"]

# TODO: clean up & squash layers with docker-squash
# See https://github.com/jwilder/docker-squash
