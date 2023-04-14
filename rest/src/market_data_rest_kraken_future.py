import base64
import datetime
import hashlib
import hmac

import pandas as pd

from core.src.column_names import PRICE, MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_PRICES, ASK_SIZES, \
    ASK_PRICES, \
    BID_SIZES, SIZE, MISC, FEES_MAKER, FEES_TAKER, LOW, OPEN, CLOSE, HIGH, TIME, BIDS, ASKS, SYMBOL
from core.src.date import get_current_timestamp, today_date, to_date
from core.src.future_syms import FUT_, check_currency_pair_future
from core.src.instrument_types import FUTURE
from core.src.markets import KRAKEN
from core.src.spot_syms import USD
from rest.src.market_data_rest import MarketDataRestApi
from rest.src.request_types import GET

# Kraken Future API uses 3 different endpoints
# see https://docs.futures.kraken.com/#introduction-api-urls
DERIVATIVES_API = "derivatives/api/v3/"
HISTORY_API = "api/history/v2/"
CHART_API = "api/charts/v1/"


class MarketDataRestApiKrakenFuture(MarketDataRestApi):
    """
    Kraken Future Api
    """

    def __init__(self,
                 public_path='/',
                 private_path='/',
                 public_key=None,
                 private_key=None):
        """

        :param public_path:
        :param private_path:
        :param public_key:
        :param private_key:
        """
        super().__init__(KRAKEN, FUTURE, public_path, private_path, public_key, private_key)

    def _sign(self, data, url_path):
        """
        Sign request data according to Kraken's scheme.
        :param data: dict, API request parameters
        :param url_path: str, API URL path sans host
        :returns: signature digest
        """
        nonce = self._nonce()
        message = data + nonce + url_path

        # step 2: hash the result of step 1 with SHA256
        sha256_hash = hashlib.sha256()
        sha256_hash.update(message.encode('utf8'))
        hash_digest = sha256_hash.digest()

        # step 3: base64 decode private_key
        secretDecoded = base64.b64decode(self.private_key)

        # step 4: use result of step 3 to has the result of step 2 with HMAC-SHA512
        hmac_digest = hmac.new(secretDecoded, hash_digest, hashlib.sha512).digest()

        # step 5: base64 encode the result of step 4 and return
        signature = base64.b64encode(hmac_digest)
        return signature

    def format_sym_for_market(self, sym):
        """
        Format the sym to the exchange format

        :param sym: str
        :return: str
        """
        check_currency_pair_future(sym)
        sym = sym.replace(FUT_, "FI_")
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
        ccy = crypto + fiat
        return ccy

    def format_crypto_back(self, crypto):
        """
        Format the crypto back from the exchange format to our standard forma

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
        Format the fiat back from the exchange format to our standard forma

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

        # @TODO: not needed for now, implement later
        pass

    def get_tob_bid(self, sym) -> float:
        """

        :return: float, top of book (tob) bid price
        """
        ticker = self.format_sym_for_market(sym)
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
        result = self._query_public(method=DERIVATIVES_API + "orderbook", params={SYMBOL: ticker}, request_type=GET)
        data_ob = result['orderBook']
        timestamp = result['serverTime']
        format_string = "%Y-%m-%dT%H:%M:%S.%fZ"
        timestamp = datetime.datetime.strptime(timestamp, format_string)
        # Convert bids and asks to DataFrames
        bids_df = pd.DataFrame(data_ob[BIDS], columns=[PRICE, SIZE])
        asks_df = pd.DataFrame(data_ob[ASKS], columns=[PRICE, SIZE])

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
        ob[MARKET_TIMESTAMP] = timestamp
        ob[GATEWAY_TIMESTAMP] = get_current_timestamp()
        ob[GATEWAY_TIMESTAMP] = ob[GATEWAY_TIMESTAMP].apply(
            lambda x: datetime.datetime.fromtimestamp(x))
        ob[MISC] = ''
        ob = ob[[MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_SIZES, BID_PRICES, ASK_SIZES,
                 ASK_PRICES, MISC]]
        return ob

    def get_ohlc(self, sym, since=None, interval=None):
        """
        Returns the ohlc data from start_timestamp at window interval

        :param sym: str
        :param since: timestamp
        :param interval: int, frequency in minutes
        :return: a pd.DataFrame with the following columns
        """
        if interval is not None:
            raise Exception("Kraken Future OHLC method cannot look back.")
        ticker = self.format_sym_for_market(sym)
        result = self._query_public(method=CHART_API + "mark/" + ticker + '/1d', request_type=GET)
        result = result['candles']
        cols = [TIME, OPEN, HIGH, LOW, CLOSE, "vwap", "volume", "count"]
        ohlc = pd.DataFrame(result, columns=cols)
        ohlc[TIME] = ohlc[TIME].apply(lambda x: datetime.datetime.fromtimestamp(x / 1000))
        ohlc[[OPEN, CLOSE, HIGH, LOW]] = ohlc[[OPEN, CLOSE, HIGH, LOW]].apply(pd.to_numeric)
        return ohlc

    def get_close(self, sym, d=today_date() + datetime.timedelta(days=-1)):
        """
        Returns the closing price at date d for sym

        :param sym: str
        :param d: timestamp
        :return: float
        """
        if d < today_date()+ datetime.timedelta(days=-1):
            raise Exception("Kraken Future OHLC method cannot look back.")
        start_date = today_date()
        ohlc = self.get_ohlc(sym)
        ohlc[TIME] = ohlc[TIME].apply(lambda x: to_date(x))

        subset = ohlc.query(f'{TIME} == @start_date')
        if len(subset) > 0:
            close_price = subset[CLOSE].values[0]
        else:
            raise Exception(f'Failed to get Kraken close for {start_date}')
        return close_price

    def get_fee_schedule(self, sym):
        """
        Retrieves the fee schedule

        :param sym: str
        :return: dict, with keys ['fees_taker', 'fees_maker', 'fee_volume_currency'] where each element is a list of
         list and each sublist has 2 elements, first the usd volume and then the fee percentage
        """
        result = self._query_public(method=DERIVATIVES_API + "feeschedules/", request_type=GET)
        result = result["feeSchedules"]
        main_fee_schedule = {}
        for r in result:
            if r["name"] == "Tiered fees":
                main_fee_schedule = r
        main_fee_schedule = main_fee_schedule["tiers"]
        fees = {FEES_TAKER: [], FEES_MAKER: []}
        json_data = main_fee_schedule

        for fee in json_data:
            fees[FEES_TAKER].append([fee['usdVolume'], fee['takerFee']])
            fees[FEES_MAKER].append([fee['usdVolume'], fee['makerFee']])

        fees['fee_volume_currency'] = USD
        return fees
