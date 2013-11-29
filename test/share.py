from __future__ import unicode_literals, absolute_import

import os
import sys
import json

self_folder = os.path.dirname(os.path.abspath(__file__))
parent_folder = os.path.dirname(self_folder)
os.environ['VG_ROOT'] = parent_folder
os.environ['VG_ENV'] = 'test'
sys.path.insert(0, parent_folder)

import vg


def setup_module(mod):
    vg.app.config['TESTING'] = True
    mod.app = vg.app.test_client()


def teardown_module(mod):
    pass


def parse_api_resp(rv):
    assert rv.status_code == 200
    d = json.loads(rv.data)
    assert type(d) is dict
    return d['code'], d['data']


######################################################




