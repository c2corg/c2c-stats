#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import os
import json
import numpy as np
from collections import Counter
from datetime import datetime
from c2cstats.parser import Outings, ParserError

ACT_SHORT = { u'alpinisme neige, glace, mixte': 'alpinisme',
              u'cascade de glace': 'glace',
              u'escalade': 'escalade',
              u'rocher haute montagne': 'rocher',
              u'ski, surf': 'ski',
              u'raquette': 'raquette',
              u'randonnée pédestre': 'rando'}


def generate_json(user_id, filename):
    """Generate a json file with all computed data.

    Arguments:
    - `filename`:
    - `user_id`:
    """
    data = Outings(user_id)

    act_long = dict([(v, k) for k,v in ACT_SHORT.items()])

    act_list = [ACT_SHORT[i] for i in data.activities]
    ctx = { 'activities': act_list,
            'nb_outings': data.nboutings }

    g = Global(data)
    ctx['global'] = { 'count_per_activity': g.count_per_activity,
                      'count_per_year_and_activity': g.count_per_year_and_activity,
                      'area': g.area }

    for act in act_list:
        d = globals()[act.title()](data)
        ctx[act] = { 'full_name': act_long[act],
                     'cotation': getattr(d, 'cotation', []) }

    d = datetime.now()
    ctx['date_generated'] = unicode(d.strftime('%d %B %Y à %X'), 'utf-8')
    ctx['generation_time'] = 0 # TODO

    with open(filename, 'w') as f:
        json.dump(ctx, f)


class Generator:
    def __init__(self, data):
        self.data = data

        self.year = np.array([int(i.split()[2]) for i in self.data.date])
        self.year_uniq = np.unique(self.year)
        self.year_labels = [str(i) for i in self.year_uniq]


    def filter_activity(self, arr, activity):
        arr_filtered = np.copy(arr)
        ind = (self.data.activity == activity)
        arr_filtered = arr_filtered[ind]
        return arr_filtered


    def cot_globale(self, activity=''):
        "Count number of outings per bin of cot_globale"

        if activity:
            c = Counter(filter_activity(self.data.cot_globale, activity))
        else:
            c = Counter(self.data.cot_globale)

        return [c[k] for k in COTATION_GLOBALE]


    def gain_per_year(self):

        if activity:
            gain = filter_activity(self.data.gain, activity)
            year = filter_activity(self.data.year, activity)
        else:
            gain = self.data.gain
            year = self.year

        counts = []
        for i in self.year_uniq:
            ind = (year == i)
            counts.append(np.sum(gain[ind]))

        return counts


class Global(Generator):
    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)

    @property
    def count_per_activity(self):
        "Count number of outings per activity"
        return Counter(self.data.activity)

    @property
    def count_per_year_and_activity(self):
        "Compute the number of outings per year and per activity"
        h = []
        for i in self.data.activities:
            ind = (self.data.activity == i)
            h.append(list(self.year[ind]))

        return h

    @property
    def area(self):
        "Count the number of outings per area"
        c = Counter(self.data.area)
        use = c.most_common(10)
        sum_use = sum(zip(*use)[1])
        use.append((u'Autres', sum(c.values()) - sum_use))
        print use

        return { 'title': u'Répartition par région',
                 'values': use }


class Escalade(Generator):

    COTATION_REF = ('3a', '3b', '3c', '4a', '4b', '4c', '5a', '5a+', '5b',
                '5b+', '5c', '5c+', '6a', '6a+', '6b', '6b+', '6c',
                '6c+', '7a', '7a+', '7b', '7b+', '7c', '7c+', '8a')
    # '2', '8a+', '8b', '8b+', '8c', '8c+', '9a', '9a+', '9b', '9b+'

    XLABEL = u'Cotation escalade'

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)

    @property
    def cotation(self):
        return self.cot_libre

    @property
    def cot_libre(self):
        c1 = Counter(self.data.cot_libre)
        return [c1[k] for k in self.COTATION_REF]

    @property
    def cot_oblige(self):
        c2 = Counter(self.data.cot_oblige)
        return [c2[k] for k in self.COTATION_REF]


class Glace(Generator):

    COTATION_REF = ('2', '3', '3+', '4', '4+', '5', '5+', '6', '6+', '7', '7+')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)

    @property
    def cotation(self):
        c = Counter(self.data.cot_glace)
        return {
            'title': u'Cotation glace',
            'labels': self.COTATION_REF,
            'values': [c[k] for k in self.COTATION_REF]
            }


class Rando(Generator):

    COTATION_REF = ('T1', 'T2', 'T3', 'T4', 'T5', 'T6')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)

    @property
    def cotation(self):
        c = Counter(self.data.cot_rando)
        return {
            'title': u'Cotation rando',
            'labels': self.COTATION_REF,
            'values': [c[k] for k in self.COTATION_REF]
            }


class Alpinisme(Generator):
    pass

class Raquette(Generator):
    pass

class Rocher(Generator):
    pass

class Ski(Generator):
    pass


