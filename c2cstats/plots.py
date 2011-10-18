#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import datetime
import os
import os.path
import itertools
import numpy as np
import matplotlib
matplotlib.use('AGG')
matplotlib.rc('legend', fancybox=True)
matplotlib.rc('figure', figsize=(6, 4.5))
matplotlib.rc('font', **{'family':'sans-serif', 'size': 10.0,
                         'sans-serif': 'Droid Sans'})

import matplotlib.pyplot as plt
from collections import Counter
from functools import wraps

# minimal number of outings needed to make a plot of one activity
ACT_MIN = 5

ACTIVITIES = (u'alpinisme neige, glace, mixte',
              u'cascade de glace',
              u'escalade',
              u'rocher haute montagne',
              u'ski, surf',
              u'raquette',
              u'randonnée pédestre')

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

# colors_list = ['#7C8BD9', '#DE2D26', '#2CA25F', '#7C1BD9', '#DE2096',
#                '#2C565F', '#99A25F' ]

colors_list = ['#D73027', '#FC8D59', '#FEE090', '#FFFFBF', '#E0F3F8',
               '#91BFDB', '#4575B4']

colors_iter = itertools.cycle(colors_list)


def barplot(x, values, xlabel, xticklabels, filename, xticks_offset=0.4,
            color=colors_list[1], remove_axes=True, rotate_xticks=False):
    "Make a bar plot"
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.bar(x, values, color=color)
    ax.set_xlabel(xlabel)
    ax.set_xticks(x + xticks_offset)
    ax.set_xticklabels(xticklabels)

    if remove_axes:
        # Remove the surrounding lines from the plot
        for loc, spine in ax.spines.iteritems():
            if loc in ['right', 'top']:
                spine.set_color('none')

        # Display ticks only at the bottom and left
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('left')

        # Switch the position of the ticks to be outside the axes
        ax.tick_params(axis='y', direction='out')

    if rotate_xticks:
        ax.autofmt_xdate(rotation=45)

    plt.savefig(filename, transparent=True)


def remove_axes(func):
    "Remove right and top axes and save fig"
    @wraps(func)
    def wrapper(self, filename, **kwargs):
        func(self, filename, **kwargs)

        ax = plt.gca()
        # Remove the surrounding lines from the plot
        for loc, spine in ax.spines.iteritems():
            if loc in ['right', 'top']:
                spine.set_color('none')

        # Display ticks only at the bottom and left
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('left')

        # Switch the position of the ticks to be outside the axes
        ax.tick_params(axis='y', direction='out')
        plt.savefig(self.get_filepath(filename), transparent=True)
    return wrapper


