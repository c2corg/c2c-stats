#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
Generate html pages for each directory of images
"""

import os
from shutil import copytree, ignore_patterns
from jinja2 import Environment, PackageLoader
from c2cstats.parser import Username

TPL_PATH = 'templates'
STATIC_DIR = 'static'

class Writer():
    """ Generate html pages for each directory of images """

    def __init__(self, data, settings):
        self.data = data
        self.settings = settings
        self.jinja_env = Environment(loader=PackageLoader('c2cstats', TPL_PATH))

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

        dst_path = os.path.normpath(os.path.join(self.settings['OUTPUT_DIR'],
                                                 '..', STATIC_DIR))

        if not os.path.isdir(dst_path):
            static_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                       STATIC_DIR)
            copytree(static_path, dst_path)


    def create_context(self):
        user = Username(self.data.user_id)
        self.context['nboutings'] = self.data.nboutings
        self.context['user_id'] = self.data.user_id
        self.context['static_path'] = os.path.join('..', STATIC_DIR)
        self.context['username'] = user.name

        output_dir = self.settings['OUTPUT_DIR']
        fileList = [os.path.normcase(f)
                    for f in os.listdir(output_dir)]
        fileList = [f for f in fileList
                    if os.path.splitext(f)[1] in self.settings['OUTPUT_EXT']]

        self.context['files'] = sorted(fileList)
