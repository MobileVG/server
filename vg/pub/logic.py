from __future__ import unicode_literals, absolute_import

from ..models import *
import datetime
from .. import util
from ..errors import *





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

def app_exists(session, app_id):
    q = session.query(App).filter(App.id == app_id)
    return session.query(q.exists()).scalar()

def create_app(session, uid, name=''):
    def _gen_app_id():
        for i in xrange(1000):
            app_id = '%s.%s' % (uid, util.randstr(4))
            if not app_exists(session, app_id):
                return app_id
        raise VGError(E_ILLEGAL_ID, "Can't gen app_id")

    now = util.now()
    app_id = _gen_app_id()
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


