# See https://hub.docker.com/r/phusion/baseimage/tags/
FROM phusion/baseimage:focal-1.0.0-arm64
ENV SEAFILE_SERVER=seafile-pro-server SEAFILE_VERSION=

RUN apt-get update --fix-missing

# Utility tools
RUN apt-get install -y vim htop net-tools psmisc wget curl git unzip

# For suport set local time zone.
RUN export DEBIAN_FRONTEND=noninteractive && apt-get install -y tzdata \
    nginx \
    libmysqlclient-dev \
    libmemcached11 libmemcached-dev \
    libxmlsec1 xmlsec1 \
    zlib1g-dev pwgen openssl poppler-utils \
    fuse \
    ldap-utils ca-certificates \
    clamdscan iputils-ping \
    ttf-wqy-microhei ttf-wqy-zenhei xfonts-wqy

# Java
RUN apt-get install -y openjdk-8-jre

# Libreoffice
RUN apt-get install -y libreoffice libreoffice-script-provider-python libsm-dev

# Python3
RUN apt-get install -y python3 python3-pip python3-setuptools python3-ldap python3-rados libffi-dev && \
    rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python && \
    python3 -m pip install --no-cache-dir --upgrade pip

RUN pip3 install --no-cache-dir --timeout=3600 click termcolor colorlog pymysql django==3.2.* \
    future mysqlclient Pillow pylibmc captcha markupsafe==2.0.1 jinja2 \
    sqlalchemy django-pylibmc django-simple-captcha pyjwt pycryptodome==3.12.0 cffi==1.14.0 \
    boto oss2 twilio python-ldap configparser psd-tools lxml

# Scripts
COPY scripts_9.0 /scripts
COPY templates /templates
COPY services /services

# acme
# RUN curl https://get.acme.sh | sh -s
RUN unzip /scripts/acme.sh-master.zip -d /scripts/ && \
    mv /scripts/acme.sh-master /scripts/acme.sh && \
    cd /scripts/acme.sh && /scripts/acme.sh/acme.sh --install

RUN echo "TLS_REQCERT     allow" >> /etc/ldap/ldap.conf && \
    echo "TCPSocket 3310" >> /etc/clamav/clamd.conf && \
    echo "TCPAddr av" >> /etc/clamav/clamd.conf && \
    chmod u+x /scripts/* && \
    mkdir -p /etc/my_init.d && \
    rm -f /etc/my_init.d/* && \
    cp /scripts/create_data_links.sh /etc/my_init.d/01_create_data_links.sh && \
    mkdir -p /etc/service/nginx && \
    rm -f /etc/nginx/sites-enabled/* /etc/nginx/conf.d/* && \
    mv /services/nginx.conf /etc/nginx/nginx.conf && \
    mv /services/nginx.sh /etc/service/nginx/run

# Seafile
WORKDIR /opt/seafile
COPY seafile-pro-server-${SEAFILE_VERSION} /opt/seafile/seafile-pro-server-${SEAFILE_VERSION}

EXPOSE 80

CMD ["/sbin/my_init", "--", "/scripts/enterpoint.sh"]
