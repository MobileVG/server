from __future__ import unicode_literals, absolute_import

E_OK = 0
E_ILLEGAL_ARG = 550
E_ILLEGAL_APP = 551
E_ILLEGAL_USER = 552
E_ILLEGAL_CATEGORY = 553
E_ILLEGAL_GOODS = 554
E_ILLEGAL_COST_TYPE = 559
E_ILLEGAL_PAID_TYPE = 560

E_TOO_MANY_GOODS = 561
E_CURRENCY_NOT_ENOUGH = 562


E_PERM = 570

E_UNKNOWN = 599

class VGError(StandardError):
    def __init__(self, code, msg=''):
        self.code = code
        self.msg = msg