class Plots:
    "Make plots from data"
    def __init__(self, data, output_dir):
        self.data = data

        self.barcolor = colors_list[1]

        self.act_count = Counter(self.data.activity)
        self.acts = np.unique(self.data.activity)
        ind = (self.acts != u'')
        self.acts = self.acts[ind]

        self.year = np.array([int(i.split()[2]) for i in data.date])
        self.year_uniq = np.unique(self.year)
        self.year_labels = [str(i) for i in self.year_uniq]

        self.out_dir = os.path.join(output_dir, str(data.user_id))
        if not os.path.isdir(self.out_dir):
            os.makedirs(self.out_dir)


    def get_filepath(self, name):
        "return path for output file: _output/userid/name.ext"
        return os.path.join(self.out_dir, name)


    def plot_all(self):
        self.plot_activity()
        self.plot_area()
        self.plot_date('years')

        self.plot_cot_globale('cot_globale')
        self.plot_cot_globale_per_activity('cot_globale_per_activity')

        if (self.act_count[u'escalade'] +
            self.act_count[u'rocher haute montagne']) > ACT_MIN:
            self.plot_cot_escalade('cot_escalade')

        if self.act_count[u'cascade de glace'] > ACT_MIN:
            self.plot_cot_glace('cot_glace')

        if self.act_count[u'randonn\xe9e p\xe9destre'] > ACT_MIN:
            self.plot_cot_rando('cot_rando')

        for act in ACTIVITIES:
            if self.act_count[act] > ACT_MIN:
                fileext = '_' + act.replace(' ', '_').replace(',', '')
                fileext = fileext.replace(u'randonnée_pédestre', 'rando')
                self.plot_gain('denivele' + fileext, activity=act)
                self.plot_gain_cumul('denivele_cumul' + fileext, activity=act)

        print "Results available in %s" % self.out_dir

    @remove_axes
    def plot_date(self, filename):
        "Plot histogram of years"
        # outings per year and per activity
        h = []
        for i in np.unique(self.data.activity):
            ind = (self.data.activity == i)
            h.append(list(self.year[ind]))

        nbact = len(np.unique(self.data.activity))

        # outings per year
        # plt.hist(year, len(self.year_uniq), histtype='bar',
        #          range=(self.year_uniq[0]-0.5, self.year_uniq[-1]+0.5), rwidth=0.6)

        # outings per year and per activity
        fig = plt.figure()
        ax = plt.axes([0.1, 0.3, 0.9, 0.7])
        ax.hist(h, len(self.year_uniq), histtype='barstacked',
                range=(self.year_uniq[0]-0.5, self.year_uniq[-1]+0.5),
                label=np.unique(self.data.activity), color=colors_list[0:nbact])

        ax.set_ylabel('Nb de sorties par an')
        ax.set_xticks(self.year_uniq)
        ax.set_xticklabels(self.year_labels)

        # Put a legend below current axis
        leg = ax.legend(loc='upper center', bbox_to_anchor=(0.45, -0.07),
                        frameon=False, ncol=2, mode="expand")

        # rotate and align the tick labels so they look better
        fig = plt.gcf()
        fig.autofmt_xdate(rotation=45)

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

        explode = np.zeros(len(self.act_count)) + 0.05
        plt.figure()
        plt.pie(self.act_count.values(), labels=self.act_count.keys(),
                explode=explode, shadow=True, autopct='%d', colors=colors_list)
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
        plt.pie(counts, labels=labels, explode=explode, shadow=True,
                autopct='%d', colors=colors_list)
        plt.title(u'Répartition par région')
        plt.savefig(self.get_filepath('regions'), transparent=True)


    def plot_cot_globale(self, filename, activity=''):
        "Hist plot for cot_globale"

        xlabel = u'Cotation globale'
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

        barplot(x, counts, xlabel, COTATION_GLOBALE, self.get_filepath(filename))


    @remove_axes
    def plot_cot_globale_per_activity(self, filename):
        "Hist plot for cot_globale"

        fig = plt.figure()
        ax = plt.axes([0.1, 0.3, 0.9, 0.7])

        x = np.arange(len(COTATION_GLOBALE))
        width = 1./len(self.acts)

        for i in np.arange(len(self.acts)):
            ind = (self.data.activity == self.acts[i])
            c = Counter(self.data.cot_globale[ind])
            counts = [c[k] for k in COTATION_GLOBALE]
            ax.bar(x + i*width, counts, width, label=self.acts[i],
                   color=colors_iter.next())

        ax.set_ylabel(u'Cotation globale')
        ax.set_xticks(x + 0.4)
        ax.set_xticklabels(COTATION_GLOBALE)

        # Put a legend below current axis
        leg = ax.legend(loc='upper center', bbox_to_anchor=(0.45, -0.07),
                        frameon=False, ncol=2, mode="expand")
        leg.get_frame().set_alpha(0.5)

    @remove_axes
    def plot_cot_escalade(self, filename):
        "Hist plot for cot_globale"

        fig = plt.figure()
        ax = fig.add_subplot(111)

        width = 0.45
        x = np.arange(len(COTATION_ESCALADE))
        c1 = Counter(self.data.cot_libre)
        counts1 = [c1[k] for k in COTATION_ESCALADE]

        c2 = Counter(self.data.cot_oblige)
        counts2 = [c2[k] for k in COTATION_ESCALADE]

        ax.bar(x, counts1, width, label=u'Cotation libre', color=self.barcolor)
        ax.bar(x+width, counts2, width, label=u'Cotation obligé', color=colors_list[-1])
        ax.set_xlabel(u'Cotation escalade')
        ax.set_xticks(x + width)
        ax.set_xticklabels(COTATION_ESCALADE)

        leg = plt.legend(loc='best')
        leg.get_frame().set_alpha(0.5)

        fig = plt.gcf()
        fig.autofmt_xdate(rotation=45)


    def plot_cot_glace(self, filename):
        "Hist plot for cot_glace"

        x = np.arange(len(COTATION_GLACE))
        c = Counter(self.data.cot_glace)
        counts = [c[k] for k in COTATION_GLACE]
        barplot(x, counts, u'Cotation glace', COTATION_GLACE, self.get_filepath(filename))


    def plot_cot_rando(self, filename):
        "Hist plot for cot_rando"

        x = np.arange(len(COTATION_RANDO))
        c = Counter(self.data.cot_rando)
        counts = [c[k] for k in COTATION_RANDO]
        barplot(x, counts, u'Cotation rando', COTATION_RANDO, self.get_filepath(filename))


    def plot_gain(self, filename, activity=''):
        "Hist plot for gain"

        xlabel = u'Dénivelé'
        gain = np.copy(self.data.gain)
        year = np.copy(self.year)

        if activity:
            xlabel += u' ' + activity
            ind = (self.data.activity == activity)
            gain = gain[ind]
            year = year[ind]
            if len(gain) == 0:
                return

        counts = []
        for i in self.year_uniq:
            ind = (year == i)
            counts.append(np.sum(gain[ind]))

        barplot(self.year_uniq, counts, xlabel, self.year_labels,
                self.get_filepath(filename))


    @remove_axes
    def plot_gain_cumul(self, filename, activity=''):
        "Cumulative plot per year for gain"

        fig = plt.figure()
        ax = fig.add_subplot(111)

        xlabel = u'Dénivelé'
        gain = np.copy(self.data.gain)
        date = np.copy(self.data.date)

        months_idx = np.arange(12)

        if activity:
            xlabel += u' ' + activity
            ind = (self.data.activity == activity)
            gain = gain[ind]
            date = date[ind]
            if len(gain) == 0:
                return

        month = np.array([i.split()[1] for i in date])
        year = np.array([int(i.split()[2]) for i in date])

        for y in self.year_uniq:
            ind = (year == y)
            counts = np.zeros(12)

            for m in months_idx:
                sel = (month[ind] == MONTHS[m])
                counts[m] = np.sum(gain[ind][sel])

            ax.plot(months_idx+1, counts.cumsum(), 'o-', label=str(y),
                    color=colors_iter.next(), linewidth=2)

        ax.set_xlabel(xlabel)
        ax.set_xticks(months_idx + 1.4)
        ax.set_xticklabels(MONTHS)

        fig = plt.gcf()
        fig.autofmt_xdate(rotation=45)

        leg = plt.legend(loc='best')
        leg.get_frame().set_alpha(0.5)
