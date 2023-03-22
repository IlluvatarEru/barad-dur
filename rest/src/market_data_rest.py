import json
import time
from abc import ABC, abstractmethod
from http import HTTPStatus

import requests

from core.src.date import today_date
from rest.src.api_utils import get_header_key_col, get_header_signature_col, get_api_url
from rest.src.request_types import GET, make_request


class MarketDataRestApi(ABC):
    """
    A base class for all Market Data REST APIs
    Child classes names should be MarketDataRestApi<Market><InstrumentType>

    When adding a method that should be enforced on all children, use @abstractmethod
    """

    def __init__(self,
                 market,
                 instrument_type,
                 public_path='',
                 private_path='',
                 public_key=None,
                 private_key=None):
        """

        :param market:
        :param instrument_type:
        :param public_path:
        :param private_path:
        :param public_key:
        :param private_key:
        """
        self.market = market
        self.instrument_type = instrument_type
        self.session = requests.Session()
        # The base url of the API depends on the market and instrument type
        self.api_url = get_api_url(market, instrument_type)

        # When doing private queries, the name of the header columns used to pass the signature and API key
        self.header_key_col = get_header_key_col(market, instrument_type)
        self.header_signature_col = get_header_signature_col(market, instrument_type)

        # Optional, some APIs have 2 different routes for public and private queries
        self.public_path = public_path
        self.private_path = private_path
        # Optional, if doing only public queries then it is not required
        self.public_key = public_key
        self.private_key = private_key

    @staticmethod
    def _nonce():
        """
        Nonce counter.
        :returns: int, an always-increasing unsigned integer (up to 64 bits wide)
        """
        return int(1000 * time.time())

    def _query_public(self, method, timeout=10, headers=None, params=None, data=None, request_type=GET) -> json:
        """
        Used to query the public endpoints

        :param method:
        :param timeout:
        :param headers:
        :param params: dict, arguments for the endpoints
        :param data:dict, data to be attached to the body
        :param request_type: str, 'GET or 'POST'
        :return:
        """
        if headers is None:
            headers = {}
        if data is None:
            data = {}

        # the url is composed of the base url + the route to public if any + the endpoint itself
        url = self.api_url + self.public_path + method
        # @TODO: remove once we have a logger
        print(f'\nurl={url}')
        print(f'\ndata={data}')

        response = make_request(self.session, url, timeout, headers, params, data, request_type)

        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            return self.process_error(response)

    def _query_private(self, method, timeout=10, headers=None, params=None, data=None, request_type=GET):
        """
        Query private information

        :param method:
        :param timeout:
        :param headers:
        :param params: dict, arguments for the endpoints
        :param data:dict, data to be attached to the body
        :param request_type:
        :return:
        """
        if data is None:
            data = {}
        data['nonce'] = self._nonce()

        method_path = self.private_path + method
        url = self.api_url + method_path

        if headers is None:
            if not self.public_key:
                raise Exception('Public key is not set!')
            if not self.private_key:
                raise Exception('Private key is not set!')
            signature = self._sign(data, method_path)

            headers = {
                self.header_key_col: self.public_key,
                self.header_signature_col: signature
            }

        response = make_request(self.session, url, timeout, headers, params, data, request_type)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        else:
            return self.process_error(response)

    @abstractmethod
    def _sign(self, data, method_path):
        """
        Used to sign request to private endpoints. Each Exchange has its own method of signing

        :param data: dict
        :param method_path: str
        :return:
        """
        pass

    @abstractmethod
    def format_sym_for_market(self, sym):
        """
        Format the sym to the exchange format

        :param sym: str
        :return: str
        """
        pass

    @abstractmethod
    def format_crypto_back(self, crypto):
        """
        Format the crypto back from the exchange format to our standard forma

        :param crypto:
        :return:
        """
        pass

    @abstractmethod
    def format_fiat_back(self, fiat):
        """
        Format the fiat back from the exchange format to our standard forma

        :param fiat:
        :return:
        """
        pass

    @abstractmethod
    def process_error(self, response):
        """
        Used to process an error received from the endpoint

        :param response: session.response
        :return:
        """
        pass

    @abstractmethod
    def get_tob_bid(self, sym) -> float:
        """

        :param sym: str
        :return: float, top of book (tob) bid price
        """
        pass

    @abstractmethod
    def get_tob_ask(self, sym) -> float:
        """

        :param sym: str
        :return: float, top of book (tob) ask price
        """
        pass

    @abstractmethod
    def get_tob_mid(self, sym) -> float:
        """

        :param sym: str
        :return: float, top of book (tob) mid price
        """
        pass

    @abstractmethod
    def get_tob_spread(self, sym) -> float:
        """

        :param sym: str
        :return: float, top of book (tob) spread
        """
        pass

    @abstractmethod
    def get_orderbook(self, sym, n_levels):
        """
        Returns the orderbook for the first n_levels

        :param sym: str
        :param n_levels: int
        :return: an orderbook, i.e. a pd.DataFrane with columns [TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET,
            BID_SIZES, BID_PRICES,ASK_SIZES, ASK_PRICES, MISC]
        """
        pass

    @abstractmethod
    def get_ohlc(self, sym, since=None, interval=None):
        """
        Returns the ohlc data from start_timestamp at window interval

        :param sym: str
        :param since: timestamp
        :param interval: int, frequency in minutes
        :return: a pd.DataFrame with the following columns
        """
        pass

    @abstractmethod
    def get_close(self, sym, d=today_date()):
        """
        Returns the closing price at date d for sym

        :param sym: str
        :param d: timestamp
        :return: float
        """
        pass

    @abstractmethod
    def get_fee_schedule(self, sym):
        """
        Retrieves the fee schedule

        :param sym: str
        :return: dict, with keys ['fees_taker', 'fees_maker', 'fee_volume_currency']
        """
        pass
