#!/usr/bin/env python3
#coding: UTF-8

"""
Bootstraping seafile server, letsencrypt (verification & cron job).
"""

import argparse
import os
from os.path import abspath, basename, exists, dirname, join, isdir
import shutil
import sys
import uuid
import time

from utils import (
    call, get_conf, get_install_dir, loginfo,
    get_script, render_template, get_seafile_version, eprint,
    cert_has_valid_days, get_version_stamp_file, update_version_stamp,
    wait_for_mysql, wait_for_nginx, read_version_stamp, is_pro_version, is_valid_bucket_name
)

seafile_version = get_seafile_version()
installdir = get_install_dir()
topdir = dirname(installdir)
shared_seafiledir = '/shared/seafile'
ssl_dir = '/shared/ssl'
generated_dir = '/bootstrap/generated'


def gen_custom_dir():
    dst_custom_dir = '/shared/seafile/seahub-data/custom'
    custom_dir = join(installdir, 'seahub/media/custom')
    if not exists(dst_custom_dir):
        os.mkdir(dst_custom_dir)
        call('rm -rf %s' % custom_dir)
        call('ln -sf %s %s' % (dst_custom_dir, custom_dir))

def init_letsencrypt():
    loginfo('Preparing for letsencrypt ...')
    wait_for_nginx()

    if not exists(ssl_dir):
        os.mkdir(ssl_dir)

    domain = get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com')
    context = {
        'ssl_dir': ssl_dir,
        'domain': domain,
    }
    render_template(
        '/templates/letsencrypt.cron.template',
        join(generated_dir, 'letsencrypt.cron'),
        context
    )

    ssl_crt = '/shared/ssl/{}.crt'.format(domain)
    if exists(ssl_crt):
        loginfo('Found existing cert file {}'.format(ssl_crt))
        if cert_has_valid_days(ssl_crt, 30):
            loginfo('Skip letsencrypt verification since we have a valid certificate')
            # Create a crontab to auto renew the cert for letsencrypt.
            with open('/var/spool/cron/crontabs/root', 'r') as f:
                crons = f.read()
            if '/scripts/ssl.sh' not in crons:
                call('echo "0 1 * * * /scripts/ssl.sh {0} {1} >> /shared/ssl/letsencrypt.log 2>&1" >> /var/spool/cron/crontabs/root'.format(ssl_dir, domain))
                call('/usr/bin/crontab /var/spool/cron/crontabs/root')
            return

    loginfo('Starting letsencrypt verification')
    # Create a temporary nginx conf to start a server, which would accessed by letsencrypt
    context = {
        'https': False,
        'domain': domain,
        'is_tmp': True,
    }
    if not os.path.isfile('/shared/nginx/conf/seafile.nginx.conf'):
        render_template('/templates/seafile.nginx.conf.template',
                        '/etc/nginx/sites-enabled/seafile.nginx.conf', context)

    call('nginx -s reload')
    time.sleep(2)

    return_code = call('/scripts/ssl.sh {0} {1}'.format(ssl_dir, domain), check_call=False)
    if return_code not in [0, 2]:
        raise RuntimeError('Failed to generate ssl certificate for domain {0}'.format(domain))

    call('echo "0 1 * * * /scripts/ssl.sh {0} {1} >> /shared/ssl/letsencrypt.log 2>&1" >> /var/spool/cron/crontabs/root'.format(ssl_dir, domain))
    call('/usr/bin/crontab /var/spool/cron/crontabs/root')
    # Create a crontab to auto renew the cert for letsencrypt.


def generate_local_nginx_conf():
    # Now create the final nginx configuratin
    domain = get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com')
    context = {
        'https': is_https(),
        'domain': domain,
        'is_tmp': False,
    }

    if not os.path.isfile('/shared/nginx/conf/seafile.nginx.conf'):
        render_template(
            '/templates/seafile.nginx.conf.template',
            '/etc/nginx/sites-enabled/seafile.nginx.conf',
            context
        )
        nginx_etc_file = '/etc/nginx/sites-enabled/seafile.nginx.conf'
        nginx_shared_file = '/shared/nginx/conf/seafile.nginx.conf'
        call('mv {0} {1} && ln -sf {1} {0}'.format(nginx_etc_file, nginx_shared_file))

