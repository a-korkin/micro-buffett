import csv
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from db.repository import add_coupon, add_coupons, get_coupons
from models.coupon import Coupon
from terminal import run

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


class Candle:
    open: float
    close: float
    high: float
    low: float
    value: float
    volume: int
    begin: datetime
    end: datetime

    def __init__(self, obj: dict):
        self.open = obj["open"]
        self.close = obj["close"]
        self.high = obj["high"]
        self.low = obj["low"]
        self.value = obj["value"]
        self.volume = obj["volume"]
        self.begin = obj["begin"]
        self.end = obj["end"]

    def __str__(self) -> str:
        return (
            f"open: {float(self.open):.2f}, close: {float(self.close):.2f}, "
            f"begin: {self.begin}, end: {self.end}, percent: {self.percent():>6.3f}, "
            f"avg: {self.average():.2f}"
        )

    def percent(self) -> float:
        return round(
            ((float(self.close) - float(self.open)) / float(self.open)) * 100.0, 3
        )

    def average(self) -> float:
        return round((float(self.open) + float(self.close)) / 2.0, 2)

    def info(self) -> str:
        prefix = ""
        suffix = "\033[0m"
        if self.open < self.close:
            prefix = "\033[32m"
        elif self.open > self.close:
            prefix = "\033[31m"
        else:
            prefix = ""
            suffix = ""

        return (
            f"{prefix}begin: {self.begin}, percent: {self.percent():>6.3f}, "
            f"avg: {self.average():.2f}{suffix}"
        )


# class Coupon:
#     isin: str
#     name: str
#     issuevalue: float
#     coupondate: datetime
#     recorddate: datetime
#     startdate: datetime
#     initialfacevalue: float
#     facevalue: float
#     faceunit: str
#     value: float
#     valueprc: float
#     value_rub: float
#     secid: str
#     primary_boardid: str
#
#     def __init__(self, obj: dict):
#         self.isin = obj["isin"]
#         self.name = obj["name"]
#         self.issuevalue = obj["issuevalue"]
#         self.coupondate = obj["coupondate"]
#         self.recorddate = obj["recorddate"]
#         self.startdate = obj["startdate"]
#         self.initialfacevalue = obj["initialfacevalue"]
#         self.facevalue = obj["facevalue"]
#         self.faceunit = obj["faceunit"]
#         self.value = obj["value"]
#         self.valueprc = safe_float(obj["valueprc"])
#         self.value_rub = obj["value_rub"]
#         self.secid = obj["secid"]
#         self.primary_boardid = obj["primary_boardid"]
#
#     def __str__(self) -> str:
#         return (
#             f"isin: {self.isin}, valueprc: {self.valueprc}, "
#             f"couponsdate: {self.coupondate}, recorddate: {self.recorddate}"
#         )


class Security:
    secid: str
    boardid: str
    shortname: str
    prevwaprice: str
    yieldatprevwaprice: str
    couponvalue: str
    nextcoupon: str
    accruedint: str
    prevprice: str
    lotsize: str
    facevalue: str
    boardname: str
    status: str
    matdate: str
    decimals: str
    couponperiod: str
    issuesize: str
    prevlegalcloseprice: str
    prevdate: str
    secname: str
    remarks: str
    marketcode: str
    instrid: str
    sectorid: str
    minstep: str
    faceunit: str
    buybackprice: str
    buybackdate: str
    isin: str
    latname: str
    regnumber: str
    currencyid: str
    issuesizeplaced: str
    listlevel: str
    sectype: str
    couponpercent: str
    offerdate: str
    settledate: str
    lotvalue: str
    facevalueonsettledate: str
    calloptiondate: str
    putoptiondate: str
    dateyieldfromissuer: str
    bondtype: str
    bondsubtype: str

    def __init__(self, obj: dict):
        self.secid = obj["SECID"]
        self.boardid = obj["BOARDID"]
        self.shortname = obj["SHORTNAME"]
        self.prevwaprice = obj["PREVWAPRICE"]
        self.yieldatprevwaprice = obj["YIELDATPREVWAPRICE"]
        self.couponvalue = obj["COUPONVALUE"]
        self.nextcoupon = obj["NEXTCOUPON"]
        self.accruedint = obj["ACCRUEDINT"]
        self.prevprice = obj["PREVPRICE"]
        self.lotsize = obj["LOTSIZE"]
        self.facevalue = obj["FACEVALUE"]
        self.boardname = obj["BOARDNAME"]
        self.status = obj["STATUS"]
        self.matdate = obj["MATDATE"]
        self.decimals = obj["DECIMALS"]
        self.couponperiod = obj["COUPONPERIOD"]
        self.issuesize = obj["ISSUESIZE"]
        self.prevlegalcloseprice = obj["PREVLEGALCLOSEPRICE"]
        self.prevdate = obj["PREVDATE"]
        self.secname = obj["SECNAME"]
        self.remarks = obj["REMARKS"]
        self.marketcode = obj["MARKETCODE"]
        self.instrid = obj["INSTRID"]
        self.sectorid = obj["SECTORID"]
        self.minstep = obj["MINSTEP"]
        self.faceunit = obj["FACEUNIT"]
        self.buybackprice = obj["BUYBACKPRICE"]
        self.buybackdate = obj["BUYBACKDATE"]
        self.isin = obj["ISIN"]
        self.latname = obj["LATNAME"]
        self.regnumber = obj["REGNUMBER"]
        self.currencyid = obj["CURRENCYID"]
        self.issuesizeplaced = obj["ISSUESIZEPLACED"]
        self.listlevel = obj["LISTLEVEL"]
        self.sectype = obj["SECTYPE"]
        self.couponpercent = obj["COUPONPERCENT"]
        self.offerdate = obj["OFFERDATE"]
        self.settledate = obj["SETTLEDATE"]
        self.lotvalue = obj["LOTVALUE"]
        self.facevalueonsettledate = obj["FACEVALUEONSETTLEDATE"]
        self.calloptiondate = obj["CALLOPTIONDATE"]
        self.putoptiondate = obj["PUTOPTIONDATE"]
        self.dateyieldfromissuer = obj["DATEYIELDFROMISSUER"]
        self.bondtype = obj["BONDTYPE"]
        self.bondsubtype = obj["BONDSUBTYPE"]

    def __str__(self) -> str:
        return f"SECID: {self.secid}, SHORTNAME: {self.shortname}"


