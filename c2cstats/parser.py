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

import json
import logging
import requests
import grequests
import time
import numpy as np

NB_ITEMS = 50
BASE_URL = "http://www.camptocamp.org/outings/list/users/%s/format/json/npp/%d/page/%d"

ACTIVITIES = ['',
              u'alpinisme neige, glace, mixte',
              u'cascade de glace',
              u'escalade',
              u'randonnée pédestre',
              u'raquette',
              u'rocher haute montagne',
              u'ski, surf']

COTATIONS = {
    'ice_rating': {'name': 'cot_glace', 'format': 'U2'},
    'mixed_rating': {'name': 'cot_mixte', 'format': 'U2'},
    'global_rating': {'name': 'cot_globale', 'format': 'U3'},
    'labande_global_rating': {'name': 'cot_globale', 'format': 'U3'},
    'rock_free_rating': {'name': 'cot_libre', 'format': 'U3'},
    'rock_required_rating': {'name': 'cot_oblige', 'format': 'U3'},
    'aid_rating': {'name': 'cot_artif', 'format': 'U2'},
    'hiking_rating': {'name': 'cot_rando', 'format': 'U2'},
    'snowshoeing_rating': {'name': 'cot_raquette', 'format': 'U2'},
    'toponeige_technical_rating': {'name': 'cot_skitech', 'format': 'U3'},
    'labande_ski_rating': {'name': 'cot_skiponc', 'format': 'U2'},
    'engagement_rating': {'name': 'engagement', 'format': 'U3'},
    'toponeige_exposition_rating': {'name': 'exposition', 'format': 'U2'},
    'equipment_rating': {'name': 'equipement', 'format': 'U2'}
}


class ParserError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class Outings:
    """Get and parse the list of outings of user `user_id``."""

    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.logger = logging.getLogger(__name__)

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
        """Download `url` and return the json converted to dict."""

        r = requests.get(url)
        r.encoding = 'utf-8'

        if r.status_code != 200:
            raise ParserError('Page not found')
        return self.page_to_json(r.text)

    def page_to_json(self, page):
        """Fix errors in the json : hasTrack & conditions miss values."""

        content = page.replace('"hasTrack": ,', '')
        content = content.replace('"conditions": ,', '')

        try:
            resp = json.loads(content)
        except ValueError:
            raise ParserError("Error while loading the json data")

        return resp

    def get_outings(self):
        """Download all the outings."""

        t0 = time.time()
        url = self.outings_url()

        self.logger.debug("Get %s ...", url)
        self.content = self.get_page(url)
        self.download_time = time.time() - t0

        self.nboutings = self.content.get('totalItems', 0)
        if self.nboutings == 0:
            raise ParserError('No items')

        self.logger.info("Process user %s - %d outings", self.user_id,
                         self.nboutings)

        # Compute the number of pages
        nb_page = ((self.nboutings - 1) / NB_ITEMS) + 1

        if nb_page > 1:
            urls = []
            for page in xrange(2, nb_page + 1):
                urls.append(self.outings_url(page=page))

            t0 = time.time()
            rs = (grequests.get(u) for u in urls)
            resp = grequests.map(rs)

            for r in resp:
                content = self.page_to_json(r.text)
                self.content['items'].extend(content['items'])
            t1 = time.time()
            self.download_time += t1 - t0

        if len(self.content['items']) != self.nboutings:
            raise ParserError('Missing items')

    def parse(self):
        """Parse the content of each line of the table."""

        self.area = []
        self.date = np.zeros(self.nboutings, dtype=np.dtype('U20'))
        self.activity = np.zeros(self.nboutings, dtype=np.dtype('U30'))
        self.altitude = np.zeros(self.nboutings, dtype=np.dtype('U6'))
        self.gain = np.zeros(self.nboutings, dtype=np.dtype(np.int16))

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
            if item['linkedAreas']:
                self.area.append(item['linkedAreas'][0]['name'])

            ratings = item.get('routes_rating', {}) or {}
            for key, val in ratings.iteritems():
                cot = getattr(self, COTATIONS[key]['name'])
                cot[n] = val

        self.area = np.array(self.area)
