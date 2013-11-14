from __future__ import unicode_literals, absolute_import
from flask import Blueprint

mod = Blueprint('BuyAPIs', __name__)
from .logic import *

@mod.route('/test')
def f1():
    return 'hello2'

