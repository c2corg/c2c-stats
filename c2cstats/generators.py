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

MONTHS = (u'janvier', u'février', u'mars', u'avril', u'mai', u'juin', u'juillet',
          u'août', u'septembre', u'octobre', u'novembre', u'décembre')

class Generator(object):

    def __init__(self, data):
        self.data = data
        self.activity = ''
        self.cotation_values = []
        self.cotation_title = ''

        self.year = np.array([int(i.split()[2]) for i in self.data.date])
        self.year_range = np.arange(np.min(self.year), np.max(self.year)+1)
        self.year_labels = [str(i) for i in self.year_range]

        self.month = np.array([i.split()[1] for i in data.date])
        self.months_idx = np.arange(12)

    @property
    def cotation(self):
        c = Counter(self.cotation_values)
        return {'title': self.cotation_title,
                'labels': self.COTATION_REF,
                'values': [c[k] for k in self.COTATION_REF]}

    def filter_activity(self, arr, activity):
        "Return a sub array of `arr` with only data for `activity`"
        ind = (self.data.activity == activity)
        return arr[ind]

    def count_per_year(self):

        if self.activity:
           gain = self.filter_activity(self.data.gain, self.activity)
           year = self.filter_activity(self.year, self.activity)
        else:
           gain = self.data.gain
           year = self.year

        self.gain_year = []
        self.gain_month = []
        self.outings_year = []
        self.outings_month = []

        for i in self.year_range:
            ind = (year == i)
            gain_y = gain[ind]

            self.outings_year.append(len(year[ind]))
            self.gain_year.append(int(np.sum(gain_y)))

            month_y = self.month[ind]
            gain_m = np.zeros(12, dtype=int)
            outings_m = np.zeros(12, dtype=int)

            for m in self.months_idx:
                sel = (month_y == MONTHS[m])
                if sel.any():
                    outings_m[m] = len(month_y[sel])
                    gain_m[m] = np.sum(gain_y[sel])

            self.outings_month.append(list(outings_m))
            self.gain_month.append(list(gain_m.cumsum()))

    @property
    def outings_per_year(self):
        "Count number of outings per bin of year"

        return {'title': u'Nombre de sorties par an',
                'labels': self.year_labels,
                'values': self.outings_year}

    @property
    def gain_per_year(self):

        return {'title': u'Dénivelé par an',
                'labels': self.year_labels,
                'values': self.gain_year,
                'values_per_month': self.gain_month}


class Global(Generator):

    COTATION_REF = COTATION_GLOBALE

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.cotation_values = self.data.cot_globale
        self.cotation_title = u'Cotation globale'
        self.count_per_year()

    @property
    def activities(self):
        "Count number of outings per activity"
        c = Counter(self.data.activity)
        return {'title': u'Répartition par activité',
                'labels': c.keys(),
                'values': c.values()}

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

    @property
    def outings_per_month(self):
        "Count number of outings per month"

        return {'title': u'Nombre de sorties par mois',
                'labels': self.year_labels,
                'values': self.outings_month}


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
        self.cotation_values = self.filter_activity(self.data.cot_libre, self.activity)
        self.cotation_values = remove_plus(self.cotation_values)
        self.cotation_title = u'Cotation escalade'
        self.count_per_year()


class Glace(Generator):

    COTATION_REF = ('2', '3', '3+', '4', '4+', '5', '5+', '6', '6+')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.activity = u'cascade de glace'
        self.cotation_values = self.data.cot_glace
        self.cotation_title = u'Cotation glace'
        self.count_per_year()


class Rando(Generator):

    COTATION_REF = ('T1', 'T2', 'T3', 'T4', 'T5', 'T6')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.activity = u'randonnée pédestre'
        self.cotation_values = self.data.cot_rando
        self.cotation_title = u'Cotation rando'
        self.count_per_year()


class Alpinisme(Generator):

    COTATION_REF = ('M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8', 'M9',
                    'M10', 'M11', 'M12')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.activity = u'alpinisme neige, glace, mixte'
        self.cotation_values = remove_plus(self.data.cot_mixte)
        self.cotation_title = u'Cotation mixte'
        self.count_per_year()


class Raquette(Generator):

    COTATION_REF = ('R1', 'R2', 'R3', 'R4', 'R5')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.activity = u'raquette'
        self.cotation_values = self.data.cot_raquette
        self.cotation_title = u'Cotation raquette'
        self.count_per_year()


class Rocher(Generator):

    COTATION_REF = Escalade.COTATION_REF

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.activity = 'rocher haute montagne'
        self.cotation_values = self.filter_activity(self.data.cot_libre, self.activity)
        self.cotation_values = remove_plus(self.cotation_values)
        self.cotation_title = u'Cotation escalade'
        self.count_per_year()


class Ski(Generator):

    COTATION_REF = ('S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7')

    def __init__(self, *args, **kwargs):
        Generator.__init__(self, *args, **kwargs)
        self.activity = u'ski, surf'
        self.cotation_values = self.data.cot_skiponc
        self.cotation_title = u'Cotation ponctuelle ski'
        self.count_per_year()


def remove_plus(nparray):
    "Remove '+' for all elements of the numpy array `nparray`"
    l = lambda x: x.replace('+','')
    vrem = np.vectorize(l)
    return vrem(nparray)


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
    for attr in ['activities', 'area', 'cotation', 'outings_per_month']:
        ctx['global'][attr] = getattr(g, attr, [])

    ctx['global']['cotation_per_activity'] = {
        'title': u'Cotation globale par activité',
        'xlabels': COTATION_GLOBALE,
        'labels': data.activities,
        'values': [g.cotation_globale_per_act(act)['values'] for act in data.activities]
        }

    # attributes for subclasses (activities)
    for cls in Generator.__subclasses__():
        d = cls(data)
        act = d.activity

        # test act to filter out the Global class
        if act and act in data.activities:
            ctx[ACT_SHORT[act]] = {'full_name': act.title(),
                                   'outings_per_year': getattr(d, 'outings_per_year', []),
                                   'gain_per_year': getattr(d, 'gain_per_year', []),
                                   'cotation': getattr(d, 'cotation', []),
                                   'cotation_globale': g.cotation_globale_per_act(act)}

    d = datetime.now()
    ctx['date_generated'] = unicode(d.strftime('%d %B %Y à %X'), 'utf-8')
    ctx['time'] = {
        'download': '{:.2}'.format(data.download_time),
        'parse': '{:.2}'.format(data.parse_time),
        'generation': '{:.3}'.format(time.time() - t1),
        'total': '{:.2}'.format(time.time() - t0)
    }

    try:
        with open(filename, 'w') as f:
            json.dump(ctx, f)
    except IOError:
        print "Erreur lors de la serialiasation du json"
