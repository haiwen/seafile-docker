#!/bin/bash

set -e

ssldir=${1:?"error params"}
domain=${2:?"error params"}

letsencryptdir=$ssldir/letsencrypt
letsencrypt_script=$letsencryptdir/acme_tiny.py

ssl_account_key=${domain}.account.key
ssl_csr=${domain}.csr
ssl_key=${domain}.key
ssl_crt=${domain}.crt

mkdir -p /var/www/challenges && chmod -R 777 /var/www/challenges
mkdir -p $ssldir

if ! [[ -d $letsencryptdir ]]; then
    git clone git://github.com/diafygi/acme-tiny.git $letsencryptdir
else
    cd $letsencryptdir
    git pull origin master:master
fi

cd $ssldir

if [[ ! -e ${ssl_account_key} ]]; then
    openssl genrsa 4096 > ${ssl_account_key}
fi

if [[ ! -e ${ssl_key} ]]; then
    openssl genrsa 4096 > ${ssl_key}
fi

if [[ ! -e ${ssl_csr} ]]; then
    openssl req -new -sha256 -key ${ssl_key} -subj "/CN=$domain" > $ssl_csr
fi

python3 $letsencrypt_script --account-key ${ssl_account_key} --csr $ssl_csr --acme-dir /var/www/challenges/ > ./signed.crt
curl -sSL -o intermediate.pem https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem
cat signed.crt intermediate.pem > ${ssl_crt}

nginx -s reload

echo "Nginx reloaded."
