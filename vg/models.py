from __future__ import unicode_literals, absolute_import

__all__ = ['Assets', 'Developer', 'App', 'Category', 'User', 'Goods',
           'History']

import json
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, \
    SmallInteger, Text, BigInteger, Boolean, Numeric
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from .db import JSONObjectType, JSONArrayType, StringsType, MTextType
from . import util

BaseModel = declarative_base()


class JSONSupport(object):
    def to_json_obj(self, col_filter=None, **kwargs):
        raise NotImplementedError()

    def _json_col(self, col_filter, jo, col, v, **kwargs):
        if col_filter is not None:
            new_col = col_filter(self, col, **kwargs)
            if new_col is not None:
                jo[new_col] = v
        else:
            jo[col] = v


class Assets(JSONSupport):
    def __init__(self, primary_currency, second_currency, goods):
        self.primary_currency = int(primary_currency)
        self.second_currency = int(second_currency)
        self.goods = goods or dict()

    def copy(self):
        return Assets(self.primary_currency,
                      self.second_currency,
                      self.goods.copy())

    def to_json_obj(self, col_filter=None, **kwargs):
        return {
            'primary_currency': self.primary_currency,
            'second_currency': self.second_currency,
            'goods': self.goods,
        }

    def primary_currency_enough(self, v):
        return self.primary_currency >= v if v is not None else False

    def second_currency_enough(self, v):
        return self.second_currency >= v if v is not None else False

    def goods_enough(self, goods_id, n):
        c = self.get_goods_count(goods_id)
        return c >= n

    def goods_limit(self, goods_id, n, limit):
        if limit <= 0:
            return True
        c = self.get_goods_count(goods_id)
        return c + n <= limit

    def incr_primary_currency(self, v):
        if v is not None:
            self.primary_currency += v
        return self.primary_currency

    def incr_second_currency(self, v):
        if v is not None:
            self.second_currency += v
        return self.second_currency

    def get_goods_count(self, goods_id):
        return self.goods.get(goods_id, 0)

    def incr_goods(self, goods_id, count, limit):
        c = self.get_goods_count(goods_id)
        c += count
        if c < 0:
            c = 0
        if limit > 0 and c > limit:
            c = limit
        if c > 0:
            self.goods[goods_id] = c
        else:
            del self.goods[goods_id]
        return c

    def has_goods(self, good_id):
        return self.goods.get(good_id, 0) > 0

    def save_to_user(self, session, uid, with_currency=True):
        d = {'goods': self.goods}
        if with_currency:
            d['primary_currency'] = self.primary_currency
            d['second_currency'] = self.second_currency
        session.query(User)\
            .filter(User.id == uid)\
            .update(d)
        return self


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

    def to_json_obj(self, col_filter=None, **kwargs):
        jo = dict()
        self._json_col(col_filter, jo, 'id', self.id, **kwargs)
        self._json_col(col_filter, jo, 'email', self.email, **kwargs)
        self._json_col(col_filter, jo, 'password', self.password, **kwargs)
        self._json_col(col_filter, jo, 'created_at',
                       self.created_at, **kwargs)
        self._json_col(col_filter, jo, 'updated_at',
                       self.updated_at, **kwargs)
        self._json_col(col_filter, jo, 'disabled_at',
                       self.disabled_at, **kwargs)
        self._json_col(col_filter, jo, 'name', self.name, **kwargs)
        self._json_col(col_filter, jo, 'desc', self.desc, **kwargs)
        self._json_col(col_filter, jo, 'apps', self.apps, **kwargs)
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

    def to_json_obj(self, col_filter=None, **kwargs):
        jo = dict()
        self._json_col(col_filter, jo, 'id', self.id, **kwargs)
        self._json_col(col_filter, jo, 'created_at',
                       self.created_at, **kwargs)
        self._json_col(col_filter, jo, 'updated_at',
                       self.updated_at, **kwargs)
        self._json_col(col_filter, jo, 'secret',
                       self.secret, **kwargs)
        self._json_col(col_filter, jo, 'name', self.name, **kwargs)
        self._json_col(col_filter, jo, 'owner', self.owner, **kwargs)
        self._json_col(col_filter, jo, 'options', self.options, **kwargs)
        self._json_col(col_filter, jo, 'categories',
                       self.categories, **kwargs)
        return jo


