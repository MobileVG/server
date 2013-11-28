from __future__ import unicode_literals

from share import *

app = None # dummy

_HEADERS = {
    'X-VG-Ticket': 'IEHwLWGLDz3Otfw8VsJox7svNNWBc1-2M6PUNc69u1s9M7l03F2-4Jd2zZMcrne1bI02tTGQyejmsctmi8x4rzgwqFm56wHl',
    'X-VG-App': 'd131115g5vEv3.oAGt',
    'X-VG-Secret': 'LBtnqfun1CKD9KWu9VIgNJOVTXlmrz6I',
}


def test_list_category_api():
    rv = app.get('/api/1/buy/category/list', headers=_HEADERS)
    code, data = parse_api_resp(rv)
    assert code == 0



