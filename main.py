import json
import requests
import re

# Invoke ATTED II web services given a locus and filter parameters
# See http://atted.jp/help/API.shtml
# Example URI: http://atted.jp/cgi-bin/api2.cgi?gene=AT2G39730&type=cor&cutoff=0.85
#              http://atted.jp/cgi-bin/API_coex.cgi?AT2G39730/cor/0.85
# Response: {[At1g42970,0.8554],[At5g66570,0.8529],[At1g06680,0.8506]} which is invalid JSON

def search(arg):

# arg contains a dict with several key:values
#
# locus is AGI identifier and is mandatory
# relationship_type: mutual_rank OR correlation_coefficient
# threshold: cuotff value for relationship
# database_version: used any time a remote service has a 'version' parameter. Onus is on end user to send correct value

    if not (('locus' in arg) and ('threshold' in arg) and ('relationship_type' in arg)):
        return
    
    locus = arg['locus']
    locus = locus.upper()
    p = re.compile('AT[1-5MC]G[0-9]{5,5}', re.IGNORECASE)
    if not p.search(locus):
        return

    rtype = arg['relationship_type']
    rtype_native = rtype
    rtype_out = rtype

    if not rtype in ['mutual_rank', 'correlation_coefficient']:
    	return
    if rtype == 'mutual_rank':
    	rtype_native = 'mr'
    	rtype_out = 'mutual_rank'
    elif rtype == 'correlation_coefficient':
    	rtype_native = 'cor'
    	rtype_out = 'correlation'
    
    # Force cutoff to be a float
    cutoff = float (arg['threshold'] )

    svc_url = 'http://atted.jp/cgi-bin/api2.cgi?gene=' + locus + '&type=' + rtype_native + '&cutoff=' + repr(cutoff)
    if ('database_version' in arg):
    	svc_url = svc_url + '&db=' + arg['database_version']

    r = requests.get(svc_url)

    # Interpret the result string, turn it into AIP JSON records
    r_json = r.json()

    if ('results' in r_json):

        for result in r_json['results']:
            # resolve_locus is an example of a function that makes an authenticated Araport API call
            agi_locus_from_entrez = resolve_locus(result['gene'], arg['headers'])

            transformed_cc = {
            'class': 'locus_relationship',
            'locus': locus,
            'related_entity': agi_locus_from_entrez,
            'relationships': [ {'type': 'coexpression', 'direction': 'undirected',
            'scores': [ 
            {rtype : result[rtype_out] }]}]}

            print json.dumps(transformed_cc, indent=3)
            print '---'


def resolve_locus(entrez_id, request_headers):
    #
    # This function demonstrates how to call an Araport API using the authentication
    # information that was passed from the service. As written, this passes all
    # the request headers, but you may also extract and send specific headers
    #
    url = 'https://api.araport.org/community/v0.3/aip/resolver_fetch_locus_by_synonym_v0.2/search?identifier=' + entrez_id
    response = requests.get(url, headers = request_headers)
    if response.ok:
        res = response.json()['result'][0]
        if ('locus' in res):
            locus_resolved = response.json()['result'][0]['locus']
            return locus_resolved

    return entrez_id


def list(arg):
	pass
