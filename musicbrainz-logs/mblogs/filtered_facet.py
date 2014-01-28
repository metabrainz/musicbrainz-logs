#!/usr/bin/env python
    
import urllib
import urllib2
import json
from operator import itemgetter
from flask import request, render_template, redirect
from cgi import escape
from ml_server import app

# Filter facets into groups: 
#   Known gratis customers: beets, vlc, open source tools, etc
#   Known paying customers: Figure 8 media, etc
#   Unknown user agents

# all string names should be lowercase
gratis_useragent_strings = ["beets", "vlc", "headphones", "picard", "banshee", "xbmc", "googlebot"]
paying_useragent_strings  = ["jaikoz", "figureeight", "songkong", "guardian.co.uk" ]

DEFAULT_QUERY = "*"
DEFAULT_FIELD = "f_useragent"
FIELDS        = [ "useragent", "f_useragent", "s_useragent", "t_useragent", "ip", "httpdate", "request", "size", "status" ]

def sort_facets(facets):
    print "sort facets --"
    ret = []
    for k in sorted(facets.keys()):
        print k
        ret.append({ 'field' : k, 'value' : facets[k]})

    return ret

def filter_useragents(docs):
    gratis_useragents = {}
    paying_useragents = {}
    other_useragents = {}
    for doc in docs:
        found = False
        lc_field = doc['field'].lower()
        for ua in gratis_useragent_strings:
            if lc_field.find(ua) != -1:
                found = True
                try:
                    count = gratis_useragents[ua]
                except KeyError:
                    count = 0

                gratis_useragents[ua] = count + doc['value']
                break
        if not found:
            for ua in paying_useragent_strings:
                if lc_field.find(ua) != -1:
                    found = True
                    try:
                        count = paying_useragents[ua]
                    except KeyError:
                        count = 0

                    paying_useragents[ua] = count + doc['value']
                    break
        if not found:
            other_useragents[ua] = count + doc['value']

    gratis_useragents = sort_facets(gratis_useragents)
    paying_useragents = sort_facets(paying_useragents)
    other_useragents = sort_facets(other_useragents)

    return (gratis_useragents,
            paying_useragents,
            other_useragents)

def jazz_up_results(doc_list):
    docs = []
    facet_count = 0
    for doc in doc_list:
        facet_count += int(doc['value'])
        docs.append({ 'field' : escape(doc['field']),
                      'value' : "{:,}".format(doc['value']) })

    return (facet_count, docs)

def generate_facet_page(field, query, title, rows=100):
    if not query:
        query = DEFAULT_QUERY
    if not field:
        field = DEFAULT_FIELD

    url = "http://%s:%d/solr/select?q=%s:%s&facet=true&facet.mincount=1&facet.field=%s&facet.limit=%d&rows=0&wt=json" % (app.SOLR_SERVER, app.SOLR_PORT, field, query, field, rows)
    print url
    try:
        response = urllib2.urlopen(url)
        pass
    except urllib2.HTTPError, e:
        code = e.code
        return render_template("filtered_facet_response", 
                               error="The SOLR servers says: Ur query sucks: '%s' %d" % (query, code), 
                               query=query,
                               field=field,
                               fields=FIELDS,
                               url=url,
                               title=title)
    except urllib2.URLError, e:
        code = e.getcode()
        return render_template("filtered_facet_response", 
                               error="The SOLR server could not be reached: %d" % code,
                               query=query,
                               field=field,
                               fields=FIELDS,
                               url=url,
                               title=title)
    except:
        return render_template("filtered_facet_response", 
                               error="Unknown error communicating with SOLR server.",
                               query=query,
                               fields=FIELDS,
                               field=field,
                               url=url,
                               title=title)
        
    jdata = response.read()

    data = json.loads(jdata)
    docs = []
    doc_data = data['facet_counts']['facet_fields'][field]
    num_found = data['response']['numFound']

    for i in xrange(len(doc_data) / 2):
        docs.append({ 'field' : doc_data[i * 2], 
                      'value' : doc_data[i * 2 + 1] })

    gratis_useragents, paying_useragents, other_useragents = filter_useragents(docs)
    ret = []
    ret.append(jazz_up_results(gratis_useragents))
    ret.append(jazz_up_results(paying_useragents))
    ret.append(jazz_up_results(other_useragents))

    return render_template("filtered_facet_response", 
                           docs=docs, 
                           num_found="{:,}".format(num_found),
                           doc_count="{:,}".format(len(docs)),
                           facet_count="{:,}".format(facet_count),
                           field=field,
                           query=query,
                           url=url,
                           fields=FIELDS,
                           title=title)

@app.route("/filtered-facet")
def filtered_facet():
    try:
        field = request.args['field']
    except KeyError:
        field = ""
    try:
        query = request.args['query']
    except KeyError:
        query = ""

    if field and query:
        return redirect("/filtered-facet/%s/%s" % (urllib.quote(field), urllib.quote(query)))
    if field:
        return redirect("/filtered-facet/%s" % urllib.quote(field))
    return generate_facet_page("", "", "Filtered facet search");

@app.route("/filtered-facet/<field>")
def filtered_facet_field(field):
    title = "Filtered facet search on %s" % field
    return generate_facet_page(field, "", title)

@app.route("/filtered-facet/<field>/<query>")
def filtered_facet_field_query(field, query):
    title = "Filtered facet search on %s for '%s'" % (field, query)
    return generate_facet_page(field, query, title)
