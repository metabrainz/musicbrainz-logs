from flask import Flask, render_template
from os import path

STATIC_PATH = "/static"
STATIC_FOLDER = "static"
TEMPLATE_FOLDER = "templates"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = path.join("..", STATIC_FOLDER),
            template_folder = path.join("..", TEMPLATE_FOLDER))

import index
import facet
import search
import filtered_facet
import common
