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

import urllib
from BeautifulSoup import BeautifulSoup

NB_ITEMS = 100

class C2CParser:
    "Compute statistics"
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


    def get_outings_url(self, page):
        return "http://www.camptocamp.org/outings/list/users/" + self.user_id + \
               "/orderby/date/order/desc/npp/" + str(NB_ITEMS) + \
               "/page/" + str(page)

    def parse_outings(self):
        pagenb = 1
        url = self.get_outings_url(pagenb)

        print "Parse outings list %s ..." % url
        page = get_page(url)
        soup = BeautifulSoup(page, convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.nboutings = int(soup.find('div', 'content_article').form.p.findAll('b')[2].text)

        self.parse_outings_list(page, pagenb)

        # parse other pages if nboutings > 100
        nbtemp = self.nboutings - 100
        while nbtemp > 0:
            pagenb += 1
            nbtemp -= 100
            url = self.get_outings_url(pagenb)
            print "Parse next page %s ..." % url
            page = get_page(url)
            self.parse_outings_list(page, pagenb)

        print "Found %d outings" % self.nboutings


    def parse_outings_list(self, page, pagenb):
        "Get the content of eah line of the table"

        soup = BeautifulSoup(page, convertEntities=BeautifulSoup.HTML_ENTITIES)
        table = soup.find('table', "list")
        lines = table.findAll('tr')
        lines = lines[1:]

        count = 0 + (pagenb-1)*100
        for l in lines:
            t = l.contents
            self.title.append(t[1].contents[0].text)
            self.date.append(t[2].contents[0].text)
            self.altitude.append(t[4].text)
            self.gain.append(t[5].text)

            # keep only the first one for now
            if t[3].find('span', "printonly"):
                self.activity.append(t[3].find('span', "printonly").text)
            else:
                self.activity.append('')

            for r in t[9].findAll('a'):
                self.area.append(r.text)

            # needed to have the same numer of values in each list
            self.cot_globale.append('')
            self.cot_libre.append('')
            self.cot_oblige.append('')
            self.cot_skitech.append('')
            self.cot_skiponc.append('')
            self.cot_glace.append('')
            self.cot_rando.append('')
            self.exposition.append('')
            self.engagement.append('')
            self.equipement.append('')

            for i in t[6].findAll('span'):
                if i['title'].startswith(u'Cotation globale'):
                    self.cot_globale[count] = i.text
                elif i['title'].startswith(u'Engagement'):
                    self.engagement[count] = i.text
                elif i['title'].startswith(u'Qualité de l\'équipement'):
                    self.equipement[count] = i.text
                elif i['title'].startswith(u'Cotation libre obligatoire'):
                    self.cot_oblige[count] = i.text
                elif i['title'].startswith(u'Cotation libre'):
                    self.cot_libre[count] = i.text
                elif i['title'].startswith(u'Cotation technique'):
                    self.cot_skitech[count] = i.text
                elif i['title'].startswith(u'Cotation ponctuelle ski'):
                    self.cot_skiponc[count] = i.text
                elif i['title'].startswith(u'Exposition'):
                    self.exposition[count] = i.text
                elif i['title'].startswith(u'Cotation glace'):
                    self.cot_glace[count] = i.text
                elif i['title'].startswith(u'Cotation randonnée'):
                    self.cot_rando[count] = i.text

            count += 1


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
