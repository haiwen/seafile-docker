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

def main():
    env = {
        'SERVER_NAME': 'seafile',
        'SERVER_IP': get_conf("server.hostname"),
    }
    call('{} auto'.format(get_script('setup-seafile.sh')), env=env)
    for fn in ('conf', 'ccnet', 'seafile-data', 'seahub-data', 'seahub.db'):
        src = join(topdir, fn)
        dst = join('/shared', fn)
        if exists(dst):
            if isdir(dst):
                shutil.rmtree(dst)
            else:
                os.unlink(dst)
        shutil.move(src, '/shared')

if __name__ == '__main__':
    main()
