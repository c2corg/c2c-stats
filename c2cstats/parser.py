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

class C2CParser:
    "Compute statistics"
    def __init__(self, url):
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

        print "Getting page %s ..." % url
        page = get_page(url)
        self.get_content(page)

    def get_content(self, page):
        "Get the content of eah line of the table"

        soup = BeautifulSoup(page, convertEntities=BeautifulSoup.HTML_ENTITIES)
        table = soup.find('table', "list")
        lines = table.findAll('tr')
        lines = lines[1:]

        for l in lines:
            t = l.contents
            self.title.append(t[1].contents[0].text)
            self.date.append(t[2].contents[0].text)
            self.altitude.append(t[4].text)
            self.gain.append(t[5].text)

            for a in t[3].findAll('span', "printonly"):
                self.activity.append(a.text)

            for r in t[9].findAll('a'):
                self.area.append(r.text)

            for i in t[6].findAll('span'):
                if i['title'].startswith(u'Cotation globale'):
                    self.cot_globale.append(i.text)
                elif i['title'].startswith(u'Engagement'):
                    self.engagement.append(i.text)
                elif i['title'].startswith(u'Qualité de l\'équipement'):
                    self.equipement.append(i.text)
                elif i['title'].startswith(u'Cotation libre obligatoire'):
                    self.cot_oblige.append(i.text)
                elif i['title'].startswith(u'Cotation libre&nbsp;'):
                    self.cot_libre.append(i.text)
                elif i['title'].startswith(u'Cotation technique'):
                    self.cot_skitech.append(i.text)
                elif i['title'].startswith(u'Cotation ponctuelle ski'):
                    self.cot_skiponc.append(i.text)
                elif i['title'].startswith(u'Exposition'):
                    self.exposition.append(i.text)
                elif i['title'].startswith(u'Cotation glace'):
                    self.cot_glace.append(i.text)
                elif i['title'].startswith(u'Cotation randonnée'):
                    self.cot_rando.append(i.text)


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
