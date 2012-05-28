#!/usr/bin/env python2
# -*- coding:utf-8 -*-

# Copyright (c) 2012 Simon C. <contact at saimon.org>

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import logging
import sys

import locale
locale.setlocale(locale.LC_ALL, '')

from c2cstats.parser import ParserError
from c2cstats.generators import generate_json

from flask import Flask, request, redirect, url_for, render_template, \
    json, jsonify

# configuration
SECRET_KEY = 'development key'
FILES_DIR = '_output'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('C2CSTATS_SETTINGS', silent=True)

# logging config
app.logger.setLevel(logging.INFO)
# app.logger.addHandler(logging.StreamHandler(sys.stdout))

@app.route('/')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


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
            msg = u'Error while generating statistics'
            app.logger.error(msg)
            data = { 'error': msg }
        except:
            import pdb; pdb.set_trace()
            msg = u'Something went wrong ...'
            app.logger.error(msg)
            data = { 'error': msg }

    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except IOError:
        msg = u'No json file with statistics'
        app.logger.error(msg)
        data = { 'error': msg }

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
