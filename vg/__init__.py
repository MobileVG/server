from __future__ import unicode_literals, absolute_import
__all__ = ['app', 'db', 'start_server']


from .gv import app, db


def start_server():
    wsgi = app.config.get('WSGI', 'gevent')
    host = app.config.get('SERVER_HOST', '')
    port = app.config.get('SERVER_PORT', 7373)
    if wsgi == 'flask':
        app.run(host=host, port=port)
    elif wsgi == 'gevent':
        print("TODO: gevent run")
