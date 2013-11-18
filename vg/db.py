from __future__ import unicode_literals, absolute_import

__all__ = ['create_db']
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.types import TypeDecorator, TEXT
import json

class JSONObject(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return ''
        if type(value) is not dict:
            raise ValueError("value is not dict")
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None or value == '':
            return dict()
        else:
            return json.loads(value)

class JSONArray(TypeDecorator):
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is None:
            return ''
        if type(value) is not list or type(value) is not set:
            raise ValueError("value is not list")
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None or value == '':
            return list()
        else:
            return json.loads(value)

class DB(object):
    def __init__(self, url):
        self.engine = create_engine(url, isolation_level='READ COMMITTED')
        self._Session = sessionmaker(bind=self.engine,
                                     autocommit=False,
                                     autoflush=False,
                                     expire_on_commit=False)

    @contextmanager
    def open_session(self):
        session = self._Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()


def create_db(app):
    return DB(app.config.get('DB_URL', None))
