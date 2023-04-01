import base64
import datetime
import hashlib
import hmac
import urllib

import pandas as pd

from core.src.column_names import PRICE, MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_PRICES, ASK_SIZES, \
    ASK_PRICES, \
    BID_SIZES, SIZE, MISC, RESULT, BIDS, ASKS, \
    TIMESTAMP, OPEN, CLOSE, HIGH, LOW, TIME
from core.src.date import get_current_timestamp, today_date, convert_expiry_to_deribit_format, to_date, \
    get_yesterday_timestamp, date_to_timestamp
from core.src.instrument_types import OPTION
from core.src.markets import DERIBIT
from core.src.option_syms import check_currency_pair_option
from core.src.spot_syms import split_currency_pair_into_lhs_rhs
from rest.src.market_data_rest import MarketDataRestApi
from rest.src.request_types import GET


class MarketDataRestApiDeribitOption(MarketDataRestApi):
    """
    A base class for Deribit Option Api
    """

    def __init__(self,
                 public_path='public/',
                 private_path='private/',
                 public_key=None,
                 private_key=None):
        """

        :param public_path:
        :param private_path:
        :param public_key:
        :param private_key:
        """
        super().__init__(DERIBIT, OPTION, public_path, private_path, public_key, private_key)

    def _sign(self, data, url_path):
        """
        Sign request data according to Kraken's scheme.
        :param data: dict, API request parameters
        :param url_path: str, API URL path sans host
        :returns: signature digest
        """
        # @TODO: not needed for now, implement later
        pass

    def format_sym_for_market(self, sym):
        """
        Format the sym to the exchange format

        :param sym: str
        :return: str
        """
        # From: C_ETHUSD_230630_1200
        # To: 'ETH-26MAY23-1200-C'
        check_currency_pair_option(sym)
        option_type, sym, expiry, strike = sym.split("_")
        lhs, rhs = split_currency_pair_into_lhs_rhs(sym)
        sym = "-".join([lhs, convert_expiry_to_deribit_format(expiry), strike, option_type])
        return sym

    def format_sym_back(self, sym):
        """
        Format the sym back from the exchange format to our standard format

        :param sym:
        :return:
        """
        # @TODO: not needed for now, implement later
        pass

    def format_crypto_back(self, crypto):
        """
        Format the crypto back from the exchange format to our standard forma

        :param crypto:
        :return:
        """
        # @TODO: not needed for now, implement later
        pass

    def format_fiat_back(self, fiat):
        """
        Format the fiat back from the exchange format to our standard forma

        :param fiat:
        :return:
        """
        # @TODO: not needed for now, implement later
        pass

    def process_error(self, response):
        """
        Used to process an error received from the endpoint

        :param response: session.response
        :return:
        """
        # @TODO: not needed for now, implement later
        pass

    def get_tob_bid(self, sym) -> float:
        """

        :return: float, top of book (tob) bid price
        """
        ob = self.get_orderbook(sym, 1)
        bid = ob[BID_PRICES].values[0][0]
        bid = float(bid)
        return bid

    def get_tob_ask(self, sym) -> float:
        """

        :param sym: str
        :return: float, top of book (tob) ask price
        """
        ob = self.get_orderbook(sym, 1)
        ask = ob[ASK_PRICES].values[0][0]
        ask = float(ask)
        return ask

    def get_tob_mid(self, sym) -> float:
        """

        :param sym: str
        :return: float, top of book (tob) mid price
        """
        bid = self.get_tob_bid(sym)
        ask = self.get_tob_ask(sym)
        mid = 0.5 * (bid + ask)
        return mid

    def get_tob_spread(self, sym) -> float:
        """

        :param sym: str
        :return: float, top of book (tob) spread
        """
        bid = self.get_tob_bid(sym)
        ask = self.get_tob_ask(sym)
        spread = ask - bid
        return spread

    def get_orderbook(self, sym, n_levels):
        """
        Returns the orderbook for the first n_levels

        :param sym: str
        :param n_levels: int
        :return: an orderbook, i.e. a pd.DataFrane with columns [TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET,
            BID_SIZES, BID_PRICES,ASK_SIZES, ASK_PRICES, MISC]
        """

        ticker = self.format_sym_for_market(sym)
        result = self._query_public(method="get_order_book", params={'instrument_name': ticker, "depth": n_levels},
                                    request_type=GET)
        data_ob = result[RESULT]

        # Convert bids and asks to DataFrames
        bids_df = pd.DataFrame(data_ob[BIDS], columns=[PRICE, SIZE])
        asks_df = pd.DataFrame(data_ob[ASKS], columns=[PRICE, SIZE])
        last_updated_timestamp = data_ob[TIMESTAMP]

        # Convert price and size columns to numeric type
        bids_df[[PRICE, SIZE]] = bids_df[[PRICE, SIZE]].apply(pd.to_numeric)
        asks_df[[PRICE, SIZE]] = asks_df[[PRICE, SIZE]].apply(pd.to_numeric)

        ob = pd.DataFrame(data=[[bids_df[SIZE].tolist()[:n_levels],
                                 bids_df[PRICE].tolist()[:n_levels],
                                 asks_df[SIZE].tolist()[:n_levels],
                                 asks_df[PRICE].tolist()[:n_levels]]],
                          columns=[BID_SIZES, BID_PRICES, ASK_SIZES, ASK_PRICES])
        ob[SYM] = sym
        ob[MARKET] = self.market
        ob[MARKET_TIMESTAMP] = last_updated_timestamp
        ob[GATEWAY_TIMESTAMP] = get_current_timestamp()
        ob[MARKET_TIMESTAMP] = ob[MARKET_TIMESTAMP].apply(
            lambda x: datetime.datetime.fromtimestamp(int(x) / 1000))
        ob[GATEWAY_TIMESTAMP] = ob[GATEWAY_TIMESTAMP].apply(
            lambda x: datetime.datetime.fromtimestamp(x))
        ob[MISC] = ''
        ob = ob[[MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_SIZES, BID_PRICES, ASK_SIZES, ASK_PRICES, MISC]]
        return ob

    def get_ohlc(self, sym, since=None, interval=None):
        """
        Returns the ohlc data from start_timestamp at window interval

        :param sym: str
        :param since: timestamp
        :param interval: int, frequency in minutes
        :return: a pd.DataFrame with the following columns
        """
        if interval is None:
            interval = "1D"
        if since is None:
            since = get_yesterday_timestamp()
        elif type(since) != int:
            since = since + datetime.timedelta(days=1)
            since = date_to_timestamp(since)
        ticker = self.format_sym_for_market(sym)
        end_timestamp = int(get_current_timestamp() * 1000)
        result = self._query_public(method="get_tradingview_chart_data", params={'instrument_name': ticker,
                                                                                 "start_timestamp": since,
                                                                                 "end_timestamp": end_timestamp,
                                                                                 "resolution": interval},
                                    request_type=GET)
        result = result[RESULT]
        ohlc = pd.DataFrame.from_dict(result)
        ohlc[[OPEN, CLOSE, HIGH, LOW]] = ohlc[[OPEN, CLOSE, HIGH, LOW]].apply(pd.to_numeric)
        ohlc = ohlc.rename(columns={"ticks": TIME})
        ohlc[TIME] = ohlc[TIME].apply(lambda x: datetime.datetime.fromtimestamp(x / 1000))
        ohlc = ohlc[[TIME, OPEN, CLOSE, HIGH, LOW]]
        return ohlc

    def get_close(self, sym, d=today_date()):
        """
        Returns the closing price at date d for sym

        :param sym: str
        :param d: timestamp
        :return: float
        """
        if type(d) != int:
            d = date_to_timestamp(d)
        start_date_timestamp = int(min(get_current_timestamp(), d))
        start_date = to_date(start_date_timestamp * 1000)
        ohlc = self.get_ohlc(sym, since=start_date_timestamp)
        ohlc[TIME] = ohlc[TIME].apply(lambda x: to_date(x))

        subset = ohlc.loc[ohlc[TIME] == to_date(d)]
        if len(subset) > 0:
            close_price = subset[CLOSE].values[0]
        else:
            raise Exception(f'Failed to get Deribit close for {to_date(d)}')
        return close_price

    def get_fee_schedule(self, sym):
        """
        Retrieves the fee schedule

        :param sym: str
        :return: dict, with keys ['fees_taker', 'fees_maker', 'fee_volume_currency'] where each element is a list of
         list and each sublist has 2 elements, first the usd volume and then the fee percentage
        """

        raise Exception(f'This method is not supported for {self.market}/{self.instrument_type}')
