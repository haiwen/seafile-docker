#!/bin/bash

set -e

ssldir=${1:?"error params"}
domain=${2:?"error params"}

ssl_key=${domain}.key
ssl_crt=${domain}.crt

cd $ssldir

if [[ ! -e ${ssl_key} ]]; then
    openssl genrsa 4096 > ${ssl_key}
fi

openssl req -x509 -key ${ssl_key} -out ${ssl_crt} -days 3650 -nodes -subj "/CN=$domain"

nginx -s reload

echo "Nginx reloaded."
