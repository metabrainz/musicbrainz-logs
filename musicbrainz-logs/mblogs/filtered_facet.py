#!/usr/bin/env python
    
import urllib
import urllib2
import json
from operator import itemgetter
from flask import request, render_template, redirect
from cgi import escape
from ml_server import app
from common import solr_query

# Filter facets into groups: 
#   Known gratis customers: beets, vlc, open source tools, etc
#   Known paying customers: Figure 8 media, etc
#   Unknown user agents

# all string names should be lowercase
gratis_useragent_strings = ["beets", "vlc", "headphones", "picard", "banshee", "xbmc", 
                            "googlebot", "check_http", "musicbee", "vox", "soundmaven", 
                            "muspy", "nsplayer", "recordlective", "mp3tag", "xld", 
                            "amarok", "gvfs", "universalscrobbler", "clementine",
                            "libjuicer", "zuseme", "rhythmbox", "foobar2000", "puddletag",
                            "bolktagger"]

# Give credit: tagscanner, audioexpert
# mysterious user agent strings: http://www.mediabrowser3.com/
prey_useragent_strings = ["songgenie", "anyplay", "tagscanner", "abelssoft", 
                          "audioexpert", "nokiamusicingestion",
                          "musicmeter.nl", "mytunespro", "younity", "muziclips",
                          "collectorz.com", "ezcdaudioconverter", "swinsian",
                          "easycddaextractor"]
paying_useragent_strings  = ["jaikoz", "figureeight", "songkong", "guardian", "magic", "yate",
                             "bbc"]


DEFAULT_QUERY = "*"
DEFAULT_FIELD = "f_useragent"
FIELDS        = [ "useragent", "f_useragent", "s_useragent", "t_useragent", "ip", "httpdate", "request", "size", "status" ]

def count_and_format(doc_list):
    docs = []
    facet_count = 0
    for doc in doc_list.keys():
        facet_count += doc_list[doc]
        docs.append([ escape(doc), doc_list[doc] ])

    docs = sorted(docs, key=itemgetter(1), reverse=True)
    for doc in docs:
        doc[1] = "{:,}".format(doc[1])

    return (facet_count, docs)

def filter_useragents(docs):
    gratis = {}
    paying = {}
    other = {}
    prey = {}
    for doc in docs:
        found = False
        lc_field = doc['field'].lower()
        for ua in gratis_useragent_strings:
            if lc_field.find(ua) != -1:
                found = True
                try:
                    count = gratis[ua]
                except KeyError:
                    count = 0

                gratis[ua] = count + doc['value']
                break
        if not found:
            for ua in paying_useragent_strings:
                if lc_field.find(ua) != -1:
                    found = True
                    try:
                        count = paying[ua]
                    except KeyError:
                        count = 0

                    paying[ua] = count + doc['value']
                    break
        if not found:
            for ua in prey_useragent_strings:
                if lc_field.find(ua) != -1:
                    found = True
                    try:
                        count = paying[ua]
                    except KeyError:
                        count = 0

                    prey[ua] = count + doc['value']
                    break
        if not found:
            try:
                count = paying[lc_field]
            except KeyError:
                count = 0
            other[lc_field] = count + doc['value']

    (gratis_facets, gratis) = count_and_format(gratis)
    (paying_facets, paying) = count_and_format(paying)
    (prey_facets, prey) = count_and_format(prey)
    (other_facets, other) = count_and_format(other)
    total_facets = gratis_facets + paying_facets + other_facets + prey_facets

    groups = []
    groups.append({ 
                  'docs' : gratis, 
                  'count' : "{:,}".format(gratis_facets),
                  'percent' : int(100 * gratis_facets / total_facets),
                  'headers' : [ 
                          { 'width' : 50, 'text' : 'Gratis' } ,
                          { 'width' : 50, 'text' : "%s (%d%%)" % ("{:,}".format(gratis_facets), 
                                               int(100 * gratis_facets / total_facets)) }
                      ]
                  }) 
    groups.append({ 
                  'docs' : paying, 
                  'count' : "{:,}".format(paying_facets),
                  'percent' : int(100 * paying_facets / total_facets),
                  'headers' : [ 
                          { 'width' : 50, 'text' : 'Paying' } ,
                          { 'width' : 50, 'text' : "%s (%d%%)" % ("{:,}".format(paying_facets), 
                                                   int(100 * paying_facets / total_facets)) }
                      ]
                  }) 
    groups.append({ 
                  'docs' : prey, 
                  'count' : "{:,}".format(prey_facets),
                  'percent' : int(100 * prey_facets / total_facets),
                  'headers' : [ 
                          { 'width' : 50, 'text' : 'Prey' } ,
                          { 'width' : 50, 'text' : "%s (%d%%)" % ("{:,}".format(prey_facets), 
                                                   int(100 * prey_facets / total_facets)) }
                      ]
                  }) 
    groups.append({ 
                  'docs' : other, 
                  'count' : "{:,}".format(other_facets),
                  'percent' : int(100 * other_facets / total_facets),
                  'headers' : [ 
                          { 'width' : 50, 'text' : 'Other' } ,
                          { 'width' : 50, 'text' : "%s (%d%%)" % ("{:,}".format(other_facets), 
                                                   int(100 * other_facets / total_facets)) }
                      ]
                  }) 

    return (total_facets, groups)

def generate_facet_page(field, query, title, rows=500):
    if not query:
        return render_template("filtered_facet_response",
                               title=title,
                               fields=FIELDS,
                               query=DEFAULT_QUERY,
                               field=DEFAULT_FIELD)
    if not field:
        field = DEFAULT_FIELD

    (data, error) = solr_query("%s:%s&facet=true&facet.mincount=1&facet.field=%s&facet.limit=%d&rows=0&wt=json" % 
                               (urllib.quote(field), urllib.quote(query), urllib.quote(field), rows))
    if error:
        return render_template("filtered_facet_response", 
                               error=error,
                               query=query,
                               field=field,
                               fields=FIELDS,
                               title=title)
    docs = []
    doc_data = data['facet_counts']['facet_fields'][field]
    num_found = data['response']['numFound']

    for i in xrange(len(doc_data) / 2):
        docs.append({ 'field' : doc_data[i * 2], 
                      'value' : doc_data[i * 2 + 1] })

    facet_count, groups = filter_useragents(docs)

    summary = "%s rows with %s facets from %s documents" % (
               "{:,}".format(len(docs)),
               "{:,}".format(facet_count),
               "{:,}".format(num_found))

    return render_template("filtered_facet_response", 
                           groups=groups,
                           summary=summary,
                           query=query,
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
