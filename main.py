import json
import logging
import os
import sys
import time
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

from db.repository import (
    add_candle,
    add_candles,
    add_coupons,
    add_security_description,
    get_best_choices,
    get_coupon,
    get_coupons,
    get_security_descriptions,
)
from models.candle import Candle
from models.coupon import Coupon
from models.security import Description, Security
from terminal import run
from utils import get_candles, parse_file

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

ISS_URL = "https://iss.moex.com/iss/engines/stock/markets"


def list_files(path: str) -> list[str]:
    return [str(f) for f in Path(path).iterdir() if f.is_file()]


def candles_show():
    candles = get_candles("ozon")
    # min_open: Candle = min(candles, key=lambda c: c.open)
    # max_open: Candle = max(candles, key=lambda c: c.open)
    # max_percent: Candle = max(candles, key=lambda c: c.percent())
    # print(min_open)
    # print(max_open)
    # print(max_percent)
    for candle in candles:
        print(candle.info())


def parse_coupons() -> list[Coupon]:
    dir = os.getenv("DIR") or ""
    files = list_files(f"{dir}/boundization/2026-06-25/coupons")
    files = [file for file in files if not file.endswith("cursor.csv")]

    coupons: list = []
    for filename in files:
        logger.info("parsing file: %s", filename)
        parsed = parse_file(filename, Coupon)
        coupons.extend(parsed)
        add_coupons(parsed)

    return coupons


# def get_securities() -> list[Security]:
#     dir = os.getenv("DIR") or ""
#     files = list_files(f"{dir}/boundization/2026-06-24")
#     files = [file for file in files if file.endswith("bonds.csv")]
#
#     result: list = []
#     for filename in files:
#         result.extend(parse_file(filename, Security))
#
#     print("=================================================")
#     for item in result:
#         print(item.bondsubtype)
#
#     print("==================================================")
#     print(len(result))
#     return result


def coupons_show():
    coupons = get_coupons()
    isins = [coupon.isin for coupon in coupons]
    for isin in isins:
        print(isin)
    print("===================================================")
    print(len(coupons))


def fetch_security_description():
    dir = os.getenv("DIR") or ""
    files = list_files(f"{dir}/boundization/2026-06-25/securities")
    files = [file for file in files]

    for filename in files:
        rows: list[Description] = parse_file(filename, Description)
        description = [row.__dict__ for row in rows]
        result = [
            {item[0]: item[1]} for item in [(row.name, row.value) for row in rows]
        ]
        info = {k: v for d in result for k, v in d.items()}
        secid = info.get("SECID", None)

        if not secid:
            continue
        try:
            logger.info("adding security description: %s", secid)
            security = Security(secid=secid, description=description, info=info)
            add_security_description(security)
        except Exception:
            logger.error("couldn't add security description: %s", secid)


def fetch_candles(path: Path, secid: str):
    response = requests.get(
        f"{ISS_URL}/bonds/securities/{secid}/candles.csv?iss.reverse=true&interval=24"
    )

    if response.status_code == HTTPStatus.OK:
        with open(f"{path}/{secid}.csv", "w", encoding="utf-8") as file:
            content = response.content.decode().splitlines()[2:]
            if len(content) > 0:
                file.write("\n".join(content))


def main():
    # candles_show()
    # coupons_show()
    # get_securities()
    # fetch_security_description()

    # parsed_coupons = parse_coupons()
    # logger.info("total: %d", len(parsed_coupons))

    # secs = [
    #     security
    #     for security in get_security_descriptions()
    #     if security.info.get("ISQUALIFIEDINVESTORS") == "0"
    # ]
    # for sec in secs:
    #     print("=================================================")
    #     print(sec.info)

    # fetch_candles("RU000A10A141")

    # today = datetime.today().date()
    today = "2026-07-04"
    path = Path(f"tests/data/bonds/{today}/candles")
    path.mkdir(parents=True, exist_ok=True)

    result = get_best_choices()
    for row in result:
        # fetch_candles(path, row.secid)

        file = f"{path}/{row.secid}.csv"
        candles = parse_file(file, Candle)
        last_candle = candles[0]
        secid = file.split("/")[-1].replace(".csv", "")
        print(
            f"secid: {secid}  price: {float(last_candle.close):>6.2f}%  percent: {float(row.valueprc):.2f}%  name: {row.name}"
        )


if __name__ == "__main__":
    # coupons_show()
    sys.exit(run())
    # main()
    # candles = get_candles("sber")
    # add_candles(candles)
