from __future__ import unicode_literals, absolute_import
from flask import Blueprint, g, request
from ..gv import db
from .. import util
from ..util import json_api, ColumnFilter, ColumnFor
from .logic import *
from ..context import need_user

COLUMN_FILTER = ColumnFilter(
    ColumnFor(User, excludes=['disabled_at', 'app']),
    ColumnFor(Category, excludes=['app'])
)


mod = Blueprint('BuyAPIs', __name__)

@mod.route('/buy/user/identify')
@json_api
def identify_user_api():
    ctx = g.context
    uid = request.args['id']
    human = request.args.get('human', '')
    app_data = util.parse_json_dict(request.args.get('app_data', None))
    with db.open_session() as session:
        user = identify_user(session, ctx.app, uid, human=human,
                             app_data=app_data)
        return util.to_json_obj(user, col_filter=COLUMN_FILTER)


@mod.route('/buy/category/list')
@json_api
@need_user
def list_categories_api():
    ctx = g.context
    with db.open_session() as session:
        categories = list_categories(session, ctx.app)
        return util.to_json_obj(categories, col_filter=COLUMN_FILTER)



