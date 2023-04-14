import pandas as pd

from core.src.exceptions import raise_instrument_type_not_supported_for_market_exception, raise_market_not_supported
from core.src.instrument_types import SPOT, FUTURE
from core.src.markets import KRAKEN, DERIBIT, SUPPORTED_MARKETS
from core.src.constants import PATH_TO_DATA


def get_api_url(market, instrument_type):
    apis = pd.read_csv(PATH_TO_DATA + 'markets_to_apis.csv')
    api_url = apis.query('market == @market and instrument_type == @instrument_type')['api_url']
    if len(api_url) == 1:
        return "https://" + api_url.values[0]
    elif len(api_url) > 1:
        raise Exception(f'Multiple api urls for {market} and {instrument_type}')
    elif len(api_url) == 0:
        raise Exception(f'No api url for {market} and {instrument_type}')


def get_header_key_col(market, instrument_type):
    if market not in SUPPORTED_MARKETS:
        raise_market_not_supported(market)
    if market == KRAKEN:
        if instrument_type == SPOT:
            return 'API-Key'
        elif instrument_type == FUTURE:
            return 'APIKey'
        else:
            raise_instrument_type_not_supported_for_market_exception(instrument_type, market)
    elif market == DERIBIT:
        return "client_id"
    # @TODO @Yves: Add other markets
    else:
        return ""


def get_header_signature_col(market, instrument_type):
    if market not in SUPPORTED_MARKETS:
        raise_market_not_supported(market)
    if market == KRAKEN:
        if instrument_type == SPOT:
            return 'API-Sign'
        elif instrument_type == FUTURE:
            return 'Authent'
        else:
            raise_instrument_type_not_supported_for_market_exception(instrument_type, market)
    elif market == DERIBIT:
        return "client_secret"
    # @TODO @Yves: Add other markets
    else:
        return ""
