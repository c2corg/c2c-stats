#!/usr/bin/env python2
# -*- coding:utf-8 -*-

# Copyright (c) 2012-2013 Simon Conseil <simon.conseil at camptocamp.org>

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

from gevent import monkey; monkey.patch_all()
from flask.ext.script import Manager, Server, Shell

from c2cstats import app
from c2cstats.generators import generate

# app.debug = True


def _make_context():
    return dict(app=app, generate=generate)

manager = Manager(app)
manager.add_command("shell", Shell(make_context=_make_context))
manager.add_command("runserver", Server(
    extra_files=['c2cstats/generators.py', 'c2cstats/parser.py']))

if app.debug:
    import logging
    app.logger.setLevel(logging.DEBUG)

    app.config['ASSETS_DEBUG'] = True

    # the toolbar is only enabled in debug mode
    try:
        from flask_debugtoolbar import DebugToolbarExtension
        toolbar = DebugToolbarExtension(app)
    except ImportError:
        print "Install Flask-DebugToolbar to use it"


if __name__ == "__main__":
    manager.run()
