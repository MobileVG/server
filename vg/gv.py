from __future__ import unicode_literals, absolute_import

import os
from flask import Flask, g
from .db import create_db

ROOT = os.getenv('VG_ROOT')
ENV = os.getenv('VG_ENV', 'debug')

# app
app = Flask('vg', instance_path=ROOT, instance_relative_config=True)
app.config.from_pyfile('config/%s.cfg' % ENV, silent=True)

# db
db = create_db(app)

# mods
from .buy import api_mod as buy_api_mod
from .pub import api_mod as pub_api_mod
from .pub import pages_mod as pub_pages_mod

app.register_blueprint(buy_api_mod, url_prefix='/api/1')
app.register_blueprint(pub_api_mod, url_prefix='/api/1')
app.register_blueprint(pub_pages_mod)


from .context import Context


@app.before_request
def before_request():
    g.context = Context.from_request()

from .errors import VGError
@app.errorhandler(VGError)
def on_error(e):
    raise e
    #return {'code': e.code, 'error_msg': e.msg}