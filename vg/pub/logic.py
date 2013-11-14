from __future__ import unicode_literals, absolute_import

from ..models import *
import datetime
from .. import util
from ..errors import *

def gen_developer_id():
    dts = datetime.datetime.strftime(util.now(), '%y%m%d')
    return dts + util.randstr(6)

def app_exists(app_id):
    # TODO:
    pass

def developer_exists(did, with_disabled=False):
    # TODO:
    pass

def create_developer(ctx, email, pwd, name, desc=None):
    now = util.now()
    developer = Developer.create(
            id=gen_developer_id(),
            created_at=now,
            updated_at=now,
            password=pwd,
            email=email,
            name=name or '',
            desc=desc or '')
    return developer

def create_app(ctx, app_sid, name):
    # TODO:
    pass
