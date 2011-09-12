#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import datetime
import os
import os.path
import numpy as np
import matplotlib
matplotlib.use('SVG')
matplotlib.rc('legend', fancybox=True)
matplotlib.rc('figure', figsize=(7, 5))

import matplotlib.pyplot as plt
from collections import Counter

MONTHS = (u'janvier', u'février', u'mars', u'avril', u'mai', u'juin', u'juillet',
          u'août', u'septembre', u'octobre', u'novembre', u'décembre')

COTATION_GLOBALE = ('F', 'PD-', 'PD', 'PD+', 'AD-', 'AD', 'AD+', 'D-', 'D',
                    'D+', 'TD-', 'TD', 'TD+', 'ED-', 'ED', 'ED+')
# , 'ED4', 'ED5', 'ED6', 'ED7'

COTATION_ESCALADE = ('3a', '3b', '3c', '4a', '4b', '4c', '5a', '5a+', '5b',
                     '5b+', '5c', '5c+', '6a', '6a+', '6b', '6b+', '6c', '6c+',
                     '7a', '7a+', '7b', '7b+', '7c', '7c+', '8a')
# '2', '8a+', '8b', '8b+', '8c', '8c+', '9a', '9a+', '9b', '9b+'

COTATION_GLACE = ('2', '3', '3+', '4', '4+', '5', '5+', '6', '6+', '7', '7+')
COTATION_RANDO = ('T1', 'T2', 'T3', 'T4', 'T5', 'T6')

