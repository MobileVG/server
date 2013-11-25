from __future__ import unicode_literals, absolute_import

import string
import datetime
from dateutil import tz
import rstr
import json
import functools
from flask import request
from werkzeug.wrappers import Response
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

def epoch_millis(dt=None):
    if dt is None:
        dt = now()
    return int(round(float(dt.strftime('%s.%f')),3)*1000)

# random
_RSTRSET = '%s%s%s' % (string.ascii_lowercase,
                       string.ascii_uppercase, string.digits)


def randstr(len):
    return rstr.rstr(_RSTRSET, len)

# Multiple lang text

class MText(UnicodeSupport):
    def __init__(self, o, **kwargs):
        self.texts = dict()
        if o is None:
            self.default = ''
        elif isinstance(o, basestring):
            self.default = u_(o)
        elif isinstance(o, dict):
            for k, v in o.items():
                self[k] = v
        else:
            raise ValueError()

        for k, v in kwargs.items():
            self[k] = v


    def __unicode__(self):
        return u_(to_json(self.texts, human=False))

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, MText):
            return False
        return self.texts == other.texts

    def to_json_obj(self, col_filter=None):
        return self.texts

    @property
    def default(self):
        return self.texts.get('def', '')

    @default.setter
    def default(self, x):
        if not isinstance(x, basestring):
            raise ValueError("Illegal default value for mlang")
        self.texts['def'] = u_(x)

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __getitem__(self, item):
        return self.texts[item] if item in self.texts else self.default

    def __setitem__(self, key, value):
        self.texts[u_(key)] = u_(value)


# JSON

def parse_json(s):
    return json.loads(s)


def parse_json_dict(s, default=None):
    return json.loads(s) if s is not None and s != '' else default


def to_json_obj(obj, col_filter=None):
    if isinstance(obj, datetime.datetime):
        return format_iso_datetime(obj)
    elif hasattr(obj, 'to_json_obj'):
        return to_json_obj(
            obj.to_json_obj(col_filter=col_filter), col_filter=col_filter)
    elif type(obj) is dict:
        return {k: to_json_obj(v, col_filter=col_filter) \
                for k, v in obj.items()}
    elif type(obj) is list or type(obj) is set \
        or type(obj) is InstrumentedList:
        return [to_json_obj(v, col_filter=col_filter) \
                for v in obj]
    else:
        return obj


def to_json(v, col_filter=None, human=True):
    indent = True if human else None
    v1 = to_json_obj(v, col_filter=col_filter)
    return u_(json.dumps(v1, indent=indent))


class ColumnFor(object):
    def __init__(self, cls, includes=None, excludes=None):
        self.cls = cls
        self.includes = includes
        self.excludes = excludes


class ColumnFilter(object):
    def __init__(self, parent, *cfs):
        self.parent = parent
        self.cls_for = dict()
        for cf in cfs:
            self.cls_for[cf.cls] = cf

    def __call__(self, obj, col):
        cf = self.cls_for.get(type(obj))
        if cf is None:
            if self.parent is not None:
                return self.parent(obj, col)
            else:
                return True

        if cf.excludes is not None:
            if col in cf.excludes:
                return False
        if cf.includes is not None:
            if col not in cf.includes:
                return False
        return True

    def special(self, *cfs):
        return ColumnFilter(self, *cfs)

# list
def as_list(v):
    if isinstance(v, InstrumentedList):
        return [x for x in v]
    elif type(v) is list:
        return v
    elif type(v) is set:
        return list(v)
    else:
        return [v]


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
        return Response(to_json(ro, human=True),\
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

# parse
def parse_int(s, default=None):
    return int(s) if s else default

def parse_bool(s, default=None):
    if (s is None):
        return default
    s = u_(s).upper()
    if s in ['1', 'T', 'TRUE', 'YES', 'Y']:
        return True
    elif s in ['0', 'F', 'FALSE', 'NO', 'N']:
        return False
    else:
        raise ValueError()

def parse_float(s, default=None):
    return float(s) if s else default

def parse_strings(s, default=','):
    return s.split(',') if s else []

def parse_paging(s, default_count_per_page=20, max_count_per_page=100):
    ss = parse_strings(s, ',')
    if len(ss) == 0:
        t = [1, default_count_per_page]
    elif len(ss) == 1:
        t = [parse_int(ss[0], 1), default_count_per_page]
    else:
        t = [parse_int(ss[0], 1), parse_int(ss[1], default_count_per_page)]

    if t[0] < 1:
        t[0] = 1
    if t[1] > max_count_per_page:
        t[1] = max_count_per_page

    return (t[0], t[1])


# request args to dict
def request_args_as_dict(*keys):
    args = request.args
    d = dict()
    for key in keys:
        if key in args:
            v = args.get(key, None)
            if v is not None:
                d[key] = v
    return d

# currency
def parse_real_money(s, default=None):
    # return (cs, amount)
    if s:
        cs = s[0:3]
        amount = float(s[3:])
        return (cs, amount)
    else:
        return default


def discount_currency(c, d):
    if d <= 0.0:
        return 0
    elif d == 1.0:
        return long(c)
    else:
        return long(round(c * d))

def discount_real_money(real_money, d):
    def discount_tuple(t):
        if d <= 0.0:
            return (t[0], 0.0)
        else:
            return (t[0], d * t[1])

    def discount_str(rms):
        discounted = []
        for rms0 in parse_strings(rms, ','):
            rms0 = rms0.strip()
            if rms0:
                rm = parse_real_money(rms, default=('', float(1)))
                rm = discount_tuple(rm)
                discounted.append('%s%s' % rm)
        return ','.join(discounted)

    real_money = u_(real_money)
    if isinstance(real_money, unicode):
        return discount_str(real_money)
    elif type(real_money) is list or type(real_money) is set:
        return [discount_real_money(x, d) for x in real_money]
    elif type(real_money) is dict:
        return {k:discount_real_money(v, d) for k, v in real_money.items()}
    elif isinstance(real_money, MText):
        return discount_real_money(real_money.texts, d)
    else:
        raise ValueError()

# dict
def dict_modify_value(d, k, f):
    v = d.get(k, None)
    d[k] = f(v)
    return d

# Ref
class Ref(object):
    def __init__(self, v = None):
        self.v = v

