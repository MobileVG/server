from __future__ import unicode_literals, absolute_import
__all__ = ['create_db']
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

class DB(object):
    def __init__(self, url):
        self.engine = create_engine(url)
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
