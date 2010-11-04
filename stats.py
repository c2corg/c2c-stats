#!/usr/bin/env python2
# -*- coding:utf-8 -*-

# c2cstats - Compute statistics for camptocamp.org
# Copyright (C) 2009, 2010 - saimon.org
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
Compute statistics for the outing list
"""

__author__ = "Simon <contact at saimon dot org>"
__version__ = "0.1"
__date__ = ""
__copyright__ = "Copyright (c) 2009, 2010 Simon <contact at saimon dot org>"
__license__ = "GPL"

import re
import string
import urllib
import matplotlib.pyplot as plt

USERID = 6424
NBOUTINGS = 100

URL = "http://www.camptocamp.org/outings/list/user/" + str(USERID) + \
      "/orderby/date/order/desc/npp/" + str(NBOUTINGS)


class c2cstats:
    table = ""
    title = []
    date = []
    activity = []
    altitude = []
    gain = []
    area = []
    cotation = []

    def __init__(self, page):
        self.gettable(page)
        self.getcontent()

    def gettable(self, page):
        "Get the table from the page"
        try:
            start = string.index(page, "<table class=\"list\">")
            page = page[start:]
            end = string.index(page, "</table>")
            page = page[:end]
        except ValueError:
            print "Error: outing list not found."
            return 0

        page = "".join(string.split(page,'\n'))

        # pattern = re.compile(r'<thead>(.*)</thead>')
        # head = re.search(pattern, page).groups()[0]

        pattern = re.compile(r'<tbody>(.*)</tbody>')
        self.table = re.search(pattern, page).groups()[0]

    def getcontent(self):
        "Get the content of eah line of the table"
        lines = string.split(self.table, '</tr>')

        # pattern = re.compile(r"""
        # <td>.*</td>
        # <td><a href=".*">(.*)</a> </td>                 # title
        # <td>(.*)</td>                                   # date
        # <td><span class=".*" title="(.*)"></span></td>  # activity
        # <td>(.*)</td>                                   # altitude
        # <td>(.*)</td>                                   # gain
        # <td>(.*)</td>                                   # cotation
        # <td>.*</td>
        # <td>.*</td>
        # <td>(<a href=".*">(.*)</a>)*</td>               # regions
        # <td>.*</td>
        # <td>.*</td>
        # <td>.*</td>
        # """, re.VERBOSE)

        pattern = re.compile(r'<td>.*</td><td><a href=".*">(.*)</a> </td>'+
                             '<td>(.*)</td>'+
                             '<td><span class=".*" title="(.*)"></span></td>'+
                             '<td>(.*)</td><td>(.*)</td><td>(.*)</td>'+
                             '<td>.*</td><td>.*</td>'+
                             '<td>(<a href=".*">(.*)</a>)*</td>'+
                             '<td>.*</td><td>.*</td><td>.*</td>')

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

    def plotyear(self):
        year = [int(string.split(i)[2]) for i in self.date]
        h = plt.hist(year, max(year) - min(year))
        plt.xlabel('Year')
        plt.ylabel('Nb of outings')
        plt.title('Nb of outings per year')
        plt.axis([min(year), max(year), 0, max(h[0])+1])
        plt.show()

        rects1 = plt.bar([2004,2005,2006,2007,2008,2009], list(h[0]))


def getpage(url):
    usock = urllib.urlopen(url)
    page = usock.read()
    usock.close()
    return page

if __name__ == "__main__":
    page = getpage(URL)

    stats = c2cstats(page)
