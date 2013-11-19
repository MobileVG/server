from __future__ import unicode_literals, absolute_import

from sqlalchemy import desc
from ..errors import *
from .. import util
from ..models import *
from ..pub import get_app, create_currency_category


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
    categories = util.as_list(
        session.query(Category).filter(Category.app == app).all())
    categories.insert(0, create_currency_category(app))
    return categories


SORT_PUBLISH = 1
SORT_SALES = 2

PAID_ALL = 1
PAID_PAID = 2
PAID_FREE = 3


def query_goods(session, app, category, **kwargs):
    paid = util.parse_int(kwargs.get('paid'), PAID_ALL)
    tags = util.parse_strings(kwargs.get('tags'))
    search = kwargs.get('search', '').strip()
    sort = kwargs.get('sort', SORT_PUBLISH)
    paging = util.parse_paging(kwargs.get('paging', None))


    q = session.query(Goods).filter(Goods.app == app \
        and Goods.disabled_at != None)
    # category
    if category is not None:
        q = q.filter(Goods.category == category)

    # paid
    if paid == PAID_PAID:
        q = q.filter(Goods.paid_type == Goods.PT_PAID)
    elif paid == PAID_FREE:
        q = q.filter(
            Goods.paid_type == Goods.PT_FREE \
                or Goods.paid_type == Goods.PT_ANON_FREE)
    elif paid == PAID_ALL:
        pass
    else:
        raise VGError(E_ILLEGAL_ARG, "Illegal paid")

    # tags
    if tags:
        for tag in tags:
            tag = tag.strip()
            if tag:
                q = q.filter(Goods.tags.like('%%%s%%' % tag))

    # search_key
    if search:
        like_str = '%%%s%%' % search
        q = q.filter(Goods.name.like(like_str)
        or (Goods.publisher_info != None
            and Goods.publisher_info.like(like_str)))

    # sort by
    if sort == SORT_SALES:
        q = q.order_by(desc(Goods.sales_count))
    else:
        q = q.order_by(desc(Goods.created_at))

    # paging
    q = q.offset((paging[0] - 1) * paging[1]).limit(paging[1])

    # Query!
    return util.as_list(q.all())


def attach_info_to_goods_objs(session, ctx, goods_objs):
    # TODO: ...
    pass



