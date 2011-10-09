#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from c2cstats import app
from flask import url_for

with app.test_request_context():
    print url_for('index')
    print url_for('show_user_stats', user_id=1000)
    print url_for('static', filename='css/style.css')
    print url_for('static', filename='_output/1424')

app.debug = True
app.run()
