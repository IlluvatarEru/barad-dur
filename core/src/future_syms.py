import datetime
import re

from core.src.spot_syms import ETHUSD, BTCUSD, XRPUSD, LTCUSD, BCHUSD, SUPPORTED_CCY_PAIRS

# Futures
# This is the standard form of a future, but this instrument is not itself tradeable, what is tradeable is the future
# with a precise expiry
# eg: FUT_ETHUSD_230630

# Below are the one tradeable on KRAKEN
FUT_ = "FUT_"
FUT_ETHUSD_ = FUT_ + ETHUSD + "_"
FUT_BTCUSD_ = FUT_ + BTCUSD + "_"
FUT_XRPUSD_ = FUT_ + XRPUSD + "_"
FUT_LTCUSD_ = FUT_ + LTCUSD + "_"
FUT_BCHUSD_ = FUT_ + BCHUSD + "_"


def raise_wrong_future_format(sym):
    raise Exception(f'Future {sym} has wrong format, it should be FUT_LHSRHS_YYMMDD')


def check_currency_pair_future(sym):
    pattern = re.compile("_")
    if len(pattern.findall(sym)) != 2:
        raise_wrong_future_format(sym)
    if sym[:4] != FUT_:
        raise_wrong_future_format(sym)
    spot = sym.split("_")[1]
    if spot not in SUPPORTED_CCY_PAIRS:
        raise Exception(f'Future {sym} has wrong format, currency pair {spot} not supported')
    return True


def get_future_expiry(sym):
    check_currency_pair_future(sym)
    expiry = sym.split("_")[-1]
    # it should have this format: YYMMDD
    if len(expiry) != 6:
        raise Exception(f'Future {sym} has wrong expiry format')
    year = expiry[:1]
    month = expiry[1:3]
    day = expiry[3:]

    year = 2000 + int(year)
    month = int(month)
    day = int(day)
    expiry = datetime.date(year, month, day)
    return expiry
