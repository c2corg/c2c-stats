#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import urlparse

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

    if user_id not in os.listdir(data_dir):
        try:
            data = Outings(user_id)
        except ParserError:
            flash('Error while loading page', 'error')

        plots = Plots(data, data_dir)
        plots.plot_all()

    context = {
        'img_url': app.config['IMG_URL'],
        'user_id': user_id,
        }

    context['files'] = [f for f in os.listdir(os.path.join(data_dir, user_id))
                        if os.path.splitext(f)[1] in app.config['IMG_EXT']]

    return render_template('user.html', **context)


@app.route('/query', methods=['POST'])
def query_user():
    return redirect(url_for('show_user_stats',
                            user_id=int(request.form['user_id'])))

