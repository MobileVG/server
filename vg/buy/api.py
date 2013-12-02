from __future__ import unicode_literals, absolute_import
from flask import Blueprint, g, request, Response, redirect
from ..gv import db
from .. import util
from ..util import u_, json_api, ColumnFilter, WithColumns
from .logic import *
from ..context import need_buyer, need_user
from ..valid import ArgsSchema, AsInt, AsBool, AsJsonObj, \
    AsList, AsPaging, NoValid, \
    Required, Optional, All, Coerce, Length, Range

_GOODS_COLS = ['id', 'version',
               'publisher',
               'created_at',
               'updated_at',
               'tags', 'logo_url',
               'preview_urls',
               'name', 'desc',
               'publisher_info',
               'app_data',
               'paid_type',
               'primary_currency',
               'second_currency',
               'real_money',
               'discounted_primary_currency',
               'discounted_second_currency',
               'discounted_real_money',
               'pay_info',
               'discount',
               'consumable',
               #'limit_per_user',
               'content_type']

_HISTORY_COLS = [
    'app_data', 'category', 'cost', 'cost_currency_type',
    'count', 'created_at', 'discount', 'goods', 'id',
    'parent_goods', 'pay_channel', 'pay_id', 'type',
]

COLUMN_FILTER = ColumnFilter({
    User: WithColumns(excludes=['disabled_at', 'app']),
    Category: WithColumns(excludes=['app']),
    History: WithColumns(includes=_HISTORY_COLS),
    Goods: WithColumns(_GOODS_COLS),
})


mod = Blueprint('BuyAPIs', __name__)


@mod.route('/buy/user/identify')
@json_api
def identify_user_api():
    schema = ArgsSchema({
        Required('id'): Length(min=1),
        Optional('human'): NoValid(),
        Optional('app_data'): AsJsonObj(),
    })
    args = schema.validate_request_args()
    ctx = g.context
    uid = args['id']
    human = args.get('human', '')
    app_data = args.get('app_data', {})
    with db.open_session() as session:
        user = identify_user(session, ctx.app, uid, human=human,
                             app_data=app_data)
        return util.to_json_obj(user, col_filter=COLUMN_FILTER)


@mod.route('/buy/category/list')
@json_api
@need_buyer
def list_categories_api():
    ctx = g.context
    with db.open_session() as session:
        categories = list_categories(session, ctx.app)
        return util.to_json_obj(categories, col_filter=COLUMN_FILTER)


@mod.route('/buy/goods/query')
@json_api
@need_buyer
def query_goods_api():
    schema = ArgsSchema({
        Optional('category'): NoValid(),
        Optional('paid'): AsInt(),
        Optional('tags'): AsList(sep=','),
        Optional('search'): NoValid(),
        Optional('sort'): AsInt(),
        Optional('paging'): AsPaging(),
    })
    args = schema.validate_request_args()
    ctx = g.context
    with db.open_session() as session:
        goods = query_goods(session, ctx, **args)
        expanded_goods = expand_goods(session,
                                      [goods0.id for goods0 in goods])
        goods_objs = util.to_json_obj(goods, col_filter=COLUMN_FILTER,
                                      context=ctx)

        assets = get_assets(session, ctx.uid)
        attach_info_to_goods_objs(session, ctx, goods_objs, expanded_goods,
                                  assets)
        return goods_objs

@mod.route('/buy/buy')
@json_api
@need_user
def buy_api():
    schema = ArgsSchema({
        Required('cost_type'): AsInt(),
        Required('goods_id'): Length(min=1),
        Optional('count'): AsInt(),
        Optional('cost_real_money'): NoValid(),
        Optional('pay_channel'): NoValid(),
        Optional('pay_id'): NoValid(),
        Optional('app_data'): NoValid(),
    })
    args = schema.validate_request_args()
    ctx = g.context
    cost_type = args['cost_type']
    goods_id = args['goods_id']
    count = args.get('count', 1)
    cost_real_money = args.get('cost_real_money')
    pay_channel = args.get('pay_channel')
    pay_id = args.get('pay_id')
    app_data = args.get('app_data')
    with db.open_session() as session:
        assets = buy(session, ctx, cost_type, goods_id, count,
                     cost_real_money=cost_real_money,
                     pay_channel=pay_channel,
                     pay_id=pay_id,
                     app_data=app_data)
        return assets


@mod.route('/buy/give_many')
@json_api
@need_buyer
def give_many_api():
    schema = ArgsSchema({
        Required('good_ids'): AsList(sep=','),
    })
    args = schema.validate_request_args()
    ctx = g.context
    goods_ids = args['good_ids']
    with db.open_session() as session:
        contents = give_many(session, ctx, goods_ids)
        return contents


@mod.route('/buy/give')
@json_api
@need_buyer
def give_one_api():
    schema = ArgsSchema({
        Required('good_id'): Length(min=1),
        Optional('raw'): AsBool(),
    })
    args = schema.validate_request_args()
    ctx = g.context
    good_id = args['goods_id']
    raw = args.get('raw', False)
    with db.open_session() as session:
        r = give_one(session, ctx, good_id, raw=raw)
        if not raw:
            return r
        else:
            if r is None:
                return Response(response='', status=404)
            elif 'text' in r:
                return Response(response=r['text'],
                                content_type='text/plain')
            elif 'url' in r:
                return redirect(r['url'])
            else:
                return Response(response='', status=404)


@mod.route('/buy/consume')
@json_api
@need_user
def consume_api():
    schema = ArgsSchema({
        Required('good_id'): Length(min=1),
        Optional('count'): AsInt(),
        Optional('app_data'): NoValid(),
    })
    args = schema.validate_request_args()
    ctx = g.context
    goods_id = args['goods_id'].strip()
    count = args.get('count', 1)
    app_data = args.get('app_data', '')
    with db.open_session() as session:
        r = consume(session, ctx, goods_id, count, app_data=app_data)
        return r


@mod.route('/buy/assets')
@json_api
@need_user
def get_assets_api():
    with db.open_session() as session:
        r = get_assets(session, g.context.uid)
        return r


@mod.route('/buy/history')
@json_api
@need_user
def list_history_api():
    schema = ArgsSchema({
        Optional('type'): AsList(subtype=int, sep=','),
        Optional('paging'): AsPaging(),
    })
    args = schema.validate_request_args()
    ctx = g.context
    types = args.get('type') or None
    paging = args.get('paging', Paging(1, 20))
    with db.open_session() as session:
        histories = list_history(session, ctx.app, ctx.uid,
                                 types=types, paging=paging)
        return util.to_json_obj(histories, col_filter=COLUMN_FILTER)


