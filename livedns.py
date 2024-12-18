#!/usr/bin/env python3
""" Helper script allowing DNS records updates on Gandi LiveDNS

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

See https://github.com/mysterfr/Syno-Gandi-LiveDNS

"""
import urllib.request
import sys
import json
import ssl

api_key = ''
ENDPOINT = 'https://api.gandi.net/v5/livedns'

def get_gandi_ip(domain, hostname):
    req = urllib.request.Request('%s/domains/%s/records/%s/A' % (ENDPOINT, domain, hostname))
    req.add_header('Authorization', 'Bearer %s' % api_key)
    try:
        response = urllib.request.urlopen(req, context = ssl.create_default_context()).read()
    except HTTPError as e:                                                                                                                                                    
        print('HTTP Error encountered while trying to fetch recordset: ',e.code)                                                                                                                                          
        exit()
    except URLError as e:                                                                                                                                                     
        print('URL Error encountered while trying to fetch recordset: ', e.reason)
        exit()
    else:
        payload = json.loads(response.decode('utf-8'))
        return payload['rrset_values'][0]

def set_gandi_ip(addr, domain, hostname):
    update = {
       'rrset_name': hostname,
       'rrset_type': 'A',
       'rrset_values': [addr],
       'rrset_ttl': 300,
    }

    req = urllib.request.Request('%s/domains/%s/records/%s/A' % (ENDPOINT, domain, hostname), method='PUT')
    req.add_header('Authorization', 'Bearer %s' % api_key)
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req, data = json.dumps(update).encode('utf-8'), context = ssl.create_default_context()).read()
    except HTTPError as e:
        print('HTTP error encountered while trying to configure recordset: ',e.code)
        exit()
    except URLError as e:
        print('URL Error encountered while trying to configure recordset: ', e.reason)
        exit()
    else:
        payload = json.loads(response.decode('utf-8'))



#       good -  Update successfully.
#       nochg - Update successfully but the IP address have not changed.
#       nohost - The hostname specified does not exist in this user account.
#       abuse - The hostname specified is blocked for update abuse.
#       notfqdn - The hostname specified is not a fully-qualified domain name.
#       badauth - Authenticate failed.
#       911 - There is a problem or scheduled maintenance on provider side
#       badagent - The user agent sent bad request(like HTTP method/parameters is not permitted)
#       badresolv - Failed to connect to  because failed to resolve provider address.
#       badconn - Failed to connect to provider because connection timeout.


if __name__ == '__main__':

    if len(sys.argv) != 5:
        print("Usage: livedns <username> <api key> <fqdn> <ip>")
        sys.exit(1)

    username = sys.argv[1] # ignored
    api_key = sys.argv[2]
    fqdn = sys.argv[3]
    ip = sys.argv[4]

    dot = fqdn.find('.')
    if dot == -1:
        print('notfqdn')
        exit()

    # if this is a top domain (a-la kofemann.dev) then use '@' as a special placeholder for empty name
    if fqdn.find('.', dot + 1) == -1:
        hostname = '@'
        domain = fqdn
    else:
        hostname = fqdn[:dot]
        domain = fqdn[dot+1:]

    set_gandi_ip(ip, domain, hostname)
    new_ip = get_gandi_ip(domain, hostname)
    print('good')

    exit()
