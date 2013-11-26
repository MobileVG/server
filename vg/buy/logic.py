from __future__ import unicode_literals, absolute_import

from sqlalchemy import desc, distinct
from ..errors import *
from .. import util
from ..util import Paging
from ..models import *
from ..pub import get_app, create_currency_category


def user_exists(session, uid, with_disabled=False):
    q = session.query(User).filter(User.id == uid)
    if not with_disabled:
        q = q.filter(User.disabled_at == None)
    return session.query(q.exists()).scalar()


def get_user(session, uid, with_disabled=False, with_goods=True):
    q = session.query(User).filter(User.id == uid)
    if not with_disabled:
        q = q.filter(User.disabled_at == None)
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
                    goods={})
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


def query_goods(session, ctx, **opts):
    category = opts.get('category')
    paid = opts.get('paid', PAID_ALL)
    tags = opts.get('tags')
    search = opts.get('search', '').strip()
    sort = opts.get('sort', SORT_PUBLISH)
    paging = opts.get('paging', Paging(1, 20))

    q = session.query(Goods).filter(Goods.app == ctx.app \
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

    # app_version
    if ctx.app_version and ctx.app_version > 0:
        if ctx.is_android:
            q.filter(ctx.app_version >= Goods.app_min_version_ard) \
                .filter(ctx.app_version <= Goods.app_max_version_ard)
        elif ctx.is_ios:
            q.filter(ctx.app_version >= Goods.app_min_version_ios) \
                .filter(ctx.app_version <= Goods.app_max_version_ios)
        else:
            pass

    # sort by
    if sort == SORT_SALES:
        q = q.order_by(desc(Goods.sales_count))
    else:
        q = q.order_by(desc(Goods.created_at))


    # paging
    q = q.offset(paging.offset).limit(paging.limit)

    # Query!
    return util.as_list(q.all())


def get_goods(session, goods_id):
    return session.query(Goods).get(goods_id)


def list_goods(session, goods_ids, cts=None):
    q = session.query(Goods) \
        .filter(Goods.id.in_(goods_ids)) \
        .filter(Goods.disabled_at == None)
    if cts:
        q = q.filter(Goods.content_type.in_(cts))
    return util.as_list(q.all())


def _expand_goods(session, goods_ids, cts=None):
    # return {good_id: goods} with subs
    d = dict()
    goods_list = list_goods(session, goods_ids, cts=cts)
    sub_ids = set()
    for goods in goods_list:
        if goods.id not in d:
            d[goods.id] = goods
            if goods.is_package:
                for k in goods.subs.keys():
                    sub_ids.add(k)
    if sub_ids:
        sub_goods_list = list_goods(session, util.as_list(sub_ids), cts=cts)
        for sub_goods in sub_goods_list:
            if sub_goods.id not in d:
                d[sub_goods.id] = sub_goods
    return d

def bought_batch(session, app, uid, goods_ids):
    r = {}
    if goods_ids:
        q = session.query(distinct(History.goods))\
            .filter(History.app == app) \
            .filter(History.buyer == uid) \
            .filter(History.goods.in_(goods_ids)) \
            .filter(History.type == History.TYPE_RECEIPT)
        bought_ids = set([t[0] for t in q.all()])
        for goods_id in goods_ids:
            r[goods_id] = bool(goods_id in bought_ids)

    return r


def attach_info_to_goods_objs(session, ctx, goods_objs, assets):
    goods_ids = [goods['id'] for goods in goods_objs]

    # 'bought'
    bought_result = bought_batch(session, ctx.app, ctx.uid, goods_ids)
    for goods in goods_objs:
        goods_id = goods['id']
        b = bought_result[goods_id]
        goods['bought'] = b

    # TODO: 'buyable'
    # TODO: 'givable'
    return goods_objs


def get_assets(session, uid):
    user = get_user(session, uid, with_goods=True)
    return user.assets if user is not None else None


def _buyable(session, ctx, cost_type, goods_id, count, assets,
             expanded_goods):
    def buyable0(goods_id0, count0, for_sub):
        goods0 = expanded_goods[goods_id0]

        # check paid_type
        if goods0.paid_type == Goods.PT_ANON_FREE:
            return E_ILLEGAL_PAID_TYPE

        # check count
        if not goods0.is_package:
            if not assets.goods_limit(goods_id0, count0,
                                      goods0.limit_per_user):
                return E_TOO_MANY_GOODS

        # check currency
        if not for_sub:
            if cost_type == History.CC_PRIMARY_CURRENCY:
                dpc = goods0.discounted_primary_currency
                if dpc is None:
                    return E_ILLEGAL_COST_TYPE
                if not assets.primary_currency_enough(dpc * count0):
                    return E_CURRENCY_NOT_ENOUGH
            elif cost_type == History.CC_SECOND_CURRENCY:
                dsc = goods0.discounted_second_currency
                if dsc is None:
                    return E_ILLEGAL_COST_TYPE
                if not assets.second_currency_enough(dsc * count0):
                    return E_CURRENCY_NOT_ENOUGH
            elif cost_type == History.CC_REAL_MONEY:
                drm = goods0.discounted_real_money
                if drm is None:
                    return E_ILLEGAL_COST_TYPE

        return E_OK

    if not ctx.is_user():
        return False

    goods = expanded_goods[goods_id]
    if not goods.is_package:
        return buyable0(goods_id, count, False)
    else:
        cr = buyable0(goods_id, count, False)
        if cr != E_OK:
            return cr
        cr = E_TOO_MANY_GOODS
        subs = goods.subs
        for sub_id, sub_count in subs.items():
            cr = buyable0(sub_id, sub_count * count, True)
            if cr == E_OK:
                cr = E_OK
        return cr


def buyable(session, ctx, cost_type, goods_id, count):
    assets = get_assets(session, ctx.uid)
    if assets is None:
        raise VGError(E_ILLEGAL_USER)
    expanded_goods = _expand_goods(session, [goods_id])
    cr = _buyable(session, ctx, cost_type, goods_id, count, assets,
                  expanded_goods)
    return cr == E_OK


def _gen_history_id(goods_id, dt, type):
    return 'h%s%s.%s%s' % \
           (type, goods_id, util.epoch_millis(dt), util.randstr(4))


def buy(session, ctx, cost_type, goods_id, count,
        app_data=None, cost_real_money=None, pay_channel=None, pay_id=None):
    def buy0(goods_id0, count0, parent_goods_id):
        goods0 = expanded_goods[goods_id0]

        # modify currency
        if parent_goods_id is None: # is_package
            if cost_type == History.CC_PRIMARY_CURRENCY:
                assets.incr_primary_currency(
                    -goods0.discounted_primary_currency * count)
            elif cost_type == History.CC_SECOND_CURRENCY:
                assets.incr_second_currency(
                    -goods0.discounted_second_currency * count)

        # modify assets
        if not goods0.is_package:
            assets.incr_goods(goods_id0, count0, goods0.limit_per_user)

        # update sales_count
        session.query(Goods).filter(Goods.id == goods0.id) \
            .update({'sales_count': Goods.sales_count + count0})

        # save to history
        h = History()
        h.id = _gen_history_id(goods0.id, now, History.TYPE_RECEIPT)
        h.app = ctx.app
        h.category = goods0.category
        h.buyer = ctx.uid
        h.buyer_human = ctx.uid_human
        h.goods = goods0.id
        h.parent_goods = parent_goods_id
        h.count = count0
        h.created_at = now
        h.type = History.TYPE_RECEIPT
        h.app_data = app_data or ''

        if parent_goods_id is None: # not for sub
            cc = 0
            crmc = ''
            crma = 0.0
            if cost_type == History.CC_PRIMARY_CURRENCY:
                cc = goods0.discounted_primary_currency
            elif cost_type == History.CC_SECOND_CURRENCY:
                cc = goods0.discounted_second_currency
            elif cost_type == History.CC_REAL_MONEY:
                if cost_real_money is None:
                    raise VGError(E_ILLEGAL_ARG, "Missing real_money")
                rm = util.parse_real_money(cost_real_money, ('', 0.0))
                crmc = rm[0]
                crma = rm[1]
            h.cost_currency_type = cost_type
            h.cost_currency = cc
            h.cost_real_money_cs = crmc
            h.cost_real_money_amount = crma
            h.discount = goods0.discount
        else:
            h.cost_currency_type = cost_type
            h.cost_currency = 0
            h.cost_real_money_cs = ''
            h.cost_real_money_amount = 0.0
            h.discount = 1.0

        h.pay_channel = pay_channel or ''
        h.pay_id = pay_id or ''
        h.buyer_device = ctx.device or ''
        h.buyer_locale = ctx.locale or ''
        h.buyer_ip = ctx.ip or ''
        session.add(h)


    now = util.now()
    assets = get_assets(session, ctx.uid)
    if assets is None:
        raise VGError(E_ILLEGAL_USER)
    expanded_goods = _expand_goods(session, [goods_id])
    if not expanded_goods:
        raise VGError(E_ILLEGAL_GOODS)

    cr = _buyable(session, ctx, cost_type, goods_id, count, assets,
                  expanded_goods)
    if cr != E_OK:
        raise VGError(cr)

    goods = expanded_goods[goods_id]

    buy0(goods_id, count, None)
    if goods.is_package:
        subs = goods.subs
        for sub_id, sub_count in subs.items():
            buy0(sub_id, count * sub_count, goods_id)

    assets.save_to_user(session, ctx.uid)
    return assets


def _make_gc(goods):
    if goods.content_type == Goods.CT_URL:
        return {'url': goods.content}
    elif goods.content_type == Goods.CT_TEXT:
        return {'text': goods.content}
    else:
        return None


def give_many(session, ctx, good_ids):
    # Returns:
    # {
    #   "goods1_id":null, // NOT FOUND or content_type error or not perm
    #   "goods2_id":{"url": "http://..."},
    #   "goods3_id":{"text": "TEXT"}
    # }

    if not good_ids:
        return {}
    r = {}

    assets = get_assets(session, ctx.uid) if ctx.is_user() else None
    expanded_goods = _expand_goods(session, good_ids,
                                   cts=[Goods.CT_URL, Goods.CT_TEXT])
    for goods_id in good_ids:
        gc = None
        goods = expanded_goods.get(goods_id)
        if goods is not None:
            if ctx.is_user():
                if goods.paid_type == Goods.PT_ANON_FREE:
                    gc = _make_gc(goods)
                else:
                    if assets.has_goods(goods.id):
                        gc = _make_gc(goods)
            else:
                if goods.paid_type == Goods.PT_ANON_FREE:
                    gc = _make_gc(goods)
        r[goods_id] = gc

    return r


def give_one(session, ctx, goods_id, raw=False):
    # Returns:
    # None or {'url':'...'} or {'text':'...'}
    cs = give_many(session, ctx, [goods_id])
    return cs.get(goods_id)


def consume(session, ctx, goods_id, count, app_data=None):
    def consume0(goods_id0, count0):
        goods0 = expanded_goods[goods_id0]
        if not goods0.consumable:
            raise VGError(E_GOODS_NOT_CONSUMABLE, goods_id0)
        if not assets.goods_enough(goods_id0, count0):
            raise VGError(E_GOODS_NOT_ENOUGH, goods_id0)
        assets.incr_goods(goods_id0, -count0, goods.limit_per_user)

        # save to history
        h = History()
        h.id = _gen_history_id(goods0.id, now, History.TYPE_CONSUMPTION)
        h.app = ctx.app
        h.category = goods0.category
        h.buyer = ctx.uid
        h.buyer_human = ctx.uid_human
        h.goods = goods0.id
        h.parent_goods = ''
        h.count = count0
        h.created_at = now
        h.type = History.TYPE_CONSUMPTION
        h.app_data = app_data or ''
        h.cost_currency_type = 0
        h.cost_currency = 0
        h.cost_real_money_cs = ''
        h.cost_real_money_amount = 0.0
        h.discount = 1.0
        h.pay_channel = ''
        h.pay_id = ''
        h.buyer_device = ctx.device or ''
        h.buyer_locale = ctx.locale or ''
        h.buyer_ip = ctx.ip or ''
        session.add(h)

    now = util.now()
    assets = get_assets(session, ctx.uid)
    if assets is None:
        raise VGError(E_ILLEGAL_USER)
    expanded_goods = _expand_goods(session, [goods_id])
    if not expanded_goods:
        raise VGError(E_ILLEGAL_GOODS)

    goods = expanded_goods[goods_id]
    if not goods.is_package:
        consume0(goods_id, count)
    else:
        subs = goods.subs
        for sub_id, sub_count in subs.items():
            consume0(sub_id, count * sub_count)
    assets.save_to_user(session, ctx.uid, with_currency=False)
    return assets


def list_history(session, app, uid, types=None, **kwargs):
    paging = kwargs.get('paging', Paging(1, 20))
    q = session.query(History) \
        .filter(History.app == app) \
        .filter(History.buyer == uid)
    if types:
        q = q.filter(History.type.in_(util.as_list(types)))
    q.order_by(desc(History.created_at))
    q = q.offset(paging.offset).limit(paging.limit)

    # Query!
    return util.as_list(q.all())



