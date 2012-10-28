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

import locale
locale.setlocale(locale.LC_ALL, '')

from c2cstats.parser import ParserError
from c2cstats.generators import generate

from flask import Flask, request, redirect, url_for, render_template, \
    jsonify, flash
from flask.ext.cache import Cache
from flask.ext.assets import Environment

# configuration
SECRET_KEY = 'development key'
CACHE_TYPE = 'null'
CACHE_DIR = '_cache'
CACHE_THRESHOLD = 100
LOGGING_FILE = 'c2cstats.log'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('C2CSTATS_SETTINGS', silent=True)

assets = Environment(app)
cache = Cache(app)

# logging config
if not app.debug:
    import logging
    file_handler = logging.FileHandler(app.config['LOGGING_FILE'])
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(filename)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)


@app.route('/')
@cache.cached(timeout=86400)
def index():
    return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/user/')
def user_index():
    return redirect(url_for('index'))


@app.route('/user/<int:user_id>/json')
@cache.cached(timeout=604800)
def get_user_stats(user_id):

    try:
        data = generate(str(user_id))
    except ParserError:
        msg = u'Error while generating statistics'
        app.logger.error(msg)
        data = {'error': msg}
    except:
        msg = u'Something went wrong ...'
        app.logger.error(msg)
        data = {'error': msg}

    # jsonify uses indent=None for XMLHttpRequest
    return jsonify(**data)

    # resp = make_response(json.dumps(data, indent=None))
    # resp.mimetype = 'application/json'
    # return resp


@app.route('/user/<int:user_id>')
@cache.cached(timeout=86400)
def show_user_stats(user_id):
    user_id = str(user_id)

    context = {
        'json_url': url_for('get_user_stats', user_id=user_id),
        'user_id': user_id
        }

    return render_template('user.html', **context)


@app.route('/query', methods=['POST'])
def query_user():
    try:
        user_id = int(request.form['user_id'])
    except ValueError:
        flash(u"Le numéro d'utilisateur n'est pas valide", 'alert-error')
        return redirect(url_for('index'))

    return redirect(url_for('show_user_stats', user_id=user_id))
