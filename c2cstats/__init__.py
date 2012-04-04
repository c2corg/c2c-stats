#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import locale
locale.setlocale(locale.LC_ALL, '')

from c2cstats.parser import ParserError
from c2cstats.generators import generate_json

from flask import Flask, request, redirect, url_for, render_template, json, jsonify

# configuration
SECRET_KEY = 'development key'
FILES_DIR = '_output'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('C2CSTATS_SETTINGS', silent=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/')
def user_index():
    return redirect(url_for('index'))


@app.route('/user/<int:user_id>/json')
def get_user_stats(user_id):
    user_id = str(user_id)
    json_file = os.path.join(app.config['FILES_DIR'], user_id + '.json')

    if not os.path.isfile(json_file):
        try:
            generate_json(user_id, json_file)
        except ParserError:
            data = { 'error': u'Erreur lors du chargement de la page' }
        except:
            data = { 'error': u'Erreur, il y a un truc qui va pas ;-)' }

    with open(json_file, 'r') as f:
        data = json.load(f)
    return jsonify(**data)


@app.route('/user/<int:user_id>')
def show_user_stats(user_id):
    user_id = str(user_id)

    context = {
        'json_url': url_for('get_user_stats', user_id=user_id),
        'user_id': user_id
        }

    return render_template('user.html', **context)


@app.route('/query', methods=['POST'])
def query_user():
    return redirect(url_for('show_user_stats',
                            user_id=int(request.form['user_id'])))
