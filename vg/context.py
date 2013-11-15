from __future__ import unicode_literals, absolute_import

__all__ = ['Ticket', 'Context', 'need_developer']
import pyDes
import functools
from flask import request, g
from . import util
from .util import UnicodeSupport
from .errors import *

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
        ss = s.split('@')
        dt = util.parse_iso_time(ss[0])
        uid = ss[1]
        return Ticket(uid, dt)


class Context(object):
    def __init__(self, uid, accessed_at=None):
        self.uid = uid
        self.accessed_at = accessed_at or util.now()

    def is_developer(self):
        return self.uid is not None and util.is_developer_uid(self.uid)

    def is_user(self):
        return self.uid is not None and util.is_user_uid(self.uid)

    def is_login(self):
        return self.uid is not None

    @staticmethod
    def from_request():
        try:
            t = Ticket.decode(request.headers.get('X-VG-Ticket', None))
            # TODO: check uid exists
            return Context(t.uid if t is not None else None)
        except:
            return Context(None)


def need_developer(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        ctx = g.context
        if not ctx.is_developer():
            raise VGError(E_PERM)
        return f(*args, **kwargs)
    return decorator