import hmac
import hashlib
import time
import json
import requests
import base64
from threading import Lock
from lend_bid import LendBid

mutex = Lock()

class Bitfinex(object):
    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret
        self.url = 'https://api.bitfinex.com/v1/'
        self._nonce = 0
        self._fee = 0.15
        self._rate_type = 'apr'

    def _get_nonce(self):
            self._nonce += 1
            self._nonce = max(int(time.time()*1000000000), self._nonce)
            return self._nonce


    def _get(self, api, *args):
        params = "/" + "/".join(args) if args else ''
        r = requests.get(self.url + api + params)
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
            return r.json()
        finally:
            mutex.release()


    def lend_demand(self, currency):
        lb_json = self._get('lendbook', currency)['bids']
        lend_bids = []
        for lbj in lb_json:
            lend_bids.append(LendBid(rate=lbj['rate'], amount=lbj['amount'], period=lbj['period'], rate_type=self._rate_type, fee=self._fee))
        
        return sorted(lend_bids, key=lambda lb: float(lb.rate), reverse=True)

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
