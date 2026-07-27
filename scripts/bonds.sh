#!/bin/bash

source .env

start=0
step=50
from=$(date +%F)
till=$(date -d"+1 months" +%F)
base_dir="${DIR}/bonds/${from}"
count=0

replacement="secid: RU000A10AHU1  price: 101.85%  percent: 33.00%  name: ОилРесурс 001P-01 \\
secid: RU000A10BM56  price: 100.85%  percent: 30.50%  name: АПРИ БО-002Р-10 \\
secid: RU000A10AUG3  price: 100.93%  percent: 29.50%  name: АПРИ БО-002Р-07 \\
secid: RU000A10DB16  price:  77.13%  percent: 29.00%  name: Оил Ресурс 001P-03 \\
secid: RU000A10ATR2  price: 105.84%  percent: 28.00%  name: ГЛОРАКС 001P-03 \\
secid: RU000A10C8H9  price:  91.72%  percent: 28.00%  name: Оил Ресурс 001P-02 \\
secid: RU000A10AHE5  price: 104.89%  percent: 27.50%  name: Новые технологии 001Р-02 \\
secid: RU000A10B396  price:   2.69%  percent: 26.50%  name: МОНОПОЛИЯ 001P-04 \\
secid: RU000A10AEF9  price: 112.14%  percent: 26.50%  name: ПАО \"ТГК-14\" 001Р-03 \\
secid: RU000A10ASE2  price: 103.44%  percent: 26.00%  name: РОЛЬФ БО 001Р-07 \\
secid: RU000A10B8X7  price: 101.14%  percent: 26.00%  name: ДАРС-Девелопмент 001Р-03 \\
secid: RU000A10B2P6  price: 107.16%  percent: 26.00%  name: АйДи Коллект 001P-01 \\
secid: RU000A10BFP3  price: 102.10%  percent: 26.00%  name: МВ ФИНАНС 001Р-06 \\
secid: RU000A10BQ60  price: 104.46%  percent: 25.50%  name: РОЛЬФ БО 001Р-08 \\
secid: RU000A10BWL7  price:   2.72%  percent: 25.50%  name: МОНОПОЛИЯ 001P-05 \\
secid: RU000A10BNM4  price: 108.66%  percent: 25.50%  name: АБЗ-1 002P-03 \\
secid: RU000A10BFJ6  price: 104.92%  percent: 25.50%  name: Полипласт АО П02-БО-04 \\
secid: RU000A10B9Q9  price: 109.84%  percent: 25.50%  name: ГЛОРАКС 001Р-04 \\
secid: RU000A10BFX7  price: 101.78%  percent: 25.50%  name: ГК Самолет БО-П16 \\
secid: RU000A10B0R6  price: 100.31%  percent: 25.50%  name: Кокс ПАО 001P-02 \\
secid: RU000A10AS28  price: 100.46%  percent: 25.50%  name: Биннофарм Групп 001Р-04 \\
secid: RU000A10BPN7  price: 105.23%  percent: 25.50%  name: Полипласт АО П02-БО-05 \\
secid: RU000A10BAP4  price: 103.88%  percent: 25.50%  name: Эталон-Финанс 002Р-03 \\
secid: RU000A10BQH7  price: 102.95%  percent: 25.25%  name: АйДи Коллект 001P-04 \\
secid: RU000A10BW88  price: 103.22%  percent: 25.25%  name: АйДи Коллект 001P-05 \\
secid: RU000A10E6J7  price: 101.98%  percent: 25.25%  name: Страна Девелопмент 002Р-02 \\
secid: RU000A10AV15  price: 101.05%  percent: 25.25%  name: ВИС ФИНАНС БО-П07 \\
secid: RU000A10AA10  price: 104.11%  percent: 25.00%  name: ПСБ Лизинг БО-П01 \\
secid: RU000A10ATS0  price:  72.14%  percent: 25.00%  name: ЕвроТранс БО-001Р-06 \\
secid: RU000A10CM06  price:  99.00%  percent: 25.00%  name: АПРИ БО-002Р-11 \\
secid: RU000A10DZH4  price:  99.03%  percent: 25.00%  name: АПРИ БО-002Р-12 \\
secid: RU000A10AAQ4  price: 103.68%  percent: 25.00%  name: СФО Сплит Финанс 1 01 \\
secid: RU000A10E747  price: 100.13%  percent: 25.00%  name: ГК Сегежа 003P-10R \\
secid: RU000A10B7T7  price: 103.93%  percent: 25.00%  name: СФО ТБ-3 класс А \\
secid: RU000A10A141  price:  74.01%  percent: 25.00%  name: ЕвроТранс БО-001Р-05 \\
secid: RU000A10A3Z4  price: 111.22%  percent: 25.00%  name: ГТЛК БО 002P-04"

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
    local filename="${DIR}/${2}${3}.csv"
    local dirpath=$(dirname $filename)
    check_dir_exists $dirpath

    curl -s -X GET ${1} | iconv -f WINDOWS-1251  -t UTF-8 | tail -n +3 > ${filename}
    count=$(grep -c '.' ${filename})
    if [[ $count -le 1 ]]; then
        rm -rf $filename
    fi
    echo $count
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
        --upload-file scripts/mail.txt
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
    "smtp")
        send_mail
    ;;
    "candles")
        start=0
        secid="ozon"
        period=$(date -d"-1 days" +%F)
        iteration=1

        # выкачать свечи по secid за определённый день
        while true; do
            url="${BASE_URL}/stock/markets/shares/securities/${secid}/candles.csv\
?from=${period}&till=${period}&interval=1&start=${start}"
            print_status
            fn=$(printf "$period_%02d" $iteration)
            count=$(download_csv $url "candles/${secid}/" "${period}_${fn}")
            ((start += count-1))
            ((iteration += 1))

            if [[ $count -le 1 ]]; then
                break
            fi
        done
    ;;
    "replace_mail")
        sed -i -z "s|<code>.*</code>|<code>\n${replacement}\n</code>|g" scripts/mail.txt
    ;;
    *)
        echo "unknown command"
        exit 1
    ;;
esac

