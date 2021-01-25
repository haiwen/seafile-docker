#!/bin/bash

/scripts/swarm-dns.sh &

caddy run --config /etc/caddy/Caddyfile --adapter caddyfile

