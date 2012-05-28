#!/usr/bin/env python2
# -*- coding:utf-8 -*-

# Copyright (c) 2012 Simon C. <contact at saimon.org>

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

import json
import requests
import time
import numpy as np

NB_ITEMS = 100
BASE_URL = "http://www.camptocamp.org/outings/list/users/%s/format/json/npp/%d/page/%d"

ACTIVITIES = ['', u'ski, surf', u'alpinisme neige, glace, mixte',
              u'rocher haute montagne', u'escalade', u'cascade de glace',
              u'randonnée pédestre', u'raquette']

COTATIONS = {
    'ice_rating'                 :  {'name': 'cot_glace'   , 'format': 'U2'},
    'mixed_rating'               :  {'name': 'cot_mixte'   , 'format': 'U2'},
    'global_rating'              :  {'name': 'cot_globale' , 'format': 'U3'},
    'labande_global_rating'      :  {'name': 'cot_globale' , 'format': 'U3'},
    'rock_free_rating'           :  {'name': 'cot_libre'   , 'format': 'U3'},
    'rock_required_rating'       :  {'name': 'cot_oblige'  , 'format': 'U3'},
    'aid_rating'                 :  {'name': 'cot_artif'   , 'format': 'U2'},
    'hiking_rating'              :  {'name': 'cot_rando'   , 'format': 'U2'},
    'snowshoeing_rating'         :  {'name': 'cot_raquette', 'format': 'U2'},
    'toponeige_technical_rating' :  {'name': 'cot_skitech' , 'format': 'U3'},
    'labande_ski_rating'         :  {'name': 'cot_skiponc' , 'format': 'U2'},
    'engagement_rating'          :  {'name': 'engagement'  , 'format': 'U3'},
    'toponeige_exposition_rating':  {'name': 'exposition'  , 'format': 'U2'},
    'equipment_rating'           :  {'name': 'equipement'  , 'format': 'U2'}
    }


class ParserError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg


class Outings:
    "Get and parse the list of outings of user `user_id``"

    def __init__(self, user_id):
        self.user_id = str(user_id)
        self._session = requests.session()
        self.get_outings()
        self.parse()

    @property
    def activities(self):
        acts = np.unique(self.activity)
        ind = (acts != u'')
        return list(acts[ind])

    def outings_url(self, page=1):
        return BASE_URL % (self.user_id, NB_ITEMS, page)

    def get_page(self, url):
        "Download `url` and return the json converted to dict"

        r = self._session.get(url)
        r.encoding = 'utf-8'

        if r.status_code != 200:
            raise ParserError('Page not found')

        # Fix errors in the json : hasTrack & conditions miss values
        content = r.text.replace('"hasTrack": ,','')
        content = content.replace('"conditions": ,', '')

        try:
            resp = json.loads(content)
        except ValueError:
            raise ParserError("Error while loading the json data")

        return resp

    def get_outings(self):

        t0 = time.time()
        url = self.outings_url()
        print "Get %s ..." % url
        self.content = self.get_page(url)
        self.download_time = time.time() - t0

        self.nboutings = self.content.get('totalItems', 0)
        if self.nboutings == 0:
            raise ParserError('No items')

        print "Get the %d outings" % self.nboutings
        nb_page = (self.nboutings / 100) + 1
        if nb_page > 1:
            for p in xrange(2, nb_page+1):
                t0 = time.time()
                url = self.outings_url(page=p)
                print "Get %s ..." % url
                content = self.get_page(url)
                t1 = time.time()
                self.download_time += t1 - t0
                self.content['items'].extend(content['items'])

        if len(self.content['items']) != self.nboutings:
            raise ParserError('Missing items')

    def parse(self):
        "Get the content of each line of the table"

        self.area = []
        self.date     = np.zeros(self.nboutings, dtype=np.dtype('U20'))
        self.activity = np.zeros(self.nboutings, dtype=np.dtype('U30'))
        self.altitude = np.zeros(self.nboutings, dtype=np.dtype('U6'))
        self.gain     = np.zeros(self.nboutings, dtype=np.dtype('I6'))

        # initialize cotation arrays
        for c in COTATIONS.itervalues():
            if not hasattr(self, c['name']):
                setattr(self, c['name'],
                        np.zeros(self.nboutings, dtype=np.dtype(c['format'])))

        for n, item in enumerate(self.content['items']):
            # self.title.append(t[1].a.text)
            self.date[n] = item['date']
            # keep only the first activity
            act = item['activities'][0]
            if act:
                self.activity[n] = ACTIVITIES[int(act)]
            self.altitude[n] = item.get('maxElevation', 0)
            self.gain[n] = item.get('heightDiffUp', 0)
            self.area.append(item['linkedAreas'][0]['name'])

            ratings = item.get('routes_rating', {})
            for key, val in ratings.iteritems():
                cot = getattr(self, COTATIONS[key]['name'])
                cot[n] = val

        self.area = np.array(self.area)
