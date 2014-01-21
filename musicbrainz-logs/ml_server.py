#!/usr/bin/env python

from mblogs import app

app.SOLR_SERVER   = "localhost"
app.SOLR_PORT     = 8983

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
