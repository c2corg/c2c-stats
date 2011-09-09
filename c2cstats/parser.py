#!/usr/bin/env python2
# -*- coding:utf-8 -*-

# c2cstats - Compute statistics for camptocamp.org
# Copyright (C) 2009, 2010, 2011 - saimon.org
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

import json
import urllib
import numpy as np
from BeautifulSoup import BeautifulSoup

NB_ITEMS = 100
BASE_URL = "http://www.camptocamp.org/outings/list/layout/light/users/%s/npp/%d/page/%d"

class Outings:
    "Parse the list of outings of user user_id"
    def __init__(self, user_id):
        self.user_id = str(user_id)
        self.parse_outings()

    def parse_outings(self):
        pagenb = 1
        url = get_outings_url(self.user_id, pagenb)

        print u"Récupération de %s ..." % url
        page = get_page(url)
        soup = BeautifulSoup(page, convertEntities=BeautifulSoup.HTML_ENTITIES)
        nbout = soup.p.findAll('b')

        if len(nbout) == 1:
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

        self.parse_outings_list(page, pagenb)

        # parse other pages if nboutings > 100
        nbtemp = self.nboutings - 100
        while nbtemp > 0:
            pagenb += 1
            nbtemp -= 100
            url = get_outings_url(self.user_id, pagenb)
            print u"Récupération de %s ..." % url
            page = get_page(url)
            self.parse_outings_list(page, pagenb)

        self.area = np.array(self.area)
        print u"%d sorties trouvées" % self.nboutings

    def parse_outings_list(self, page, pagenb):
        "Get the content of eah line of the table"

        soup = BeautifulSoup(page, convertEntities=BeautifulSoup.HTML_ENTITIES)
        lines = soup.table.tbody.findAll('tr')

        cotations = {'cot_globale': u'Cotation globale',
                     'engagement': u'Engagement',
                     'equipement': u'Qualité de l\'équipement',
                     'exposition': u'Exposition',
                     'cot_oblige': u'Cotation libre obligatoire',
                     'cot_libre': u'Cotation libre',
                     'cot_skitech': u'Cotation technique',
                     'cot_skiponc': u'Exposition',
                     'cot_glace': u'Cotation glace',
                     'cot_rando': u'Cotation randonnée'
                     }

        n = 0 + (pagenb-1)*100
        for l in lines:
            t = l.contents
            # self.title.append(t[1].a.text)
            self.date[n] = t[2].time.text
            self.altitude[n] = t[4].text
            if t[5].text:
                self.gain[n] = int(t[5].text[:-1])
            self.area.append(t[9].a.text)

            # keep only the first one for now
            if t[3].find('span', "printonly"):
                self.activity[n] = t[3].find('span', "printonly").text

            for i in t[6].findAll('span'):
                for c in cotations.keys():
                    if i['title'].startswith(cotations[c]):
                        self.__dict__[c][n] = i.text

            n += 1


class Username:
    "Retrieve the name of user_id"
    def __init__(self, user_id):
        url = "http://www.camptocamp.org/users/fr/%s.json" % str(user_id)
        p = get_page(url)
        j = json.loads(p)
        self.name = j[u'properties'][u'name']


def get_page(url):
    """ Retourne le code source de la page 'url' """

    page = urllib.urlopen(url)
    page_content = page.read()
    page_code = page.getcode()

    if page_content == "Not Found" or page_code == 404:
        print "Erreur, la page n'existe pas."
        exit()

    #Suppression des sauts de ligne, les tabulations et les retours chariot
    page_content = page_content.replace("\n","").replace("\t","").replace("\r","")
    return page_content
    # return page.decode('utf-8')

def get_outings_url(user_id, page):
    return BASE_URL % (user_id, NB_ITEMS, page)

