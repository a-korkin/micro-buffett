#!/bin/bash

LIMIT=5
FIELDS="{SECID, LASTTOPREVPRICE, NUMTRADES, CHANGE, VALTODAY, WAPRICE}"

# curl -X GET "https://iss.moex.com/iss/engines/stock/markets/shares/boardgroups/57/securities.jsonp?iss.meta=off&lang=ru&security_collection=3&sort_column=VALTODAY&sort_order=desc&iss.only=marketdata" \
#     | jq -r ".[1] | .marketdata[] | select(.LASTTOPREVPRICE >= 2.5) | ${FIELDS}" 

curl -X GET "https://iss.moex.com/iss/engines/stock/markets/shares/boardgroups/57/securities.csv?iss.meta=on&lang=ru&security_collection=3&sort_column=VALTODAY&sort_order=desc&iss.only=marketdata" > data/top_today.csv

