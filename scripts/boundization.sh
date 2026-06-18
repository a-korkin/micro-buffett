#!/bin/bash

start=0
url="https://iss.moex.com/iss/statistics/engines/stock/markets/bonds/bondization.json?from=2026-07-01&till=2026-07-31&start=${start}&limit=20&iss.only=coupons&sort_order=desc&iss.json=extended&iss.meta=off&lang=ru&is_traded=1"

# date -d "+5 days"
# date +%F
# curl -s https://example.com | iconv -f ISO-8859-1 -t UTF-8 > output.txt

curl -s -X GET ${url} | jq ".[1].coupons"
