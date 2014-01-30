#!/usr/bin/env python
    
import urllib
import urllib2
from flask import request, render_template, redirect
from cgi import escape
from ml_server import app
from common import solr_query

DEFAULT_QUERY = "*"
DEFAULT_FIELD = "useragent"
FIELDS        = [ "useragent", "f_useragent", "s_useragent", "t_useragent", "ip", "httpdate", "request", "size", "status" ]

def generate_search_page(field, query, title, rows=1000):
    if not query:
        return render_template("search_response",
                               title=title,
                               fields=FIELDS,
                               query=DEFAULT_QUERY,
                               field=DEFAULT_FIELD)

    (data, error) = solr_query("%s:%s&rows=%d&wt=json" % (urllib.quote(field), urllib.quote(query), rows))
    if error:
        return render_template("search_response", 
                               error=error,
                               query=query,
                               field=field,
                               fields=FIELDS,
                               title=title)

    docs = data['response']['docs']
    num_found = data['response']['numFound']

    return render_template("search_response", 
                           docs=docs, 
                           num_found="{:,}".format(num_found),
                           doc_count="{:,}".format(len(docs)),
                           field=field,
                           query=query,
                           fields=FIELDS,
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
