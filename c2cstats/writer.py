#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
Generate html pages for each directory of images
"""

import os
import os.path
from shutil import copytree, ignore_patterns
from jinja2 import Environment, PackageLoader
from c2cstats.parser import Username

THEMES_PATH = os.path.normpath(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                            '..', 'themes'))
STATIC_PATH = os.path.join('..', 'static')

class Writer():
    """ Generate html pages for each directory of images """

    def __init__(self, data, settings):
        self.data = data
        self.settings = settings
        self.theme_path = os.path.join(THEMES_PATH, self.settings['THEME'])

        theme_rel_path = os.path.relpath(self.theme_path,
                                         os.path.dirname(__file__))
        self.jinja_env = Environment(loader=PackageLoader('c2cstats',
                                                          theme_rel_path))

        self.context = {}
        self.create_context()
        self.copy_static_files()
        self.render_template(self.settings['INDEX_PAGE'])

    def render_template(self, template_name):
        "Render the html page"
        # , **context
        t = self.jinja_env.get_template(template_name)
        page = t.render(self.context) #.encode('utf-8')

        # save page
        f = open(os.path.join(self.settings['OUTPUT_DIR'], template_name), 'w')
        f.write(page)
        f.close()

    def copy_static_files(self):
        "Copy static files (css, js) to _output/static/"
        path = os.path.normpath(os.path.join(self.settings['OUTPUT_DIR'],
                                             STATIC_PATH))

        if os.path.isdir(path):
            return
        copytree(self.theme_path, path, ignore=ignore_patterns('*.html'))

    def create_context(self):
        user = Username(self.data.user_id)
        self.context['nboutings'] = self.data.nboutings
        self.context['user_id'] = self.data.user_id
        self.context['static_path'] = STATIC_PATH
        self.context['username'] = user.name

        plots = self.settings['PLOTS']
        for p in plots:
            p['file'] += self.settings['OUTPUT_EXT']
        self.context['plots'] = plots


