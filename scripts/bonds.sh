#!/bin/bash

source .env

start=0
step=50
from=$(date +%F)
till=$(date -d"+1 months" +%F)
base_dir="${DIR}/bonds/${from}"

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
    url="${BASE_URL}\
?from=${from}&till=${till}&start=${start}&limit=${step}&iss.only=${1}\
&sort_order=desc&iss.json=extended&lang=ru&is_traded=1"
    download_csv ${url} coupons.cursor

    line=$(tail -n +2 ${dir}/coupons.cursor.csv | head -n 1)
    IFS=";" read -r index total pagesize <<< $line 
}

iterate_through_pages() {
    iteration=0

    while [ $start -lt $total ]; do
        url="${BASE_URL}\
?from=${from}&till=${till}&start=${start}&limit=${step}&iss.only=${1}\
&sort_order=desc&iss.json=extended&lang=ru&is_traded=1"
        # print_status
        echo "step: ${start} from total: ${total}"
        suffix=$(printf "%03d" $iteration)
        download_csv ${url} coupons "_${suffix}"
        sleep 1
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
    url="${ISS_HOST}/securities/${1}.csv?iss.only=description"
    print_status
    check_dir_exists ${dir}
    download_csv ${url} ${1}
}

get_bonds_securities() {
    url="${ISS_HOST}/engines/stock/markets/bonds/securities.csv?iss.only=securities"
    dir="${base_dir}"
    check_dir_exists ${dir}
    download_csv ${url} "bonds"
}

send_mail() {
    curl --ssl-reqd \
        --url "smtps://${SMTP_SERVER}:${SMTP_PORT}" \
        --user "${SENDER_EMAIL}:${SENDER_PASSWORD}" \
        --mail-from "${SENDER_EMAIL}" \
        --mail-rcpt "${RECIPIENT_EMAIL}" \
        --upload-file tests/data/mail.txt
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
    "isins")
        search_dir="$base_dir/coupons"
        for entry in "$search_dir"/*; do
            if [[ $entry != *".cursor.csv" ]]; then
                while read -r secid; do
                    get_info $secid
                    sleep 1
                done < <(awk -F';' '{print $1}' ${entry} | tail -n +2 | grep '.')
            fi
        done
    ;;
    "check")
        # printf "%04d" 7
        echo $base_dir
    ;;
    "smtp")
        send_mail
    ;;
    *)
        echo "unknown command"
        exit 1
    ;;
esac

