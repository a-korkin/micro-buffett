#!/bin/bash

start=0
step=50
from=$(date +%F)
till=$(date -d"+1 months" +%F)
base_dir="/home/ss/projects/personal/micro-buffett/tests/data/boundization/${from}"
base_url="https://iss.moex.com/iss/statistics/engines/stock/markets/bonds/bondization.csv"

if [ "$#" -ne 1 ]; then
    echo "Error: exactly 1 argument required"
    exit 1
fi

print_status() {
    echo $(date +"%F %T") "[INFO]: url >>> ${url}"
}

check_dir_exists() {
    if [ ! -d ${1} ]; then
        mkdir -p ${1}
    fi
}

download_csv() {
    curl -s -X GET ${1} | iconv -f WINDOWS-1251  -t UTF-8 | tail -n +3 > ${dir}/${2}${3}.csv
}

get_pages() {
    url="${base_url}\
?from=${from}&till=${till}&start=${start}&limit=${step}&iss.only=${1}\
&sort_order=desc&iss.json=extended&lang=ru&is_traded=1"
    download_csv ${url} coupons.cursor

    line=$(tail -n +2 ${dir}/coupons.cursor.csv | head -n 1)
    IFS=";" read -r index total pagesize <<< $line 
}

iterate_through_pages() {
    iteration=0

    while [ $start -lt $total ]; do
        url="${base_url}\
?from=${from}&till=${till}&start=${start}&limit=${step}&iss.only=${1}\
&sort_order=desc&iss.json=extended&lang=ru&is_traded=1"
        print_status
        download_csv ${url} coupons "_${iteration}"
        sleep 5
        ((start += step))
        ((iteration += 1))
    done
}

get_coupons() {
    dir="${base_dir}/coupons"
    check_dir_exists ${dir}
    get_pages coupons.cursor 
    iterate_through_pages coupons
}

get_info() {
    dir="${base_dir}/securities"
    url="https://iss.moex.com/iss/securities/${1}.csv?iss.only=description"
    print_status
    check_dir_exists ${dir}
    download_csv ${url} ${1}
}

get_bonds_securities() {
    url="https://iss.moex.com/iss/engines/stock/markets/bonds/securities.csv?iss.only=securities"
    dir="${base_dir}"
    check_dir_exists ${dir}
    download_csv ${url} "bonds"
}

case "$1" in
    "coupons")
        get_coupons
    ;;
    "info")
        get_info "RU000A10BGE5"
    ;;
    "bonds")
        get_bonds_securities
    ;;
    "infos")
        while read -r secid; do
            get_info $secid
            sleep 3
        done < <(awk -F';' '{print $1}' ${base_dir}/bonds.csv | tail -n +2)
    ;;
    *)
        echo "unknown command"
        exit 1
    ;;
esac

