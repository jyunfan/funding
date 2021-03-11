#!/usr/bin/env python3

import datetime
import hmac
import json
import time

from requests import Request, Session

config = json.load(open('ftx.json'))

s = Session()

ts = int(time.time() * 1000)
start_time = int(datetime.datetime(2020,3,1).timestamp())
end_time = int(datetime.datetime(2021,3,31).timestamp())
future = 'BTC-PERP'

request = Request('GET', f'https://ftx.com/api/funding_rates?start_time={start_time}&end_time={end_time}&future={future}')
prepared = request.prepare()
signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
signature = hmac.new(config['secret'].encode(), signature_payload, 'sha256').hexdigest()

request.headers['FTX-KEY'] = config['key']
request.headers['FTX-SIGN'] = signature
request.headers['FTX-TS'] = str(ts)

r = s.send(prepared)
print(r.text)

