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

import grequests
import json
import logging
import numpy as np
import requests
import time

NB_ITEMS = 50
DOMAIN = "http://www.camptocamp.org"
BASE_URL = DOMAIN + "/outings/list/users/%s/format/json/npp/%d/page/%d"

# List of activities. The order matters !
# see https://dev.camptocamp.org/trac/c2corg/browser/trunk/camptocamp.org/apps/frontend/config/app.yml.in#L147
ACTIVITIES = ['',
              u'ski, surf',
              u'alpinisme neige, glace, mixte',
              u'rocher haute montagne',
              u'escalade',
              u'cascade de glace',
              u'randonnée pédestre',
              u'raquette']

COTATIONS = {
    'aid_rating': {'name': 'cot_artif', 'format': 'U2'},
    'engagement_rating': {'name': 'engagement', 'format': 'U3'},
    'equipment_rating': {'name': 'equipement', 'format': 'U2'},
    'global_rating': {'name': 'cot_globale', 'format': 'U3'},
    'hiking_rating': {'name': 'cot_rando', 'format': 'U2'},
    'ice_rating': {'name': 'cot_glace', 'format': 'U2'},
    'labande_global_rating': {'name': 'cot_globale', 'format': 'U3'},
    'labande_ski_rating': {'name': 'cot_skiponc', 'format': 'U2'},
    'mixed_rating': {'name': 'cot_mixte', 'format': 'U2'},
    'objective_risk_rating': {'name': 'objective_risk', 'format': 'U2'},
    'rock_free_rating': {'name': 'cot_libre', 'format': 'U3'},
    'rock_required_rating': {'name': 'cot_oblige', 'format': 'U3'},
    'snowshoeing_rating': {'name': 'cot_raquette', 'format': 'U2'},
    'toponeige_exposition_rating': {'name': 'exposition', 'format': 'U2'},
    'toponeige_technical_rating': {'name': 'cot_skitech', 'format': 'U3'},
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
            raise ParserError(
                u"Page non trouvée ({}, {})".format(r.status_code, url))
        return self.load_json(r.text)

    def load_json(self, text):
        """Load the json and fix errors."""

        # hasTrack & conditions miss values
        content = text.replace('"hasTrack": ,', '')\
                      .replace('"conditions": ,', '')

        try:
            resp = json.loads(content)
        except ValueError:
            raise ParserError(u"Erreur lors du chargement du json")

        return resp

    def get_outings(self):
        """Download all the outings."""

        url = self.outings_url()
        self.logger.debug("Get %s ...", url)

        t0 = time.time()
        self.content = self.get_page(url)
        self.download_time = time.time() - t0

        self.nboutings = self.content.get('totalItems', 0)
        if self.nboutings == 0:
            raise ParserError(u"Pas de sorties")
        elif self.nboutings > 5000:
            raise ParserError(u"Trop de sorties !")

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
            self.download_time += (time.time() - t0)

            for r in resp:
                content = self.load_json(r.text)
                self.content['items'].extend(content['items'])

        if len(self.content['items']) != self.nboutings:
            raise ParserError(u"Des sorties sont manquantes")

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
                if key in COTATIONS:
                    cot = getattr(self, COTATIONS[key]['name'])
                    cot[n] = val

        self.area = np.array(self.area)
