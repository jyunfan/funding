#!/bin/bash
curl -s https://api.dydx.exchange/v1/historical-funding-rates > dydx.json
echo "BTC 24h"
cat dydx.json | jq '[."PBTC-USDC".history|.[:24]|.[]|.fundingRate8Hr|tonumber]|add/length*3*365*100'
echo "ETH 24h"
cat dydx.json | jq '[."WETH-PUSD".history|.[:24]|.[]|.fundingRate8Hr|tonumber]|add/length*3*365*100'

