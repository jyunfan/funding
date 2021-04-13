import argparse
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

def fetch(last_date):
    if last_date:
        r = requests.get(f'https://api.dydx.exchange/v1/historical-funding-rates?startingBefore={last_date}')
    else:
        r = requests.get(f'https://api.dydx.exchange/v1/historical-funding-rates')
    result = r.json()
    print("pair count:", len(result))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--last_date", default='')
    args = parser.parse_args()

    result = fetch(args.last_date)
    convert2csv(result)


