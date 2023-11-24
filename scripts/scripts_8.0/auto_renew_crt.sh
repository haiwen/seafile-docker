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
renew_cert_script=/scripts/renew_cert.sh

if [[ ! -x ${renew_cert_script} ]]; then
    cat > ${renew_cert_script} << EOF
#!/bin/bash
python3 ${letsencrypt_script} --account-key ${ssldir}/${ssl_account_key} --csr ${ssldir}/${ssl_csr} --acme-dir /var/www/challenges/ > ${ssldir}/${ssl_crt} || exit
$(which nginx) -s reload
EOF

    chmod u+x ${renew_cert_script}

    if [[ ! -d "/var/www/challenges" ]]; then
        mkdir -p /var/www/challenges
    fi

    cat >> /etc/crontab << EOF
00 1    1 * *   root    /scripts/renew_cert.sh 2>> /var/log/acme_tiny.log
EOF

    echo 'Created a crontab to auto renew the cert for letsencrypt.'
else
    echo 'Found existing the script for renew the cert.'
    echo 'Skip create the crontab for letscncrypt since maybe we have created before.'
fi
