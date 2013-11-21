from __future__ import unicode_literals, absolute_import

from flask import Blueprint, jsonify, request, g
from .logic import *
from ..gv import db
from . import util
from ..util import json_api, ColumnFilter, ColumnFor, MText
from ..context import Ticket, need_developer

mod = Blueprint('PubAPIs', __name__)


COLUMN_FILTER = ColumnFilter(None,
    ColumnFor(Developer, excludes=['password', 'disabled_at']),
    ColumnFor(App, excludes=['secret', 'owner']),
    ColumnFor(Category, excludes=['app']),
    ColumnFor(Goods, includes=['id', 'category', 'version', 'publisher',
                               'created_at', 'updated_at', 'disabled_at',
                               'tags', 'logo_url', 'preview_urls',
                               'name', 'desc', 'publisher_info', 'app_data',
                               'paid_type', 'primary_currency',
                               'second_currency', 'real_money',
                               'pay_info', 'discount',
                               'consumable', 'limit_per_user',
                               'app_min_version_ard', 'app_max_version_ard',
                               'app_min_version_ios', 'app_max_version_ios',
                               'content_type', 'content',
                               'parent', 'subs'])
)

# developer

@mod.route('/pub/developer/create')
@json_api
def create_developer_api():
    email = request.args['email']
    name = request.args.get('name', '')
    with db.open_session() as session:
        developer = create_developer(session, email, 'pwd', name)
        jo = util.to_json_obj(developer, col_filter=COLUMN_FILTER)
        return jo


@mod.route('/pub/developer/self')
@json_api
@need_developer
def get_self_api():
    with db.open_session() as session:
        developer = get_developer(session, g.context.uid)
        return util.to_json_obj(developer, col_filter=COLUMN_FILTER)

# app

@mod.route('/pub/app/create')
@json_api
@need_developer
def create_app_api():
    ctx = g.context
    name = request.args['name']
    with db.open_session() as session:
        app = create_app(session, ctx.uid, name)
        return util.to_json_obj(app, col_filter=COLUMN_FILTER)


# category

@mod.route('/pub/category/create')
@json_api
@need_developer
def create_category_api():
    ctx = g.context
    id = request.args['id']
    name = request.args['name']
    desc = request.args.get('desc', '')
    with db.open_session() as session:
        category = create_category(session, ctx.app, id, name, desc=desc)
        return util.to_json_obj(category, col_filter=COLUMN_FILTER)


# goods
@mod.route('/pub/goods/create')
@json_api
@need_developer
def create_goods_api():
    ctx = g.context
    args = request.args
    category = args['category']
    tags = util.parse_strings(args.get('tags'))
    logo_url = '' # TODO
    preview_urls = [] # TODO
    name = MText(args.get('name', ''))
    desc = MText(args.get('desc', ''))
    publisher_info = util.parse_json_dict(args.get('publisher_info'), {})
    app_data = util.parse_json_dict(args.get('app_data'), {})
    paid_type = int(args['paid_type'])
    primary_currency = util.parse_int(args.get('primary_currency', None))
    second_currency = util.parse_int(args.get('second_currency', None))
    real_money = MText(args.get('real_money', ''))
    pay_info = util.parse_json_dict(args.get('pay_info'), {})
    discount = util.parse_float(args.get('discount'), default=float(1))
    consumable = util.parse_bool(args['consumable'])
    limit_per_user = util.parse_int(args.get('limit_per_user'), 0)
    app_min_version_ard = util.parse_int(args.get('app_min_version_ard'), 0)
    app_max_version_ard = util.parse_int(args.get('app_max_version_ard'), 0)
    app_min_version_ios = util.parse_int(args.get('app_min_version_ios'), 0)
    app_max_version_ios = util.parse_int(args.get('app_max_version_ios'), 0)
    content_type = util.parse_int(args['content_type'])
    content = args.get('content', '')


    ctx = g.context
    with db.open_session() as session:
        goods = Goods(app=ctx.app,
                      category=category,
                      publisher = ctx.uid,
                      tags=tags,
                      logo_url=logo_url,
                      preview_urls=preview_urls,
                      name=name,
                      desc=desc,
                      publisher_info=publisher_info,
                      app_data=app_data,
                      paid_type=paid_type,
                      primary_currency=primary_currency,
                      second_currency=second_currency,
                      real_money=real_money,
                      pay_info=pay_info,
                      discount=discount,
                      consumable=consumable,
                      limit_per_user=limit_per_user,
                      app_min_version_ard=app_min_version_ard,
                      app_max_version_ard=app_max_version_ard,
                      app_min_version_ios=app_min_version_ios,
                      app_max_version_ios=app_max_version_ios,
                      content_type=content_type,
                      content=content,)
        goods = create_goods(session, goods)
        return util.to_json_obj(goods, col_filter=COLUMN_FILTER)



# For develop


@mod.route('/_dev/gen_ticket')
@json_api
def gen_ticket_api():
    uid = request.args['uid']
    return Ticket(uid).encode()

@mod.route('/_dev/parse_ticket')
@json_api
def parse_ticket_api():
    t = request.args['ticket']
    t1 = Ticket.decode(t)
    return {'uid':t1.uid, 'dt':t1.dt}


@mod.route('/_dev/whoami')
@json_api
def whoami_api():
    return g.context.uid