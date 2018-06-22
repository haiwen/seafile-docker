FROM seafileltd/base:16.04

# syslog-ng and syslog-forwarder would mess up the container stdout, not good
# when debugging/upgrading.
RUN apt update

RUN apt-get install -y openjdk-8-jre libmemcached-dev zlib1g-dev pwgen curl openssl poppler-utils libpython2.7 libreoffice \
libreoffice-script-provider-python ttf-wqy-microhei ttf-wqy-zenhei xfonts-wqy python-requests

RUN apt-get install -y python-pip python-setuptools python-urllib3 python-ldap python-ceph

RUN pip install pylibmc django-pylibmc boto twilio oss2


RUN apt clean
