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

class C2CPlots:
    "Make plots from data"
    def __init__(self, data):
        self.data = data
        self.act = np.array(self.data.activity)
        self.year = np.array([int(i.split()[2]) for i in self.data.date])

        if not os.path.isdir(OUTPUT_DIR):
            print "Creating output directory"
            os.mkdir(os.path.realpath(OUTPUT_DIR))

    def get_filepath(self, name):
        "return path for output file: _output/userid_plotname.ext"
        return os.path.join(OUTPUT_DIR, str(self.data.user_id)+'_'+name+FILE_EXT)

    def plot_all(self):
        self.plot_date()
        self.plot_activity()
        self.plot_area()

        self.plot_cot_globale()
        self.plot_cot_globale(u'alpinisme neige, glace, mixte')
        self.plot_cot_globale(u'cascade de glace')
        self.plot_cot_globale(u'escalade')
        self.plot_cot_globale(u'rocher haute montagne')
        self.plot_cot_globale(u'ski, surf')

        self.plot_gain()
        self.plot_gain(u'alpinisme neige, glace, mixte')
        self.plot_gain(u'cascade de glace')
        self.plot_gain(u'escalade')
        self.plot_gain(u'rocher haute montagne')
        self.plot_gain(u'ski, surf')


    def plot_date(self):
        "Plot histogram of years"
        x = np.unique(self.year)
        labels = [str(i) for i in np.unique(self.year)]

        # outings per year and per activity
        h = []
        for i in np.unique(self.act):
            ind = (self.act == i)
            h.append(list(self.year[ind]))

        plt.figure()

        # outings per year
        # plt.hist(year, len(x), histtype='bar', range=(x[0]-0.5, x[-1]+0.5), rwidth=0.6)
        # outings per year and per activity
        plt.hist(h, len(x), histtype='barstacked', range=(x[0]-0.5, x[-1]+0.5),
                 label=np.unique(self.act))

        plt.xlabel(u'Année')
        plt.ylabel('Nb de sorties')
        plt.title('Nb de sorties par an')
        plt.xticks(x, labels)
        plt.legend()
        plt.savefig(self.get_filepath('years'))

        # try with plot_date
        # d = []
        # for i in self.data.date:
        #     t = i.split(' ')
        #     d.append(datetime.date(int(t[2]), MONTHS[t[1]], int(t[0])))

        # plt.figure()
        # plt.plot_date(d, np.ones(100))
        # plt.savefig(self.get_filepath('timeline'))

    def plot_activity(self):
        "Pie plot for activities"

        c = Counter(self.data.activity)
        explode = np.zeros(len(c)) + 0.05

        plt.figure()
        plt.pie(c.values(), labels=c.keys(), explode=explode, shadow=True, autopct='%d')
        plt.title(u'Répartition par activité')
        plt.savefig(self.get_filepath('activities'))

    def plot_area(self):
        "Pie plot for areas"

        c = Counter(self.data.area)
        use = c.most_common(10)

        labels = [k for k,v in use]
        counts = [v for k,v in use]
        labels.append(u'Autres')
        counts.append(sum(c.values()) - sum(counts))

        explode = np.zeros(len(counts)) + 0.05

        plt.figure()
        plt.pie(counts, labels=labels, explode=explode, shadow=True, autopct='%d')
        plt.title(u'Répartition par région')
        plt.savefig(self.get_filepath('regions'))

    def plot_cot_globale(self, activity=''):
        "Hist plot for cot_globale"

        xlabel = u'Cotation globale'
        filename = 'cot_global'
        cot = np.array(self.data.cot_globale)

        if activity:
            ind = (self.act == activity)
            cot = cot[ind]
            if len(cot) == 0:
                return

            filename += '_'+activity
            xlabel += u' ' + activity

        c = Counter(cot)
        counts = [c[k] for k in COTATION_GLOBALE]
        x = np.arange(len(counts))

        plt.figure()
        plt.bar(x, counts)
        plt.xlabel(xlabel)
        plt.xticks(x + 0.4, COTATION_GLOBALE)
        plt.savefig(self.get_filepath(filename))

    def plot_cot_escalade(self):
        "Hist plot for cot_globale"

        width = 0.45
        x = np.arange(len(COTATION_ESCALADE))
        c1 = Counter(self.data.cot_libre)
        counts1 = [c1[k] for k in COTATION_ESCALADE]

        c2 = Counter(self.data.cot_oblige)
        counts2 = [c2[k] for k in COTATION_ESCALADE]

        plt.figure()
        p1 = plt.bar(x, counts1, width, color='r')
        p2 = plt.bar(x+width, counts2, width)
        plt.xlabel(u'Cotation escalade')
        plt.xticks(x + width, COTATION_ESCALADE)
        plt.legend( (p1[0], p2[0]), ('Cotation libre', u'Cotation obligé') )
        plt.savefig(self.get_filepath('cot_escalade'))

    def plot_gain(self, activity=''):
        "Hist plot for gain"

        xlabel = u'Dénivelé'
        filename = 'denivele'
        gain = np.array(self.data.gain)
        year = self.year
        x = np.unique(year)
        labels = [str(i) for i in np.unique(self.year)]

        if activity:
            ind = (self.act == activity)
            gain = gain[ind]
            year = year[ind]
            if len(gain) == 0:
                return

            filename += '_'+activity
            xlabel += u' ' + activity

        counts = []
        for i in x:
            ind = (year == i)
            select = np.array([int(k[:-1]) for k in gain[ind] if k])
            counts.append(np.sum(select))

        plt.figure()
        plt.bar(x, counts)
        plt.xlabel(xlabel)
        plt.xticks(x + 0.4, labels)
        plt.savefig(self.get_filepath(filename))
