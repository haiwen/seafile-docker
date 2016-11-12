#!/usr/bin/env python
#coding: UTF-8

"""
This script calls the appropriate seafile init scripts (e.g.
setup-seafile.sh or setup-seafile-mysql.sh. It's supposed to run inside the
container.
"""

import os
from os.path import abspath, basename, exists, dirname, join, isdir
import shutil
import sys

from utils import call, get_conf, get_install_dir, get_script

installdir = get_install_dir()
topdir = dirname(installdir)
shared_seafiledir = '/shared/seafile'

def main():
    if not exists(shared_seafiledir):
        os.mkdir(shared_seafiledir)
    env = {
        'SERVER_NAME': 'seafile',
        'SERVER_IP': get_conf("server.hostname"),
    }
    call('{} auto'.format(get_script('setup-seafile.sh')), env=env)
    for fn in ('conf', 'ccnet', 'seafile-data', 'seahub-data', 'seahub.db'):
        src = join(topdir, fn)
        dst = join(shared_seafiledir, fn)
        if not exists(dst) and exists(src):
            shutil.move(src, shared_seafiledir)

if __name__ == '__main__':
    main()
