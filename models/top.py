from datetime import datetime
from datetime import time as _time
from typing import Optional

from sqlalchemy import DateTime, Float, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from utils import optional_date, optional_datetime, optional_float, safe_float, safe_int

from .base import Base


class TopToday(Base):
    __tablename__ = "top_today"
    secid: Mapped[str] = mapped_column(String(256), primary_key=True)
    boardid: Mapped[str] = mapped_column(String(256))
    bid: Mapped[float] = mapped_column(Float())
    biddepth: Mapped[Optional[float]] = mapped_column(Float())
    offer: Mapped[Optional[float]] = mapped_column(Float())
    offerdepth: Mapped[Optional[float]] = mapped_column(Float())
    spread: Mapped[float] = mapped_column(Float())
    biddeptht: Mapped[int] = mapped_column(Integer())
    offerdeptht: Mapped[int] = mapped_column(Integer())
    open: Mapped[float] = mapped_column(Float())
    low: Mapped[float] = mapped_column(Float())
    high: Mapped[float] = mapped_column(Float())
    last: Mapped[float] = mapped_column(Float())
    lastchange: Mapped[float] = mapped_column(Float())
    lastchangeprcnt: Mapped[float] = mapped_column(Float())
    qty: Mapped[int] = mapped_column(Integer())
    value: Mapped[float] = mapped_column(Float())
    value_usd: Mapped[float] = mapped_column(Float())
    waprice: Mapped[float] = mapped_column(Float())
    lastcngtolastwaprice: Mapped[float] = mapped_column(Float())
    waptoprevwapriceprcnt: Mapped[float] = mapped_column(Float())
    waptoprevwaprice: Mapped[float] = mapped_column(Float())
    closeprice: Mapped[float] = mapped_column(Float())
    marketpricetoday: Mapped[float] = mapped_column(Float())
    marketprice: Mapped[float] = mapped_column(Float())
    lasttoprevprice: Mapped[float] = mapped_column(Float())
    numtrades: Mapped[int] = mapped_column(Integer())
    voltoday: Mapped[int] = mapped_column(Integer())
    valtoday: Mapped[int] = mapped_column(Integer())
    valtoday_usd: Mapped[int] = mapped_column(Integer())
    etfsettleprice: Mapped[float] = mapped_column(Float())
    tradingstatus: Mapped[str] = mapped_column(String(256))
    updatetime: Mapped[_time] = mapped_column(Time())
    lastbid: Mapped[float] = mapped_column(Float())
    lastoffer: Mapped[float] = mapped_column(Float())
    lcloseprice: Mapped[float] = mapped_column(Float())
    lcurrentprice: Mapped[float] = mapped_column(Float())
    marketprice2: Mapped[float] = mapped_column(Float())
    numbids: Mapped[float] = mapped_column(Float())
    numoffers: Mapped[float] = mapped_column(Float())
    change: Mapped[float] = mapped_column(Float())
    time: Mapped[_time] = mapped_column(Time())
    highbid: Mapped[float] = mapped_column(Float())
    lowoffer: Mapped[float] = mapped_column(Float())
    priceminusprevwaprice: Mapped[float] = mapped_column(Float())
    openperiodprice: Mapped[float] = mapped_column(Float())
    seqnum: Mapped[float] = mapped_column(Float())
    systime: Mapped[datetime] = mapped_column(DateTime())
    closingauctionprice: Mapped[float] = mapped_column(Float())
    closingauctionvolume: Mapped[float] = mapped_column(Float())
    issuecapitalization: Mapped[float] = mapped_column(Float())
    issuecapitalization_updatetime: Mapped[_time] = mapped_column(Time())
    etfsettlecurrency: Mapped[str] = mapped_column(String(256))
    valtoday_rur: Mapped[float] = mapped_column(Float())
    tradingsession: Mapped[str] = mapped_column(String(256))
    trendissuecapitalization: Mapped[float] = mapped_column(Float())

    def __init__(self, obj: dict):
        self.secid = obj["SECID"]
        self.boardid = obj["BOARDID"]
        self.bid = safe_float(obj["BID"])
        self.biddepth = optional_float(obj["BIDDEPTH"])
        self.offer = optional_float(obj["OFFER"])
        self.offerdepth = optional_float(obj["OFFERDEPTH"])
        self.spread = safe_float(obj["SPREAD"])
        self.biddeptht = safe_int(obj["BIDDEPTHT"])
        self.offerdeptht = safe_int(obj["OFFERDEPTHT"])
        self.open = safe_float(obj["OPEN"])
        self.low = safe_float(obj["LOW"])
        self.high = safe_float(obj["HIGH"])
        self.last = safe_float(obj["LAST"])
        self.lastchange = safe_float(obj["LASTCHANGE"])
        self.lastchangeprcnt = safe_float(obj["LASTCHANGEPRCNT"])
        self.qty = safe_int(obj["QTY"])
        self.value = safe_float(obj["VALUE"])
        self.value_usd = safe_float(obj["VALUE_USD"])
        self.waprice = safe_float(obj["WAPRICE"])
        self.lastcngtolastwaprice = safe_float(obj["LASTCNGTOLASTWAPRICE"])
        self.waptoprevwapriceprcnt = safe_float(obj["WAPTOPREVWAPRICEPRCNT"])
        self.waptoprevwaprice = safe_float(obj["WAPTOPREVWAPRICE"])
        self.closeprice = safe_float(obj["CLOSEPRICE"])
        self.marketpricetoday = safe_float(obj["MARKETPRICETODAY"])
        self.marketprice = safe_float(obj["MARKETPRICE"])
        self.lasttoprevprice = safe_float(obj["LASTTOPREVPRICE"])
        self.numtrades = safe_int(obj["NUMTRADES"])
        self.voltoday = safe_int(obj["VOLTODAY"])
        self.valtoday = safe_int(obj["VALTODAY"])
        self.valtoday_usd = safe_int(obj["VALTODAY_USD"])
        self.etfsettleprice = safe_float(obj["ETFSETTLEPRICE"])
        self.tradingstatus = obj["TRADINGSTATUS"]
        self.updatetime = obj["UPDATETIME"]
        self.lastbid = safe_float(obj["LASTBID"])
        self.lastoffer = safe_float(obj["LASTOFFER"])
        self.lcloseprice = safe_float(obj["LCLOSEPRICE"])
        self.lcurrentprice = safe_float(obj["LCURRENTPRICE"])
        self.marketprice2 = safe_float(obj["MARKETPRICE2"])
        self.numbids = safe_float(obj["NUMBIDS"])
        self.numoffers = safe_float(obj["NUMOFFERS"])
        self.change = safe_float(obj["CHANGE"])
        self.time = obj["TIME"]
        self.highbid = safe_float(obj["HIGHBID"])
        self.lowoffer = safe_float(obj["LOWOFFER"])
        self.priceminusprevwaprice = safe_float(obj["PRICEMINUSPREVWAPRICE"])
        self.openperiodprice = safe_float(obj["OPENPERIODPRICE"])
        self.seqnum = safe_float(obj["SEQNUM"])
        self.systime = obj["SYSTIME"]
        self.closingauctionprice = safe_float(obj["CLOSINGAUCTIONPRICE"])
        self.closingauctionvolume = safe_float(obj["CLOSINGAUCTIONVOLUME"])
        self.issuecapitalization = safe_float(obj["ISSUECAPITALIZATION"])
        self.issuecapitalization_updatetime = obj["ISSUECAPITALIZATION_UPDATETIME"]
        self.etfsettlecurrency = obj["ETFSETTLECURRENCY"]
        self.valtoday_rur = safe_float(obj["VALTODAY_RUR"])
        self.tradingsession = obj["TRADINGSESSION"]
        self.trendissuecapitalization = safe_float(obj["TRENDISSUECAPITALIZATION"])
