#!/usr/bin/env python
    
import urllib
import urllib2
import json
from ml_server import app

def solr_query(query):
    url = "http://%s:%d/solr/select?q=%s" % (app.SOLR_SERVER, app.SOLR_PORT, query)
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        return (None,  "The SOLR servers says: Ur query sucks: '%s' %d: %s" % (query, e.code, e.reason)) 
    except urllib2.URLError, e:
        return (None, "The SOLR server could not be reached: %s" % e.args[0][1])
    except:
        return (None, "Unknown error communicating with SOLR server.")
    
    try:
        jdata = response.read()
    except IOError, e:
        return (None, "Problem communicating with SORL server: " + str(e))

    print jdata

    try:
        return (json.loads(jdata), "")
    except ValueError, e:
        return (None, "JSON Error: %s" % str(e))
