# See https://hub.docker.com/r/phusion/baseimage/tags/
FROM phusion/baseimage:focal-1.0.0-arm64
ENV SEAFILE_SERVER=seafile-pro-server SEAFILE_VERSION=

RUN apt-get update --fix-missing

# Utility tools
RUN apt-get install -y vim htop net-tools psmisc wget curl git

# For suport set local time zone.
RUN export DEBIAN_FRONTEND=noninteractive && apt-get install tzdata -y

# Nginx
RUN apt-get install -y nginx

# Mysqlclient
RUN apt-get install -y libmysqlclient-dev

# Memcache
RUN apt-get install -y libmemcached11 libmemcached-dev

# SAML
RUN apt-get install -y libxmlsec1 xmlsec1

# Java
RUN apt-get install -y openjdk-8-jre

# Libreoffice
RUN apt-get install -y libreoffice libreoffice-script-provider-python libsm-dev
RUN apt-get install -y ttf-wqy-microhei ttf-wqy-zenhei xfonts-wqy

# Tools
RUN apt-get install -y zlib1g-dev pwgen openssl poppler-utils

# Fuse
RUN apt-get install -y fuse

# Cffi
RUN apt-get install -y libffi-dev

# Ldap
RUN apt-get install -y ldap-utils ca-certificates
RUN echo "TLS_REQCERT     allow" >> /etc/ldap/ldap.conf

# Python3
RUN apt-get install -y python3 python3-pip python3-setuptools python3-ldap python3-rados
RUN rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python
RUN python3 -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple && rm -r /root/.cache/pip

RUN pip3 install --timeout=3600 click termcolor colorlog pymysql \
    django==3.2.* -i https://mirrors.aliyun.com/pypi/simple && rm -r /root/.cache/pip

RUN pip3 install --timeout=3600 future mysqlclient Pillow pylibmc captcha markupsafe==2.0.1 jinja2 \
    sqlalchemy django-pylibmc django-simple-captcha pyjwt pycryptodome==3.12.0 cffi==1.14.0 -i https://mirrors.aliyun.com/pypi/simple && \
    rm -r /root/.cache/pip

RUN pip3 install --timeout=3600 boto oss2 twilio python-ldap configparser -i https://mirrors.aliyun.com/pypi/simple && \
    rm -r /root/.cache/pip


# Scripts
COPY scripts_9.0 /scripts
COPY templates /templates
COPY services /services
RUN chmod u+x /scripts/*

RUN mkdir -p /etc/my_init.d && \
    rm -f /etc/my_init.d/* && \
    cp /scripts/create_data_links.sh /etc/my_init.d/01_create_data_links.sh

RUN mkdir -p /etc/service/nginx && \
    rm -f /etc/nginx/sites-enabled/* /etc/nginx/conf.d/* && \
    mv /services/nginx.conf /etc/nginx/nginx.conf && \
    mv /services/nginx.sh /etc/service/nginx/run


# Seafile
WORKDIR /opt/seafile
COPY seafile-pro-server-${SEAFILE_VERSION} /opt/seafile/seafile-pro-server-${SEAFILE_VERSION}

EXPOSE 80


CMD ["/sbin/my_init", "--", "/scripts/enterpoint.sh"]
