#!/usr/bin/env python
    
import urllib2
import json
from flask import Flask, request, render_template

# 100 top user agents of all time:
# *:*&facet=true&facet.field=t_useragent&facet.limit=1000&rows=0&wt=json

SOLR_SERVER = "localhost"
SOLR_PORT   = 8983

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = STATIC_FOLDER,
            template_folder = TEMPLATE_FOLDER)

def generate_response_page(field, query):
    print "hi!"
    url = "http://%s:%d/solr/select?q=%s" % (SOLR_SERVER, SOLR_PORT, query)
    response = urllib2.urlopen(url)
    jdata = response.read()
    data = json.loads(jdata)
    ret = []
    data = data['facet_counts']['facet_fields'][field]
    for i in xrange(len(data) / 2):
        ret.append({ 'field' : data[i * 2], 'value' : data[i * 2 + 1] })
    return ret

@app.route("/useragent/<field>")
def useragent(field):
    docs = generate_response_page(field, "*:*&facet=true&facet.field=%s&facet.limit=1000&rows=0&wt=json" % field)
    return render_template("facet_response", docs=docs, title="Top user agents: %s" % field)

@app.route("/")
def index():
    return render_template("index", title="MusicBrainz Logs")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
