import datetime
import os
import unittest

from core import root_folder
from core.src.column_names import MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_SIZES, BID_PRICES, ASK_SIZES, \
    ASK_PRICES, MISC, HIGH, LOW, OPEN, CLOSE, TIME
from core.src.date import today_date
from core.src.future_syms import FUT_ETHUSD_
from core.src.spot_syms import SUPPORTED_FIAT_CURRENCIES

dir_path = os.path.dirname(os.path.realpath(__file__))
root_folder.ROOT_FOLDER = dir_path + '/../../'

from rest.src.market_data_rest_kraken_future import MarketDataRestApiKrakenFuture

FUTURE_ETHUSD = FUT_ETHUSD_ + "230331"


class TestKrakenSpot(unittest.TestCase):

    def test_wrong_sym_is_detected(self):
        kraken_future_api = MarketDataRestApiKrakenFuture()
        wrong_sym = "FI_ETHUSD"
        with self.assertRaises(Exception) as context:
            tob_bid = kraken_future_api.get_tob_bid(wrong_sym)
        self.assertEqual(str(context.exception),
                         f'Future {wrong_sym} has wrong format, it should be FUT_LHSRHS_YYMMDD')

        wrong_sym = "FUT_ETHUSD"
        with self.assertRaises(Exception) as context:
            tob_bid = kraken_future_api.get_tob_bid(wrong_sym)
        self.assertEqual(str(context.exception),
                         f'Future {wrong_sym} has wrong format, it should be FUT_LHSRHS_YYMMDD')

    def test_tob_prices(self):
        kraken_future_api = MarketDataRestApiKrakenFuture()
        tob_bid = kraken_future_api.get_tob_bid(FUTURE_ETHUSD)
        self.assertGreater(tob_bid, 0)

        tob_ask = kraken_future_api.get_tob_ask(FUTURE_ETHUSD)
        self.assertGreater(tob_ask, tob_bid)

        tob_mid = kraken_future_api.get_tob_mid(FUTURE_ETHUSD)
        self.assertGreater(tob_mid, tob_bid)
        self.assertLess(tob_mid, tob_ask)

        tob_spread = kraken_future_api.get_tob_spread(FUTURE_ETHUSD)
        self.assertGreater(tob_spread, 0)

    def test_orderbook(self):
        kraken_future_api = MarketDataRestApiKrakenFuture()
        n_levels = 3
        ob = kraken_future_api.get_orderbook(FUTURE_ETHUSD, n_levels)
        print(ob)
        self.assertEqual(ob.columns.tolist(),
                         [MARKET_TIMESTAMP, GATEWAY_TIMESTAMP, SYM, MARKET, BID_SIZES, BID_PRICES, ASK_SIZES,
                          ASK_PRICES,
                          MISC])
        self.assertEqual(len(ob), 1)
        self.assertEqual(len(ob[BID_SIZES].values[0]), n_levels)
        self.assertEqual(len(ob[BID_PRICES].values[0]), n_levels)
        self.assertEqual(len(ob[ASK_SIZES].values[0]), n_levels)
        self.assertEqual(len(ob[ASK_PRICES].values[0]), n_levels)

        self.assertTrue(ob[BID_SIZES].values[0][0] >= 0)
        self.assertTrue(ob[BID_PRICES].values[0][0] >= 0)
        self.assertTrue(ob[ASK_SIZES].values[0][0] >= 0)
        self.assertTrue(ob[ASK_PRICES].values[0][0] >= 0)

    def test_fee_schedule(self):
        kraken_future_api = MarketDataRestApiKrakenFuture()
        fees = kraken_future_api.get_fee_schedule(FUTURE_ETHUSD)
        self.assertTrue(len(fees['fees_taker']) > 0)
        self.assertTrue(len(fees['fees_maker']) > 0)
        self.assertTrue(fees['fees_taker'][0][1] >= 0)
        self.assertTrue(fees['fees_taker'][0][1] >= 0)
        self.assertTrue(fees['fee_volume_currency'] in SUPPORTED_FIAT_CURRENCIES)

    def test_ohlc(self):
        kraken_future_api = MarketDataRestApiKrakenFuture()
        ohlc = kraken_future_api.get_ohlc(FUTURE_ETHUSD)
        max_date = ohlc[TIME].max().date()
        self.assertEqual(type(max_date), datetime.date)
        self.assertEqual(max_date, today_date())

        # check prices are >=0
        self.assertTrue(ohlc.iloc[0][OPEN] >= 0)
        self.assertTrue(ohlc.iloc[0][CLOSE] >= 0)
        self.assertTrue(ohlc.iloc[0][HIGH] >= 0)
        self.assertTrue(ohlc.iloc[0][LOW] >= 0)

    def test_close(self):
        kraken_future_api = MarketDataRestApiKrakenFuture()
        close_price = kraken_future_api.get_close(FUTURE_ETHUSD)
        self.assertTrue(close_price >= 0)
