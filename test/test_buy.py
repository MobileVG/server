from __future__ import unicode_literals

from share import *

app = None # dummy

def setup_function(func):
    # reset db
    tables = ['app', 'category', 'developer', 'goods', 'history', 'user']
    with vg.db.open_session() as session:
        # drop table
        for sql in ['drop table if exists `%s`' % t for t in tables]:
            session.execute(sql)
        # create tables
        vg.db.execute_file(os.path.join(parent_folder, 'sqls/ddl.sql'))
        # insert data
        _insert_data(session)


def teardown_function(func):
    pass


_HEADERS = {
    'X-VG-Ticket': 'IEHwLWGLDz3Otfw8VsJox7svNNWBc1-2M6PUNc69u1s9M7l03F2-4Jd2zZMcrne1bI02tTGQyejmsctmi8x4rzgwqFm56wHl',
    'X-VG-App': 'd131115g5vEv3.oAGt',
    'X-VG-Secret': 'LBtnqfun1CKD9KWu9VIgNJOVTXlmrz6I',
}


def test_list_category_api():
    rv = app.get('/api/1/buy/category/list', headers=_HEADERS)
    code, data = parse_api_resp(rv)
    assert code == 0


#####################################################

import datetime

APP_ID = 'd131115g5vEv3.oAGt'
APP_ROWS = [{'name': 'App1',
             'created_at': datetime.datetime(2013, 11, 15, 9, 40, 28),
             'updated_at': datetime.datetime(2013, 11, 15, 9, 40, 28),
             'options': '', 'secret': 'LBtnqfun1CKD9KWu9VIgNJOVTXlmrz6I',
             'owner': 'd131115g5vEv3', 'id': APP_ID}]

CATEGORY_WP_ID = 'wp'
CATEGORY_ROWS = [{'name': '{"def": "Wallpaper"}',
                  'created_at': datetime.datetime(2013, 11, 18, 10, 0, 36),
                  'updated_at': datetime.datetime(2013, 11, 18, 10, 0, 36),
                  'id': CATEGORY_WP_ID, 'app': 'd131115g5vEv3.oAGt',
                  'desc': '{"def": "Wallpaper desc"}'}]

DEVELOPER_ID = 'd131115g5vEv3'
DEVELOPER_ROWS = [{'name': 'Gao Rongxin',
                   'created_at': datetime.datetime(2013, 11, 15, 9, 13, 42),
                   'updated_at': datetime.datetime(2013, 11, 15, 9, 13, 42),
                   'email': 'gaorx@gaorx.me', 'disabled_at': None,
                   'password': '123456', 'id': DEVELOPER_ID,
                   'desc': 'Gao desc'}]

HISTORY_ROWS = []

