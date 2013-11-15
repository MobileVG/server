from __future__ import unicode_literals, absolute_import

import string
import datetime
from dateutil import tz
import rstr
import json
import functools
from flask import Response
from sqlalchemy.orm.collections import InstrumentedList
import base64
from .errors import VGError, E_UNKNOWN


# unicode
def u_(x, force_to_unicode=False):
    if isinstance(x, str):
        return x.decode('utf-8')
    elif isinstance(x, unicode):
        return x
    elif type(x) is dict:
        d = dict()
        for k, v in x.items():
            d[u_(k)] = u_(v)
        return d
    elif type(x) is list:
        return [u_(e) for e in x]
    elif type(x) is set:
        return set([u_(e) for e in x])
    else:
        return unicode(x) if force_to_unicode else x


class UnicodeSupport(object):
    def __str__(self):
        return unicode(self).encode('utf-8')

# datetime

def now(utc=True):
    if utc:
        return datetime.datetime.utcnow().replace(tzinfo=tz.tzutc())
    else:
        return datetime.datetime.now().replace(tzinfo=tz.tzlocal())


def format_iso_datetime(dt):
    dt1 = dt
    if dt1.tzinfo:
        dt1 = dt1.astimezone(tz.tzutc())
    return datetime.datetime.strftime(dt1, '%Y-%m-%dT%H:%M:%S.%fZ')


def parse_iso_time(s, utc=True):
    dt = datetime.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%fZ')
    if utc:
        return dt.replace(tzinfo=tz.tzutc())
    else:
        return dt.replace(tzinfo=tz.tzlocal())

# random
_RSTRSET = '%s%s%s' % (string.ascii_lowercase,
                       string.ascii_uppercase, string.digits)


def randstr(len):
    return rstr.rstr(_RSTRSET, len)

# Multiple lang text
def mtext(s):
    if s is None:
        return {'def': ''}
    elif isinstance(s, basestring):
        return {'def': u_(s)}
    elif type(s) is dict:
        return s
    else:
        raise ValueError()

# JSON

def parse_json(s):
    return json.loads(s)


def to_json_obj(obj, includes=None, excludes=None):
    if isinstance(obj, datetime.datetime):
        return format_iso_datetime(obj)
    elif hasattr(obj, 'to_json_obj'):
        return to_json_obj(
            obj.to_json_obj(includes=includes, excludes=excludes),
            includes=includes, excludes=excludes)
    elif type(obj) is dict:
        return {k: to_json_obj(v, includes=includes, excludes=excludes) \
                for k, v in obj.items()}
    elif type(obj) is list or type(obj) is set \
        or type(obj) is InstrumentedList:
        return [to_json_obj(v, includes=includes, excludes=excludes) \
                for v in obj]
    else:
        return obj


def to_json(v, includes=None, excludes=None, human=True):
    indent = True if human else None
    v1 = to_json_obj(v, includes=includes, excludes=excludes)
    return u_(json.dumps(v1, indent=indent))


# list
def as_list(v):
    return v if isinstance(v, list) else [v]


def list_get(l, idx, default=None):
    return l[idx] if len(l) > idx else default


# JSON api
def json_api(f):
    JSON_CONTENT_TYPE = 'application/json; charset=utf-8'

    @functools.wraps(f)
    def decorator(*args, **kwargs):
        try:
            r = f(*args, **kwargs)
            if isinstance(r, Response):
                return r
            ro = {'code': 0, 'data': r}
        except VGError as e:
            ro = {'code': e.code, 'error_msg': e.msg}
            #except:
        #    ro = {'code':E_UNKNOWN, 'error_msg':'Unknown error'}
        return Response(to_json(ro, human=True), \
                        content_type=JSON_CONTENT_TYPE)

    return decorator

# Base64
def to_base64(bytes):
    return u_(base64.urlsafe_b64encode(bytes))


def parse_base64(s):
    return base64.urlsafe_b64decode(str(s))


# UID
def gen_uid(is_developer):
    fmt = 'd%y%m%d' if is_developer else 'u%y%m%d'
    dts = datetime.datetime.strftime(now(), fmt)
    return dts + randstr(6)


def is_developer_uid(uid):
    return uid.startswith('d')


def is_user_uid(uid):
    return uid.startswith('u')


