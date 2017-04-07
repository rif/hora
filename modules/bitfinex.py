import hmac
import hashlib
import time
import json
import requests
import base64

class Bitfinex(object):
    def __init__(self, key=None, secret=None):
        self.key = key
        self.secret = secret
        self.url = 'https://api.bitfinex.com/v1/'

    def _get(self, api, *args):
        params = "/" + "/".join(args) if args else ''
        r = requests.get(self.url + api + params)
        return r.json() if r.status_code == 200 else r.status_code

    def _post(self, api, **kwargs):
        data = {
            'request': '/v1/' + api,
            'nonce': str(int(time.time()*1000))*5
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

    def lends(self, currency):
        return self._get('lendbook', currency)

    def wallets(self):
        return self._post('balances')

    def offers(self):
        return self._post('offers')

    def offer_status(self, id):
        return self._post('offer/status', offer_id=id)

    def new_offer(self, currency, amount, rate, period, direction='lend'):
        return self._post('offer/new',currency=currency, amount=str(amount), rate=str(rate), period=period, direction=direction)

    def cancel_offer(self, id):
        return self._post('offer/cancel', offer_id=id)
