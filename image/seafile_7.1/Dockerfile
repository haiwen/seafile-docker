# See https://hub.docker.com/r/phusion/baseimage/tags/
FROM phusion/baseimage:master-arm

RUN apt-get update --fix-missing

# Utility tools
RUN apt-get install -y vim htop net-tools psmisc wget curl git

# For suport set local time zone.
RUN export DEBIAN_FRONTEND=noninteractive && apt-get install tzdata -y

# Nginx
RUN apt-get install -y \
    nginx \
    libjpeg-dev \
    zlib1g-dev \
    libtiff5-dev \
    libfreetype6-dev \
    libwebp-dev \
    python3 \
    python3-pip \
    libmemcached-dev \
    python3-setuptools

RUN python3.6 -m pip install --user --upgrade pip setuptools wheel  && rm -r /root/.cache/pip

RUN python3.6 -m pip install --timeout=3600 \
    click \
    termcolor \
    colorlog \ 
    pymysql \
    django==1.11.29 \
    future \
    captcha \
    jinja2 \ 
    django-statici18n \
    django-post_office==3.3.0 \
    django-webpack_loader \
    gunicorn \
    pymysql \
    django-picklefield \
    openpyxl \
    qrcode \
    django-formtools \
    django-simple-captcha \
    djangorestframework \
    python-dateutil \
    requests \
    pillow \
    pyjwt \
    pycryptodome \
    python-memcached \
    requests_oauthlib  \
    django-pylibmc  && \
    rm -r /root/.cache/pip

# Scripts
COPY scripts_7.1 /scripts
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

ENV SEAFILE_VERSION=7.1.4 SEAFILE_SERVER=seafile-server

RUN mkdir -p /opt/seafile/ && cd /opt/seafile/ && \
    wget https://github.com/haiwen/seafile-rpi/releases/download/v7.1.4/seafile-server_7.1.4_pi-bionic-stable.tar.gz && \
    tar -zxvf seafile-server_${SEAFILE_VERSION}_pi-bionic-stable.tar.gz && \
    rm -f seafile-server_${SEAFILE_VERSION}_pi-bionic-stable.tar.gz 
    

# For using TLS connection to LDAP/AD server with docker-ce.
RUN find /opt/seafile/ \( -name "liblber-*" -o -name "libldap-*" -o -name "libldap_r*" -o -name "libsasl2.so*" \) -delete


EXPOSE 80


CMD ["/sbin/my_init", "--", "/scripts/start.py"]
