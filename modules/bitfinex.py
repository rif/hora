import hmac
import hashlib
import time
import json
import requests
import base64
from threading import Lock
from lend_rate import LendRate
from gluon import current
from pydash import py_

mutex = Lock()

class Bitfinex(object):
    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret
        self.url = 'https://api.bitfinex.com/v1/'
        self._nonce = 0
        self._fee = 0.15
        self._rate_type = 'apr'
        self._min_lend_amount = 50.0
        self._min_lend_base = 'usd'

    def _get_nonce(self):
            self._nonce += 1
            #self._nonce = max(int(time.time()*1000000000), self._nonce)
            self._nonce = max(int(time.time()*1000), self._nonce)
            return self._nonce


    def _get(self, api, *args):
        params = "/" + "/".join(args) if args else ''
        r = requests.get(self.url + api + params)
        if r.status_code != 200:
            current.logger.error('API call failed with status code:{0!s} and message:{1!r}'.format(r.status_code, r.json))
        return r.json() if r.status_code == 200 else r.status_code

    def _post(self, api, **kwargs):
        mutex.acquire()
        try:
            data = {
                'request': '/v1/' + api,
                'nonce': str(self._get_nonce())*10
            }
            data.update(kwargs)
            payload =json.dumps(data)

            body = base64.b64encode(payload)

            headers = {
                'X-BFX-APIKEY': self.key,
                'X-BFX-PAYLOAD': body,
                'X-BFX-SIGNATURE': hmac.new(
                    self.secret.encode(),
                    msg = body.encode(),
                    digestmod = hashlib.sha384
                ).hexdigest()
            }

            r = requests.post(self.url + api, headers=headers, data=body)
            if r.status_code != 200:
                current.logger.error('API call failed with status code:{0!s} and message:{1!r}'.format(r.status_code, r.json))
            return r.json()
        finally:
            mutex.release()


    def lend_demand(self, currency, bids_asks):
        current.logger.debug('Getting {0} lend demand on Bitfinex...'.format(currency))
        lb_json = self._get('lendbook', currency)[bids_asks]
        lends = []
        for lbj in lb_json:
            lends.append(LendRate(rate=lbj['rate'], amount=lbj['amount'], period=lbj['period'], rate_type=self._rate_type, fee=self._fee))
        
        return sorted(lends, key=lambda lb: float(lb.rate), reverse=True)

    def lend_bids(self, currency):
        return self.lend_demand(currency, 'bids')
        
    def lend_asks(self, currency):
        return self.lend_demand(currency, 'asks')

    def lend_matches(self, currency):
        return sorted(self._get('lends', currency), key=lambda l: float(l['timestamp']), reverse=True)

    def wallets(self):
        return self._post('balances')

    def offers(self):
        return self._post('offers')

    def new_offer(self, currency, amount, rate, period, direction='lend'):
        return self._post('offer/new',currency=currency, amount=str(amount), rate=str(rate), period=period, direction=direction)

    def cancel_offer(self, id):
        return self._post('offer/cancel', offer_id=int(id))

    def credits(self):
        return self._post('credits')

    def min_lend(self, currency):
        """computes the minimum lendable amount for the specified currency on this platform"""
        if currency.lower() == self._min_lend_base:
            return self._min_lend_amount
        else:
            pair = currency.lower() + self._min_lend_base
            tick = self._get('pubticker', pair)
            exrate = py_.get(tick, 'last_price')
            if exrate is None:
                raise Exception('Failed to get last price for pair {0}'.format(pair))
            return self._min_lend_amount / float(exrate)
