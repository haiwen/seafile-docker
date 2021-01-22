FROM alpine:3.13 AS get
ENV SEAFILE_SERVER=seafile-server SEAFILE_VERSION=8.0.2

RUN apk add --no-cache wget

RUN cd /tmp && \
    wget https://download.seadrive.org/seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz && \
    tar -zxvf seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz && \
    rm -f seafile-server_${SEAFILE_VERSION}_x86-64.tar.gz

FROM alpine:3.9 AS pip

RUN apk add \
python3-dev \
py3-pip \
py3-setuptools \
mariadb-dev \
build-base \
jpeg-dev \
zlib-dev \
freetype-dev \
lcms2-dev \
openjpeg-dev \
tiff-dev \
tk-dev \
tcl-dev \
libmemcached-dev

RUN python3 -m pip install --upgrade pip &&\
pip3 install --timeout=3600 \
Django==2.2.14 \
future \
captcha \
django-statici18n \
django-post_office==3.3.0 \
django-webpack_loader \
gunicorn \
mysqlclient \
django-picklefield==2.1.1 \
openpyxl \
qrcode \
django-formtools \
django-simple-captcha \
djangorestframework==3.11.1 \
python-dateutil \
requests \
pillow \
pyjwt \
pycryptodome \
requests_oauthlib \
django-pylibmc \
&& rm -r /root/.cache/pip

FROM alpine:3.9

RUN apk add \
bash \
socat \
python3 \
jpeg \
zlib \
freetype \
lcms2 \
openjpeg \
tiff \
tk \
mariadb-dev \
libmemcached

COPY --from=get /tmp/seafile-server*/seahub /opt/seafile/seafile-server-latest/seahub
COPY --from=get /tmp/seafile-server*/seafile/lib64/python3.6/site-packages /opt/seafile/seafile-server-latest/seafile/lib64/python3.6/site-packages
COPY --from=pip /usr/lib/python3.6/site-packages /usr/lib/python3.6/site-packages
COPY scripts /scripts
RUN chmod u+x /scripts/*

ENV PYTHONPATH=/usr/lib/python3.6/site-packages:/opt/seafile/seafile-server-latest/seahub/thirdpart:/opt/seafile/seafile-server-latest/seafile/lib64/python3.6/site-packages
ENV CCNET_CONF_DIR=/opt/seafile/conf/ccnet
ENV SEAFILE_CONF_DIR=/opt/seafile/seafile-data
ENV SEAFILE_CENTRAL_CONF_DIR=/opt/seafile/conf
ENV SEAFILE_RPC_PIPE_PATH=/opt/seafile/seafile-server-latest/runtime

EXPOSE 8000

CMD ["/scripts/start.sh"]