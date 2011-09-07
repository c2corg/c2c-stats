#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os, sys

activities = (u'alpinisme neige, glace, mixte', u'cascade de glace',
              u'escalade', u'rocher haute montagne', u'ski, surf')

_CONFIG = {'THEME': 'default',
           'INDEX_PAGE': 'index.html',
           'LINK': 'https://github.com/saimn/c2c-stats',
           'OUTPUT_DIR': '_output',
           'OUTPUT_EXT': '.svg',
           'ACTIVITIES': activities,
           }

def read_settings(filename=''):
    "Load a Python file into a dictionary."
    context = _CONFIG.copy()
    if filename:
        tempdict = {}
        execfile(filename, tempdict)
        for key in tempdict:
            if key.isupper():
                context[key] = tempdict[key]

    for path in ['OUTPUT_DIR']:
        if path in context and not os.path.isabs(context[path]):
            context[path] = os.path.abspath(os.path.normpath(context[path]))

    return context
