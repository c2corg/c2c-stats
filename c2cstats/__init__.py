#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import codecs
import urlparse
import locale
locale.setlocale(locale.LC_ALL, '')

from c2cstats.parser import ParserError
from c2cstats.generators import generate_json

from flask import Flask, request, g, redirect, url_for, \
     render_template, flash

# configuration
SECRET_KEY = 'development key'
FILES_DIR = '_output'
FILES_URL = '/files'

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
    json_file = os.path.join(app.config['FILES_DIR'], user_id + '.json')

    context = {
        'json_url': app.config['FILES_URL'] + '/' + user_id + '.json',
        'user_id': user_id,
        }

    if not os.path.isfile(json_file):
        try:
            generate_json(user_id, json_file)
            flash(u'Les statistiques ont été calculées avec succés.')
        except ParserError:
            flash(u'Erreur lors du chargement de la page', 'error')
            return redirect(url_for('index'))

    return render_template('user.html', **context)


@app.route('/query', methods=['POST'])
def query_user():
    return redirect(url_for('show_user_stats',
                            user_id=int(request.form['user_id'])))
