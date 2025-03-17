#!/bin/bash

set -e

ssldir=${1:?"error params"}
domain=${2:?"error params"}

/usr/bin/mkdir -p /var/www/.well-known/acme-challenge/
/usr/bin/chmod 755 /var/www/.well-known/acme-challenge/
/usr/bin/ln -sf /var/www/.well-known/acme-challenge/ /var/www/challenges

domain_num=$(/root/.acme.sh/acme.sh --home /shared/ssl/ --list | grep "$domain" | grep -v "grep" | wc -l)

if [ $domain_num -eq 0 ]; then
    /root/.acme.sh/acme.sh --debug --issue --home /shared/ssl/ --server letsencrypt -d ${domain} -w /var/www/
    /root/.acme.sh/acme.sh --home /shared/ssl/ --install-cert -d ${domain} --key-file /shared/ssl/${domain}.key --fullchain-file /shared/ssl/${domain}.crt
else
    /root/.acme.sh/acme.sh --debug --home /shared/ssl/ --renew -d ${domain} --days 60
fi

/usr/sbin/nginx -s reload

echo "Nginx reloaded."
