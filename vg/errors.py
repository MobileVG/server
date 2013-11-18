from __future__ import unicode_literals, absolute_import

E_OK = 0
E_ILLEGAL_APP = 551
E_ILLEGAL_USER = 552
E_ILLEGAL_ID = 554

E_PERM = 560

E_UNKNOWN = 599

class VGError(StandardError):
    def __init__(self, code, msg=''):
        self.code = code
        self.msg = msg