FROM seafileltd/base:18.04

# syslog-ng and syslog-forwarder would mess up the container stdout, not good
# when debugging/upgrading.

# Fixing the "Sub-process /usr/bin/dpkg returned an error code (1)", 
# when RUN apt-get
RUN mkdir -p /usr/share/man/man1

RUN apt update

RUN apt-get install -y openjdk-8-jre libmemcached-dev zlib1g-dev pwgen curl openssl poppler-utils libpython2.7 libreoffice \
libreoffice-script-provider-python ttf-wqy-microhei ttf-wqy-zenhei xfonts-wqy python-requests

RUN apt-get install -y tzdata python-pip python-setuptools python-urllib3 python-ldap python-ceph

# The S3 storage, oss storage and psd online preview etc, 
# depends on the python-backages as follow:
RUN pip install boto==2.43.0 \ 
    oss2==2.3.0 \ 
    psd-tools==1.4 \ 
    pycryptodome==3.7.2 \ 
    twilio==5.7.0

RUN apt clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
