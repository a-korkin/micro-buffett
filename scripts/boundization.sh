#!/bin/bash

download_path="tests/data/boundization/"
start=0
step=50
url="https://iss.moex.com/iss/statistics/engines/stock/markets/bonds/bondization.csv\
?from=2026-07-01&till=2026-07-31&start=${start}&limit=${step}&iss.only=coupons.cursor\
&sort_order=desc&iss.json=extended&lang=ru&is_traded=1"

# date -d "+5 days"
# date +%F
# curl -s https://example.com | iconv -f ISO-8859-1 -t UTF-8 > output.txt
# echo $(( 1507 / 20 ))
# echo $(( 1507 % 20 ))
# coupons,coupons.cursor

# curl -s -X GET ${url} | jq ".[1].coupons"
# tail -n +3 tests/data/boundization/second.csv

mkdir -p ${download_path}
curl -s -X GET ${url} | iconv -f WINDOWS-1251  -t UTF-8 | tail -n +3 > ${download_path}coupons.cursor.csv

# tail -n +2 tests/data/boundization/coupons.cursor.csv | head -n 1
# tail -n +2 tests/data/boundization/coupons.cursor.csv | head -n 1 | IFS=";" read -r var1 var2 var3 | echo $var2

# INDEX;TOTAL;PAGESIZE
# 0;1507;50
