# -*- coding: utf-8 -*-
from factory import clients
from collections import defaultdict
import var_utils
import json

def loans():
    return dict()



@cache.action(time_expire=10, cache_model=cache.ram, prefix='lends', quick='VLP') # vars, lang and public
def lend_bids():
    currencies = ['USD', 'BTC', 'ETH', 'LTC']
    service = 'Bitfinex'
    if not service or not currencies:
        redirect(URL('index'))
    bf = clients[service]()
    filtered_bids = []
    for currency in currencies:
        lend_bids =  var_utils.compact_lends_book(bf.lend_bids(currency))
        #get highest rate for each period. adapted from https://stackoverflow.com/questions/3749512/python-group-by
        grouped_by_period = defaultdict(list)
        for lb in lend_bids: grouped_by_period[lb.period].append(lb)
        lend_bids = [v[0] for k,v in grouped_by_period.items()]
        # convert to dict https://stackoverflow.com/questions/5906831/serializing-a-python-namedtuple-to-json
        lend_bids = list(map(lambda lb: lb.to_dict(), lend_bids))
        for lb in lend_bids: lb['currency'] = currency
        #lend_bids = list(map(lambda lb: lb['currency'] = currency, lend_bids))
        #append to the overall list
        filtered_bids.extend(lend_bids)
    filtered_bids =  json.dumps(filtered_bids)
    return dict(lend_bids = XML(filtered_bids))

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
