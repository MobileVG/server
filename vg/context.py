from __future__ import unicode_literals, absolute_import

from flask import request

class Context(object):
    def __init__(self, uid=None, did=None):
        self.uid = uid
        self.did = did

    def is_developer(self):
        # TODO
        return True

    def is_user(self):
        # TODO
        return True

    @staticmethod
    def create_with_request():
        # TODO
        return Context()