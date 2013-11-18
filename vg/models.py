from __future__ import unicode_literals, absolute_import

__all__ = ['Developer', 'App', 'Category', 'User']

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, \
        SmallInteger, Text, BigInteger
from .db import JSONObject, JSONArray

BaseModel = declarative_base()


class JSONSupport(object):
    def to_json_obj(self, col_filter=None):
        raise NotImplementedError()

    def _json_col(self, col_filter, jo, col, v):
        if col_filter is not None:
            if col_filter(self, col):
                jo[col] = v
        else:
            jo[col] = v


class Developer(BaseModel, JSONSupport):
    __tablename__ = 'developer'

    id = Column(String, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    disabled_at = Column(DateTime)
    name = Column(String)
    desc = Column(String)
    apps = relationship("App")

    def to_json_obj(self, col_filter):
        jo = dict()
        self._json_col(col_filter, jo, 'id', self.id)
        self._json_col(col_filter, jo, 'email', self.email)
        self._json_col(col_filter, jo, 'password', self.password)
        self._json_col(col_filter, jo, 'created_at',
                       self.created_at)
        self._json_col(col_filter, jo, 'updated_at',
                       self.updated_at)
        self._json_col(col_filter, jo, 'disabled_at',
                       self.disabled_at)
        self._json_col(col_filter, jo, 'name', self.name)
        self._json_col(col_filter, jo, 'desc', self.desc)
        self._json_col(col_filter, jo, 'apps', self.apps)
        return jo


class App(BaseModel, JSONSupport):
    __tablename__ = 'app'

    id = Column(String, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    secret = Column(String)
    name = Column(String)
    owner = Column(String, ForeignKey('developer.id'))
    categories = relationship('Category')
    options = Column(JSONObject)

    def to_json_obj(self, col_filter=None):
        jo = dict()
        self._json_col(col_filter, jo, 'id', self.id)
        self._json_col(col_filter, jo, 'created_at',
                       self.created_at)
        self._json_col(col_filter, jo, 'updated_at',
                       self.updated_at)
        self._json_col(col_filter, jo, 'secret',
                       self.secret)
        self._json_col(col_filter, jo, 'name', self.name)
        self._json_col(col_filter, jo, 'owner', self.owner)
        self._json_col(col_filter, jo, 'options', self.options)
        self._json_col(col_filter, jo, 'categories', self.categories)
        return jo

class Category(BaseModel, JSONSupport):
    __tablename__ = 'category'

    app = Column(String, ForeignKey("app.id"), primary_key=True)
    id = Column(String, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    name = Column(JSONObject)
    desc = Column(JSONObject)

    def to_json_obj(self, col_filter=None):
        jo = dict()
        self._json_col(col_filter, jo, 'app', self.app)
        self._json_col(col_filter, jo, 'id', self.id)
        self._json_col(col_filter, jo, 'created_at',
                       self.created_at)
        self._json_col(col_filter, jo, 'updated_at',
                       self.updated_at)
        self._json_col(col_filter, jo, 'name', self.name)
        self._json_col(col_filter, jo, 'desc', self.desc)
        return jo


class User(BaseModel, JSONSupport):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    app = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    disabled_at = Column(DateTime)
    human = Column(String)
    app_data = Column(JSONObject)
    primary_currency = Column(BigInteger)
    second_currency = Column(BigInteger)
    assets = Column(JSONObject)

    def to_json_obj(self, col_filter=None):
        jo = dict()
        self._json_col(col_filter, jo, 'id', self.id)
        self._json_col(col_filter, jo, 'app', self.app)
        self._json_col(col_filter, jo, 'created_at', self.created_at)
        self._json_col(col_filter, jo, 'updated_at', self.updated_at)
        self._json_col(col_filter, jo, 'disabled_at', self.disabled_at)
        self._json_col(col_filter, jo, 'human', self.human)
        self._json_col(col_filter, jo, 'app_data', self.app_data)
        self._json_col(col_filter, jo, 'primary_currency', self.primary_currency)
        self._json_col(col_filter, jo, 'second_currency', self.second_currency)
        self._json_col(col_filter, jo, 'assets', self.assets)
        return jo