class Category(BaseModel, JSONSupport):
    __tablename__ = 'category'

    app = Column(String, ForeignKey("app.id"), primary_key=True)
    id = Column(String, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    name = Column(MTextType)
    desc = Column(MTextType)

    def to_json_obj(self, col_filter=None, **kwargs):
        jo = dict()
        self._json_col(col_filter, jo, 'app', self.app, **kwargs)
        self._json_col(col_filter, jo, 'id', self.id, **kwargs)
        self._json_col(col_filter, jo, 'created_at',
                       self.created_at, **kwargs)
        self._json_col(col_filter, jo, 'updated_at',
                       self.updated_at, **kwargs)
        self._json_col(col_filter, jo, 'name', self.name, **kwargs)
        self._json_col(col_filter, jo, 'desc', self.desc, **kwargs)
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
    goods = Column(JSONObjectType)


    @hybrid_property
    def assets(self):
        return Assets(self.primary_currency,
                      self.second_currency,
                      self.goods)


    def to_json_obj(self, col_filter=None, **kwargs):
        jo = dict()
        self._json_col(col_filter, jo, 'id', self.id, **kwargs)
        self._json_col(col_filter, jo, 'app', self.app, **kwargs)
        self._json_col(col_filter, jo, 'created_at',
                       self.created_at, **kwargs)
        self._json_col(col_filter, jo, 'updated_at',
                       self.updated_at, **kwargs)
        self._json_col(col_filter, jo, 'disabled_at',
                       self.disabled_at, **kwargs)
        self._json_col(col_filter, jo, 'human', self.human, **kwargs)
        self._json_col(col_filter, jo, 'app_data', self.app_data, **kwargs)
        self._json_col(col_filter, jo, 'assets', self.assets, **kwargs)
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
    CT_PACKAGE = 5

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
    discount = Column(Numeric)
    consumable = Column(Boolean)
    limit_per_user = Column(Integer)
    app_min_version_ard = Column(Integer)
    app_max_version_ard = Column(Integer)
    app_min_version_ios = Column(Integer)
    app_max_version_ios = Column(Integer)
    content_type = Column(SmallInteger)
    content = Column(Text)

    # Dynamic properties
    sales_count = Column(BigInteger, default=0)


    # Hybrid properties

    @hybrid_property
    def discounted_primary_currency(self):
        return util.discount_currency(self.primary_currency, self.discount) \
            if self.primary_currency is not None else None

    @hybrid_property
    def discounted_second_currency(self):
        return util.discount_currency(self.second_currency, self.discount) \
            if self.second_currency is not None else None

    @hybrid_property
    def discounted_real_money(self):
        return util.discount_real_money(self.real_money, self.discount) \
            if self.real_money is not None else None

    @hybrid_property
    def subs(self):
        if self.is_package:
            return util.parse_json_dict(self.content, default={})
        else:
            return {}

    @hybrid_property
    def is_package(self):
        return self.content_type == Goods.CT_PACKAGE

    def to_json_obj(self, col_filter=None, **kwargs):
        jo = dict()
        self._json_col(col_filter, jo, 'id', self.id, **kwargs)
        self._json_col(col_filter, jo, 'app', self.app, **kwargs)
        self._json_col(col_filter, jo, 'category', self.category, **kwargs)
        self._json_col(col_filter, jo, 'version', self.version, **kwargs)
        self._json_col(col_filter, jo, 'publisher', self.publisher, **kwargs)
        self._json_col(col_filter, jo, 'created_at',
                       self.created_at, **kwargs)
        self._json_col(col_filter, jo, 'updated_at',
                       self.updated_at, **kwargs)
        self._json_col(col_filter, jo, 'disabled_at',
                       self.disabled_at, **kwargs)
        self._json_col(col_filter, jo, 'tags', self.tags, **kwargs)
        self._json_col(col_filter, jo, 'logo_url', self.logo_url, **kwargs)
        self._json_col(col_filter, jo, 'preview_urls',
                       self.preview_urls, **kwargs)
        self._json_col(col_filter, jo, 'name', self.name, **kwargs)
        self._json_col(col_filter, jo, 'desc', self.desc, **kwargs)
        self._json_col(col_filter, jo, 'publisher_info',
                       self.publisher_info, **kwargs)
        self._json_col(col_filter, jo, 'app_data', self.app_data, **kwargs)
        self._json_col(col_filter, jo, 'paid_type', self.paid_type, **kwargs)
        self._json_col(col_filter, jo, 'primary_currency',
                       self.primary_currency, **kwargs)
        self._json_col(col_filter, jo, 'second_currency',
                       self.second_currency, **kwargs)
        self._json_col(col_filter, jo, 'real_money',
                       self.real_money, **kwargs)
        self._json_col(col_filter, jo, 'discounted_primary_currency',
                       self.discounted_primary_currency, **kwargs)
        self._json_col(col_filter, jo, 'discounted_second_currency',
                       self.discounted_second_currency, **kwargs)
        self._json_col(col_filter, jo, 'discounted_real_money',
                       self.discounted_real_money, **kwargs)
        self._json_col(col_filter, jo, 'pay_info', self.pay_info)
        self._json_col(col_filter, jo, 'discount', self.discount)
        self._json_col(col_filter, jo, 'consumable', self.consumable)
        self._json_col(col_filter, jo, 'limit_per_user',
                       self.limit_per_user, **kwargs)
        self._json_col(col_filter, jo, 'app_min_version_ard',
                       self.app_min_version_ard, **kwargs)
        self._json_col(col_filter, jo, 'app_max_version_ard',
                       self.app_max_version_ard, **kwargs)
        self._json_col(col_filter, jo, 'app_min_version_ios',
                       self.app_min_version_ios, **kwargs)
        self._json_col(col_filter, jo, 'app_max_version_ios',
                       self.app_max_version_ios, **kwargs)
        self._json_col(col_filter, jo, 'content_type',
                       self.content_type, **kwargs)
        self._json_col(col_filter, jo, 'content', self.content, **kwargs)
        return jo


class History(BaseModel, JSONSupport):
    __tablename__ = 'history'

    TYPE_RECEIPT = 1
    TYPE_CONSUMPTION = 2

    CC_PRIMARY_CURRENCY = 11
    CC_SECOND_CURRENCY = 12
    CC_REAL_MONEY = 13

    id = Column(String, primary_key=True)
    app = Column(String)
    category = Column(String)
    buyer = Column(String)
    buyer_human = Column(String)
    goods = Column(String)
    parent_goods = Column(String)
    count = Column(Integer)
    created_at = Column(DateTime)
    type = Column(SmallInteger)
    app_data = Column(String)
    cost_currency_type = Column(SmallInteger)
    cost_currency = Column(BigInteger)
    cost_real_money_cs = Column(String)
    cost_real_money_amount = Column(Numeric)
    discount = Column(Integer)
    pay_channel = Column(String)
    pay_id = Column(String)
    buyer_device = Column(String)
    buyer_locale = Column(String)
    buyer_ip = Column(String)

    @hybrid_property
    def cost(self):
        cct = self.cost_currency_type
        if cct == self.CC_PRIMARY_CURRENCY or cct == self.CC_SECOND_CURRENCY:
            return unicode(self.cost_currency)
        elif cct == self.CC_REAL_MONEY:
            return '%s%s' % (
                self.cost_real_money_cs, self.cost_real_money_amount)
        else:
            return ''


    def to_json_obj(self, col_filter=None, **kwargs):
        jo = dict()
        self._json_col(col_filter, jo, 'id', self.id, **kwargs)
        self._json_col(col_filter, jo, 'app', self.app, **kwargs)
        self._json_col(col_filter, jo, 'category', self.category, **kwargs)
        self._json_col(col_filter, jo, 'buyer', self.buyer, **kwargs)
        self._json_col(col_filter, jo, 'buyer_human',
                       self.buyer_human, **kwargs)
        self._json_col(col_filter, jo, 'goods', self.goods, **kwargs)
        self._json_col(col_filter, jo, 'parent_goods',
                       self.parent_goods, **kwargs)
        self._json_col(col_filter, jo, 'count', self.count, **kwargs)
        self._json_col(col_filter, jo, 'created_at',
                       self.created_at, **kwargs)
        self._json_col(col_filter, jo, 'type',
                       self.type, **kwargs)
        self._json_col(col_filter, jo, 'app_data',
                       self.app_data, **kwargs)
        self._json_col(col_filter, jo, 'cost_currency_type',
                       self.cost_currency_type, **kwargs)
        self._json_col(col_filter, jo, 'cost', self.cost, **kwargs)
        self._json_col(col_filter, jo, 'discount',
                       self.discount, **kwargs)
        self._json_col(col_filter, jo, 'pay_channel',
                       self.pay_channel, **kwargs)
        self._json_col(col_filter, jo, 'pay_id', self.pay_id, **kwargs)
        self._json_col(col_filter, jo, 'buyer_device',
                       self.buyer_device, **kwargs)
        self._json_col(col_filter, jo, 'buyer_locale',
                       self.buyer_locale, **kwargs)
        self._json_col(col_filter, jo, 'buyer_ip', self.buyer_ip, **kwargs)
        return jo


