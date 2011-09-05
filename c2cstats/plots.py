#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import datetime
import os
import os.path
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

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
    def __init__(self, data, settings):
        self.data = data
        self.settings = settings

        self.activity = np.array(data.activity)
        self.acts = np.unique(self.activity)
        ind = (self.acts != u'')
        self.acts = self.acts[ind]

        self.cot_globale = np.array(data.cot_globale)
        self.gain = np.array(data.gain)
        self.year = np.array([int(i.split()[2]) for i in data.date])
        self.year_uniq = np.unique(self.year)
        self.year_labels = [str(i) for i in self.year_uniq]

        if not os.path.isdir(self.settings['OUTPUT_DIR']):
            print "Creating output directory ..."
            os.makedirs(self.settings['OUTPUT_DIR'])

    def get_filepath(self, name):
        "return path for output file: _output/userid/name.ext"
        return os.path.join(self.settings['OUTPUT_DIR'],
                            name+self.settings['OUTPUT_EXT'])

    def plot_all(self):
        self.plot_activity()
        self.plot_area()
        self.plot_date()

        self.plot_cot_escalade()
        self.plot_cot_globale()
        self.plot_cot_globale_per_activity()
        # for act in self.settings['ACTIVITIES']:
        #     self.plot_cot_globale(act)

        self.plot_gain()
        for act in self.settings['ACTIVITIES']:
            self.plot_gain(act)

    def plot_date(self):
        "Plot histogram of years"
        # outings per year and per activity
        h = []
        for i in np.unique(self.activity):
            ind = (self.activity == i)
            h.append(list(self.year[ind]))

        plt.figure()

        # outings per year
        # plt.hist(year, len(self.year_uniq), histtype='bar',
        #          range=(self.year_uniq[0]-0.5, self.year_uniq[-1]+0.5), rwidth=0.6)
        # outings per year and per activity
        plt.hist(h, len(self.year_uniq), histtype='barstacked',
                 range=(self.year_uniq[0]-0.5, self.year_uniq[-1]+0.5),
                 label=np.unique(self.activity))

        plt.xlabel(u'Année')
        plt.ylabel('Nb de sorties')
        plt.title('Nb de sorties par an')
        plt.xticks(self.year_uniq, self.year_labels)
        plt.legend(loc='upper left')
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

        c = Counter(self.activity)
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
        filename = 'cot_globale'
        cot = self.cot_globale

        if activity:
            ind = (self.activity == activity)
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


    def plot_cot_globale_per_activity(self):
        "Hist plot for cot_globale"
        x = np.arange(len(COTATION_GLOBALE))
        width = 1./len(self.acts)
        colors = ('b', 'g', 'r', 'c', 'm', 'y')

        plt.figure()
        for i in np.arange(len(self.acts)):
            ind = (self.activity == self.acts[i])
            c = Counter(self.cot_globale[ind])
            counts = [c[k] for k in COTATION_GLOBALE]
            plt.bar(x + i*width, counts, width, label=self.acts[i],
                    color=colors[i])

        plt.xlabel(u'Cotation globale')
        plt.xticks(x + 0.4, COTATION_GLOBALE)
        plt.legend(loc='upper left')
        plt.savefig(self.get_filepath('cot_globale_per_activity'))

    def plot_cot_escalade(self):
        "Hist plot for cot_globale"

        width = 0.45
        x = np.arange(len(COTATION_ESCALADE))
        c1 = Counter(self.data.cot_libre)
        counts1 = [c1[k] for k in COTATION_ESCALADE]

        c2 = Counter(self.data.cot_oblige)
        counts2 = [c2[k] for k in COTATION_ESCALADE]

        plt.figure()
        plt.bar(x, counts1, width, color='r', label=u'Cotation libre')
        plt.bar(x+width, counts2, width, color='b', label=u'Cotation obligé')
        plt.xlabel(u'Cotation escalade')
        plt.xticks(x + width, COTATION_ESCALADE)
        plt.legend(loc='upper left')
        plt.savefig(self.get_filepath('cot_escalade'))

    def plot_gain(self, activity=''):
        "Hist plot for gain"

        xlabel = u'Dénivelé'
        filename = 'denivele'
        gain = self.gain
        year = self.year

        if activity:
            ind = (self.activity == activity)
            gain = gain[ind]
            year = year[ind]
            if len(gain) == 0:
                return

            filename += '_'+activity
            xlabel += u' ' + activity

        counts = []
        for i in self.year_uniq:
            ind = (year == i)
            select = np.array([int(k[:-1]) for k in gain[ind] if k])
            counts.append(np.sum(select))

        plt.figure()
        plt.bar(self.year_uniq, counts)
        plt.xlabel(xlabel)
        plt.xticks(self.year_uniq + 0.4, self.year_labels)
        plt.savefig(self.get_filepath(filename))
