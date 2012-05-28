#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from c2cstats import app

# the toolbar is only enabled in debug mode
app.debug = True

try:
    from flask_debugtoolbar import DebugToolbarExtension
    toolbar = DebugToolbarExtension(app)
except ImportError:
    print "Install Flask-DebugToolbar to use it"

# if app.config['DEBUG']:
#     from werkzeug import SharedDataMiddleware
#     import os
#     app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
#       app.config['FILES_URL']: os.path.join(os.path.dirname(__file__),
#                                             app.config['FILES_DIR'])
#     })

# useful code to test urls:
# with app.test_request_context():
#     from flask import url_for
#     print url_for('index')
#     print url_for('show_user_stats', user_id=1000)
#     print url_for('static', filename='css/style.css')

app.run()
