#!/usr/bin/env python
# encoding: utf-8
'''
Gandi v5 LiveDNS - DynDNS Update via REST API and CURL/requests

@author: cave
License GPLv3
https://www.gnu.org/licenses/gpl-3.0.html

Created on 13 Aug 2017
http://api.gandi.net/docs
http://api.gandi.net/v5/livedns
'''

import requests, json
import config
import argparse

api_endpoint = 'https://api.gandi.net/v5/livedns/domains/'
headers = {"Content-Type": "application/json", "Authorization": "Bearer " + config.api_token}

def get_dynip(ifconfig_provider):
    ''' find out own IPv4 at home <-- this is the dynamic IP which changes more or less frequently
    similar to curl ifconfig.me/ip, see example.config.py for details to ifconfig providers 
    ''' 
    r = requests.get(ifconfig_provider)
    print('Checking dynamic IP: ' , r.text.strip('\n'))
    return r.text.strip('\n')

def get_dnsip(subdomain):
    '''Find out IP for subdomain'''

    url = api_endpoint + config.domain + '/records/' + subdomain + '/A'
    u = requests.get(url, headers=headers)
    if u.status_code == 200:
        json_object = json.loads(u._content)
        print('Checking IP from DNS Record' , subdomain, ':', json_object['rrset_values'][0].strip('\n'))
        return json_object['rrset_values'][0].strip('\n')
    else:
        print('Error: HTTP Status Code ', u.status_code, 'when trying to get IP from subdomain', subdomain)
        print(json_object['message'])
        exit()

def update_records(dynIP, subdomain):
    '''Update DNS Records for subdomain'''

    url = api_endpoint + config.domain + '/records/' + subdomain
    payload = {"items" : [{"rrset_ttl": config.ttl, "rrset_values": [dynIP], "rrset_type": "A"}]}
    u = requests.put(url, data=json.dumps(payload), headers=headers)
    json_object = json.loads(u._content)

    if u.status_code == 201:
        print('Status Code:', u.status_code, ',', json_object['message'], ', IP updated for', subdomain)
        return True
    else:
        print('Error: HTTP Status Code ', u.status_code, 'when trying to update IP from subdomain', subdomain)
        print(json_object['message'])
        exit()



def main(force_update, verbosity):

    if verbosity:
        print("verbosity turned on - not implemented by now")

    #compare dynIP and DNS IP 
    dynIP = get_dynip(config.ifconfig)
    dnsIP = get_dnsip(config.subdomains[0])
    
    if force_update:
        print("Going to update/create the DNS Records for the subdomains")
        for sub in config.subdomains:
            update_records(dynIP, sub)
    else:
        if dynIP == dnsIP:
            print("IP Address Match - no further action")
        else:
            print("IP Address Mismatch - going to update the DNS Records for the subdomains with new IP", dynIP)
            for sub in config.subdomains:
                update_records(dynIP, sub)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help="increase output verbosity", action="store_true")
    parser.add_argument('-f', '--force', help="force an update/create", action="store_true")
    args = parser.parse_args()
        
        
    main(args.force, args.verbose)

