from __future__ import unicode_literals
__all__ = ['Developer']
from peewee import Model, CharField, \
        DateTimeField, ForeignKeyField, IntegerField
from .gv import db
from . import util


class JSONSupport(object):
    def to_json_obj(self, fields=None):
        raise NotImplementedError()

    @staticmethod
    def _jsonfield(fields, jobj, field, v):
        if fields is None:
            jobj[field] = v
        else:
            if field in fields:
                jobj[field] = v


class Developer(Model, JSONSupport):
    class Meta:
        database = db
        db_table = 'developer'

    id = CharField(max_length=100, primary_key=True)
    email = CharField(max_length=100, unique=True)
    password = CharField(max_length=100)
    created_at = DateTimeField()
    updated_at = DateTimeField()
    disabled_at = DateTimeField(null=True)
    type_ = IntegerField(db_field='type')
    name = CharField(max_length=100, default='')
    desc = CharField(max_length=1000, default='')

    def to_json_obj(self, fields=None):
        jobj = dict()
        self._jsonfield(fields, jobj, 'id', self.id)
        self._jsonfield(fields, jobj, 'email', self.email)
        self._jsonfield(fields, jobj, 'password', self.password)
        self._jsonfield(fields, jobj, 'created_at', self.created_at)
        self._jsonfield(fields, jobj, 'updated_at', self.updated_at)
        self._jsonfield(fields, jobj, 'disabled_at', self.disabled_at)
        self._jsonfield(fields, jobj, 'type', self.type_)
        self._jsonfield(fields, jobj, 'name', self.name)
        self._jsonfield(fields, jobj, 'desc', self.desc)
        return jobj


class App(Model, JSONSupport):
    class Meta:
        database = db
        db_table = 'app'

    id = CharField(max_length=100, primary_key=True)
    secret = CharField(max_length=100)
    created_at = DateTimeField()
    updated_at = DateTimeField()
    name = CharField(max_length=100)
    owner = ForeignKeyField(Developer)


class User(Model, JSONSupport):
    class Meta:
        database = db
        db_table = 'user'

    id = CharField(max_length=100, primary_key=True)


class Assets(Model, JSONSupport):
    class Meta:
        database = db
        db_table = 'assets'

    # TODO: 

class Goods(Model, JSONSupport):
    class Meta:
        database = db
        db_table = 'goods'

    id = CharField(max_length=100, primary_key=True)


class BuyHistory(Model, JSONSupport):
    class Meta:
        database = db
        db_table = 'buy_history'

    id = CharField(max_length=100, primary_key=True)