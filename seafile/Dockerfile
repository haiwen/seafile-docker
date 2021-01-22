# See https://hub.docker.com/r/phusion/baseimage/tags/
FROM phusion/baseimage:bionic-1.0.0
ENV SEAFILE_SERVER=seafile-server SEAFILE_VERSION=8.0.2

RUN export DEBIAN_FRONTEND=noninteractive

# Package installation
RUN apt-get update --fix-missing && apt-get install -y vim htop net-tools psmisc wget curl git socat \
tzdata \
nginx \
python3 python3-pip python3-setuptools \
libmysqlclient-dev \
&& rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/seafile/ && cd /opt/seafile/ && \
    wget https://download.seadrive.org/seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz && \
    tar -zxvf seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz && \
    rm -f seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz

# Python3
RUN python3.6 -m pip install --upgrade pip \
&& pip3 install --timeout=3600 click termcolor colorlog pymysql \
Pillow pylibmc captcha jinja2 sqlalchemy django==1.11.29 django-pylibmc django-simple-captcha \
future mysqlclient \
&& rm -r /root/.cache/pip

# Scripts
COPY scripts /scripts
RUN chmod u+x /scripts/*

RUN mkdir -p /etc/my_init.d && \
    rm -f /etc/my_init.d/* && \
    cp /scripts/create_data_links.sh /etc/my_init.d/01_create_data_links.sh


# Seafile
WORKDIR /opt/seafile

# For using TLS connection to LDAP/AD server with docker-ce.
RUN find /opt/seafile/ \( -name "liblber-*" -o -name "libldap-*" -o -name "libldap_r*" -o -name "libsasl2.so*" \) -delete


EXPOSE 8080 8082 8001


CMD ["/sbin/my_init", "--", "/scripts/start.py"]
