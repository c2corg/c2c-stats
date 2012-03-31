#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from c2cstats import app
from flask import url_for
from flask_debugtoolbar import DebugToolbarExtension

# the toolbar is only enabled in debug mode
app.debug = True
toolbar = DebugToolbarExtension(app)

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
      app.config['FILES_URL']: os.path.join(os.path.dirname(__file__),
                                            app.config['FILES_DIR'])
    })

# with app.test_request_context():
#     print url_for('index')
#     print url_for('show_user_stats', user_id=1000)
#     print url_for('static', filename='css/style.css')

app.run()