class BondDescription:
    name: str
    title: str
    value: str
    type: str
    sort_order: int
    is_hidden: int
    precision: Optional[int] = None

    def __init__(self, obj: dict):
        self.name = obj["name"]
        self.title = obj["title"]
        self.value = obj["value"]
        self.type = obj["type"]
        self.sort_order = obj["sort_order"]
        self.is_hidden = obj["is_hidden"]
        self.precision = obj["precision"]

    def __str__(self) -> str:
        return f"name: {self.name}, title: {self.title}, value: {self.value}"


def parse_file(filename: str, _type: type) -> list:
    with open(file=filename, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        return [_type(row) for row in reader]


def list_files(path: str) -> list[str]:
    return [str(f) for f in Path(path).iterdir() if f.is_file()]


def candles_show():
    filename = os.getenv("FILENAME") or ""
    candles = parse_file(filename, Candle)
    min_open: Candle = min(candles, key=lambda c: c.open)
    max_open: Candle = max(candles, key=lambda c: c.open)
    max_percent: Candle = max(candles, key=lambda c: c.percent())
    print(min_open)
    print(max_open)
    print(max_percent)
    # for candle in candles:
    #     print(candle.info())


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


def get_securities() -> list[Security]:
    dir = os.getenv("DIR") or ""
    files = list_files(f"{dir}/boundization/2026-06-24")
    files = [file for file in files if file.endswith("bonds.csv")]

    result: list = []
    for filename in files:
        result.extend(parse_file(filename, Security))

    print("=================================================")
    for item in result:
        print(item.bondsubtype)

    print("==================================================")
    print(len(result))
    return result


# def coupons_show():
#     coupons = get_coupons()
#     isins = [coupon.isin for coupon in coupons]
#     for isin in isins:
#         print(isin)
#     print("===================================================")
#     print(len(coupons))


def bond_descriptions_show():
    dir = os.getenv("DIR") or ""
    files = list_files(f"{dir}/boundization/2026-06-25/securities")
    files = [file for file in files]

    result: list = []
    for filename in files:
        rows: list[BondDescription] = parse_file(filename, BondDescription)
        data = {row.name: row.value for row in rows}

        if data.get("ISQUALIFIEDINVESTORS", "1") != "1":
            result.append(data)

    for item in result:
        print("=======================================")
        # print(item)
        print(item["SECID"])
    print(len(result))


def main():
    # candles_show()
    # coupons_show()
    # get_securities()
    # bond_descriptions_show()

    parsed_coupons = parse_coupons()
    logger.info("total: %d", len(parsed_coupons))
    # add_coupons(parsed_coupons)

    # coupon = parsed_coupons[0]
    # add_coupon(coupon)
    # coupons = get_coupons()
    # print(coupons)


if __name__ == "__main__":
    # sys.exit(run())
    main()
