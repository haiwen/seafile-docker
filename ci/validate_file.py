#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
import sys

"""
Get token
"""
hostname = 'http://127.0.0.1'
username = 'me@example.com'
password = 'asecret'
get_token_url = '{}/api2/auth-token/'.format(hostname)
data = urllib.urlencode({'username': username, 'password': password})
request = urllib2.Request(get_token_url,data)
response = urllib2.urlopen(request)
_js_py = json.load(response)
token = _js_py['token']
response.close()

"""
Get default repo_id
"""
get_library_url = '{}/api2/default-repo/'.format(hostname)
get_repo_id = urllib2.Request(get_library_url)
get_repo_id.add_header('Authorization','Token ' + token)
response_repo_id = urllib2.urlopen(get_repo_id)
_js_py = json.load(response_repo_id)
repo_id = _js_py['repo_id']
response_repo_id.close()

"""
Get upload link
"""
filename = sys.argv[1]
view_file_url = '{}/api2/repos/{}/file/?p={}'.format(hostname, repo_id, filename)
view_file_link = urllib2.Request(view_file_url)
view_file_link.add_header('Authorization','Token ' + token)
try:
    response_view_file_link = urllib2.urlopen(view_file_link)
    res = json.load(response_view_file_link)
except Exception as e:
    print e
    sys.exit(1)
else:
    code = 0 if repo_id in res and filename in res else 1
