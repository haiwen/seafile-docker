#!/usr/bin/env python
#coding: UTF-8

"""
This script calls the appropriate seafile init scripts (e.g.
setup-seafile.sh or setup-seafile-mysql.sh. It's supposed to run inside the
container.
"""

import json
import os
from os.path import abspath, basename, exists, dirname, join, isdir
import shutil
import sys

from utils import call, get_conf, get_install_dir, get_script

installdir = get_install_dir()
topdir = dirname(installdir)

def main():
    admin_pw = {
        'email': get_conf('admin.email'),
        'password': get_conf('admin.password'),
    }
    password_file = join(topdir, 'conf', 'admin.txt')
    with open(password_file, 'w') as fp:
        json.dump(admin_pw, fp)

    try:
        call('{} start'.format(get_script('seafile.sh')), check_call=True)
        call('{} start'.format(get_script('seahub.sh')), check_call=True)
    finally:
        if exists(password_file):
            os.unlink(password_file)

if __name__ == '__main__':
    main()
