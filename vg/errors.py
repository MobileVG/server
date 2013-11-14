from __future__ import unicode_literals, absolute_import

E_OK = 0
E_PERM = 550
E_UNKNOWN = 599

class VGError(StandardError):
    def __init__(self, code, msg=''):
        self.code = code
        self.msg = msg