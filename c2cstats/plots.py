#!/usr/bin/env python2
# -*- coding:utf-8 -*-

"""module docstring"""

import datetime
import string
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

MONTHS = {u'janvier': 1, u'février': 2, u'mars': 3, u'avril': 4, u'mai': 5,
          u'juin': 6, u'juillet': 7, u'août': 8, u'septembre': 9,
          u'octobre': 10, u'novembre': 11, u'décembre': 12}

def plot_all(data):
    plot_date(data.date)
    plot_activity(data.activity)
    plot_area(data.area)

def plot_date(data):
    "Plot histogram of years"
    year = [int(string.split(i)[2]) for i in data]
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
    for i in data:
        t = i.split(' ')
        d.append(datetime.date(int(t[2]), MONTHS[t[1]], int(t[0])))

    plt.figure()
    plt.plot_date(d, np.ones(100))
    plt.savefig('timeline.svg')


def plot_activity(data):
    "Pie plot for activities"

    c = Counter(data)
    explode = np.zeros(len(c)) + 0.05

    plt.figure()
    plt.pie(c.values(), labels=c.keys(), explode=explode, shadow=True, autopct='%d')
    plt.title(u'Répartition par activité')
    plt.savefig('activities.svg')

def plot_area(data):
    "Pie plot for areas"

    c = Counter(data)
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
