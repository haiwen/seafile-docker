import time
import os

from utils import (get_command_output, logdbg, listen_on_https, behind_ssl_termination, get_conf, render_template, call)

def wait_for_nginx():
    while True:
        logdbg('waiting for nginx server to be ready')
        output = get_command_output('netstat -nltp')
        if ':80 ' in output:
            logdbg(output)
            logdbg('nginx is ready')
            return
        time.sleep(2)


def change_nginx_config(https = None, skip_writing_shared_conf = False):
    if https is None:
        https = listen_on_https()
        
    domain = get_conf('SEAFILE_SERVER_HOSTNAME', 'seafile.example.com')

    nginx_shared_file = '/shared/nginx/conf/seafile.nginx.conf'

    if not os.path.isfile(nginx_shared_file):
        nginx_etc_file = '/etc/nginx/sites-enabled/seafile.nginx.conf'
        context = {
            'https': https,
            'behind_ssl_termination': behind_ssl_termination(),
            'domain': domain,
            'enable_webdav': get_conf('ENABLE_WEBDAV', '0') != '0'
        }
        render_template('/templates/seafile.nginx.conf.template',
                        nginx_etc_file, context)
        if not skip_writing_shared_conf:
            call('mv {0} {1} && ln -sf {1} {0}'.format(nginx_etc_file, nginx_shared_file))

    call('nginx -s reload')
    time.sleep(2)

    
    