def is_https():
    return get_conf('SEAFILE_SERVER_LETSENCRYPT', 'false').lower() == 'true'

def get_proto():
    proto = 'https' if is_https() else 'http'
    seafile_server_proto = get_conf('SEAFILE_SERVER_PROTOCOL', 'http')
    if seafile_server_proto == 'https':
        proto = 'https'
    return proto

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--parse-ports', action='store_true')

    return ap.parse_args()

def init_seafile_server():
    version_stamp_file = get_version_stamp_file()
    if exists(join(shared_seafiledir, 'seafile-data')):
        if not exists(version_stamp_file):
            update_version_stamp(os.environ['SEAFILE_VERSION'])
        # sysbol link unlink after docker finish.
        latest_version_dir='/opt/seafile/seafile-server-latest'
        current_version_dir='/opt/seafile/' + get_conf('SEAFILE_SERVER', 'seafile-server') + '-' +  read_version_stamp()
        if not exists(latest_version_dir):
            call('ln -sf ' + current_version_dir + ' ' + latest_version_dir)
        loginfo('Skip running setup-seafile-mysql.py because there is existing seafile-data folder.')
        return

    loginfo('Now running setup-seafile-mysql.py in auto mode.')
    env = {
        'SERVER_NAME': 'seafile',
        'SERVER_IP': get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com'),
        'MYSQL_USER': get_conf('SEAFILE_MYSQL_DB_USER', 'seafile'),
        'MYSQL_USER_PASSWD': get_conf('SEAFILE_MYSQL_DB_PASSWORD', str(uuid.uuid4())),
        'MYSQL_USER_HOST': '%',
        'MYSQL_HOST': get_conf('SEAFILE_MYSQL_DB_HOST', 'db'),
        'MYSQL_PORT': get_conf('SEAFILE_MYSQL_DB_PORT', '3306'),
        # Default MariaDB root user has empty password and can only connect from localhost.
        'MYSQL_ROOT_PASSWD': get_conf('INIT_SEAFILE_MYSQL_ROOT_PASSWORD', ''),
    }

    setup_script = get_script('setup-seafile-mysql.sh')
    call('{} auto -n seafile'.format(setup_script), env=env)

    domain = get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com')
    proto = get_proto()

    cache_provider = get_conf('CACHE_PROVIDER', 'redis')
    clsuter_mode = get_conf('CLUSTER_SERVER', 'false') == 'true'
    init_cluster = get_conf('CLUSTER_INIT_MODE', 'false') == 'true'
    # pre check value
    if cache_provider not in ('redis', 'memcached') and not clsuter_mode:
        raise ValueError(f'Invalid CACHE_PROVIDER: {cache_provider}')
    
    redis_host = get_conf('REDIS_HOST', 'redis')
    redis_port = get_conf('REDIS_PORT', '6379')
    redis_pasword = get_conf('REDIS_PASSWORD')
    memcached_host = get_conf('MEMCACHED_HOST', 'memcached')
    memcached_port = get_conf('MEMCACHED_PORT', '11211')

    int(redis_port if cache_provider == 'redis' and not clsuter_mode else memcached_port)

    with open(join(topdir, 'conf', 'seahub_settings.py'), 'a+') as fp:
        fp.write('\n')
        if not clsuter_mode and cache_provider == 'redis':
            redis_cfg = f'redis://{(redis_pasword + "@") if redis_pasword else ""}{redis_host}:{redis_port}'
            fp.write("""CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://""" + redis_cfg + """',
    },""")
        else:
            memcached_cfg = f'{memcached_host}:{memcached_port}'
            fp.write("""CACHES = {
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'LOCATION': '""" + memcached_cfg + """',
    },""")

        fp.write("""
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
}
COMPRESS_CACHE_BACKEND = 'locmem'""")
        fp.write('\n')
        fp.write("\nTIME_ZONE = '{time_zone}'".format(time_zone=os.getenv('TIME_ZONE',default='Etc/UTC')))
        fp.write('\nFILE_SERVER_ROOT = \'{proto}://{domain}/seafhttp\''.format(proto=proto, domain=domain))
        fp.write('\n')
        if clsuter_mode and init_cluster:
            fp.write(f'\nSERVICE_URL = \'{proto}://{domain}/\'')
            fp.write(f'\nAVATAR_FILE_STORAGE = \'seahub.base.database_storage.DatabaseStorage\'')
            fp.write('\n')

    # Disabled the Elasticsearch process on Seafile-container
    # Connection to the Elasticsearch-container
    if os.path.exists(join(topdir, 'conf', 'seafevents.conf')):
        with open(join(topdir, 'conf', 'seafevents.conf'), 'r') as fp:
            fp_lines = fp.readlines()
            if '[INDEX FILES]\n' in fp_lines:
                insert_index = fp_lines.index('[INDEX FILES]\n') + 1
                if clsuter_mode and init_cluster:
                    insert_lines = [
                        f'es_port = {get_conf("CLUSTER_INIT_ES_PORT", "9200")}\n',
                        f'es_host = {get_conf("CLUSTER_INIT_ES_HOST", "<your elasticsearch server HOST>")}\n',
                        'external_es_server = true\n'
                    ]
                else:
                    insert_lines = [
                        'es_port = 9200\n', 
                        'es_host = elasticsearch\n',
                        'external_es_server = true\n'
                    ]
                for line in insert_lines:
                   fp_lines.insert(insert_index, line)
            if not clsuter_mode and cache_provider == 'redis':
                fp_lines += ['\n[REDIS]\n',
                             f'server = {redis_host}\n',
                             f'port = {redis_port}\n'
                             ]
                if redis_pasword:
                    fp_lines += [f'password = {redis_pasword}\n']

        with open(join(topdir, 'conf', 'seafevents.conf'), 'w') as fp:
            fp.writelines(fp_lines)

    # Modify seafdav config
    if os.path.exists(join(topdir, 'conf', 'seafdav.conf')):
        with open(join(topdir, 'conf', 'seafdav.conf'), 'r') as fp:
            fp_lines = fp.readlines()
            if 'share_name = /\n' in fp_lines:
               replace_index = fp_lines.index('share_name = /\n')
               replace_line = 'share_name = /seafdav\n'
               fp_lines[replace_index] = replace_line
        with open(join(topdir, 'conf', 'seafdav.conf'), 'w') as fp:
            fp.writelines(fp_lines)

    # Modify seafile config
    if is_pro_version():
        # for seafile-pro-server
        with open(join(topdir, 'conf', 'seafile.conf'), 'a+') as fp:
            if cache_provider == 'redis':
                fp.write('\n[redis]')
                fp.write(f'\nredis_host = {redis_host}')
                fp.write(f'\nredis_port = {redis_port}')
                if redis_pasword:
                    fp.write(f'\nredis_password = {redis_pasword}')
                fp.write(f'\nmax_connections = 100')
                fp.write('\n')
            else:
                if clsuter_mode and init_cluster:
                    fp.write('\n[cluster]')
                    fp.write('\nenable = true')
                    fp.write('\n')

                fp.write('\n[memcached]')
                fp.write(f'\nmemcached_options = --SERVER={memcached_host}:{memcached_port} --POOL-MIN=10 --POOL-MAX=100')
                fp.write('\n')

            
            commit_bucket = get_conf('INIT_S3_COMMIT_BUCKET', '<your-commit-objects>')
            fs_bucket = get_conf('INIT_S3_FS_BUCKET',  '<your-fs-objects>')
            block_bucket = get_conf('INIT_S3_BLOCK_BUCKET',  '<your-block-objects>')
            key_id = get_conf('INIT_S3_KEY_ID',  '<your-key-id>')
            key = get_conf('INIT_S3_SECRET_KEY',  '<your-secret-key>')

            init_with_s3_config = is_valid_bucket_name(commit_bucket) \
                and is_valid_bucket_name(fs_bucket) \
                and is_valid_bucket_name(block_bucket) \
                and key_id and key_id != '<your-key-id>' \
                and key and key != '<your-secret-key>'

            if init_with_s3_config:
                use_v4_signature = get_conf('INIT_S3_USE_V4_SIGNATURE', 'true')
                aws_region = get_conf('INIT_S3_AWS_REGION', 'us-east-1')
                host = get_conf('INIT_S3_HOST', 's3.us-east-1.amazonaws.com')
                use_https = get_conf('INIT_S3_USE_HTTPS', 'true')
                path_style_request = get_conf('INIT_S3_PATH_STYLE_REQUEST', 'false')
                sse_c_key = get_conf('INIT_S3_SSE_C_KEY')

                fp.write('\n[commit_object_backend]')
                fp.write('\nname = s3')
                fp.write(f'\nbucket = {commit_bucket}')
                fp.write(f'\nkey_id = {key_id}')
                fp.write(f'\nkey = {key}')
                fp.write(f'\nuse_v4_signature = {use_v4_signature}')
                fp.write(f'\naws_region = {aws_region}')
                fp.write(f'\nhost = {host}')
                fp.write(f'\nuse_https = {use_https}')
                fp.write(f'\npath_style_request = {path_style_request}')
                if sse_c_key:
                    fp.write(f'\nsse_c_key = {sse_c_key}')
                fp.write('\n')

                fp.write('\n[fs_object_backend]')
                fp.write('\nname = s3')
                fp.write(f'\nbucket = {fs_bucket}')
                fp.write(f'\nkey_id = {key_id}')
                fp.write(f'\nkey = {key}')
                fp.write(f'\nuse_v4_signature = {use_v4_signature}')
                fp.write(f'\naws_region = {aws_region}')
                fp.write(f'\nhost = {host}')
                fp.write(f'\nuse_https = {use_https}')
                fp.write(f'\npath_style_request = {path_style_request}')
                if sse_c_key:
                    fp.write(f'\nsse_c_key = {sse_c_key}')
                fp.write('\n')

                fp.write('\n[block_backend]')
                fp.write('\nname = s3')
                fp.write(f'\nbucket = {block_bucket}')
                fp.write(f'\nkey_id = {key_id}')
                fp.write(f'\nkey = {key}')
                fp.write(f'\nuse_v4_signature = {use_v4_signature}')
                fp.write(f'\naws_region = {aws_region}')
                fp.write(f'\nhost = {host}')
                fp.write(f'\nuse_https = {use_https}')
                fp.write(f'\npath_style_request = {path_style_request}')
                if sse_c_key:
                    fp.write(f'\nsse_c_key = {sse_c_key}')
                fp.write('\n')

    # After the setup script creates all the files inside the
    # container, we need to move them to the shared volume
    #
    # e.g move "/opt/seafile/seafile-data" to "/shared/seafile/seafile-data"
    files_to_copy = ['conf', 'ccnet', 'seafile-data', 'seahub-data', 'pro-data']
    for fn in files_to_copy:
        src = join(topdir, fn)
        dst = join(shared_seafiledir, fn)
        if not exists(dst) and exists(src):
            call('mv -f ' + str(src) + ' ' + str(dst))
            call('ln -sf ' + str(dst) + ' ' + str(src))

    gen_custom_dir()

    loginfo('Updating version stamp')
    update_version_stamp(os.environ['SEAFILE_VERSION'])

    # non root 
    non_root = os.getenv('NON_ROOT', default='') == 'true'
    if non_root:
        call('chmod -R a+rwx /shared/seafile/')
