# -*- coding: utf-8 -*-
from factory import clients
import var_utils
import json

def loans():
    return dict()



@cache.action(time_expire=5, cache_model=cache.ram, prefix='lends', quick='VLP') # vars, lang and public
def lend_bids():
    currency = 'USD'
    service = 'Bitfinex'
    if not service or not currency:
        redirect(URL('index'))
    bf = clients[service]()
    lend_bids =  var_utils.compact_lends_book(bf.lend_bids(currency))
    # https://stackoverflow.com/questions/5906831/serializing-a-python-namedtuple-to-json
    lend_bids = list(map(lambda lb: lb.to_dict(), lend_bids))
    lend_bids =  json.dumps(lend_bids)
    return dict(lend_bids = XML(lend_bids))

def lend_book():
    currency = request.vars.currency
    service = request.vars.service
    if not service or not currency:
        redirect(URL('index'))
    bf = clients[service]()
    lend_book =  var_utils.compact_lends_book(bf.lend_bids(currency))
    return dict(lend_book = lend_book)

def lend_book_basic():
    currency = request.vars.currency
    service = request.vars.service
    if not service or not currency:
        redirect(URL('index'))
    bf = clients[service]()
    lend_book =  var_utils.compact_lends_book(bf.lend_bids(currency))
    return dict(lend_book = lend_book)

@cache.action(time_expire=5, cache_model=cache.ram, prefix='lends', quick='VLP') # vars, lang and public
def lend_matches():
    currency = request.vars.currency
    service = request.vars.service
    if not service or not currency:
        redirect(URL('index'))
    bf = clients[service]()
    lend_matches = bf.lend_matches(currency)
    return dict(lend_matches = lend_matches)
