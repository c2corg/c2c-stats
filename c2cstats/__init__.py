#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import urlparse

from c2cstats.parser import Outings, ParserError
from c2cstats.plots import Plots
from c2cstats.settings import read_settings
from c2cstats.writer import Writer

from flask import Flask, request, g, redirect, url_for, \
     render_template, flash, send_from_directory

# configuration
SETTINGS = read_settings()
SECRET_KEY = 'development key'

app = Flask(__name__)

# app.config['STATIC_ROOT'] = 'http://static.example.com/'
app.config['STATIC_ROOT'] = '/'

app.config.from_object(__name__)
app.config.from_envvar('C2CSTATS_SETTINGS', silent=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user/<int:user_id>')
def show_user_stats(user_id):
    user_id = str(user_id)

    data_dir = SETTINGS['OUTPUT_DIR']

    if user_id not in os.listdir(data_dir):
        try:
            data = Outings(user_id)
        except ParserError:
            flash('Error while loading page', 'error')

        plots = Plots(data, SETTINGS, data_dir)
        plots.plot_all()
        flash('Generated plots')
        # w = Writer(data, SETTINGS)

    output_dir = os.path.join(data_dir, user_id)
    # print output_dir

    files = [os.path.join(user_id, f)
             for f in os.listdir(output_dir)
             if os.path.splitext(f)[1] in SETTINGS['IMG_EXT']]

    return render_template('user.html', user_id=user_id, files=files)


@app.route('/query', methods=['POST'])
def query_user():
    flash("Statistiques pour l'utilisateur %s" % request.form['user_id'])
    return redirect(url_for('show_user_stats',
                            user_id=int(request.form['user_id'])))


@app.route('/images/<path:filename>')
def images(filename):
     return send_from_directory(SETTINGS['OUTPUT_DIR'], filename)