class Plots:
    "Make plots from data"
    def __init__(self, data, settings):
        self.data = data
        self.settings = settings

        self.acts = np.unique(self.data.activity)
        ind = (self.acts != u'')
        self.acts = self.acts[ind]

        self.year = np.array([int(i.split()[2]) for i in data.date])
        self.year_uniq = np.unique(self.year)
        self.year_labels = [str(i) for i in self.year_uniq]

        if not os.path.isdir(self.settings['OUTPUT_DIR']):
            os.makedirs(self.settings['OUTPUT_DIR'])

    def get_filepath(self, name):
        "return path for output file: _output/userid/name.ext"
        return os.path.join(self.settings['OUTPUT_DIR'], name)

    def plot_all(self):
        self.plot_activity()
        self.plot_area()
        self.plot_date()

        self.plot_cot_globale()
        self.plot_cot_globale_per_activity()

        if u'escalade' in self.acts or u'rocher haute montagne' in self.acts:
            self.plot_cot_escalade()

        if u'cascade de glace' in self.acts:
            self.plot_cot_glace()

        if u'randonn\xe9e p\xe9destre' in self.acts:
            self.plot_cot_rando()

        for act in self.settings['ACTIVITIES']:
            if act in self.acts:
                self.plot_gain(act)
                self.plot_gain_cumul(act)

        print "Results available in %s" % self.settings['OUTPUT_DIR']

    def plot_date(self):
        "Plot histogram of years"
        # outings per year and per activity
        h = []
        for i in np.unique(self.data.activity):
            ind = (self.data.activity == i)
            h.append(list(self.year[ind]))

        fig = plt.figure()

        # outings per year
        # plt.hist(year, len(self.year_uniq), histtype='bar',
        #          range=(self.year_uniq[0]-0.5, self.year_uniq[-1]+0.5), rwidth=0.6)
        # outings per year and per activity
        plt.hist(h, len(self.year_uniq), histtype='barstacked',
                 range=(self.year_uniq[0]-0.5, self.year_uniq[-1]+0.5),
                 label=np.unique(self.data.activity))

        plt.xlabel(u'Année')
        plt.ylabel('Nb de sorties')
        plt.title('Nb de sorties par an')
        plt.xticks(self.year_uniq, self.year_labels)
        leg = plt.legend(loc='best')
        leg.get_frame().set_alpha(0.5)

        # rotate and align the tick labels so they look better
        fig.autofmt_xdate(rotation=45)

        plt.savefig(self.get_filepath('years'), transparent=True)

        # try with plot_date
        # d = []
        # for i in self.data.date:
        #     t = i.split(' ')
        #     d.append(datetime.date(int(t[2]), MONTHS[t[1]], int(t[0])))

        # plt.figure()
        # plt.plot_date(d, np.ones(100))
        # plt.savefig(self.get_filepath('timeline'), transparent=True)

    def plot_activity(self):
        "Pie plot for activities"

        c = Counter(self.data.activity)
        explode = np.zeros(len(c)) + 0.05

        plt.figure()
        plt.pie(c.values(), labels=c.keys(), explode=explode, shadow=True, autopct='%d')
        plt.title(u'Répartition par activité')
        plt.savefig(self.get_filepath('activities'), transparent=True)

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
        plt.savefig(self.get_filepath('regions'), transparent=True)

    def plot_cot_globale(self, activity=''):
        "Hist plot for cot_globale"

        xlabel = u'Cotation globale'
        filename = 'cot_globale'
        cot = np.copy(self.data.cot_globale)

        if activity:
            ind = (self.data.activity == activity)
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
        plt.savefig(self.get_filepath(filename), transparent=True)


    def plot_cot_globale_per_activity(self):
        "Hist plot for cot_globale"
        x = np.arange(len(COTATION_GLOBALE))
        width = 1./len(self.acts)
        colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')

        plt.figure()
        for i in np.arange(len(self.acts)):
            ind = (self.data.activity == self.acts[i])
            c = Counter(self.data.cot_globale[ind])
            counts = [c[k] for k in COTATION_GLOBALE]
            plt.bar(x + i*width, counts, width, label=self.acts[i],
                    color=colors[i])

        plt.xlabel(u'Cotation globale')
        plt.xticks(x + 0.4, COTATION_GLOBALE)
        leg = plt.legend(loc='best')
        leg.get_frame().set_alpha(0.5)
        plt.savefig(self.get_filepath('cot_globale_per_activity'), transparent=True)

    def plot_cot_escalade(self):
        "Hist plot for cot_globale"

        width = 0.45
        x = np.arange(len(COTATION_ESCALADE))
        c1 = Counter(self.data.cot_libre)
        counts1 = [c1[k] for k in COTATION_ESCALADE]

        c2 = Counter(self.data.cot_oblige)
        counts2 = [c2[k] for k in COTATION_ESCALADE]

        fig = plt.figure()
        plt.bar(x, counts1, width, color='r', label=u'Cotation libre')
        plt.bar(x+width, counts2, width, color='b', label=u'Cotation obligé')
        plt.xlabel(u'Cotation escalade')
        plt.xticks(x + width, COTATION_ESCALADE)
        leg = plt.legend(loc='best')
        leg.get_frame().set_alpha(0.5)
        fig.autofmt_xdate(rotation=45)
        plt.savefig(self.get_filepath('cot_escalade'), transparent=True)

    def plot_cot_glace(self):
        "Hist plot for cot_glace"

        x = np.arange(len(COTATION_GLACE))
        c = Counter(self.data.cot_glace)
        counts = [c[k] for k in COTATION_GLACE]

        fig = plt.figure()
        plt.bar(x, counts)
        plt.xlabel(u'Cotation glace')
        plt.xticks(x + 0.4, COTATION_GLACE)
        plt.savefig(self.get_filepath('cot_glace'), transparent=True)

    def plot_cot_rando(self):
        "Hist plot for cot_rando"

        x = np.arange(len(COTATION_RANDO))
        c = Counter(self.data.cot_rando)
        counts = [c[k] for k in COTATION_RANDO]

        fig = plt.figure()
        plt.bar(x, counts)
        plt.xlabel(u'Cotation rando')
        plt.xticks(x + 0.4, COTATION_RANDO)
        plt.savefig(self.get_filepath('cot_rando'), transparent=True)

    def plot_gain(self, activity=''):
        "Hist plot for gain"

        xlabel = u'Dénivelé'
        filename = 'denivele'
        gain = np.copy(self.data.gain)
        year = np.copy(self.year)

        if activity:
            ind = (self.data.activity == activity)
            gain = gain[ind]
            year = year[ind]
            if len(gain) == 0:
                return

            filename += '_' + activity.replace(' ', '_').replace(',', '')
            xlabel += u' ' + activity

        counts = []
        for i in self.year_uniq:
            ind = (year == i)
            counts.append(np.sum(gain[ind]))

        fig = plt.figure()
        plt.bar(self.year_uniq, counts)
        plt.xlabel(xlabel)
        plt.xticks(self.year_uniq + 0.4, self.year_labels)
        fig.autofmt_xdate(rotation=45)
        plt.savefig(self.get_filepath(filename), transparent=True)

    def plot_gain_cumul(self, activity=''):
        "Cumulative plot per year for gain"

        xlabel = u'Dénivelé'
        filename = 'denivele_cumul'
        gain = np.copy(self.data.gain)
        date = np.copy(self.data.date)

        months_idx = np.arange(12)

        if activity:
            ind = (self.data.activity == activity)
            gain = gain[ind]
            date = date[ind]
            if len(gain) == 0:
                return

            filename += '_' + activity.replace(' ', '_').replace(',', '')
            xlabel += u' ' + activity

        month = np.array([i.split()[1] for i in date])
        year = np.array([int(i.split()[2]) for i in date])

        fig = plt.figure()
        for y in self.year_uniq:
            ind = (year == y)
            counts = np.zeros(12)

            for m in months_idx:
                sel = (month[ind] == MONTHS[m])
                counts[m] = np.sum(gain[ind][sel])

            plt.plot(months_idx+1, counts.cumsum(), label=str(y))

        plt.xlabel(xlabel)
        plt.xticks(months_idx + 1.4, MONTHS)
        fig.autofmt_xdate(rotation=45)
        leg = plt.legend(loc='best')
        leg.get_frame().set_alpha(0.5)
        plt.savefig(self.get_filepath(filename), transparent=True)
