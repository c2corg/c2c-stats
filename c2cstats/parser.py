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

import requests
import time
import numpy as np
from bs4 import BeautifulSoup

NB_ITEMS = 100
BASE_URL = "http://www.camptocamp.org/outings/list/layout/light/users/%s/npp/%d/page/%d"

COTATIONS = {
    u'Cotation glace': { 'name': 'cot_glace', 'format': 'U2' },
    u'Cotation mixte': { 'name': 'cot_mixte', 'format': 'U2' },
    u'Cotation globale': { 'name': 'cot_globale', 'format': 'U3' },
    u'Cotation globale ski': { 'name': 'cot_globale', 'format': 'U3' },
    u'Cotation libre': { 'name': 'cot_libre', 'format': 'U3' },
    u'Cotation libre obligatoire': { 'name': 'cot_oblige', 'format': 'U3' },
    u'Cotation libre et libre obligatoire': { 'name': 'cot_libre', 'format': 'U3' },
    u'Cotation escalade artificielle': { 'name': 'cot_artif', 'format': 'U2' },
    u'Cotation randonnée': { 'name': 'cot_rando', 'format': 'U2' },
    u'Cotation raquette': { 'name': 'cot_raquette', 'format': 'U2' },
    u'Cotation technique': { 'name': 'cot_skitech', 'format': 'U3' },
    u'Cotation ponctuelle ski': { 'name': 'cot_skiponc', 'format': 'U2' },
    u'Engagement': { 'name': 'engagement', 'format': 'U3' },
    u'Exposition': { 'name': 'exposition', 'format': 'U2' },
    u'Qualité de l\'équipement en place': { 'name': 'equipement', 'format': 'U2' }
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
        self.session = requests.session()
        self.parse_outings()

    @property
    def activities(self):
        acts = np.unique(self.activity)
        ind = (acts != u'')
        return list(acts[ind])

    def outings_url(self, page):
        return BASE_URL % (self.user_id, NB_ITEMS, page)

    def get_page(self, url):
        "Return the HTML source of the page 'url'"
        r = self.session.get(url)
        r.encoding = 'utf-8'

        if r.text == "Not Found" or r.status_code != 200:
            raise ParserError('Page not found')

        # Remove linebreaks & tabulations
        page_content = r.text.replace("\n","").replace("\t","").replace("\r","")
        return page_content

    def parse_outings(self):
        pagenb = 1
        url = self.outings_url(pagenb)

        print "Get %s ..." % url
        t0 = time.time()
        page = self.get_page(url)
        self.download_time = time.time() - t0

        soup = BeautifulSoup(page, 'lxml')
        nbout = soup.p.findAll('b')

        if len(nbout) == 0:
            raise ParserError('Invalid page')
        elif len(nbout) == 1:
            self.nboutings = int(nbout[0].text)
        else:
            self.nboutings = int(nbout[2].text)

        # self.title = []
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

        t0 = time.time()
        self.parse_outings_list(page, pagenb, soup=soup)
        self.parse_time = time.time() - t0

        # parse other pages if nboutings > 100
        nbtemp = self.nboutings - 100
        while nbtemp > 0:
            pagenb += 1
            nbtemp -= 100
            url = self.outings_url(pagenb)

            print "Get %s ..." % url
            t0 = time.time()
            page = self.get_page(url)
            t1 = time.time()
            self.download_time += t1 - t0

            t0 = time.time()
            self.parse_outings_list(page, pagenb)
            self.parse_time += time.time() - t1

        self.area = np.array(self.area)
        print "Found %d outings" % self.nboutings

    def parse_outings_list(self, page, pagenb, soup=False):
        "Get the content of each line of the table"

        if not soup:
            soup = BeautifulSoup(page, 'lxml')

        lines = soup.table.tbody.findAll('tr')

        n = (pagenb-1)*100
        for l in lines:
            t = l.contents
            # self.title.append(t[1].a.text)
            self.date[n] = t[2].time.text

            # keep only the first one for now
            if t[3].find('span', "printonly"):
                self.activity[n] = t[3].find('span', "printonly").text

            self.altitude[n] = t[4].text

            if t[5].text:
                self.gain[n] = int(t[5].text[:-1])

            for i in t[6].findAll('span'):
                cot_title = i['title'].split(u'\xa0:')[0]
                try:
                    cot = getattr(self, COTATIONS[cot_title]['name'])
                    cot[n] = i.text
                except KeyError:
                    # TODO: add logging
                    pass

            if t[9].text:
                self.area.append(t[9].a.text)

            n += 1
