#!/bin/bash
# `/sbin/setuser memcache` runs the given command as the user `memcache`.
# If you omit that part, the command will be run as root.
exec /sbin/setuser memcache /usr/bin/memcached >>/var/log/memcached.log 2>&1
