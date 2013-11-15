from __future__ import unicode_literals, absolute_import

from flask import Blueprint, jsonify, request, g
from .logic import *
from ..gv import db
from . import util
from ..util import json_api
from ..context import Ticket, need_developer

mod = Blueprint('PubAPIs', __name__)


# developer

@mod.route('/pub/developer/create')
@json_api
def create_developer_api():
    email = request.args['email']
    name = request.args.get('name', '')
    with db.open_session() as session:
        developer = create_developer(session, email, 'pwd', name)
        jo = util.to_json_obj(developer,
                              excludes=['password', 'disabled_at'])
        return jo


@mod.route('/pub/developer/self')
@json_api
@need_developer
def get_self_api():
    with db.open_session() as session:
        developer = get_developer(session, g.context.uid)
        return util.to_json_obj(developer,
                                excludes=['password', 'disabled_at'])

# app

@mod.route('/pub/app/create')
@json_api
@need_developer
def create_app_api():
    ctx = g.context
    name = request.args['name']
    with db.open_session() as session:
        app = create_app(session, ctx.uid, name)
        return util.to_json_obj(app)


@mod.route('/_dev/gen_ticket')
@json_api
def gen_ticket_api():
    uid = request.args['uid']
    return Ticket(uid).encode()


@mod.route('/_dev/whoami')
@json_api
def whoami_api():
    return g.context.uid