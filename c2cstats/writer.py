#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""
Generate html pages for each directory of images
"""

import os
from shutil import copytree
from jinja2 import Environment, PackageLoader
from c2cstats.parser import Username

TPL_PATH = 'templates'
STATIC_DIR = 'static'
IMG_EXT = '.png'

class Writer():
    """ Generate html pages for each directory of images """

    def __init__(self, data_dir, user_id, nboutings, static=False):
        self.out_dir = data_dir
        self.jinja_env = Environment(loader=PackageLoader('c2cstats', TPL_PATH))

        self.create_context(user_id, nboutings)
        if static:
            self.copy_static_files()

        self.render_template('index.html')


    def render_template(self, template_name):
        "Render the html page"
        # , **context
        t = self.jinja_env.get_template(template_name)
        page = t.render(self.context) #.encode('utf-8')

        # save page
        f = open(os.path.join(self.out_dir, template_name), 'w')
        f.write(page)
        f.close()


    def copy_static_files(self):
        "Copy static files (css, js) to _output/static/"

        dst_path = os.path.normpath(os.path.join(self.out_dir, '..', STATIC_DIR))

        if not os.path.isdir(dst_path):
            static_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                       STATIC_DIR)
            copytree(static_path, dst_path)


    def create_context(self, user_id, nboutings):
        self.context = {}
        self.context['nboutings'] = nboutings
        self.context['user_id'] = user_id
        self.context['static_path'] = os.path.join('..', STATIC_DIR)

        user = Username(self.context['user_id'])
        self.context['username'] = user.name

        fileList = [os.path.normcase(f)
                    for f in os.listdir(self.out_dir)]
        fileList = [f for f in fileList
                    if os.path.splitext(f)[1] in IMG_EXT]

        self.context['files'] = sorted(fileList)
