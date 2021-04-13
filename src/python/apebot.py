#!/usr/bin/env python
# pylint: disable=C0116

# TODO help

import argparse
import datetime
import json
import logging
import time

from attrdict import AttrDict
import requests
import telegram
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def ad(obj={}, **kw):
    if kw:
        obj.update(kw)
    if isinstance(obj, dict):
        return AttrDict(obj)
    elif isinstance(obj, list):
        return [AttrDict(i) for i in obj]
    else:
        return obj

def req(url):
    r = requests.get(url)
    logger.info(f"GET {url} {r.status_code}")
    return ad(r.json())

def yesterday():
    return datetime.datetime.now() - datetime.timedelta(days=1)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
config = ad(json.load(open("config.json")))


def ftx_funding(symbol):
    if symbol:
        r = req(f"https://ftx.com/api/funding_rates?future={symbol.upper()}-PERP")
        if r.success:
            rate = sum(float(i.rate) for i in r.result[:24]) * 365
            return [ad(exchange='ftx', symbol=symbol, rate=rate)]
        else:
            return []
    else:
        r = req(f"https://ftx.com/api/funding_rates")
        if r.success:
            samples = {}
            t = yesterday().isoformat()
            for i in r.result:
                if i.time > t and i.future.endswith('-PERP'):
                    symbol = i.future.replace('-PERP', '').lower()
                    samples.setdefault(symbol, []).append(i.rate)
            rates = []
            for symbol in samples:
                rate = sum(samples[symbol]) / len(samples[symbol]) * 24 * 365
                rates.append(ad(exchange='ftx', symbol=symbol, rate=rate))
            top = sorted(rates, key=lambda i:-i.rate)[:10]
            rates = []
            for i in top:
                rates += ftx_funding(i.symbol)
                time.sleep(0.1)
            return rates
        else:
            return []

def binance_funding(symbol):
    if symbol:
        r = req(f"https://fapi.binance.com/fapi/v1/fundingRate?symbol={symbol.upper()}USDT")
        if r:
            rate = sum(float(i['fundingRate']) for i in r[-3:]) * 365
            return [ad(exchange='binance', symbol=symbol, rate=rate)]
        else:
            return []
    else:
        r = req(f"https://fapi.binance.com/fapi/v1/fundingRate")
        if r:
            samples = {}
            t = yesterday().timestamp() * 1000
            for i in r:
                if i.fundingTime > t and i.symbol.endswith('USDT'):
                    symbol = i.symbol.replace('USDT', '').lower()
                    samples.setdefault(symbol, []).append(float(i.fundingRate))
            rates = []
            for symbol in samples:
                rate = sum(samples[symbol]) / len(samples[symbol]) * 3 * 365
                rates.append(ad(exchange='binance', symbol=symbol, rate=rate))
            top = sorted(rates, key=lambda i:-i.rate)[:10]
            rates = []
            for i in top:
                rates += binance_funding(i.symbol)
                time.sleep(0.1)
            return rates
        else:
            return []


DYDXL1_MARKETS = {'btc':'PBTC-USDC', 'eth':'WETH-PUSD'}
def dydxL1_funding(symbol):
    if symbol:
        symbols = [symbol] if symbol in DYDXL1_MARKETS else []
    else:
        symbols = ['btc', 'eth']
    r = req(f"https://api.dydx.exchange/v1/historical-funding-rates")
    rates = []
    for symbol in symbols:
        market = DYDXL1_MARKETS[symbol]
        rate = sum(float(i.fundingRate8Hr) for i in ad(r[market]).history[:24])/24*3 * 365
        rates.append(ad(exchange='dydxL1', symbol=symbol, rate=rate))
    return rates

def dydx_funding(symbol):
    if symbol:
        symbols = [symbol] if symbol in DYDXL1_MARKETS else []
    else:
        symbols = ['btc', 'eth']
    rates = []
    for symbol in symbols:
        r = req(f"https://api.dydx.exchange/v3/historical-funding/{symbol.upper()}-USD")
        rate = sum(float(i.rate) for i in r.historicalFunding[:24]) * 365
        rates.append(ad(exchange='dydx', symbol=symbol, rate=rate))
    return rates

EXCHANGES = {
    'ftx': ftx_funding,
    'binance': binance_funding,
    'dydx': dydx_funding,
    'dydxL1': dydxL1_funding,
}

def funding_command(update: Update, _: CallbackContext) -> None:
    logger.info(update.message.text)
    args = update.message.text.split()[1:]
    exchanges = [i for i in args if i in EXCHANGES] or EXCHANGES.keys()
    symbols = [i for i in args if i not in EXCHANGES] or [None]
    rates = []
    for exchange in exchanges:
        for symbol in symbols:
            rates += EXCHANGES[exchange](symbol)
    rates = sorted(rates, key=lambda r:-r.rate)[:10]
    rows = []
    for r in rates:
        rows.append((r.symbol.upper(), r.exchange, f"{round(r.rate * 100, 2)}%"))
    w = [max(len(r) for r in c) for c in zip(*rows)]
    message = '24hr funding rates: \(APR\)\n'
    message += '\n'.join(f'`{r[0]:{w[0]}} {r[1]:{w[1]}} {r[2]:{w[2]}}`' for r in rows)
    update.message.reply_text(message, parse_mode=telegram.ParseMode.MARKDOWN_V2)


def main() -> None:
    updater = Updater(config.apebot.token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("funding", funding_command))
    dispatcher.add_handler(CommandHandler("f", funding_command))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

