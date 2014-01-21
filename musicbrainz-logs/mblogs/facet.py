#!/usr/bin/env python
    
import urllib
import urllib2
import json
from flask import request, render_template, redirect
from cgi import escape
from ml_server import app

DEFAULT_QUERY = "*"
DEFAULT_FIELD = "f_useragent"
FIELDS        = [ "useragent", "f_useragent", "s_useragent", "t_useragent", "ip", "httpdate", "request", "size", "status" ]

def generate_facet_page(field, query, title, rows=100):
    if not query:
        query = DEFAULT_QUERY
    if not field:
        field = DEFAULT_FIELD

    url = "http://%s:%d/solr/select?q=%s:%s&facet=true&facet.mincount=1&facet.field=%s&facet.limit=%d&rows=0&wt=json" % (app.SOLR_SERVER, app.SOLR_PORT, field, query, field, rows)
    try:
        response = urllib2.urlopen(url)
        pass
    except urllib2.HTTPError, e:
        return render_template("facet_response", 
                               error="The SOLR servers says: Ur query sucks: '%s'" % query, 
                               query=query,
                               field=field,
                               fields=FIELDS,
                               title=title)
    except urllib2.URLError:
        return render_template("facet_response", 
                               error="The SOLR server could not be reached.",
                               query=query,
                               field=field,
                               fields=FIELDS,
                               title=title)
    except:
        return render_template("facet_response", 
                               error="Unknown error communicating with SOLR server.",
                               query=query,
                               fields=FIELDS,
                               field=field,
                               title=title)
        
    jdata = response.read()
    data = json.loads(jdata)
    docs = []
    doc_data = data['facet_counts']['facet_fields'][field]
    num_found = data['response']['numFound']
    total = 0
    for i in xrange(len(doc_data) / 2):
        total += doc_data[i * 2 + 1]
        docs.append({ 'field' : escape(doc_data[i * 2]), 
                      'value' : "{:,}".format(doc_data[i * 2 + 1]) })

    return render_template("facet_response", 
                           docs=docs, 
                           count=len(docs),
                           num_found=num_found,
                           field=field,
                           query=query,
                           url=url,
                           fields=FIELDS,
                           total="{:,}".format(total),
                           title=title)

@app.route("/facet")
def facet():
    try:
        field = request.args['field']
    except KeyError:
        field = ""
    try:
        query = request.args['query']
    except KeyError:
        query = ""

    if field and query:
        print "/facet/%s/%s" % (urllib.quote(field), urllib.quote(query))
        return redirect("/facet/%s/%s" % (urllib.quote(field), urllib.quote(query)))
    if field:
        return redirect("/facet/%s" % urllib.quote(field))
    return generate_facet_page("", "", "Facet search");

@app.route("/facet/<field>")
def facet_field(field):
    title = "Facet search on %s" % field
    return generate_facet_page(field, "", title)

@app.route("/facet/<field>/<query>")
def facet_field_query(field, query):
    title = "Facet search on %s for '%s'" % (field, query)
    return generate_facet_page(field, query, title)