#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
import requests
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
Generate default repo_id
"""
get_library_url = '{}/api2/default-repo/'.format(hostname)
headers = {'Authorization': 'Token ' + token, 'Connection':'close'}
r = requests.post(get_library_url, headers=headers)
assert r.status_code == 200

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
upload_link_url = '{}/api2/repos/{}/upload-link/'.format(hostname, repo_id)
get_upload_link = urllib2.Request(upload_link_url)
get_upload_link.add_header('Authorization','Token ' + token)
response_upload_link = urllib2.urlopen(get_upload_link)
upload_link = json.load(response_upload_link).replace('seafile.example.com', '127.0.0.1').replace('https', 'http')
response_upload_link.close()

"""
Upload file
"""

filename = sys.argv[1]
url = upload_link
files = {'file': open(filename, 'rb')}
r = requests.post(
		url, data={'filename': filename, 'parent_dir': '/'},
		files=files, headers={'Authorization': 'Token ' + token})
files['file'].close()

