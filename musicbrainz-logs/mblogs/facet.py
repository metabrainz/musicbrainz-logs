#!/usr/bin/env python
    
import urllib
import urllib2
import json
from flask import request, render_template, redirect
from cgi import escape
from ml_server import app
from common import solr_query

DEFAULT_QUERY = "*"
DEFAULT_FIELD = "f_useragent"
FIELDS        = [ "useragent", "f_useragent", "s_useragent", "t_useragent", "ip", "httpdate", "request", "size", "status" ]

def generate_facet_page(field, query, title, rows=1000):
    if not query:
        return render_template("facet_response",
                               title=title,
                               fields=FIELDS,
                               query=DEFAULT_QUERY,
                               field=DEFAULT_FIELD)

    (data, error) = solr_query("%s:%s&facet=true&facet.mincount=1&facet.field=%s&facet.limit=%d&rows=0&wt=json" % 
                               (urllib.quote(field), urllib.quote(query), urllib.quote(field), rows))
    if error:
        return render_template("facet_response", 
                               error=error,
                               query=query,
                               field=field,
                               fields=FIELDS,
                               title=title)
    docs = []
    doc_data = data['facet_counts']['facet_fields'][field]
    num_found = data['response']['numFound']
    facet_count = 0
    for i in xrange(len(doc_data) / 2):
        facet_count += doc_data[i * 2 + 1]
        docs.append({ 'field' : escape(doc_data[i * 2]), 
                      'value' : "{:,}".format(doc_data[i * 2 + 1]) })

    return render_template("facet_response", 
                           docs=docs, 
                           num_found="{:,}".format(num_found),
                           doc_count="{:,}".format(len(docs)),
                           facet_count="{:,}".format(facet_count),
                           field=field,
                           query=query,
                           fields=FIELDS,
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
