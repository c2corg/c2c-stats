#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import codecs
import urlparse
import locale
locale.setlocale(locale.LC_ALL, '')

from datetime import datetime

from c2cstats.parser import Outings, ParserError
from c2cstats.generators import generate_json

from flask import Flask, request, g, redirect, url_for, \
     render_template, flash

# configuration
SECRET_KEY = 'development key'
IMG_DIR = '_output'
IMG_URL = '/images'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('C2CSTATS_SETTINGS', silent=True)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/')
def user_index():
    return redirect(url_for('index'))

@app.route('/user/<int:user_id>')
def show_user_stats(user_id):
    user_id = str(user_id)

    data_dir = app.config['IMG_DIR']
    json_file = os.path.join(data_dir, user_id + '.json')

    context = {
        'json_url': app.config['IMG_URL'] + '/' + user_id + '.json',
        'user_id': user_id,
        }

    if not os.path.isfile(json_file):
        try:
            generate_json(user_id, json_file)
        except ParserError:
            flash('Error while loading page', 'error')
            return redirect(url_for('index'))

    # context['nboutings'] = data.nboutings

    d = datetime.now()
    context['date_generated'] = unicode(d.strftime('%d %B %Y à %X'), 'utf-8')

    return render_template('user.html', **context)


@app.route('/query', methods=['POST'])
def query_user():
    return redirect(url_for('show_user_stats',
                            user_id=int(request.form['user_id'])))

