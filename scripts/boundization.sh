#!/bin/bash

start=0
step=50
from=$(date +%F)
till=$(date -d"+1 months" +%F)
dir="tests/data/boundization/${from}"
base_url="https://iss.moex.com/iss/statistics/engines/stock/markets/bonds/bondization.csv"
# url="${base_url}\
# ?from=${from}&till=${till}&start=${start}&limit=${step}&iss.only=coupons.cursor\
# &sort_order=desc&iss.json=extended&lang=ru&is_traded=1"

# date -d "+5 days"
# date +%F
# curl -s https://example.com | iconv -f ISO-8859-1 -t UTF-8 > output.txt
# echo $(( 1507 / 20 ))
# echo $(( 1507 % 20 ))
# coupons,coupons.cursor

# curl -s -X GET ${url} | jq ".[1].coupons"
# tail -n +3 tests/data/boundization/second.csv



check_dir_exists() {
    if [ -d $dir ]; then
        echo "directory: ${dir} already exists"
    else
        mkdir -p $dir
    fi
}

download_csv() {
    url="${base_url}\
?from=${from}&till=${till}&start=${start}&limit=${step}&iss.only=${1}\
&sort_order=desc&iss.json=extended&lang=ru&is_traded=1"
    echo $url
    curl -s -X GET ${url} | iconv -f WINDOWS-1251  -t UTF-8 | tail -n +3 > ${dir}/${1}${2}.csv
}

get_pages() {
    line=$(tail -n +2 ${dir}/coupons.cursor.csv | head -n 1)
    IFS=";" read -r index total pagesize <<< $line 
}

iterate_through_pages() {
    iteration=0

    while [ $start -lt $total ]; do
        echo "start: ${start}, total: ${total}, iteration: ${iteration}"
        download_csv coupons "_${iteration}"
        sleep 5
        ((start += step))
        ((iteration += 1))
    done
}

check_dir_exists
download_csv coupons.cursor
get_pages
iterate_through_pages
