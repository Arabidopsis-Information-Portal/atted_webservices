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

    locus = arg['locus']
    locus = locus.upper()
    p = re.compile('AT[1-5MC]G[0-9]{5,5}', re.IGNORECASE)
    if not p.search(locus):
        raise Exception('Invalid locus ID')

    rtype = arg['relationship_type']
    rtype_native = rtype
    rtype_out = rtype

    if not rtype in ['mutual_rank', 'correlation_coefficient']:
        raise Exception('Invalid relationship_type')

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

    # Raise exception on bad HTTP status
    r.raise_for_status()

    # Interpret the result string, turn it into AIP JSON records
    try:
        r_json = r.json()

        if ('results' in r_json):

            for result in r_json['results']:

                #agi_locus_from_entrez = resolve_locus(result['gene'])
                agi_locus_from_entrez = result['gene']

                transformed_cc = {
                'class': 'locus_relationship',
                'locus': locus,
                'related_entity': agi_locus_from_entrez,
                'relationships': [ {'type': 'coexpression', 'direction': 'undirected',
                'scores': [
                {rtype : result[rtype_out] }]}]}

                print json.dumps(transformed_cc, indent=3)
                print '---'
    except ValueError:
        raise Exception('Unable to handle response '.format(r.text) )

def resolve_locus(entrez_id):
	# Here, I replicate the code for the aip/synonym_to_locus because I can't make an authenticated call to an ADAMA service from within
	# an ADAMA script. This will be remedied in 0.4 and I will replace this code with a call to synonym_to_locus
    NEO4J_SERVER_IP='52.4.211.39'
    NEO4J_SERVER_PORT='7474'
    URL = 'http://' + NEO4J_SERVER_IP + ':' + NEO4J_SERVER_PORT + '/db/data/transaction/commit'

    payload = json.dumps({
'statements': [{
'statement': "MATCH (a:Identifier { name:'%s' })-[:SYNONYM_OF*1..2]-(x:Identifier) WHERE x.kind IN ['TAIR'] return DISTINCT x.name, a.kind ORDER BY x.name" %(entrez_id,) }]})
    response = requests.post( URL,
        auth=('neo4j', '4UbczmDtK4eY6sfS'),
        data=payload,
        headers={'Content-Type': 'application/json','Accept': 'application/json; charset=UTF-8'})
    result = response.json()['results'][0]['data'][0]['row'][0]
    return result

def list(args):
    raise Exception('Not implemented yet')
