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
from BeautifulSoup import BeautifulSoup

NB_ITEMS = 100
BASE_URL = "http://www.camptocamp.org/outings/list/layout/light/users/%s/npp/%d/page/%d"

class Outings:
    "Parse the list of outings of user user_id"
    def __init__(self, user_id):
        self.user_id = str(user_id)

        self.title = []
        self.date = []
        self.activity = []
        self.altitude = []
        self.gain = []
        self.area = []

        self.cot_globale = []
        self.cot_libre = []
        self.cot_oblige = []
        self.cot_skitech = []
        self.cot_skiponc = []
        self.cot_glace = []
        self.cot_rando = []
        self.exposition = []
        self.engagement = []
        self.equipement = []

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

        print u"%d sorties trouvées" % self.nboutings

    def parse_outings_list(self, page, pagenb):
        "Get the content of eah line of the table"

        soup = BeautifulSoup(page, convertEntities=BeautifulSoup.HTML_ENTITIES)
        lines = soup.table.tbody.findAll('tr')

        cotations = {'cot_globale': u'Cotation globale',
                     'engagement': u'Qualité de l\'équipement',
                     'equipement': u'Qualité de l\'équipement',
                     'cot_oblige': u'Cotation libre obligatoire',
                     'cot_libre': u'Cotation libre',
                     'cot_skitech': u'Cotation technique',
                     'cot_skiponc': u'Exposition',
                     'cot_glace': u'Cotation glace',
                     'cot_rando': u'Cotation randonnée'
                     }

        count = 0 + (pagenb-1)*100
        for l in lines:
            t = l.contents
            self.title.append(t[1].a.text)
            self.date.append(t[2].time.text)
            self.altitude.append(t[4].text)
            self.gain.append(t[5].text)
            self.area.append(t[9].a.text)

            # keep only the first one for now
            if t[3].find('span', "printonly"):
                self.activity.append(t[3].find('span', "printonly").text)
            else:
                self.activity.append('')

            # add null string  to have the same numer of values in each list
            for c in cotations.keys():
                self.__dict__[c].append('')

            for i in t[6].findAll('span'):
                for c in cotations.keys():
                    if i['title'].startswith(cotations[c]):
                        self.__dict__[c][count] = i.text

            count += 1


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

