from __future__ import unicode_literals

__all__ = ['Developer', 'App']

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger

BaseModel = declarative_base()


class JSONSupport(object):
    def to_json_obj(self, includes=None, excludes=None):
        raise NotImplementedError()

    @staticmethod
    def _jsonfield(includes, excludes, jobj, field, v):
        if excludes is not None:
            if field in excludes:
                return
        if includes is not None:
            if field not in includes:
                return
        jobj[field] = v


class Developer(BaseModel, JSONSupport):
    __tablename__ = 'developer'

    id = Column(String(100), primary_key=True)
    email = Column(String(100), unique=True)
    password = Column(String(100))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    disabled_at = Column(DateTime)
    name = Column(String(100))
    desc = Column(String(100))
    apps = relationship("App")

    def to_json_obj(self, includes=None, excludes=None):
        jo = dict()
        self._jsonfield(includes, excludes, jo, 'id', self.id)
        self._jsonfield(includes, excludes, jo, 'email', self.email)
        self._jsonfield(includes, excludes, jo, 'password', self.password)
        self._jsonfield(includes, excludes, jo, 'created_at',
                        self.created_at)
        self._jsonfield(includes, excludes, jo, 'updated_at',
                        self.updated_at)
        self._jsonfield(includes, excludes, jo, 'disabled_at',
                        self.disabled_at)
        self._jsonfield(includes, excludes, jo, 'name', self.name)
        self._jsonfield(includes, excludes, jo, 'desc', self.desc)
        self._jsonfield(includes, excludes, jo, 'apps', self.apps)
        return jo


class App(BaseModel, JSONSupport):
    __tablename__ = 'app'

    id = Column(String, primary_key=True)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    secret = Column(String(100))
    name = Column(String(100))
    owner = Column(String(100), ForeignKey('developer.id'))

    def to_json_obj(self, includes=None, excludes=None):
        jo = dict()
        self._jsonfield(includes, excludes, jo, 'id', self.id)
        self._jsonfield(includes, excludes, jo, 'created_at',
                        self.created_at)
        self._jsonfield(includes, excludes, jo, 'updated_at',
                        self.updated_at)
        self._jsonfield(includes, excludes, jo, 'secret',
                        self.secret)
        self._jsonfield(includes, excludes, jo, 'name', self.name)
        self._jsonfield(includes, excludes, jo, 'owner', self.owner)
        return jo


