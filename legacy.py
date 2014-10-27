import json
import requests
import re

# Invoke ATTED web services given a locus and correlation coefficient. Return a list of coexpressed genes as JSON
# Example URI: http://atted.jp/cgi-bin/API_coex.cgi?At2g39730/cor/0.85
#              http://atted.jp/cgi-bin/API_coex.cgi?AT2G39730/cor/0.85
# Response: {[At1g42970,0.8554],[At5g66570,0.8529],[At1g06680,0.8506]} which is invalid JSON

def search(arg):

# arg contains a dict with two key:values
#
# locus is AGI identifier and is mandatory
# correlation_coefficient is the minimum correlation coefficient to return

    if not (('locus' in arg) and ('correlation_coefficient' in arg)):
        return
        
	# Check that client has requested what looks like a valid transcript identifier    
    locus = arg['locus']
    locus = locus.upper()
    p = re.compile('AT[1-5MC]G[0-9]{5,5}', re.IGNORECASE)
    if not p.search(locus):
        return

    # Validate correlation_coefficient between 0-1
    cc = arg['correlation_coefficient']
    if not ((cc > 0.0) and (cc <= 1.0)):
    	return
    
    # When constructing the URI, it's critical that locus be in the form At[1-5]g[0-9]{5,5}
    # because the remote service is case sensitive
    locus_cased = locus.replace('AT', 'At')
    locus_cased = locus_cased.replace('G', 'g')
    svc_url = 'http://atted.jp/cgi-bin/API_coex.cgi?' + locus_cased + '/cor/' + repr(cc)

    r = requests.get(svc_url)

    # Interpret the result string, turn it into AIP JSON records
    rt = r.text
    # Double check for empty result set
    if not rt == '{}':

	    rt = rt.replace('{','')
	    rt = rt.replace('}','')
	    rt = rt.replace(' ','')

	    records = rt.split('],[')

	    for rec in records:
	    	rec = rec.replace('[','')
	    	rec = rec.replace(']','')
	    	fields = rec.split(',')
	    	# fields should now contain JUST locus and coefficient, suitable for presentation
	        
	        transformed_cc = {
	    	    'class': 'locus_relationship',
	    	    'reference': 'TAIR10',
	            'locus': locus,
	            'related_entity': fields[0].upper(),
	            'relationships': [ {'type': 'coexpression', 'direction': 'undirected',
	                                'scores': [ 
	                                    {'correlation_coefficient' : fields[1] }
	                                ]}]}

	        # Note that this is the same data structure being sent by the BAR expresslogs service.                        
	        print json.dumps(transformed_cc, indent=3)
	        print '---'



def list(arg):
	pass

