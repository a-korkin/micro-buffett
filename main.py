import json
import logging
import os
import sys
import time
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

import requests
from dotenv import load_dotenv

from db.repository import (
    Interval,
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


def candles_show(secid: str):
    candles = get_candles(secid)
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


def parse_candles(secid: str) -> list[Candle]:
    dir = os.getenv("DIR") or ""
    files = list_files(f"{dir}/candles/{secid}")
    candles: list = []

    for filename in files:
        logger.info("parsing file: %s", filename)
        parsed = parse_file(filename, Candle, {"secid": secid})
        candles.extend(parsed)

    return candles


def _test_rsi(candles: list[Candle]):
    size = 6
    prev = candles[0]
    averages = [prev.average()] * size
    iteration = 0
    # print(f"iter{iteration}: {averages}, {(sum(averages) / size):.2f}")

    for candle in candles[1:]:
        iteration += 1
        print("=========================================================")
        for i in range(size - 1):
            averages[i] = averages[i + 1]
        averages[size - 1] = prev.average()

        print(
            f"iter{iteration}: {averages}, {(sum(averages) / size):.2f}, {str(candle.begin)[11:]}"
        )

        prev = candle

    # iter9: [2759.0, 2756.88, 2754.12, 2756.38, 2756.75, 2753.75], 2756.15, 15:28:00
    # begin: 2026-07-20 15:19:00, percent: -0.254, avg: 2756.25
    # begin: 2026-07-20 15:20:00, percent:  0.036, avg: 2753.50
    # begin: 2026-07-20 15:21:00, percent:  0.109, avg: 2757.00
    # begin: 2026-07-20 15:22:00, percent:  0.036, avg: 2759.00
    # begin: 2026-07-20 15:23:00, percent: -0.109, avg: 2756.88
    # begin: 2026-07-20 15:24:00, percent: -0.109, avg: 2754.12
    # begin: 2026-07-20 15:25:00, percent:  0.145, avg: 2756.38
    # begin: 2026-07-20 15:26:00, percent: -0.181, avg: 2756.75
    # begin: 2026-07-20 15:27:00, percent: -0.127, avg: 2753.75
    # begin: 2026-07-20 15:28:00, percent:  0.127, avg: 2754.50


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 0:
        if args[0] == "candles_add":
            if len(args) < 2:
                logger.error("'secid' not presented")
                sys.exit(1)
            secid = args[1]
            candles = parse_candles(secid)
            add_candles(candles)
        if args[0] == "terminal":
            period = datetime.strptime("2026-07-20", "%Y-%m-%d")
            interval = Interval.min_1
            sys.exit(run(secid="ozon", period=period, interval=interval))
        if args[0] == "show":
            if len(args) < 2:
                logger.error("'secid' not presented")
                sys.exit(1)
            secid = args[1]
            candles_show(secid)
        if args[0] == "check":
            all_candles = get_candles("ozon")
            cans = all_candles[:10]
            _test_rsi(cans)

    # coupons_show()
    # main()

    # candles = get_candles("ozon")
