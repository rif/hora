# -*- coding: utf-8 -*-
from factory import clients
from collections import defaultdict
import var_utils
import json

def loans():
    return dict()



# define call in the format /market/lends.json/bids/bitfinex/usd,btc
@cache.action(time_expire=10, cache_model=cache.ram, prefix='lends', quick='VLP') # vars, lang and public
def lends():
    bids_or_asks = request.args[0]
    service = request.args[1].title()
    currencies = request.args[2].split('.') #['USD', 'BTC', 'ETH', 'LTC']
    #TODO: add better param checks with useful feedback
    if not service or not currencies:
        redirect(URL('index'))
    provider = clients[service]()
    filtered_lends = []
    for currency in currencies:
        lends = getattr(provider, 'lend_' + bids_or_asks)(currency)
        lends =  var_utils.compact_lends_book(lends)
        # if checking multiple currencies, flatten further, and only get highest rate for each period.
        # adapted from https://stackoverflow.com/questions/3749512/python-group-by
        if len(currencies) > 1:
            grouped_by_period = defaultdict(list)
            for lb in lends: grouped_by_period[lb.period].append(lb)
            lends = [v[0] for k,v in grouped_by_period.items()]
        # convert to dict https://stackoverflow.com/questions/5906831/serializing-a-python-namedtuple-to-json
        lends = list(map(lambda lb: lb.to_dict(), lends))
        for lb in lends: lb['currency'] = currency
        #append to the overall list
        filtered_lends.extend(lends)
    filtered_lends =  json.dumps(filtered_lends)
    return dict(lends = XML(filtered_lends))

def lend_book():
    currency = request.vars.currency
    service = request.vars.service
    if not service or not currency:
        redirect(URL('index'))
    provider = clients[service]()
    lend_book =  var_utils.compact_lends_book(provider.lend_bids(currency))
    return dict(lend_book = lend_book)

def lend_book_basic():
    currency = request.vars.currency
    service = request.vars.service
    if not service or not currency:
        redirect(URL('index'))
    provider = clients[service]()
    lend_book =  var_utils.compact_lends_book(provider.lend_bids(currency))
    return dict(lend_book = lend_book)

@cache.action(time_expire=5, cache_model=cache.ram, prefix='lends', quick='VLP') # vars, lang and public
def lend_matches():
    currency = request.vars.currency
    service = request.vars.service
    if not service or not currency:
        redirect(URL('index'))
    provider = clients[service]()
    lend_matches = provider.lend_matches(currency)
    return dict(lend_matches = lend_matches)
