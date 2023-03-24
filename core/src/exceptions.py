def raise_instrument_type_not_supported_for_market_exception(instrument_type, market):
    raise Exception(f'Instrument type {instrument_type} not supported for market {market}.')


def raise_market_not_supported(market):
    raise Exception(f'Market {market} not supported.')
