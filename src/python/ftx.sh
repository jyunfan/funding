#!/bin/bash
cd `dirname $0`
env/bin/python ftx.py --format json --token $@ | jq -s '[.[]|.rate]|add/length*24*365*100'

