import base64
import hashlib
import hmac
import urllib

import pandas as pd

from core.src.column_names import PRICE, TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_PRICES, ASK_SIZES, ASK_PRICES, \
    BID_SIZES, SIZE, MISC, FEES, FEES_MAKER, FEES_TAKER, RESULT, PAIR
from core.src.date import get_current_timestamp
from core.src.instrument_types import SPOT
from core.src.markets import KRAKEN
from core.src.syms import split_currency_pair_into_lhs_rhs, BTC
from rest.src.market_data_rest import MarketDataRestApi
from rest.src.request_types import POST


class MarketDataRestApiKrakenSpot(MarketDataRestApi):
    """
    A base class for Kraken Spot Api
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
        super().__init__(KRAKEN, SPOT, public_path, private_path, public_key, private_key)

    def _sign(self, data, url_path):
        """
        Sign request data according to Kraken's scheme.
        :param data: dict, API request parameters
        :param url_path: str, API URL path sans host
        :returns: signature digest
        """
        post_data = urllib.parse.urlencode(data)

        # Unicode-objects must be encoded before hashing
        encoded = (str(data['nonce']) + post_data).encode()
        message = url_path.encode() + hashlib.sha256(encoded).digest()

        signature = hmac.new(base64.b64decode(self.private_key),
                             message, hashlib.sha512)
        sig_digest = base64.b64encode(signature.digest())

        return sig_digest.decode()

    def format_sym_for_market(self, sym):
        """
        Format the sym to the exchange format

        :param sym: str
        :return: str
        """
        # Sometimes it is XBT sometimes BTC
        # needs Z prefix before fiat and X before crypto part

        crypto, fiat = split_currency_pair_into_lhs_rhs(sym)
        if crypto == BTC:
            crypto = 'XBT'
        sym = "X" + crypto + "Z" + fiat
        return sym

    def format_sym_back(self, sym):
        """
        Format the sym back from the exchange format to our standard format

        :param sym:
        :return:
        """
        # fiat is always 3 letters
        fiat = sym[-3:]
        fiat = self.format_fiat_back(sym)
        crypto = self.format_crypto_back(sym[:-4])
        return crypto + fiat

    def format_crypto_back(self, crypto):
        """
        Format the sym back from the exchange format to our standard forma

        :param crypto:
        :return:
        """
        if len(crypto) == 3:
            return crypto
        elif crypto[0] == 'X':
            return crypto[1:]
        else:
            raise Exception(f'Failed to convert back to fiat: {crypto}')

    def format_fiat_back(self, fiat):
        """
        Format the sym back from the exchange format to our standard forma

        :param fiat:
        :return:
        """
        if len(fiat) == 3:
            return fiat
        elif fiat[0] == 'Z':
            return fiat[1:]
        else:
            raise Exception(f'Failed to convert back to fiat: {fiat}')

    def process_error(self, response):
        """
        Used to process an error received from the endpoint

        :param response: session.response
        :return:
        """
        pass

    def get_ticker_info(self, sym):
        """
        Returns ticker info as described:
        https://docs.kraken.com/rest/#tag/Market-Data/operation/getTickerInformation

        :param sym:
        :return:
        """
        ticker = self.format_sym_for_market(sym)
        ticker_info = self._query_public(method="Ticker", data={PAIR: ticker}, request_type=POST)
        return ticker_info

    def get_tob_bid(self, sym) -> float:
        """

        :return: float, top of book (tob) bid price
        """
        ticker = self.format_sym_for_market(sym)
        ticker_info = self.get_ticker_info(sym)
        bid = ticker_info[RESULT][ticker]['b'][0]
        return float(bid)

    def get_tob_ask(self, sym) -> float:
        """

        :param sym: str
        :return: float, top of book (tob) ask price
        """
        ticker = self.format_sym_for_market(sym)
        ticker_info = self.get_ticker_info(sym)
        ask = ticker_info[RESULT][ticker]['a'][0]
        return float(ask)

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
        result = self._query_public(method="Depth", data={PAIR: ticker, "count": n_levels}, request_type=POST)
        data_ob = result[RESULT][ticker]

        # Convert bids and asks to DataFrames
        bids_df = pd.DataFrame(data_ob['bids'], columns=[PRICE, SIZE, TIMESTAMP])
        asks_df = pd.DataFrame(data_ob['asks'], columns=[PRICE, SIZE, TIMESTAMP])
        timestamps = set(bids_df[TIMESTAMP].tolist() + asks_df[TIMESTAMP].tolist())
        last_updated_timestamp = max(timestamps)

        # Convert price and size columns to numeric type
        bids_df[[PRICE, SIZE]] = bids_df[[PRICE, SIZE]].apply(pd.to_numeric)
        asks_df[[PRICE, SIZE]] = asks_df[[PRICE, SIZE]].apply(pd.to_numeric)

        ob = pd.DataFrame(data=[[bids_df[SIZE].tolist(),
                                 bids_df[PRICE].tolist(),
                                 asks_df[SIZE].tolist(),
                                 asks_df[PRICE].tolist()]],
                          columns=[BID_SIZES, BID_PRICES, ASK_SIZES, ASK_PRICES])
        ob[SYM] = sym
        ob[MARKET] = self.market
        ob[TIMESTAMP] = last_updated_timestamp
        ob[GATEWAY_TIMESTAMP] = get_current_timestamp()
        ob[MISC] = ''
        return ob[[TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_SIZES, BID_PRICES, ASK_SIZES,
                   ASK_PRICES, MISC]]

    def get_fee_schedule(self, sym):
        """
        Retrieves the fee schedule

        :param sym: str
        :return: dict, with keys ['fees_taker', 'fees_maker', 'fee_volume_currency']
        """
        fees = {}
        ticker = self.format_sym_for_market(sym)
        result = self._query_public(method="AssetPairs", data={PAIR: ticker}, request_type=POST)
        result = result[RESULT][ticker]
        fees[FEES_TAKER] = result[FEES]
        fees[FEES_MAKER] = result[FEES_MAKER]
        fee_currency = result['fee_volume_currency']
        fees['fee_volume_currency'] = self.format_fiat_back(fee_currency)
        return fees
