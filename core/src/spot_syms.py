"""
NOTE: Please read the doc about syms before modifying anything in here

Future: BTCTUSD/Future/230231
Spot: BTCUSD
"""
import warnings

# fiat
USD = 'USD'
EUR = 'EUR'

# crypto
ETH = 'ETH'
STETH = 'STETH'
BTC = 'BTC'
USDC = 'USDC'
USDT = 'USDT'
NEAR = 'NEAR'
SOL = 'SOL'
MATIC = 'MATIC'
ADA = 'ADA'
AVAX = 'AVAX'
XRP = "XRP"
LTC = "LTC"
BCH = "BCH"

# Currency Pairs vs USD
ETHUSD = ETH + USD
STETHUSD = STETH + USD
BTCUSD = BTC + USD
USDCUSD = USDC + USD
USDTUSD = USDT + USD
NEARUSD = NEAR + USD
SOLUSD = SOL + USD
MATICUSD = MATIC + USD
ADAUSD = ADA + USD
AVAXUSD = AVAX + USD
XRPUSD = XRP + USD
LTCUSD = LTC + USD
BCHUSD = BCH + USD

# Currency Pairs vs EUR
USDCEUR = USDC + EUR
USDTEUR = USDT + EUR
SUPPORTED_CRYPTO_CURRENCIES = [ETH, STETH, BTC, USDC, USDT, NEAR, SOL, MATIC, ADA, AVAX, XRP, LTC, BCH]
SUPPORTED_FIAT_CURRENCIES = [USD, EUR]
SUPPORTED_CURRENCIES = SUPPORTED_CRYPTO_CURRENCIES + SUPPORTED_FIAT_CURRENCIES
SUPPORTED_CCY_PAIRS = [crypto + USD for crypto in SUPPORTED_CRYPTO_CURRENCIES]
CCY_PAIRS_VS_EUR = [USDCEUR]


def split_currency_pair_into_lhs_rhs(sym):
    if sym.upper() != sym:
        warnings.warn(f'sym should always be upper case but received {sym}')
    sym = sym.upper()
    fiat = sym[-3:]
    if fiat in SUPPORTED_FIAT_CURRENCIES:
        crypto = sym[:-3]
        return crypto, fiat
    else:
        raise Exception(f'fiat not supported: {fiat} in {sym}')


def extract_crypto_ccy_from_pair(sym):
    crypto, _ = split_currency_pair_into_lhs_rhs(sym)
    return crypto


def extract_fiat_ccy_from_pair(sym):
    _, fiat = split_currency_pair_into_lhs_rhs(sym)
    return fiat


def check_currency_pairs(syms, include_eur_pairs=False):
    syms = syms.split("-")
    formatted_syms = []
    for sym in syms:
        formatted_sym = check_currency_pair_spot(sym, include_eur_pairs)
        formatted_syms.append(formatted_sym)
    return formatted_syms


def check_currency_pair_spot(sym, include_eur_pairs=False):
    sym = sym.upper()
    supported_pairs = SUPPORTED_CCY_PAIRS + CCY_PAIRS_VS_EUR if include_eur_pairs else SUPPORTED_CCY_PAIRS
    if sym not in supported_pairs:
        raise Exception('Unsupported currency pair:', sym, 'Supported currency pairs:', supported_pairs)
    return sym


def check_currencies(syms):
    checked_syms = []
    for sym in syms:
        checked_syms.append(check_currency(sym))
    return checked_syms


def check_currency(sym):
    sym = sym.upper()
    if sym not in SUPPORTED_CURRENCIES:
        raise Exception('Unsupported currency:', sym, 'Supported currencies:', SUPPORTED_CURRENCIES)
    return sym


def keep_support_currencies(df, supported_currencies):
    df['sym'] = df['sym'].str.upper()
    df = df.loc[df['sym'].isin(supported_currencies)]
    return df
