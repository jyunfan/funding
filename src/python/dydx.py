import datetime
import os
import json
import time
import requests

def convert2csv(data):
    for pair in data:
        for record in data[pair]['history']:
            dt = record['effectiveAt']
            os.makedirs('data/dydx/csv/%s' % pair, exist_ok=True)
            with open('data/dydx/csv/%s/%s.csv' % (pair, dt), 'w') as fid:
                fid.write(','.join(record.keys()) + '\n')
                fid.write(','.join(record.values()) + '\n')

if __name__ == '__main__':
    while True:
        print('Download fuding rate from dydx')
        r = requests.get('https://api.dydx.exchange/v1/historical-funding-rates')
        result = r.json()
        print("pair count:", len(result))
        curtime = datetime.datetime.now()
        convert2csv(result)
        print('Sleep')
        time.sleep(60*50)

