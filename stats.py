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

"""
C2C user's stats
================

Compute some statistics for the outing list of a user.
"""

__author__ = "Simon <contact at saimon dot org>"
__version__ = "0.1"
__date__ = ""
__copyright__ = "Copyright (c) 2009, 2010 Simon <contact at saimon dot org>"
__license__ = "GPL"

import argparse
import datetime
import string
import sys
import urllib
import numpy as np
import matplotlib.pyplot as plt
from BeautifulSoup import BeautifulSoup
from collections import Counter

MONTHS = {u'janvier': 1, u'février': 2, u'mars': 3, u'avril': 4, u'mai': 5,
          u'juin': 6, u'juillet': 7, u'août': 8, u'septembre': 9,
          u'octobre': 10, u'novembre': 11, u'décembre': 12}

class C2CStats:
    "Compute statistics"
    def __init__(self, page):
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


    def plot_date(self):
        "Plot histogram of years"
        year = [int(string.split(i)[2]) for i in self.date]
        # n, bins, patches = plt.hist(year, max(year)-min(year)+1,
        #                             range = (min(year)-0.5, max(year)+0.5))

        n, bins = np.histogram(year, max(year) - min(year) + 1,
                               range=(min(year) - 0.5, max(year) + 0.5))

        plt.figure()
        plt.bar(bins[:-1], n)
        plt.xlabel(u'Année')
        plt.ylabel('Nb de sorties')
        plt.title('Nb de sorties par an')
        # plt.axis([min(year), max(year), 0, max(n)+1])

        labels = [str(i) for i in range(min(year), max(year) + 1)]
        plt.xticks(bins[:-1] + 0.4, labels)
        # plt.yticks(np.arange(0,81,10))
        # plt.legend( (p1[0], p2[0]), ('Men', 'Women')
        plt.savefig('years.svg')

        # try with plot_date
        d = []
        for i in self.date:
            t = i.split(' ')
            d.append(datetime.date(int(t[2]), MONTHS[t[1]], int(t[0])))

        plt.figure()
        plt.plot_date(d, np.ones(100))
        plt.savefig('timeline.svg')


    def plot_activity(self):
        "Pie plot for activities"

        c = Counter(self.activity)
        explode = np.zeros(len(c)) + 0.05

        plt.figure()
        plt.pie(c.values(), labels=c.keys(), explode=explode, shadow=True, autopct='%d')
        plt.title(u'Répartition par activité')
        plt.savefig('activities.svg')

    def plot_area(self):
        "Pie plot for areas"

        c = Counter(self.area)
        use = c.most_common(10)

        labels = [k for k,v in use]
        counts = [v for k,v in use]
        labels.append(u'Autres')
        counts.append(sum(c.values()) - sum(counts))

        explode = np.zeros(len(counts)) + 0.05

        plt.figure()
        plt.pie(counts, labels=labels, explode=explode, shadow=True, autopct='%d')
        plt.title(u'Répartition par région')
        plt.savefig('regions.svg')


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

def main():
    "main program"

    version = "version %s, %s" % (__version__, __date__)

    parser = argparse.ArgumentParser(description='Compute some statistics for camptocamp.org.')
    parser.add_argument('user_id', help='user id')
    parser.add_argument('--version', action='version',
                        version="%(prog)s " + version)
    parser.add_argument('-n', '--nboutings', default=100,
                        help=u"Nombre de sorties à récupérer")

    args = parser.parse_args()

    url = "http://www.camptocamp.org/outings/list/users/" + str(args.user_id) + \
          "/orderby/date/order/desc/npp/" + str(args.nboutings)

    print "Getting page %s ..." % url
    page = get_page(url)

    print "Analyzing data ..."
    stats = C2CStats(page)
    stats.plot_date()
    stats.plot_activity()
    stats.plot_area()
    plt.show()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
