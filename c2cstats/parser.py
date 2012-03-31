#!/usr/bin/env python2
# -*- coding:utf-8 -*-

# c2cstats - Compute statistics for camptocamp.org
# Copyright (C) 2011-2012 - saimon.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; If not, see http://www.gnu.org/licenses/

import time
import urllib
import numpy as np
from bs4 import BeautifulSoup

NB_ITEMS = 100
BASE_URL = "http://www.camptocamp.org/outings/list/layout/light/users/%s/npp/%d/page/%d"

class ParserError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class Outings:
    "Parse the list of outings of user user_id"
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.parse_outings()

    @property
    def activities(self):
        acts = np.unique(self.activity)
        ind = (acts != u'')
        return list(acts[ind])

    def parse_outings(self):
        pagenb = 1
        url = get_outings_url(self.user_id, pagenb)

        print "Get %s ..." % url
        t0 = time.time()
        page, headers = get_page(url)
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
        self.date = np.zeros(self.nboutings, dtype=np.dtype('U20'))
        self.activity = np.zeros(self.nboutings, dtype=np.dtype('U30'))
        self.altitude = np.zeros(self.nboutings, dtype=np.dtype('U6'))
        self.gain = np.zeros(self.nboutings, dtype=np.dtype('I6'))
        self.area = []

        self.cot_globale = np.zeros(self.nboutings, dtype=np.dtype('U3'))
        self.cot_libre = np.zeros(self.nboutings, dtype=np.dtype('U3'))
        self.cot_oblige = np.zeros(self.nboutings, dtype=np.dtype('U3'))
        self.cot_skitech = np.zeros(self.nboutings, dtype=np.dtype('U3'))
        self.cot_skiponc = np.zeros(self.nboutings, dtype=np.dtype('U2'))
        self.cot_glace = np.zeros(self.nboutings, dtype=np.dtype('U2'))
        self.cot_rando = np.zeros(self.nboutings, dtype=np.dtype('U2'))
        self.engagement = np.zeros(self.nboutings, dtype=np.dtype('U3'))
        self.equipement = np.zeros(self.nboutings, dtype=np.dtype('U2'))
        self.exposition = np.zeros(self.nboutings, dtype=np.dtype('U2'))

        t0 = time.time()
        self.parse_outings_list(page, pagenb, soup=soup)
        self.parse_time = time.time() - t0

        # parse other pages if nboutings > 100
        nbtemp = self.nboutings - 100
        while nbtemp > 0:
            pagenb += 1
            nbtemp -= 100
            url = get_outings_url(self.user_id, pagenb)

            print "Get %s ..." % url
            t0 = time.time()
            page, headers = get_page(url)
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

        cotations = {'cot_globale': u'Cotation globale',
                     'engagement': u'Engagement',
                     'equipement': u'Qualité de l\'équipement',
                     'exposition': u'Exposition',
                     'cot_oblige': u'Cotation libre obligatoire\xa0:',
                     'cot_libre': u'Cotation libre\xa0:',
                     'cot_skitech': u'Cotation technique',
                     'cot_skiponc': u'Exposition',
                     'cot_glace': u'Cotation glace',
                     'cot_rando': u'Cotation randonnée'
                     }

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
                for c in cotations.keys():
                    if i['title'].startswith(cotations[c]):
                        self.__dict__[c][n] = i.text

            if t[9].text:
                self.area.append(t[9].a.text)

            n += 1


def get_page(url):
    "Return the HTML source of the page 'url'"
    page = urllib.urlopen(url)
    page_content = page.read()
    page_code = page.getcode()

    if page_content == "Not Found" or page_code == 404:
        raise ParserError('Page not found')

    # Remove linebreaks & tabulations
    page_content = page_content.replace("\n","").replace("\t","").replace("\r","")
    return page_content, page.headers
    # return page.decode('utf-8')

def get_outings_url(user_id, page):
    return BASE_URL % (user_id, NB_ITEMS, page)

