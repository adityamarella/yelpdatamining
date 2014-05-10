import logging
import os

from flask import Flask, render_template, url_for, json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/treemap')
def index():
    context = {}
    with open('data/category_tree.json') as fp:
        data = json.load(fp)

    context['data'] = json.dumps(data)

    return render_template('treemap.html', **context)
