# -*- coding:utf-8 -*-

import codecs
import json
import locale
import numpy as np
import os
import pytest
from httpretty import HTTPretty, httprettified

from c2cstats.generators import (generate, Global, Escalade, Alpinisme, Ski,
                                 Rocher, Raquette, Glace, Rando, remove_plus)
from c2cstats.parser import Outings

URL = "http://www.camptocamp.org/outings/list/users/113594/format/json/npp/50"
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


@pytest.fixture(scope="module")
@httprettified
def data():
    locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))
    filename = os.path.join(DATA_DIR, '113594.1.json')
    with codecs.open(filename, "r", "utf-8") as f:
        content = f.read()

    HTTPretty.register_uri(HTTPretty.GET, URL + '/page/1', body=content,
                           content_type="application/json")

    filename = os.path.join(DATA_DIR, '113594.2.json')
    with codecs.open(filename, "r", "utf-8") as f:
        content = f.read()

    HTTPretty.register_uri(HTTPretty.GET, URL + '/page/2', body=content,
                           content_type="application/json")

    filename = os.path.join(DATA_DIR, '113594.3.json')
    with codecs.open(filename, "r", "utf-8") as f:
        content = f.read()

    HTTPretty.register_uri(HTTPretty.GET, URL + '/page/3', body=content,
                           content_type="application/json")

    return generate(113594)


@pytest.fixture(scope="module")
@httprettified
def outings():
    locale.setlocale(locale.LC_ALL, ('en_US', 'UTF-8'))
    filename = os.path.join(DATA_DIR, '113594.1.json')
    with codecs.open(filename, "r", "utf-8") as f:
        content = f.read()

    HTTPretty.register_uri(HTTPretty.GET, URL + '/page/1', body=content,
                           content_type="application/json")

    filename = os.path.join(DATA_DIR, '113594.2.json')
    with codecs.open(filename, "r", "utf-8") as f:
        content = f.read()

    HTTPretty.register_uri(HTTPretty.GET, URL + '/page/2', body=content,
                           content_type="application/json")

    filename = os.path.join(DATA_DIR, '113594.3.json')
    with codecs.open(filename, "r", "utf-8") as f:
        content = f.read()

    HTTPretty.register_uri(HTTPretty.GET, URL + '/page/3', body=content,
                           content_type="application/json")

    return Outings(113594)


@pytest.fixture(scope="module")
def ref():
    filename = os.path.join(DATA_DIR, 'result.json')
    with codecs.open(filename, "r", "utf-8") as f:
        ref = json.loads(f.read())
    return ref


def test_global(outings, ref):
    g = Global(outings)
    for key in ['activities', 'area', 'cotation', 'outings_per_month']:
        assert getattr(g, key)['values'] == ref['global'][key]['values']


def test_escalade(outings, ref):
    g = Escalade(outings)
    for key in ['cotation', 'gain_per_year', 'outings_per_year']:
        assert getattr(g, key)['values'] == ref['escalade'][key]['values']


def test_glace(outings, ref):
    g = Glace(outings)
    for key in ['cotation', 'gain_per_year', 'outings_per_year']:
        assert getattr(g, key)['values'] == ref['glace'][key]['values']


def test_rando(outings, ref):
    g = Rando(outings)
    for key in ['cotation', 'gain_per_year', 'outings_per_year']:
        assert getattr(g, key)['values'] == ref['rando'][key]['values']


def test_alpinisme(outings, ref):
    g = Alpinisme(outings)
    for key in ['cotation', 'gain_per_year', 'outings_per_year']:
        assert getattr(g, key)['values'] == ref['alpinisme'][key]['values']


def test_ski(outings, ref):
    g = Ski(outings)
    for key in ['cotation', 'gain_per_year', 'outings_per_year']:
        assert getattr(g, key)['values'] == ref['ski'][key]['values']


def test_rocher(outings, ref):
    g = Rocher(outings)
    for key in ['cotation', 'gain_per_year', 'outings_per_year']:
        assert getattr(g, key)['values'] == ref['rocher'][key]['values']


def test_raquette(outings, ref):
    g = Raquette(outings)
    for key in ['cotation', 'gain_per_year', 'outings_per_year']:
        assert getattr(g, key)['values'] == ref['raquette'][key]['values']


def test_generate(data, ref):
    for key in ['activities', 'nb_outings', 'url', 'user_url']:
        assert data[key] == ref[key]

    for act in data['activities']:
        for key in ['cotation', 'cotation_globale', 'gain_per_year',
                    'outings_per_year']:
            if key in data[act]:
                assert data[act][key]['values'] == ref[act][key]['values']

        assert data[act]['gain_per_year']['values_per_month'] == \
            ref[act]['gain_per_year']['values_per_month']


def test_remove_plus():
    arr = np.array(['5a+', '4+', '3c', '7b+', '8a'])
    assert remove_plus(arr).tolist() == ['5a', '4', '3c', '7b', '8a']
    assert remove_plus(np.array([])).tolist() == []
