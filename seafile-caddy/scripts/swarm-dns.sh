#!/bin/bash

if [ "$SWARM_DNS" = true ]; then
    
    cp /etc/caddy/Caddyfile /etc/caddy/Caddyfile.default
    
    while true; do 

        SEAHUB_IPS=$(dig +short seahub | sed -e 's/$/:8000/' | tr ' ' '\n' | sort | tr '\n' ' ')
        SEAHUB_MEDIA_IPS=$(dig +short seahub-media | sed -e 's/$/:80/' | tr ' ' '\n' | sort | tr '\n' ' ')

        cp /etc/caddy/Caddyfile.default /etc/caddy/Caddyfile.tmp

        sed -i "s/seahub:8000/$(echo $SEAHUB_IPS)/g" /etc/caddy/Caddyfile.tmp
        sed -i "s/seahub-media:80/$(echo $SEAHUB_MEDIA_IPS)/g" /etc/caddy/Caddyfile.tmp

        if ! diff -q "/etc/caddy/Caddyfile" "/etc/caddy/Caddyfile.tmp"; then
            rm -f /etc/caddy/Caddyfile
            mv /etc/caddy/Caddyfile.tmp /etc/caddy/Caddyfile
            echo "Applying new Caddyfile:"
            cat /etc/caddy/Caddyfile
            caddy reload --config /etc/caddy/Caddyfile
        fi

        sleep 10

    done
fi
