#!/usr/bin/env python
    
import urllib
import urllib2
import json
from flask import Flask, request, render_template, redirect
from cgi import escape

# 100 top user agents of all time:
# *:*&facet=true&facet.field=t_useragent&facet.limit=1000&rows=0&wt=json
test_json = '{"responseHeader":{"status":0,"QTime":12011,"params":{"facet":"true","facet.mincount":"1","q":"f_useragent:beets*","facet.limit":"100","facet.field":"f_useragent","wt":"json","rows":"0"}},"response":{"numFound":32114276,"start":0,"docs":[]},"facet_counts":{"facet_queries":{},"facet_fields":{"f_useragent":["beets/1.0b15 python-musicbrainz-ngs/0.3devMODIFIED ( http://beets.radbox.org/ )",31294218,"beets/1.3.2 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",539976,"beets/1.3.1 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",94607,"beets/1.3.3 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",47742,"beets/1.3.0 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",44375,"beets/1.2.1 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",24520,"beets/1.2.2 python-musicbrainz-ngs/0.5dev ( http://beets.radbox.org/ )",23337,"beets/1.0b15  i-really-like-fish-n-chips/0.3devMODIFIED ( http://beets.radbox.org/ )",9427,"beets/1.0b15 i-hope-this-works/0.3devMODIFIED ( http://beets.radbox.org/ )",7389,"beets/1.0.0 python-musicbrainz-ngs/0.2dev ( http://beets.radbox.org/ )",4313,"beets/1.0b14 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",3155,"beets/1.0b12 python-musicbrainz-ngs/0.1 ( http://beets.radbox.org/ )",3142,"beets/1.0b15 valheru-musicbrainz/0.3devMODIFIED ( http://beets.radbox.org/ )",2928,"beets/1.1.0-beta.2 python-musicbrainz-ngs/0.2dev ( http://beets.radbox.org/ )",2451,"beets/1.0b14 python-musicbrainz-ngs/0.2dev ( http://beets.radbox.org/ )",1819,"beets/1.0b15 wajdi-bsoul-xyz/0.3devMODIFIED ( http://beets.radbox.org/ )",1620,"beets/1.0b14 python-musicbrainz-ngs/0.3dev ( http://beets.radbox.org/ )",1140,"beets/1.2.0 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",1091,"beets/1.1.0-beta.3 python-musicbrainz-ngs/0.3 ( http://beets.radbox.org/ )",974,"beets/1.2.2 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",809,"beets/1.0b15 bills-music/0.3devMODIFIED ( http://beets.radbox.org/ )",774,"beets/1.0b15 python-musicbrainz/0.3devMODIFIED ( http://beets.radbox.org/ )",469,"beets/1.3.2 python-musicbrainzngs/0.5dev ( http://beets.radbox.org/ )",463,"beets/1.0b15 python-hgf-ngs/0.3devMODIFIED ( http://beets.radbox.org/ )",411,"beets/1.0b15 kruijf/0.3devMODIFIED ( http://beets.radbox.org/ )",403,"beets/1.0b15 Mozilla 5.0/0.3devMODIFIED ( http://beets.radbox.org/ )",371,"beets/1.0b15 FUCKTHEPOLICE/0.3devMODIFIED ( http://beets.radbox.org/ )",357,"beets/1.1.0-beta.3 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",343,"beets/1.0b15 pyhead/0.3devMODIFIED ( http://beets.radbox.org/ )",300,"beets/1.0b15 musicbrainz-hps/0.3devMODIFIED ( http://beets.radbox.org/ )",275,"beets/1.1.0 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",267,"beets/1.0b15 chrome/0.3devMODIFIED ( http://beets.radbox.org/ )",244,"beets/1.3.1 python-musicbrainz-ngs/0.5dev ( http://beets.radbox.org/ )",140,"beets/1.1.0 python-musicbrainz-ngs/0.3 ( http://beets.radbox.org/ )",98,"beets/1.0b15 python-musicbrainz-ngs/0.2dev ( http://beets.radbox.org/ )",78,"beets/1.0b15 ipad-safari/0.3devMODIFIED ( http://beets.radbox.org/ )",75,"beets/1.0b16 python-musicbrainz-ngs/0.2dev ( http://beets.radbox.org/ )",47,"beets/1.3.1 python-musicbrainzngs/0.5dev ( http://beets.radbox.org/ )",33,"beets/1.0b15 thug-passion-04/0.3devMODIFIED ( http://beets.radbox.org/ )",25,"beets/1.1.0-beta.1 python-musicbrainz-ngs/0.2dev ( http://beets.radbox.org/ )",24,"beets/1.0b15 IESomething/0.3devMODIFIED ( http://beets.radbox.org/ )",15,"beets/1.1.0-beta.2 python-musicbrainz-ngs/0.3 ( http://beets.radbox.org/ )",12,"beets/1.0b13 python-musicbrainz-ngs/0.2dev ( http://beets.radbox.org/ )",11,"beets/1.0rc1 python-musicbrainz-ngs/0.2dev ( http://beets.radbox.org/ )",6,"beets/1.0rc2-dev python-musicbrainz-ngs/0.2dev ( http://beets.radbox.org/ )",1,"beets/1.1.1 python-musicbrainz-ngs/0.4 ( http://beets.radbox.org/ )",1]},"facet_dates":{},"facet_ranges":{}}}'

SOLR_SERVER   = "localhost"
SOLR_PORT     = 8983
DEFAULT_QUERY = "*"
DEFAULT_FIELD = "f_useragent"

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)

def generate_response_page(field, query, title, rows=100):
    if not query:
        query = DEFAULT_QUERY
    if not field:
        field = DEFAULT_FIELD

    url = "http://%s:%d/solr/select?q=%s:%s&facet=true&facet.mincount=1&facet.field=%s&facet.limit=%d&rows=0&wt=json" % (SOLR_SERVER, SOLR_PORT, field, query, field, rows)
    print url
    try:
#        response = urllib2.urlopen(url)
        pass
    except urllib2.HTTPError, e:
        return render_template("facet_response", 
                               error="The SOLR servers says: Ur query sucks: '%s'" % query, 
                               query=query,
                               field=field,
                               title=title)
    except urllib2.URLError:
        return render_template("facet_response", 
                               error="The SOLR server could not be reached.",
                               query=query,
                               field=field,
                               title=title)
    except:
        return render_template("facet_response", 
                               error="Unknown error communicating with SOLR server.",
                               query=query,
                               field=field,
                               title=title)
        
#    jdata = response.read()
    jdata = test_json
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
    return generate_response_page("", "", "Facet search");

@app.route("/facet/<field>")
def facet_field(field):
    title = "Facet search on %s" % field
    return generate_response_page(field, "", title)

@app.route("/facet/<field>/<query>")
def facet_field_query(field, query):
    title = "Facet search on %s for '%s'" % (field, query)
    return generate_response_page(field, query, title)

@app.route("/")
def index():
    return render_template("index", title="MusicBrainz Logs")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
