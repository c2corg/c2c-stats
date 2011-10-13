#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import codecs
import urlparse
import locale
locale.setlocale(locale.LC_ALL, '')

from datetime import datetime

from c2cstats.parser import Outings, ParserError
from c2cstats.plots import Plots
from c2cstats.writer import Writer

from flask import Flask, request, g, redirect, url_for, \
     render_template, flash

# configuration
SECRET_KEY = 'development key'
IMG_DIR = '_output'
IMG_URL = '/images'
IMG_EXT = ['.png']

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

    context = {
        'img_url': app.config['IMG_URL'],
        'user_id': user_id,
        }

    user_path = os.path.join(data_dir, user_id)
    index_file = os.path.join(user_path, 'index.html')

    if os.path.isfile(index_file):
        with codecs.open(index_file, encoding='utf-8', mode='r') as f:
            page = f.read()
    else:
        try:
            data = Outings(user_id)
        except ParserError:
            flash('Error while loading page', 'error')
            return redirect(url_for('index'))

        plots = Plots(data, data_dir)
        plots.plot_all()

        context['nboutings'] = data.nboutings

        d = datetime.now()
        context['date_generated'] = unicode(d.strftime('%d %B %Y à %X'), 'utf-8')

        context['files'] = [f for f in os.listdir(user_path)
                            if os.path.splitext(f)[1] in app.config['IMG_EXT']]

        page = render_template('user.html', **context)
        with codecs.open(index_file, encoding='utf-8', mode='w') as f:
            f.write(page)

    return page


@app.route('/query', methods=['POST'])
def query_user():
    return redirect(url_for('show_user_stats',
                            user_id=int(request.form['user_id'])))

