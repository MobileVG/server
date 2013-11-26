from __future__ import unicode_literals, absolute_import

from voluptuous import *
from . import util as _util


class ArgsSchema(Schema):
    def __init__(self, args_schema):
        super(ArgsSchema, self).__init__(args_schema, extra=True)

    def validate_request_args(self, includes=None, excludes=None):
        return self(_util.request_args_as_dict(includes=includes,
                                               excludes=excludes))


def AsInt(msg=None):
    def f(v):
        return int(v)
    return Coerce(f, msg=msg)


def AsBool(msg=None):
    def f(v):
        if isinstance(v, basestring):
            v = v.lower()
            if v in ('1', 'true', 'yes', 'on', 'enable', 't', 'y'):
                return True
            if v in ('0', 'false', 'no', 'off', 'disable', 'f', 'n'):
                return False
        raise ValueError("Illegal bool string")
    return Coerce(f, msg=msg)


def AsList(subtype=None, sep=None, msg=None):
    def f(v):
        l = _util.parse_strings(v, sep=sep or ',')
        return [subtype(x) if subtype is not None else x for x in l]
    return Coerce(f, msg=msg)


def AsJsonObj(msg=None):
    def f(v):
        if isinstance(v, basestring):
            jo = _util.parse_json_dict(v, default=None)
            if isinstance(jo, dict):
                return jo
        raise ValueError("Illegal json object")
    return Coerce(f, msg=msg)


def AsPaging(msg=None):
    def f(v):
        return _util.Paging.parse(v)
    return Coerce(f, msg=msg)


def NoValid():
    return lambda v: v
