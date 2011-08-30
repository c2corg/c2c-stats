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

import re
import string
import urllib
import numpy as np
import matplotlib.pyplot as plt

ACT = ('escalade', 'rocher haute montagne', 'alpinisme neige, glace, mixte',
       'cascade de glace', 'ski, surf, raquette', 'randonée pédestre')


class C2CStats:
    "Compute statistics"
    def __init__(self, page):
        self.title = []
        self.date = []
        self.activity = []
        self.altitude = []
        self.gain = []
        self.area = []
        self.cotation = []
        self.get_content(self.get_table(page))

    def get_table(self, page):
        "Get the table from the page"
        try:
            start = string.index(page, "<table class=\"list\">")
            page = page[start:]
            end = string.index(page, "</table>")
            page = page[:end]
        except ValueError:
            print "Error: outing list not found."
            return 0

        page = "".join(string.split(page, '\n'))

        # pattern = re.compile(r'<thead>(.*)</thead>')
        # head = re.search(pattern, page).groups()[0]

        pattern = re.compile(r'<tbody>(.*)</tbody>')
        return re.search(pattern, page).groups()[0]

    def get_content(self, table):
        "Get the content of eah line of the table"
        lines = string.split(table, '</tr>')

        # pattern = re.compile(r"""
        # <td>.*</td>                                     # checkbox
        # <td><a href=".*">(.*)</a> </td>                 # link, title
        # <td>(.*)</td>                                   # date
        # <td><span class=".*" title="(.*)"></span>
        # <span class="printonly">.*</span></td>          # activity
        # <td>(.*)</td>                                   # altitude
        # <td>(.*)</td>                                   # gain
        # <td>(.*)</td>                                   # cotation
        # <td>.*</td>                                     # conditions
        # <td><span .*></span>
        # <span class="printonly">.*</span></td>          # frequentation
        # <td>(<a href=".*">(.*)</a>)*</td>               # regions
        # <td>.*</td>                                     # nb images
        # <td>.*</td>                                     # nb comments
        # <td>.*</td>                                     # user
        # """, re.VERBOSE)

        pattern = re.compile(r'<td>.*</td><td><a href=".*">(.*)</a> </td>' +
                             '<td>(.*)</td>' +
                             '<td><span class=".*" title="(.*)"></span>' +
                             '<span class="printonly">.*</span></td>' +
                             '<td>(.*)</td><td>(.*)</td><td>(.*)</td>' +
                             '<td>.*</td><td>.*</td>' +
                             '<td>(<a href=".*">(.*)</a>)*</td>' +
                             '<td>.*</td><td>.*</td><td>.*</td>')

        # # cotation detail :
        # <td>
        # <span title="Cotation globale&nbsp;: D">D</span>/
        # <span title="Engagement&nbsp;: I">I</span>/
        # <span title="Qualit\xc3\xa9 de l\'\xc3\xa9quipement en place&nbsp;:
        # P1 (bien \xc3\xa9quip\xc3\xa9)">P1</span>
        # <span title="Cotation libre&nbsp;: 5c">5c</span>
        # (<span title="Cotation libre obligatoire&nbsp;: 5b">5b</span>)
        # </td>
        # # regions
        # <td><a href="/areas/14403/fr/ecrins">&Eacute;crins</a>
        # <a href="/areas/14361/fr/hautes-alpes">Hautes-Alpes</a></td>

        for l in lines:
            if not re.search(pattern, l):
                continue

            data = re.search(pattern, l).groups()
            self.title.append(data[0])
            self.date.append(data[1])
            self.activity.append(data[2])
            self.altitude.append(data[3])
            self.gain.append(data[4])
            self.cotation.append(data[5])
            self.area.append(data[6])

    def plot_year(self):
        "Plot histogram of years"
        year = [int(string.split(i)[2]) for i in self.date]
        # n, bins, patches = plt.hist(year, max(year)-min(year)+1,
        #                             range = (min(year)-0.5, max(year)+0.5))

        n, bins = np.histogram(year, max(year) - min(year) + 1,
                               range=(min(year) - 0.5, max(year) + 0.5))

        plt.figure()
        plt.bar(bins[:-1], n)
        plt.xlabel('Year')
        plt.ylabel('Nb of outings')
        plt.title('Nb of outings per year')
        # plt.axis([min(year), max(year), 0, max(n)+1])

        labels = [str(i) for i in range(min(year), max(year) + 1)]
        plt.xticks(bins[:-1] + 0.4, labels)
        # plt.yticks(np.arange(0,81,10))
        # plt.legend( (p1[0], p2[0]), ('Men', 'Women')
        plt.savefig('years.svg')

    def plot_act(self):
        "Plot activities"
        ind = [ACT.index(i) for i in self.activity]

        n, bins = np.histogram(ind, len(ACT), range=(-0.5, max(ind) + 0.5))
        fracs = n / float(n.sum())

        explode = np.zeros(len(ACT)) + 0.05

        plt.figure()
        plt.pie(fracs, explode=explode, labels=ACT, autopct='%1.1f%%',
                shadow=True)
        plt.title('Repartition between activities',
                  bbox={'facecolor': '0.8', 'pad': 5})
        plt.savefig('activities.svg')


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

if __name__ == "__main__":
    userid = 7286
    nboutings = 150

    url = "http://www.camptocamp.org/outings/list/user/" + str(userid) + \
          "/orderby/date/order/desc/npp/" + str(nboutings)

    print "Getting page %s ..." % url
    p = get_page(url)

    print "Analyzing data ..."
    stats = C2CStats(p)
    stats.plot_year()
    stats.plot_act()
    plt.show()
