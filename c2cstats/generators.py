#!/usr/bin/env python2
# -*- coding:utf-8 -*-

import json
import time
import numpy as np
from collections import Counter
from datetime import datetime
from c2cstats.parser import Outings

ACT_SHORT = {u'alpinisme neige, glace, mixte': 'alpinisme',
             u'escalade': 'escalade',
             u'cascade de glace': 'glace',
             u'randonnée pédestre': 'rando',
             u'raquette': 'raquette',
             u'rocher haute montagne': 'rocher',
             u'ski, surf': 'ski'}

COTATION_GLOBALE = ('F', 'PD-', 'PD', 'PD+', 'AD-', 'AD', 'AD+', 'D-', 'D',
                    'D+', 'TD-', 'TD', 'TD+', 'ED-', 'ED', 'ED+')


def generate_json(user_id, filename):
    "Generate a json file with all computed data."

    t0 = time.time()
    data = Outings(user_id)
    t1 = time.time()

    ctx = {'activities': [ACT_SHORT[i] for i in data.activities],
           'nb_outings': data.nboutings,
           'url': "http://www.camptocamp.org/outings/list/users/%s" % user_id,
           'user_url': "http://www.camptocamp.org/users/%s" % user_id
           }

    # global attributes
    g = Global(data)
    ctx['global'] = {}
    for attr in ['activities', 'activities_per_year', 'area', 'cotation']:
        ctx['global'][attr] = getattr(g, attr, [])

    ctx['global']['cotation_per_activity'] = {
        'title': u'Cotation globale par activité',
        'xlabels': COTATION_GLOBALE,
        'labels': [act.title() for act in data.activities],
        'values': [g.cotation_globale_per_act(act)['values'] for act in data.activities]
        }

    # attributes for subclasses (activities)
    for cls in Generator.__subclasses__():
        d = cls(data)
        act = d.activity

        # test act to filter out the Global class
        if act:
            ctx[ACT_SHORT[act]] = {'full_name': act.title(),
                                   'cotation': getattr(d, 'cotation', [])}

    d = datetime.now()
    ctx['date_generated'] = unicode(d.strftime('%d %B %Y à %X'), 'utf-8')
    ctx['time'] = {
        'download': '{:.2}'.format(data.download_time),
        'parse': '{:.2}'.format(data.parse_time),
        'generation': '{:.3}'.format(time.time() - t1),
        'total': '{:.2}'.format(time.time() - t0)
    }

    with open(filename, 'w') as f:
        json.dump(ctx, f)


def remove_plus(nparray):
    "Remove '+' for all elements of the numpy array `nparray`"
    l = lambda x: x.replace('+','')
    vrem = np.vectorize(l)
    return vrem(nparray)


class Generator(object):

    def __init__(self, data):
        self.data = data
        self.activity = ''
        self.cotation_values = []
        self.cotation_title = ''

        self.year = np.array([int(i.split()[2]) for i in self.data.date])
        self.year_uniq = np.unique(self.year)
        self.year_labels = [str(i) for i in self.year_uniq]


    def filter_activity(self, arr, activity):
        "Return a sub array of `arr` with only data for `activity`"
        arr_filtered = np.copy(arr)
        ind = (self.data.activity == activity)
        arr_filtered = arr_filtered[ind]
        return arr_filtered


    @property
    def cotation(self):
        c = Counter(self.cotation_values)
        return {'title': self.cotation_title,
                'labels': self.COTATION_REF,
                'values': [c[k] for k in self.COTATION_REF]}


    def gain_per_year(self):

        if self.activity:
            gain = self.filter_activity(self.data.gain, self.activity)
            year = self.filter_activity(self.data.year, self.activity)
        else:
            gain = self.data.gain
            year = self.year

        counts = []
        for i in self.year_uniq:
            ind = (year == i)
            counts.append(np.sum(gain[ind]))

        return counts


class Global(Generator):

    COTATION_REF = COTATION_GLOBALE

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.cotation_values = self.data.cot_globale
        self.cotation_title = u'Cotation globale'

    @property
    def activities(self):
        "Count number of outings per activity"
        c = Counter(self.data.activity)
        return {'title': u'Répartition par activité',
                'labels': c.keys(),
                'values': c.values()}

    @property
    def activities_per_year(self):
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
        use = zip(*use)
        return {'title': u'Répartition par région',
                'labels': use[0],
                'values': use[1]}


    def cotation_globale_per_act(self, activity):
        "Count number of outings per bin of cot_globale"
        c = Counter(self.filter_activity(self.data.cot_globale, activity))
        return {'title': u'Cotation globale',
                'labels': COTATION_GLOBALE,
                'values': [c[k] for k in COTATION_GLOBALE]}


class Escalade(Generator):

    COTATION_REF = ('3a', '3b', '3c', '4a', '4b', '4c', '5a', '5b',
                    '5c', '6a', '6b', '6c', '7a', '7b', '7c', '8a')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.activity = 'escalade'
        self.cotation_values = remove_plus(self.data.cot_libre)
        self.cotation_title = u'Cotation escalade'


class Glace(Generator):

    COTATION_REF = ('2', '3', '3+', '4', '4+', '5', '5+', '6', '6+')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.activity = u'cascade de glace'
        self.cotation_values = self.data.cot_glace
        self.cotation_title = u'Cotation glace'


class Rando(Generator):

    COTATION_REF = ('T1', 'T2', 'T3', 'T4', 'T5', 'T6')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.activity = u'randonnée pédestre'
        self.cotation_values = self.data.cot_rando
        self.cotation_title = u'Cotation rando'


class Alpinisme(Generator):
    pass

class Raquette(Generator):
    pass

class Rocher(Generator):
    pass

class Ski(Generator):

    COTATION_REF = ('S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.activity = u'ski, surf'
        self.cotation_values = self.data.cot_skiponc
        self.cotation_title = u'Cotation ponctuelle ski'
