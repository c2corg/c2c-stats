#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import datetime
import os.path
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

OUTPUT_DIR = "_output"
FILE_EXT = ".svg"

MONTHS = {u'janvier': 1, u'février': 2, u'mars': 3, u'avril': 4, u'mai': 5,
          u'juin': 6, u'juillet': 7, u'août': 8, u'septembre': 9,
          u'octobre': 10, u'novembre': 11, u'décembre': 12}


COTATION_GLOBALE = ('F', 'PD-', 'PD', 'PD+', 'AD-', 'AD', 'AD+', 'D-', 'D',
                    'D+', 'TD-', 'TD', 'TD+', 'ED-', 'ED', 'ED+')
# , 'ED4', 'ED5', 'ED6', 'ED7'

COTATION_ESCALADE = ('3a', '3b', '3c', '4a', '4b', '4c', '5a', '5a+', '5b',
                     '5b+', '5c', '5c+', '6a', '6a+', '6b', '6b+', '6c', '6c+',
                     '7a', '7a+', '7b', '7b+', '7c', '7c+', '8a')
# '2', '8a+', '8b', '8b+', '8c', '8c+', '9a', '9a+', '9b', '9b+'

def plot_all(data):
    plot_date(data)
    plot_activity(data.activity)
    plot_area(data.area)
    plot_cot_globale(data.cot_globale)

def get_filepath(name):
    return os.path.join(OUTPUT_DIR, name+FILE_EXT)

def plot_date(data):
    "Plot histogram of years"

    act = np.array(data.activity)
    year = np.array([int(i.split()[2]) for i in data.date])

    x = np.unique(year)
    labels = [str(i) for i in np.unique(year)]

    # outings per year and per activity
    h = []
    for i in np.unique(act):
        ind = (act == i)
        h.append(list(year[ind]))

    plt.figure()

    # outings per year
    # plt.hist(year, len(x), histtype='bar', range=(x[0]-0.5, x[-1]+0.5), rwidth=0.6)
    # outings per year and per activity
    plt.hist(h, len(x), histtype='barstacked', range=(x[0]-0.5, x[-1]+0.5),
             label=np.unique(act))

    plt.xlabel(u'Année')
    plt.ylabel('Nb de sorties')
    plt.title('Nb de sorties par an')
    plt.xticks(x, labels)
    plt.legend()
    plt.savefig(get_filepath('years'))

    # try with plot_date
    # d = []
    # for i in data.date:
    #     t = i.split(' ')
    #     d.append(datetime.date(int(t[2]), MONTHS[t[1]], int(t[0])))

    # plt.figure()
    # plt.plot_date(d, np.ones(100))
    # plt.savefig(get_filepath('timeline'))

def plot_activity(data):
    "Pie plot for activities"

    c = Counter(data)
    explode = np.zeros(len(c)) + 0.05

    plt.figure()
    plt.pie(c.values(), labels=c.keys(), explode=explode, shadow=True, autopct='%d')
    plt.title(u'Répartition par activité')
    plt.savefig(get_filepath('activities'))

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
    plt.savefig(get_filepath('regions'))

def plot_cot_globale(data):
    "Hist plot for cot_globale"

    c = Counter(data)
    counts = [c[k] for k in COTATION_GLOBALE]
    x = np.arange(len(counts))

    plt.figure()
    plt.bar(x, counts)
    plt.xlabel(u'Cotation globale')
    plt.xticks(x + 0.4, COTATION_GLOBALE)
    plt.savefig(get_filepath('cot_global'))

def plot_cot_escalade(cot_libre, cot_oblige):
    "Hist plot for cot_globale"

    width = 0.45
    x = np.arange(len(COTATION_ESCALADE))
    c1 = Counter(cot_libre)
    counts1 = [c1[k] for k in COTATION_ESCALADE]

    c2 = Counter(cot_oblige)
    counts2 = [c2[k] for k in COTATION_ESCALADE]

    plt.figure()
    p1 = plt.bar(x, counts1, width, color='r')
    p2 = plt.bar(x+width, counts2, width)
    plt.xlabel(u'Cotation escalade')
    plt.xticks(x + width, COTATION_ESCALADE)
    plt.legend( (p1[0], p2[0]), ('Cotation libre', u'Cotation obligé') )
    plt.savefig(get_filepath('cot_escalade'))

