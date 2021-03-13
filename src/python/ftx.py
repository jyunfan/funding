#!/usr/bin/env python3

import argparse
import csv
import datetime
import hmac
import json
import sys
import time

from requests import Request, Session

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('--start', help='example: 20210101, inclusive')
    parser.add_argument('--end', help='example: 20210102, exclusive')
    parser.add_argument('--token', default='btc', help='example: btc')
    parser.add_argument('--config', default='ftx.json', help='example: ftx.json')
    parser.add_argument('--output', help='example: btc_20210101.csv, default stdout')
    parser.add_argument('--format', default='csv', help='csv|json, default csv')
    args = parser.parse_args()

    config = json.load(open(args.config))

    s = Session()

    if args.end:
        end_dt = datetime.datetime.strptime(args.end, '%Y%m%d')
    else:
        end_dt = datetime.datetime.now()
    if args.start:
        start_dt = datetime.datetime.strptime(args.start, '%Y%m%d')
    else:
        start_dt = end_dt - datetime.timedelta(days=1)
    start_time = int(start_dt.timestamp())
    end_time = int(end_dt.timestamp())
    ts = int(time.time() * 1000)
    future = f'{args.token.upper()}-PERP'

    request = Request('GET', f'https://ftx.com/api/funding_rates?start_time={start_time}&end_time={end_time}&future={future}')
    prepared = request.prepare()
    signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
    signature = hmac.new(config['secret'].encode(), signature_payload, 'sha256').hexdigest()

    request.headers['FTX-KEY'] = config['key']
    request.headers['FTX-SIGN'] = signature
    request.headers['FTX-TS'] = str(ts)

    r = s.send(prepared)
    if not r.ok:
        print(f'{r.status_code} {r.text}', file=sys.stderr)
        return 1

    output = open(args.output, 'w') if args.output else sys.stdout
    if args.format == 'json':
        for row in r.json()['result']:
            json.dump(row, output)
            output.write('\n')
    elif args.format == 'csv':
        writer = csv.writer(output)
        for row in r.json()['result']:
            writer.writerow([row['future'], row['time'], row['rate']])
    output.close()

if __name__ == '__main__':
    main()

