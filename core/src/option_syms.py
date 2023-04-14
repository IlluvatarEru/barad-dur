# Options
# This is the standard form of an option, but this instrument is not itself tradeable, what is tradeable is the option
# with a precise expiry and strike:
# eg: C_ETHUSD_230630_1200
import datetime
import re

from core.src.spot_syms import ETHUSD, BTCUSD, SUPPORTED_CCY_PAIRS

C_ = "C_"
P_ = "P_"
C_ETHUSD_ = C_ + ETHUSD + "_"
C_BTCUSD_ = C_ + BTCUSD + "_"


def raise_wrong_format_option(sym):
    raise Exception(f'Option {sym} has wrong format, it should be C_LHSRHS_YYMMDD_K or P_LHSRHS_YYMMDD_K')


def check_currency_pair_option(sym):
    pattern = re.compile("_")
    if len(pattern.findall(sym)) != 3:
        raise_wrong_format_option(sym)
    if sym[:2] not in [C_, P_]:
        raise_wrong_format_option(sym)
    spot = sym.split("_")[1]
    if spot not in SUPPORTED_CCY_PAIRS:
        raise Exception(f'Option {sym} has wrong format, currency pair {spot} not supported')
    return True


def get_expiry_option(sym):
    check_currency_pair_option(sym)
    expiry = sym.split("_")[-2]
    # it should have this format: YYMMDD
    if len(expiry) != 6:
        raise Exception(f'Option {sym} has wrong expiry format')
    year = expiry[:1]
    month = expiry[1:3]
    day = expiry[3:]

    year = 2000 + int(year)
    month = int(month)
    day = int(day)
    expiry = datetime.date(year, month, day)
    return expiry
