import hmac
import hashlib
import time
import websocket
import json

API_KEY = "yMn0s71JpKRZpJQBV57NyyRze90XjKsLOKh1KuIvDos"
API_SECRET = "Ka6Pb4MpScpL8Osr2Vc4Mm8XhyZVZk79ovSugXR81ZB"

nonce = int(time.time() * 1000000)
auth_payload = 'AUTH{}'.format(nonce)
signature = hmac.new(
  API_SECRET.encode(),
  msg = auth_payload.encode(),
  digestmod = hashlib.sha384
).hexdigest()

payload = {
  'apiKey': API_KEY,
  'event': 'auth',
  'authPayload': auth_payload,
  'authNonce': nonce,
  'authSig': signature
}

ws = websocket.WebSocket()
ws.connect("wss://api.bitfinex.com/ws/2")

ws.send(json.dumps(payload))
print(ws.recv())

payload = {
  'event': 'ping'
}

ws.send(json.dumps(payload))
print(ws.recv())

ws.close()
