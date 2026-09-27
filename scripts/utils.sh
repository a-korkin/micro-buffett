#!/bin/bash

# LIMIT=5
# FIELDS="{SECID, LASTTOPREVPRICE, NUMTRADES, CHANGE, VALTODAY, WAPRICE}"

# curl -X GET "https://iss.moex.com/iss/engines/stock/markets/shares/boardgroups/57/securities.json?iss.meta=on&lang=ru&security_collection=3&sort_column=VALTODAY&sort_order=desc&iss.only=marketdata" | jq #\
    # | jq -r ".[1] | .marketdata[] | select(.LASTTOPREVPRICE >= 2.5) | ${FIELDS}" > data/top_today.json

# curl -X GET "https://iss.moex.com/iss/engines/stock/markets/shares/boardgroups/57/securities.csv?iss.meta=on&lang=ru&security_collection=3&sort_column=VALTODAY&sort_order=desc&iss.only=marketdata" | tail -n +3 > data/top_today.csv

curl -X GET "https://iss.moex.com/iss/engines/stock/markets/shares/boardgroups/57/securities.json?iss.meta=off&iss.json=extended&lang=ru&security_collection=3&sort_column=VALTODAY&sort_order=desc&iss.only=marketdata" | jq