GOODS_ROWS = [
    {'paid_type': 1, 'pay_info': '{}', 'app': 'd131115g5vEv3.oAGt',
     'updated_at': datetime.datetime(2013, 11, 19, 8, 35, 40),
     'real_money': None, 'app_data': '{}',
     'id': 'gd131115g5vEv3.oAGt.131119083540EPsL', 'category': 'wp',
     'content': 'http://www.baidu.com', 'version': 1384821340981L,
     'publisher_info': '{"name": "GaoRongxin"}', 'logo_url': '',
     'app_min_version_ios': 0L, 'tags': '', 'limit_per_user': 100L,
     'preview_urls': '[]', 'discount': 1.0, 'disabled_at': None,
     'content_type': 1, 'second_currency': None, 'consumable': 1,
     'desc': '{"def": ""}', 'primary_currency': 10L,
     'publisher': 'd131115g5vEv3', 'app_min_version_ard': 0L,
     'name': '{"def": ""}',
     'created_at': datetime.datetime(2013, 11, 19, 8, 35, 40),
     'app_max_version_ard': 0L, 'app_max_version_ios': 0L,
     'sales_count': 0L},
    {'paid_type': 1, 'pay_info': '{}', 'app': 'd131115g5vEv3.oAGt',
     'updated_at': datetime.datetime(2013, 11, 19, 8, 36, 17),
     'real_money': None, 'app_data': '{}',
     'id': 'gd131115g5vEv3.oAGt.131119083617Mf17', 'category': 'wp',
     'content': 'Text1', 'version': 1384821377406L,
     'publisher_info': '{"name": "GaoRongxin"}', 'logo_url': '',
     'app_min_version_ios': 0L, 'tags': '', 'limit_per_user': 200L,
     'preview_urls': '[]', 'discount': 1.0, 'disabled_at': None,
     'content_type': 2, 'second_currency': None, 'consumable': 1,
     'desc': '{"def": ""}', 'primary_currency': 5L,
     'publisher': 'd131115g5vEv3', 'app_min_version_ard': 0L,
     'name': '{"def": ""}',
     'created_at': datetime.datetime(2013, 11, 19, 8, 36, 17),
     'app_max_version_ard': 0L, 'app_max_version_ios': 0L,
     'sales_count': 0L},
    {'paid_type': 1, 'pay_info': '{}', 'app': 'd131115g5vEv3.oAGt',
     'updated_at': datetime.datetime(2013, 11, 19, 8, 36, 22),
     'real_money': '{"def": "USD0.99"}', 'app_data': '{}',
     'id': 'gd131115g5vEv3.oAGt.131119083622J7fR',
     'category': 'Currency', 'content': '{"primary":100}',
     'version': 1384821382094L,
     'publisher_info': '{"name": "GaoRongxin"}', 'logo_url': '',
     'app_min_version_ios': 0L, 'tags': '', 'limit_per_user': 0L,
     'preview_urls': '[]', 'discount': 0.8, 'disabled_at': None,
     'content_type': 4, 'second_currency': None, 'consumable': 1,
     'desc': '{"def": "PC 100 desc"}', 'primary_currency': None,
     'publisher': 'd131115g5vEv3', 'app_min_version_ard': 0L,
     'name': '{"def": "PC 100"}',
     'created_at': datetime.datetime(2013, 11, 19, 8, 36, 22),
     'app_max_version_ard': 0L, 'app_max_version_ios': 0L,
     'sales_count': 0L},
    {'paid_type': 1, 'pay_info': '{}', 'app': 'd131115g5vEv3.oAGt',
     'updated_at': datetime.datetime(2013, 11, 21, 6, 40, 49),
     'real_money': None, 'app_data': '{}',
     'id': 'gd131115g5vEv3.oAGt.131121064049IfTC', 'category': 'wp',
     'content': '{"gd131115g5vEv3.oAGt.131119083540EPsL":1,"gd131115g5vEv3.oAGt.131119083617Mf17":2}',
     'version': 1384987249104L,
     'publisher_info': '{"name": "GaoRongxin"}', 'logo_url': '',
     'app_min_version_ios': 0L, 'tags': '', 'limit_per_user': 0L,
     'preview_urls': '[]', 'discount': 1.0, 'disabled_at': None,
     'content_type': 5, 'second_currency': None, 'consumable': 1,
     'desc': '{"def": ""}', 'primary_currency': 18L,
     'publisher': 'd131115g5vEv3', 'app_min_version_ard': 0L,
     'name': '{"def": ""}',
     'created_at': datetime.datetime(2013, 11, 21, 6, 40, 49),
     'app_max_version_ard': 0L, 'app_max_version_ios': 0L,
     'sales_count': 0L}
]

USER_ROWS = [{'primary_currency': 1000L, 'goods': '{}',
              'created_at': datetime.datetime(2013, 11, 18, 9, 15, 54),
              'updated_at': datetime.datetime(2013, 11, 18, 9, 15, 54),
              'id': 'ud131115g5vEv3.oAGt.rongxin.gao@gmail.com',
              'disabled_at': None, 'app_data': '{}', 'human': 'gaorx',
              'second_currency': 1000L, 'app': 'd131115g5vEv3.oAGt'}]


def _insert_data(session):
    vg.DB.insert_rows(session, 'app', APP_ROWS)
    vg.DB.insert_rows(session, 'category', CATEGORY_ROWS)
    vg.DB.insert_rows(session, 'developer', DEVELOPER_ROWS)
    vg.DB.insert_rows(session, 'history', HISTORY_ROWS)
    vg.DB.insert_rows(session, 'goods', GOODS_ROWS)
    vg.DB.insert_rows(session, 'user', USER_ROWS)


