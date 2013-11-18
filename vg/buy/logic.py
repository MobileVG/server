from __future__ import unicode_literals, absolute_import


from .. import util
from ..models import *
from ..pub import get_app


def user_exists(session, uid, with_disabled=False):
    q = session.query(User).filter(User.id == uid)
    if not with_disabled:
        q = q.filter(User.disabled_at == None)
    return session.query(q.exists()).scalar()

def get_user(session, uid, with_disabled=False, with_assets=True):
    q = session.query(User).filter(User.id == uid)
    if not with_disabled:
        q = q.filter(User.disabled_at == None)
    print q
    return q.first()


def identify_user(session, app, app_uid, human='', app_data=None):
    def gen_uid():
        return 'u%s.%s' % (app, app_uid)

    now = util.now()
    uid = gen_uid()
    if not user_exists(session, uid, with_disabled=True):
        app1 = get_app(session, app)
        assert app1 is not None
        init_primary_currency = app1.options.get('init_primary_currency', 0)
        init_second_currency = app1.options.get('init_second_currency', 0)
        user = User(id=uid, app=app,
                    created_at=now, updated_at=now, disabled_at=None,
                    human=human, app_data=app_data,
                    primary_currency=init_primary_currency,
                    second_currency=init_second_currency,
                    assets=dict())
        session.add(user)
        session.flush()

    return get_user(session, uid)

def list_categories(session, app):
    return session.query(Category).filter(Category.app == app).all()



