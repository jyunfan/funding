#!/bin/bash
curl -s https://api.dydx.exchange/v1/historical-funding-rates > dydx.json
echo -n "dydx L1 BTC 24h "
cat dydx.json | jq '[."PBTC-USDC".history|.[:24]|.[]|.fundingRate8Hr|tonumber]|add/length*3*365*10000|floor/100|tostring+"%"'
echo -n "dydx L1 ETH 24h "
cat dydx.json | jq '[."WETH-PUSD".history|.[:24]|.[]|.fundingRate8Hr|tonumber]|add/length*3*365*10000|floor/100|tostring+"%"'

echo -n "dydx L2 BTC 24h "
curl -s https://api.dydx.exchange/v3/historical-funding/BTC-USD | jq '[.historicalFunding|.[0:24]|.[]|.rate|tonumber]|add/length*24*365*10000|floor/100|tostring+"%"'
echo -n "dydx L2 ETH 24h "
curl -s https://api.dydx.exchange/v3/historical-funding/ETH-USD | jq '[.historicalFunding|.[0:24]|.[]|.rate|tonumber]|add/length*24*365*10000|floor/100|tostring+"%"'

