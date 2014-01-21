#!/usr/bin/env python
    
import urllib
import urllib2
import json
from flask import request, render_template, redirect
from cgi import escape
from ml_server import app

DEFAULT_QUERY = "*"
DEFAULT_FIELD = "useragent"
FIELDS        = [ "useragent", "f_useragent", "s_useragent", "t_useragent", "ip", "httpdate", "request", "size", "status" ]

def generate_search_page(field, query, title, rows=100):
    if not query:
        query = DEFAULT_QUERY
    if not field:
        field = DEFAULT_FIELD

    url = "http://%s:%d/solr/select?q=%s:%s&rows=%d&wt=json" % (app.SOLR_SERVER, app.SOLR_PORT, field, query, rows)
    try:
        response = urllib2.urlopen(url)
        pass
    except urllib2.HTTPError, e:
        return render_template("search_response", 
                               error="The SOLR servers says: Ur query sucks: '%s'" % query, 
                               query=query,
                               field=field,
                               fields=FIELDS,
                               title=title)
    except urllib2.URLError:
        return render_template("search_response", 
                               error="The SOLR server could not be reached.",
                               query=query,
                               field=field,
                               fields=FIELDS,
                               title=title)
    except:
        return render_template("search_response", 
                               error="Unknown error communicating with SOLR server.",
                               query=query,
                               fields=FIELDS,
                               field=field,
                               title=title)
        
    jdata = response.read()
    #    print jdata
    data = json.loads(jdata)
    docs = []
    doc_data = data['response']['docs']
    num_found = data['response']['numFound']
    total = 0
    for doc in doc_data:
        print doc

    return render_template("search_response", 
                           docs=doc_data, 
                           count=len(docs),
                           num_found=num_found,
                           field=field,
                           query=query,
                           url=url,
                           fields=FIELDS,
                           total="{:,}".format(total),
                           title=title)

@app.route("/search")
def search():
    try:
        field = request.args['field']
    except KeyError:
        field = ""
    try:
        query = request.args['query']
    except KeyError:
        query = ""

    if field and query:
        print "/search/%s/%s" % (urllib.quote(field), urllib.quote(query))
        return redirect("/search/%s/%s" % (urllib.quote(field), urllib.quote(query)))
    if field:
        return redirect("/search/%s" % urllib.quote(field))
    return generate_search_page("", "", "Search");

@app.route("/search/<field>")
def search_field(field):
    title = "Search on %s" % field
    return generate_search_page(field, "", title)

@app.route("/search/<field>/<query>")
def search_field_query(field, query):
    title = "Search on %s for '%s'" % (field, query)
    return generate_search_page(field, query, title)
