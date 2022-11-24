#!/bin/bash

set -e

ssldir=${1:?"error params"}
ssldir=$(echo "$ssldir/" | sed 's|//|/|')
domain=${2:?"error params"}

mkdir -p /var/www/.well-known/acme-challenge/
chmod 755 /var/www/.well-known/acme-challenge/
ln -sf /var/www/.well-known/acme-challenge/ /var/www/challenges

domain_num=$(/root/.acme.sh/acme.sh --home ${ssldir} --list | grep "$domain" | grep -v "grep" | wc -l)

if [ $domain_num -eq 0 ]; then
    /root/.acme.sh/acme.sh --debug --issue --home ${ssldir} --server letsencrypt -d ${domain} -w /var/www/
    /root/.acme.sh/acme.sh --home ${ssldir} --install-cert -d ${domain} --key-file ${ssldir}${domain}.key --fullchain-file ${ssldir}${domain}.crt
else
    /root/.acme.sh/acme.sh --debug --home ${ssldir} --renew -d ${domain} --days 60
fi

nginx -s reload

echo "Nginx reloaded."
