from __future__ import unicode_literals, absolute_import
__all__ = ['create_db']
from peewee import MySQLDatabase


class DB(MySQLDatabase):
    pass

def create_db(app):
    cfg = app.config
    db = DB(cfg.get('DB_DB', None),
            host=cfg.get('DB_HOST', None),
            port=cfg.get('DB_PORT', 3306),
            user=cfg.get('DB_USER', None),
            passwd=cfg.get('DB_PASSWD', None),
            threadlocals=False, 
            autocommit=False)
    return db