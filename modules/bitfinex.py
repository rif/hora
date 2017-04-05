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

    def _get(self, api):
        r = requests.get(self.url + api)
        return r.json() if r.status_code == 200 else r.status_code

    def _post(self, api):
        payload =json.dumps({
            'request': '/v1/' + api,
            'nonce': str(int(time.time()*1000))*5
        })

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
        return self._get('lendbook/'+currency)

    def wallets(self):
        return self._post('balances')
