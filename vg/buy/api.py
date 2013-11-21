from __future__ import unicode_literals, absolute_import
from flask import Blueprint, g, request, Response, redirect
from ..gv import db
from .. import util
from ..util import json_api, ColumnFilter, ColumnFor
from .logic import *
from ..context import need_buyer

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
               'limit_per_user',
               'app_min_version_ard',
               'app_max_version_ard',
               'app_min_version_ios',
               'app_max_version_ios',
               'content_type',
               'content']

COLUMN_FILTER = ColumnFilter(None,
                             ColumnFor(User,
                                       excludes=['disabled_at', 'app']),
                             ColumnFor(Category, excludes=['app']),
                             ColumnFor(Goods, includes=_GOODS_COLS)
)

mod = Blueprint('BuyAPIs', __name__)


@mod.route('/buy/user/identify')
@json_api
def identify_user_api():
    ctx = g.context
    uid = request.args['id']
    human = request.args.get('human', '')
    app_data = util.parse_json_dict(request.args.get('app_data', None), {})
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
    ctx = g.context
    category = request.args.get('category', None)
    with db.open_session() as session:
        goods = query_goods(session, ctx.app, category,
                            **util.request_args_as_dict('paid', 'tags',
                                                        'search', 'sort',
                                                        'paging'))
        goods_objs = util.to_json_obj(goods, col_filter=COLUMN_FILTER)
        attach_info_to_goods_objs(session, ctx, goods_objs)
        return goods_objs


@mod.route('/buy/buy')
@json_api
@need_buyer
def buy_api():
    ctx = g.context
    args = request.args
    cost_type = int(args['cost_type'])
    goods_id = args['goods_id']
    count = util.parse_int(args.get('count'), 1)
    cost_real_money = args.get('cost_real_money', None)
    pay_channel = args.get('pay_channel', None)
    pay_id = args.get('pay_id', None)
    with db.open_session() as session:
        assets = buy(session, ctx, cost_type, goods_id, count,
                     cost_real_money=cost_real_money,
                     pay_channel=pay_channel,
                     pay_id=pay_id)
        return assets


@mod.route('/buy/give_many')
@json_api
@need_buyer
def give_many_api():
    ctx = g.context
    goods_ids = util.parse_strings(request.args['good_ids'], ',')
    with db.open_session() as session:
        contents = give_many(session, ctx, goods_ids)
        return contents


@mod.route('/buy/give')
@json_api
@need_buyer
def give_one_api():
    ctx = g.context
    good_id = request.args['goods_id']
    raw = util.parse_bool(request.args.get('raw'), False)
    with db.open_session() as session:
        r = give_one(session, ctx, good_id, raw=raw)
        if not raw:
            return r
        else:
            if r is None:
                return Response(response='', status=404)
            elif 'text' in r:
                return Response(response=r['text'], content_type='text/plain')
            elif 'url' in r:
                return redirect(r['url'])
            else:
                return Response(response='', status=404)




