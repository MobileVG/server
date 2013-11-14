from __future__ import unicode_literals, absolute_import

from flask import Blueprint, jsonify, request, g
from .logic import *
from ..gv import db
from . import util
from ..util import json_api

mod = Blueprint('PubPages', __name__)

@mod.route('/test')
@json_api
def test():
    email = request.args['email']
    name = request.args.get('name', '')
    with db.transaction():
        return create_developer(g.context, email, pwd='pwd', name=name)
        
