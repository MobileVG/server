from __future__ import unicode_literals, absolute_import

from ..models import *
import datetime
from .. import util
from ..errors import *
from ..util import MText





# developer

def developer_exists(session, uid, with_disabled=False):
    q = session.query(Developer).filter(Developer.id == uid)
    if not with_disabled:
        q = q.filter(Developer.disabled_at == None)
    return session.query(q.exists()).scalar()


def create_developer(session, email, pwd, name, desc=None):
    now = util.now()
    # TODO: check new id exists
    developer = Developer(id=util.gen_uid(True),
                          created_at=now,
                          updated_at=now,
                          password=pwd,
                          email=email,
                          name=name or '',
                          desc=desc or '')
    session.add(developer)
    return developer

def get_developer(session, uid):
    return session.query(Developer).get(uid)



# app

def app_exists(session, app):
    q = session.query(App).filter(App.id == app)
    return session.query(q.exists()).scalar()

def create_app(session, uid, name=''):
    def gen_app_id():
        for i in xrange(1000):
            app_id = '%s.%s' % (uid, util.randstr(4))
            if not app_exists(session, app_id):
                return app_id
        raise VGError(E_ILLEGAL_APP, "Can't gen app_id")

    now = util.now()
    app_id = gen_app_id()
    secret = util.randstr(32)
    app = App(id=app_id,
              created_at=now,
              updated_at=now,
              secret=secret,
              name=name,
              owner=uid
              )
    session.add(app)
    return app

def get_app(session, app):
    return session.query(App).get(app)


# category

CURRENCY_CATEGORY = 'Currency'

def create_currency_category(app):
    return Category(app=app, id=CURRENCY_CATEGORY,
                    created_at=None, updated_at=None,
                    name=MText('Currency'), desc=MText('Currency'))

def category_exists(session, app, category):
    if category == CURRENCY_CATEGORY:
        return True
    q = session.query(Category).filter(Category.app == app) \
            .filter(Category.id == category)
    return session.query(q.exists()).scalar()

def create_category(session, app, category, name, desc=''):
    if category_exists(session, app, category):
        raise VGError(E_ILLEGAL_CATEGORY)
    now = util.now()
    category = Category(app=app, id=category,
                        created_at=now, updated_at=now,
                        name=util.mtext(name), desc=util.mtext(desc))
    session.add(category)
    return category


# goods

def goods_exists(session, id, with_disabled=False):
    q = session.query(Goods).filter(Goods.id == id)
    if not with_disabled:
        q = q.filter(Goods.disabled_at == None)
    return session.query(q.exists()).scalar()

def create_goods(session, goods):
    def gen_goods_id():
        dts = datetime.datetime.strftime(now, '%y%m%d%H%M%S')
        return 'g%s.%s%s' % (app, dts, util.randstr(4))

    app = goods.app
    category = goods.category
    now = util.now()
    id = gen_goods_id()

    if not category_exists(session, app, category):
        raise VGError(E_ILLEGAL_CATEGORY)
    goods.id = id
    goods.version = util.epoch_millis(now)
    goods.created_at = now
    goods.updated_at = now
    # other fields
    session.add(goods)
    return goods




