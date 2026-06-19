#!/bin/bash

start=0
step=50
from=$(date +%F)
till=$(date -d"+1 months" +%F)
dir="tests/data/boundization/${from}"
base_url="https://iss.moex.com/iss/statistics/engines/stock/markets/bonds/bondization.csv"

print_status() {
    echo $(date +"%F %T") "[INFO]: url >>> ${url}"
}

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
    curl -s -X GET ${url} | iconv -f WINDOWS-1251  -t UTF-8 | tail -n +3 > ${dir}/${1}${2}.csv
}

get_pages() {
    line=$(tail -n +2 ${dir}/coupons.cursor.csv | head -n 1)
    IFS=";" read -r index total pagesize <<< $line 
}

iterate_through_pages() {
    iteration=0
    while [ $start -lt $total ]; do
        print_status
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
