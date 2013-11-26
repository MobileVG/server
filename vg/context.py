from __future__ import unicode_literals, absolute_import

__all__ = ['Ticket', 'Context', 'need_developer']
import pyDes
import functools
from flask import request, g
from . import util
from .util import UnicodeSupport
from .errors import *
from .gv import db
from .pub import get_app, developer_exists


_deskey = pyDes.des(str('FOhR1VER'), pyDes.CBC, str('\0\0\0\0\0\0\0\0'),
                    pad=None,
                    padmode=pyDes.PAD_PKCS5)


class Ticket(UnicodeSupport):
    def __init__(self, uid, dt=None):
        self.uid = uid
        self.dt = dt or util.now()

    def __unicode__(self):
        return '%s # %s' % (self.uid, util.format_iso_datetime(self.dt))

    def __eq__(self, other):
        if other is self:
            return True
        if not isinstance(other, Ticket):
            return False
        return self.uid == other.uid and self.dt == other.dt

    def encode(self):
        s = '%s@%s' % (util.format_iso_datetime(self.dt), self.uid)
        return util.to_base64(_deskey.encrypt(str(s)))

    @staticmethod
    def decode(s):
        if s is None:
            return None

        bytes = util.parse_base64(s)
        s = unicode(_deskey.decrypt(bytes, padmode=pyDes.PAD_PKCS5))
        ss = s.split('@', 1)
        dt = util.parse_iso_time(ss[0])
        uid = ss[1]
        return Ticket(uid, dt)


class Context(object):
    def __init__(self, app, uid, uid_human, device, locale, ip,
                 app_version, accessed_at=None):
        self.app = app
        self.uid = uid
        self.uid_human = uid_human
        self.device = device
        self.locale = locale
        self.ip = ip
        self.app_version = app_version
        self.accessed_at = accessed_at or util.now()

    def is_developer(self):
        return self.uid is not None and util.is_developer_uid(self.uid)

    def is_user(self):
        return self.uid is not None and util.is_user_uid(self.uid)

    def is_login(self):
        return self.uid is not None

    def is_android(self):
        return True # TODO: impl

    def is_ios(self):
        return False # TODO: impl

    @staticmethod
    def from_request():
        if '/_dev' in request.path:
            return

        from .buy import user_exists

        headers= request.headers
        app = headers.get('X-VG-App', None)
        secret = headers.get('X-VG-Secret', None)
        t = Ticket.decode(headers.get('X-VG-Ticket', None))
        uid = t.uid if t is not None else None
        uid_human = ''
        device = headers.get('X-VG-Device', '')
        locale = '' # TODO: get
        ip = request.remote_addr
        app_version = headers.get('X-VG-AppVersion', 0)

        if not app or not secret:
            raise VGError(E_ILLEGAL_APP)

        with db.open_session() as session:
            # check app
            app1 = get_app(session, app)
            if app1.secret != secret:
                raise VGError(E_ILLEGAL_APP)

            # check uid
            if uid is not None:
                if util.is_developer_uid(uid):
                    if not developer_exists(session, uid):
                        raise VGError(E_ILLEGAL_USER)
                    if app1.owner != uid:
                        raise VGError(E_PERM)

                elif util.is_user_uid(uid) \
                    and not user_exists(session, uid):
                    raise VGError(E_ILLEGAL_USER)

                    # TODO: get uid_human

        return Context(app, uid, uid_human, device, locale, ip, app_version)


def need_developer(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        ctx = g.context
        if not ctx.is_developer():
            raise VGError(E_PERM)
        return f(*args, **kwargs)

    return decorator


def need_buyer(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        ctx = g.context
        if not (not ctx.is_login() or ctx.is_user()):
            raise VGError(E_PERM)
        return f(*args, **kwargs)

    return decorator


def need_user(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        ctx = g.context
        if not ctx.is_user():
            raise VGError(E_PERM)
        return f(*args, **kwargs)

    return decorator