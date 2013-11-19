from __future__ import unicode_literals, absolute_import

__all__ = ['Developer', 'App', 'Category',
           'User', 'Goods']

import json
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, \
    SmallInteger, Text, BigInteger, Boolean
from .db import JSONObjectType, JSONArrayType, StringsType, MTextType

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
    options = Column(JSONObjectType)

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
    name = Column(MTextType)
    desc = Column(MTextType)

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
    app_data = Column(JSONObjectType)
    primary_currency = Column(BigInteger)
    second_currency = Column(BigInteger)
    assets = Column(JSONObjectType)

    def to_json_obj(self, col_filter=None):
        jo = dict()
        self._json_col(col_filter, jo, 'id', self.id)
        self._json_col(col_filter, jo, 'app', self.app)
        self._json_col(col_filter, jo, 'created_at', self.created_at)
        self._json_col(col_filter, jo, 'updated_at', self.updated_at)
        self._json_col(col_filter, jo, 'disabled_at', self.disabled_at)
        self._json_col(col_filter, jo, 'human', self.human)
        self._json_col(col_filter, jo, 'app_data', self.app_data)
        self._json_col(col_filter, jo, 'primary_currency',
                       self.primary_currency)
        self._json_col(col_filter, jo, 'second_currency',
                       self.second_currency)
        self._json_col(col_filter, jo, 'assets', self.assets)
        return jo


class Goods(BaseModel, JSONSupport):
    __tablename__ = 'goods'


    PT_FREE = 0
    PT_PAID = 1
    PT_ANON_FREE = 2

    CT_NONE = 0
    CT_URL = 1
    CT_TEXT = 2
    CT_CONCURRENCY = 4

    # Static properties
    id = Column(String, primary_key=True)
    app = Column(String)
    category = Column(String)
    publisher = Column(String)
    version = Column(BigInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    disabled_at = Column(DateTime, default=None)
    tags = Column(StringsType, default=[])
    logo_url = Column(String, default='')
    preview_urls = Column(JSONArrayType, default=[])
    name = Column(MTextType)
    desc = Column(MTextType)
    publisher_info = Column(JSONObjectType)
    app_data = Column(JSONObjectType)
    paid_type = Column(SmallInteger)
    primary_currency = Column(BigInteger)
    second_currency = Column(BigInteger)
    real_money = Column(MTextType)
    pay_info = Column(JSONObjectType)
    discount = Column(JSONObjectType)
    consumable = Column(Boolean)
    limit_per_user = Column(Integer)
    app_min_version_ard = Column(Integer)
    app_max_version_ard = Column(Integer)
    app_min_version_ios = Column(Integer)
    app_max_version_ios = Column(Integer)
    content_type = Column(SmallInteger)
    content = Column(Text)
    subs = Column(StringsType)

    # Dynamic properties
    sales_count = Column(BigInteger, default=0)

    def to_json_obj(self, col_filter=None):
        jo = dict()
        self._json_col(col_filter, jo, 'id', self.id)
        self._json_col(col_filter, jo, 'app', self.app)
        self._json_col(col_filter, jo, 'category', self.category)
        self._json_col(col_filter, jo, 'version', self.version)
        self._json_col(col_filter, jo, 'publisher', self.publisher)
        self._json_col(col_filter, jo, 'created_at', self.created_at)
        self._json_col(col_filter, jo, 'updated_at', self.updated_at)
        self._json_col(col_filter, jo, 'disabled_at', self.disabled_at)
        self._json_col(col_filter, jo, 'tags', self.tags)
        self._json_col(col_filter, jo, 'logo_url', self.logo_url)
        self._json_col(col_filter, jo, 'preview_urls', self.preview_urls)
        self._json_col(col_filter, jo, 'name', self.name)
        self._json_col(col_filter, jo, 'desc', self.desc)
        self._json_col(col_filter, jo, 'publisher_info', self.publisher_info)
        self._json_col(col_filter, jo, 'app_data', self.app_data)
        self._json_col(col_filter, jo, 'paid_type', self.paid_type)
        self._json_col(col_filter, jo, 'primary_currency', self.primary_currency)
        self._json_col(col_filter, jo, 'second_currency', self.second_currency)
        self._json_col(col_filter, jo, 'real_money', self.real_money)
        self._json_col(col_filter, jo, 'pay_info', self.pay_info)
        self._json_col(col_filter, jo, 'discount', self.discount)
        self._json_col(col_filter, jo, 'consumable', self.consumable)
        self._json_col(col_filter, jo, 'limit_per_user', self.limit_per_user)
        # TODO: app_versions
        self._json_col(col_filter, jo, 'content_type', self.content_type)
        self._json_col(col_filter, jo, 'content', self.content)
        self._json_col(col_filter, jo, 'subs', self.subs)
        return jo





